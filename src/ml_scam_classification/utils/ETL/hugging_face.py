from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Union, Dict

import pandas as pd
from datasets import load_dataset, concatenate_datasets, DatasetDict, Dataset, IterableDataset


def get_dataset_from_huggingface(
    dataset_name: str,
    *,
    split: Optional[str] = None,
    streaming: bool = False,
    **load_kwargs
) -> Union[DatasetDict, Dataset, IterableDataset]:
    """
    Load a dataset from HuggingFace using `datasets.load_dataset`.

    Parameters
    ----------
    dataset_name : str
        HuggingFace dataset path, e.g. "BothBosu/youtube-scam-conversations".
    split : Optional[str], default None
        If None, returns a DatasetDict (for multi-split datasets).
        If a split expression (e.g. "train" or "train+test+validation"),
        returns a single Dataset (or IterableDataset if streaming=True).
    streaming : bool, default False
        If True, returns an IterableDataset (when split is provided).
    **load_kwargs
        Forwarded to `load_dataset` (e.g., revision, data_dir, trust_remote_code).

    Returns
    -------
    Union[DatasetDict, Dataset, IterableDataset]
    """
    if streaming and split is None:
        raise ValueError("When streaming=True, provide a 'split' (e.g., 'train+test').")

    if split is None:
        # Typical case: return all splits as a DatasetDict
        ds = load_dataset(dataset_name, **load_kwargs)
    else:
        # Single concatenated Dataset (Arrow) or IterableDataset (streaming)
        ds = load_dataset(dataset_name, split=split, streaming=streaming, **load_kwargs)

    return ds


def get_all_HF_ds_splits_as_df(
    ds: Union[DatasetDict, Dataset, IterableDataset],
    *,
    add_split_column: bool = True,
) -> pd.DataFrame:
    """
    Convert all splits to ONE pandas DataFrame.
    - If `ds` is a DatasetDict: Arrow-concatenate splits, then convert once (most efficient).
    - If `ds` is a single Dataset: convert directly.
    - If `ds` is an IterableDataset (streaming): materializes by iterating (least memory-friendly).

    Parameters
    ----------
    ds : DatasetDict | Dataset | IterableDataset
        Object returned by `load_dataset`.
    add_split_column : bool, default True
        Adds a 'split' column preserving the original split for each row (if known).

    Returns
    -------
    pd.DataFrame
    """
    # Case 1: DatasetDict -> concatenate Arrow datasets, then convert once
    if isinstance(ds, DatasetDict):
        parts = []
        for split_name, d in ds.items():
            if add_split_column:
                parts.append(d.add_column("split", [split_name] * len(d)))
            else:
                parts.append(d)
        if len(parts) == 0:
            return pd.DataFrame()
        all_d = concatenate_datasets(parts) if len(parts) > 1 else parts[0]
        return all_d.to_pandas()

    # Case 2: Plain Dataset -> just convert
    if isinstance(ds, Dataset):
        return ds.to_pandas()

    # Case 3: IterableDataset (streaming) -> iterate (no Arrow concat available)
    if isinstance(ds, IterableDataset):
        rows = []
        for row in ds:
            rows.append(row)
        return pd.DataFrame(rows)

    raise TypeError(f"Unsupported dataset type: {type(ds)}")


def get_store_HF_ds_all_splits(
    dataset_name: str,
    out_csv_path: str,
    *,
    add_split_column: bool = True,
    streaming: bool = False,
    split_expr: Optional[str] = None,
    **load_kwargs
) -> pd.DataFrame:
    """
    Load all splits from HuggingFace, merge them, write a single CSV, and return the DataFrame.

    Efficiency strategy
    -------------------
    - If `streaming=False` (default):
        * Load DatasetDict
        * Add 'split' column (optional)
        * Arrow-concat, then `to_pandas()` once, then write CSV
    - If `streaming=True`:
        * Requires `split_expr` like "train+test+validation"
        * Streams rows to CSV without holding everything in memory
        * Also returns a DataFrame (note: this materializes the data; omit if huge)

    Parameters
    ----------
    dataset_name : str
        HuggingFace dataset path.
    out_csv_path : str
        Destination CSV path. Parent directories are created if needed.
    add_split_column : bool, default True
        Include a 'split' provenance column when possible.
    streaming : bool, default False
        Use IterableDataset streaming mode. Requires `split_expr`.
    split_expr : Optional[str], default None
        Split expression (e.g., "train+test+validation"). Required if `streaming=True`.
    **load_kwargs
        Forwarded to `load_dataset`.

    Returns
    -------
    pd.DataFrame
        DataFrame containing all splits (note: can be large).
    """
    out_path = Path(out_csv_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if streaming:
        if not split_expr:
            raise ValueError("When streaming=True, you must provide split_expr (e.g., 'train+test+validation').")

        # Stream rows and write incrementally to CSV
        streamed = get_dataset_from_huggingface(
            dataset_name,
            split=split_expr,
            streaming=True,
            **load_kwargs
        )

        import csv
        header_written = False
        columns = None
        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = None
            for row in streamed:
                # Add split provenance if possible — not available in streaming union.
                # You can compute provenance only if you iterate split-by-split separately.
                if not header_written:
                    columns = list(row.keys())
                    writer = csv.DictWriter(f, fieldnames=columns)
                    writer.writeheader()
                    header_written = True
                writer.writerow(row)

        # If you still want a DataFrame, read back (this loads all into memory).
        df_all = pd.read_csv(out_path)
        return df_all

    # Non-streaming: load all splits, concat at Arrow level, convert once
    ds = get_dataset_from_huggingface(dataset_name, **load_kwargs)  # DatasetDict expected
    if not isinstance(ds, DatasetDict):
        # If the dataset truly has only one split, it might already be a Dataset
        df_all = get_all_HF_ds_splits_as_df(ds, add_split_column=add_split_column)
        df_all.to_csv(out_path, index=False)
        return df_all

    # Build Arrow pieces with optional split column
    parts = []
    for split_name, d in ds.items():
        parts.append(d.add_column("split", [split_name] * len(d)) if add_split_column else d)

    all_d = concatenate_datasets(parts) if len(parts) > 1 else parts[0]
    df_all = all_d.to_pandas()
    df_all.to_csv(out_path, index=False)
    return df_all
