import csv
import pandas as pd

def assert_is_df(data):
    if not (type(data) is pd.DataFrame):
        raise ValueError(f"Attempted to assert type as df for: {data}")

def write_df_to_csv(path, df):
    assert_is_df(df)

    df.to_csv(path, index=False)


def get_first_row_csv(path, separator=','):
    with open(path, 'r', newline='') as file:
        return file.readline().strip().split(separator)


def append_df_rows_to_csv(path_to_csv, df):
    assert_is_df(df)

    """
    assert ["1", "ab"] == ["1", "ab"]

    if df.columns == pd.read_csv(path_to_csv)

    with open(path_to_csv,'a') as fa:
        fa.write(row)
    """

    # TESTING with built-in
    df.to_csv(path_to_csv, mode='a', index=False, header=False)

if __name__ == "__main__":
    append_df_rows_to_csv("test.csv", pd.DataFrame({"id": [3], "color": ["orange"], "cost": ["$3"]}))