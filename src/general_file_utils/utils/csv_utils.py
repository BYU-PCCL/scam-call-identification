import csv
import pandas as pd

from src.general_file_utils.utils.str_formatting import (
    format_self_contained_item_pretty,
    format_title
)


def assert_is_df(data):
    """Ensure the object is a pandas DataFrame."""
    if not isinstance(data, pd.DataFrame):
        raise ValueError(f"Attempted to assert type as df for: {type(data)}")


def write_df_to_csv(path, df):
    """Write a DataFrame to CSV, overwriting if it exists."""
    assert_is_df(df)
    df.to_csv(path, index=False)


def get_first_row_csv(path, separator=','):
    """
    Read only the first row of a CSV.
    Robust to quoted fields and embedded newlines inside quotes.
    """
    with open(path, 'r', newline='') as file:
        reader = csv.reader(file, delimiter=separator)
        return next(reader, [])


def append_df_rows_to_csv(path_to_csv, df):
    """
    Append rows of a DataFrame to an existing CSV.
    Header is omitted to avoid duplication.
    """
    assert_is_df(df)
    df.to_csv(path_to_csv, mode='a', index=False, header=False)


def print_entries_pretty(
        path=None,
        df=None,
        row_ranges=None,  # list of (start, end) index ranges to print (end exclusive)
        chars_per_row=80,
        space_padding=3,
        values_indentation=12,
        title_divider_char='#',
        title_side_char='#',
        title_line_width=29,
        title_indent=0,
        trunc_str="...(TRUNC.)",
        max_output_len=None
):
    """
    Pretty-print selected rows from a CSV (read efficiently with skiprows/nrows)
    or from an in-memory DataFrame (sliced directly).

    Each value is rendered with format_self_contained_item_pretty, which is newline-aware.

    Parameters
    ----------
    path : str, optional
        Path to CSV file.
    df : pd.DataFrame, optional
        DataFrame to pretty print.
    row_ranges : list of (start, end) tuples
        Row index ranges to print (end exclusive).
        Example: [(0, 5), (100, 105)] prints first 5 and rows 100–104.
    chars_per_row : int
        Width of each formatted line (including borders and padding).
    space_padding : int
        Spaces to left/right of values inside box borders.
    values_indentation : int
        Spaces to indent each printed value block.
    title_divider_char : str
        Character used to build divider lines around row titles.
    title_side_char : str
        Character used as border around row title.
    title_line_width : int
        Width of row title boxes.
    title_indent : int
        Indentation for row titles.
    trunc_str : str
        String used when truncating long values.
    max_output_len : int or None
        Maximum length of value string before truncation.
    """
    neither = (path is None) and (df is None)
    both = (path is not None) and (df is not None)
    if neither or both:
        raise ValueError("Provide either a path or a df, but not both.")

    if not row_ranges:
        raise ValueError("Must provide row_ranges, e.g. [(0, 5), (100, 105)].")

    # Collect relevant slices
    slices = []
    if path is not None:
        for (start, end) in row_ranges:
            if start < 0 or end <= start:
                continue
            nrows = end - start
            # skiprows skips header too, so adjust to keep header at top
            chunk = pd.read_csv(path, skiprows=range(1, start + 1), nrows=nrows)
            slices.append(chunk)
        df = pd.concat(slices, axis=0)
        # Reset index to reflect original row indices
        df.index = [i for (start, end) in row_ranges for i in range(start, end)]
    else:
        for (start, end) in row_ranges:
            if start < 0 or end > len(df) or end <= start:
                raise IndexError(
                    f"Range {(start, end)} invalid for DataFrame of length {len(df)}"
                )
            slices.append(df.iloc[start:end])
        df = pd.concat(slices, axis=0)

    # Pretty print each row
    for i, row in df.iterrows():
        # Title for the row
        print("\n\n" + format_title(
            f"ROW {i}",
            divider_char=title_divider_char,
            side_char=title_side_char,
            line_width=title_line_width,
            n_topbottom_dividers=2,
            indent=title_indent
        ), end="")

        # Print each column/value
        for col_name, row_value in row.items():
            print(f"\n      (ROW {i}) - {col_name}")
            print(format_self_contained_item_pretty(
                item=row_value,
                line_width_chars=chars_per_row,
                space_padding=space_padding,
                indent=values_indentation,
                trunc_str=trunc_str,
                max_output_len=max_output_len
            ))
