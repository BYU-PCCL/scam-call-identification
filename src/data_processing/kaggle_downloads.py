from __future__ import annotations

import os
import shutil
import sys
import re
from pathlib import Path
from typing import List, Optional, Tuple, Union
from urllib.parse import urlparse, parse_qs, unquote

import kagglehub
from kagglehub import KaggleDatasetAdapter

from src.ml_scam_classification.utils.file_utils import make_dir_rec


class _AuthError(RuntimeError):
    """Raised when Kaggle authentication fails."""


def download_csv_from_kaggle(
    kaggle_url: str,
    save_dir: Union[str, Path],
    *,
    create_path: bool = False,
    overwrite: bool = False,
    download_all_csvs: bool = False,
    interactive_auth_retry: bool = True,
) -> Union[Path, List[Path]]:
    """
    Download CSV file(s) from a Kaggle dataset link and save them under `save_dir` using
    the original Kaggle filenames.

    Behavior (per agreed spec):
    - Strictly validates the URL:
        * Domain must be kaggle.com (any subdomain, e.g., www.kaggle.com, is allowed).
        * Path must start with /datasets/{owner}/{dataset}[...].
        * Supports versioned links (/versions/{n}) and file selection via:
              ?select=FullTranscriptData.csv
              #select=FullTranscriptData.csv
              #fileName=FullTranscriptData.csv
    - When `download_all_csvs=False` (default), the link MUST specify a file with `select=...`.
      That file must end with `.csv`, otherwise a ValueError is raised.
    - When `download_all_csvs=True`, we ignore `select` if present and fetch all CSV files
      in the dataset. This requires KaggleHub to provide dataset-level download; if not
      available in the installed version, we raise a RuntimeError suggesting use of `select=`.
    - `save_dir` must be a directory path (NOT a path ending in `.csv`). We derive final
      filenames from Kaggle and join them to `save_dir`. If the caller passes a path ending
      with `.csv`, we raise ValueError.
    - Path creation:
        * If `create_path=False` and `save_dir` doesn't exist → FileNotFoundError.
        * If `create_path=True`, creates the directory tree using `make_dir_rec`.
    - Overwrite policy:
        * If a target file already exists and `overwrite=False` → FileExistsError.
        * If `overwrite=True`, we overwrite.
    - Authentication:
        * On Kaggle auth failure, we print a clear setup guide (env vars KAGGLE_USERNAME/KAGGLE_KEY
          or ~/.kaggle/kaggle.json) and, if `interactive_auth_retry=True`, pause for Enter and retry once.
          If it still fails, we raise a RuntimeError.
    - Returns:
        * Path to the saved file (Path) for a single-file download.
        * List[Path] for multi-file downloads (`download_all_csvs=True` with multiple CSVs).
    - Side effects:
        * On success, prints exactly:  "saved {filename}.csv at {abs_path}"

    Parameters
    ----------
    kaggle_url : str
        Kaggle dataset URL. Supported forms include:
          - https://www.kaggle.com/datasets/{owner}/{dataset}?select=FullTranscriptData.csv
          - https://www.kaggle.com/datasets/{owner}/{dataset}/versions/{n}?select=subdir%2Ffile.csv
          - ... with anchors #select=... or #fileName=...
    save_dir : str | Path
        Directory in which to save the CSV(s). Must not end with '.csv'.
    create_path : bool, default False
        If True, creates `save_dir` when it doesn't exist. If False and `save_dir` is missing, raises FileNotFoundError.
    overwrite : bool, default False
        If True, overwrite existing files at destination; otherwise raise FileExistsError.
    download_all_csvs : bool, default False
        If True and the link doesn't specify a file, download all CSV files available in the dataset.
        If False (default), the link must specify a `select=<csv-name>`, which must end with '.csv'.
    interactive_auth_retry : bool, default True
        If an auth error occurs, print guidance and wait for user input to retry once.

    Returns
    -------
    pathlib.Path | list[pathlib.Path]
        - Single `Path` when downloading one CSV.
        - `List[Path]` when downloading multiple CSVs.

    Raises
    ------
    ValueError
        - Invalid URL/domain/path; `save_dir` ends with `.csv`; missing `select` when not downloading all;
          selected file not a `.csv` under single-file mode.
    FileNotFoundError
        - `save_dir` does not exist and `create_path=False`.
    FileExistsError
        - Destination file already exists and `overwrite=False`.
    RuntimeError
        - Kaggle fetch failures, auth failures after retry, or inability to gather CSVs when required.

    Examples
    --------
    >>> download_csv_from_kaggle(
    ...     "https://www.kaggle.com/datasets/rivalcults/youtube-scam-phone-call-transcripts?select=FullTranscriptData.csv",
    ...     "data/raw/youtube_scams",
    ...     create_path=True
    ... )
    PosixPath('.../data/raw/youtube_scams/FullTranscriptData.csv')

    >>> download_csv_from_kaggle(
    ...     "https://www.kaggle.com/datasets/rivalcults/youtube-scam-phone-call-transcripts",
    ...     "data/raw/youtube_scams_all",
    ...     create_path=True,
    ...     download_all_csvs=True
    ... )
    [PosixPath('.../FullTranscriptData.csv'), ...]
    """

    dataset_slug, selected_file = _parse_and_validate_kaggle_url(kaggle_url)

    # Directory validation
    save_dir_path = Path(save_dir)
    if save_dir_path.suffix.lower() == ".csv":
        raise ValueError("save_dir must be a directory path, not a '.csv' file path.")

    if not save_dir_path.exists():
        if create_path:
            # Use your helper to create parent dirs in a file-like path.
            # We won't actually create this file; `make_dir_rec` should just ensure directories exist.
            placeholder = save_dir_path / "__placeholder__.csv"
            make_dir_rec(str(placeholder))
        else:
            raise FileNotFoundError(
                f"Directory does not exist: {save_dir_path}. "
                "Pass create_path=True to create it."
            )
    elif not save_dir_path.is_dir():
        raise ValueError(f"save_dir exists but is not a directory: {save_dir_path}")

    # Mode-specific constraints
    if not download_all_csvs:
        if not selected_file:
            raise ValueError(
                "Link must include ?select=<csv-name> (or #select= / #fileName=) "
                "when download_all_csvs=False."
            )
        if not selected_file.lower().endswith(".csv"):
            raise ValueError(
                "Selected file is not a .csv. Either choose a .csv with ?select=... "
                "or set download_all_csvs=True."
            )

    # Execution
    if download_all_csvs:
        return _download_all_csvs(dataset_slug, save_dir_path, overwrite, interactive_auth_retry)
    else:
        # Single CSV
        dest = save_dir_path / Path(selected_file).name
        _ensure_overwrite_policy(dest, overwrite, create_path)
        _download_single_csv(dataset_slug, selected_file, dest, interactive_auth_retry)
        print(f"saved {dest.name} at {dest.resolve()}")
        return dest


# ----------------------------- Helpers ----------------------------- #

def _parse_and_validate_kaggle_url(url: str) -> Tuple[str, Optional[str]]:
    """
    Returns:
        dataset_slug: 'owner/dataset'
        selected_file: relative CSV path if specified; else None
    """
    parsed = urlparse(url)

    # Domain check: accept any subdomain that ends with kaggle.com
    netloc = parsed.netloc.split(":")[0].lower()
    if not (netloc == "kaggle.com" or netloc.endswith(".kaggle.com")):
        raise ValueError(f"URL must be under kaggle.com, got domain: {parsed.netloc}")

    # Path must start with /datasets/{owner}/{dataset}
    # Accept optional /versions/{n} after that.
    path_parts = [p for p in parsed.path.split("/") if p]
    if len(path_parts) < 3 or path_parts[0] != "datasets":
        raise ValueError(
            "Kaggle URL path must start with /datasets/{owner}/{dataset}[...]. "
            f"Got path: {parsed.path}"
        )
    owner = path_parts[1]
    dataset = path_parts[2]
    if not owner or not dataset:
        raise ValueError("Could not extract {owner}/{dataset} from the URL path.")
    dataset_slug = f"{owner}/{dataset}"

    # Extract file selection from query or fragment
    selected_file = None
    q = parse_qs(parsed.query)
    if "select" in q and len(q["select"]) > 0:
        selected_file = unquote(q["select"][0])

    # Handle anchor forms: #select=..., #fileName=...
    if selected_file is None and parsed.fragment:
        frag_q = parse_qs(parsed.fragment)
        if "select" in frag_q and frag_q["select"]:
            selected_file = unquote(frag_q["select"][0])
        elif "fileName" in frag_q and frag_q["fileName"]:
            selected_file = unquote(frag_q["fileName"][0])

    # Normalize relative path if present (strip leading slashes)
    if selected_file:
        selected_file = selected_file.lstrip("/")

    return dataset_slug, selected_file


def _ensure_overwrite_policy(dest: Path, overwrite: bool, create_path: bool) -> None:
    # Ensure parent directory exists if we're allowed to create it (already handled globally),
    # but we also ensure per-file path via your helper to mirror prior usage pattern.
    if create_path and not dest.parent.exists():
        make_dir_rec(str(dest))
    if dest.exists() and not overwrite:
        raise FileExistsError(
            f"Destination file already exists: {dest}. Pass overwrite=True to replace it."
        )


def _download_single_csv(
    dataset_slug: str,
    rel_file_path: str,
    dest: Path,
    interactive_auth_retry: bool,
) -> None:
    """
    Prefer a file-level download when KaggleHub supports it; otherwise fall back to
    loading via pandas and writing out (index=False) to preserve typical CSV shape.
    """
    # Try file-level download if available in this kagglehub version
    if hasattr(kagglehub, "dataset_download_file"):
        local_file = _with_auth_retry(
            lambda: kagglehub.dataset_download_file(dataset_slug, rel_file_path),
            interactive_auth_retry=interactive_auth_retry,
        )
        if not local_file or not Path(local_file).exists():
            raise RuntimeError(
                f"Downloaded file not found via KaggleHub: {local_file}"
            )
        shutil.copy2(local_file, dest)
        return

    # Fallback: use pandas adapter (may alter formatting minimally, but maintains data)
    df = _with_auth_retry(
        lambda: kagglehub.load_dataset(
            KaggleDatasetAdapter.PANDAS,
            dataset_slug,
            rel_file_path,
        ),
        interactive_auth_retry=interactive_auth_retry,
    )
    # Ensure parent dirs exist (your helper)
    make_dir_rec(str(dest))
    # Write without index to match typical Kaggle CSVs
    df.to_csv(dest, index=False)


def _download_all_csvs(
    dataset_slug: str,
    save_dir: Path,
    overwrite: bool,
    interactive_auth_retry: bool,
) -> List[Path]:
    """
    Download all CSV files from a dataset. Requires dataset-level download support.
    """
    if not hasattr(kagglehub, "dataset_download"):
        raise RuntimeError(
            "download_all_csvs=True requires a kagglehub version that supports "
            "`dataset_download`. Please upgrade kagglehub or pass a link with ?select=<csv-name>."
        )

    local_dir = _with_auth_retry(
        lambda: kagglehub.dataset_download(dataset_slug),
        interactive_auth_retry=interactive_auth_retry,
    )
    local_dir = Path(local_dir)
    if not local_dir.exists():
        raise RuntimeError(f"KaggleHub returned a non-existent path: {local_dir}")

    csv_files = sorted(local_dir.rglob("*.csv"))
    if not csv_files:
        raise RuntimeError("No .csv files found in the dataset.")

    saved_paths: List[Path] = []
    seen_names: set[str] = set()
    for src in csv_files:
        # Prevent filename collisions when different subdirs share the same basename.
        # If collision occurs and overwrite is False, raise an error.
        dest = save_dir / src.name
        if src.name in seen_names and not overwrite:
            raise FileExistsError(
                f"Multiple CSVs share the same filename '{src.name}'. "
                f"Use overwrite=True or move existing files."
            )
        _ensure_overwrite_policy(dest, overwrite, create_path=True)
        shutil.copy2(src, dest)
        print(f"saved {dest.name} at {dest.resolve()}")
        saved_paths.append(dest)
        seen_names.add(src.name)

    return saved_paths


def _with_auth_retry(func, interactive_auth_retry: bool):
    """
    Execute a KaggleHub call with a guided, one-time interactive retry on authentication errors.
    """
    try:
        return func()
    except Exception as e:
        if _looks_like_auth_error(e):
            _print_auth_help()
            if interactive_auth_retry:
                try:
                    input("Set credentials, then press Enter to retry once...")
                except EOFError:
                    # Non-interactive context
                    pass
                # Retry once
                try:
                    return func()
                except Exception as e2:
                    if _looks_like_auth_error(e2):
                        raise _AuthError(
                            "Kaggle authentication failed after retry. "
                            "Please verify your credentials and try again."
                        ) from e2
                    raise RuntimeError("Kaggle operation failed.") from e2
            raise _AuthError(
                "Kaggle authentication required. Re-run with interactive_auth_retry=True "
                "or set credentials and try again."
            ) from e
        # Not an auth error → propagate as a general runtime error
        raise RuntimeError("Kaggle operation failed.") from e


def _looks_like_auth_error(exc: Exception) -> bool:
    """
    Heuristic detection since kagglehub exception classes can vary by version.
    """
    msg = f"{type(exc).__name__}: {exc}".lower()
    auth_markers = [
        "unauthorized", "forbidden", "401", "403",
        "credentials", "kaggle_username", "kaggle_key",
        "not authenticated", "authentication",
    ]
    return any(m in msg for m in auth_markers)


def _print_auth_help() -> None:
    guide = """
Kaggle authentication required.

Option 1 (Environment variables):
  export KAGGLE_USERNAME=<your_username>
  export KAGGLE_KEY=<your_api_key>

Option 2 (kaggle.json file):
  Create ~/.kaggle/kaggle.json with:
    { "username": "<your_username>", "key": "<your_api_key>" }
  and ensure permissions are restricted (e.g., chmod 600).

After setting credentials, press Enter to retry (if interactive_auth_retry=True).
"""
    sys.stderr.write(guide)
