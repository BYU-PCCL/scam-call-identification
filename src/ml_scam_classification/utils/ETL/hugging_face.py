from __future__ import annotations

import os
import pandas as pd
from pathlib import Path
from typing import Optional, Union, Dict

from datasets import (
    load_dataset,
    get_dataset_split_names,
    DatasetDict,
    Dataset,
    IterableDataset,
    concatenate_datasets,
)

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
    - If streaming=False: Arrow-concat then convert once (fastest in-memory path).
    - If streaming=True:
        * If split_expr is given: stream the union (no split provenance).
        * If split_expr is None: auto-detect splits, stream each split individually,
          add 'split' column, and write incrementally.
    """
    out_path = Path(out_csv_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if streaming:
        import csv

        # If user provided split_expr, stream union (no per-row split available)
        if split_expr:
            streamed = load_dataset(
                dataset_name, split=split_expr, streaming=True, **load_kwargs
            )
            header_written = False
            with out_path.open("w", newline="", encoding="utf-8") as f:
                writer = None
                for row in streamed:
                    if not header_written:
                        columns = list(row.keys())
                        if add_split_column and "split" not in columns:
                            columns.append("split")  # won't have correct values here
                        writer = csv.DictWriter(f, fieldnames=columns)
                        writer.writeheader()
                        header_written = True
                    # We cannot know the original split in a union expression.
                    if add_split_column:
                        row = dict(row)
                        row.setdefault("split", "unknown")
                    writer.writerow(row)

            # Return a DataFrame (materializes); skip if file is huge
            return pd.read_csv(out_path)

        # No split_expr: discover splits, then stream per split to preserve provenance
        discovered_splits = get_dataset_split_names(dataset_name, **load_kwargs)
        header_written = False
        columns = None

        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = None
            for sp in discovered_splits:
                it = load_dataset(
                    dataset_name, split=sp, streaming=True, **load_kwargs
                )
                for row in it:
                    if not header_written:
                        columns = list(row.keys())
                        if add_split_column and "split" not in columns:
                            columns.append("split")
                        writer = csv.DictWriter(f, fieldnames=columns)
                        writer.writeheader()
                        header_written = True

                    if add_split_column:
                        row = dict(row)
                        row["split"] = sp
                    writer.writerow(row)

        return pd.read_csv(out_path)

    # -------- Non-streaming path (fastest if it fits in RAM) --------
    ds = load_dataset(dataset_name, **load_kwargs)  # usually a DatasetDict
    if isinstance(ds, DatasetDict):
        parts = []
        for split_name, d in ds.items():
            parts.append(d.add_column("split", [split_name] * len(d)) if add_split_column else d)
        all_d = concatenate_datasets(parts) if len(parts) > 1 else parts[0]
        df_all = all_d.to_pandas()
        df_all.to_csv(out_path, index=False)
        return df_all

    if isinstance(ds, Dataset):
        df_all = ds.to_pandas()
        if add_split_column and "split" not in df_all.columns:
            df_all["split"] = "unknown"
        df_all.to_csv(out_path, index=False)
        return df_all

    if isinstance(ds, IterableDataset):
        # Extremely uncommon here because streaming=False, but handle gracefully.
        rows = list(ds)
        df_all = pd.DataFrame(rows)
        if add_split_column and "split" not in df_all.columns:
            df_all["split"] = "unknown"
        df_all.to_csv(out_path, index=False)
        return df_all

    raise TypeError(f"Unsupported dataset type: {type(ds)}")
