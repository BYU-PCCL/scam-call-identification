import pandas as pd

from src.general_file_utils.utils.csv_utils import print_entries_pretty
from src.general_file_utils.utils.path_strings import get_path_of_file_w_latest_unix_timestamp

if __name__ == "__main__":
    # get whichever path ends with the most recent unix timestamp
    dir = "src/ml_scam_classification/data/compiled"
    path = get_path_of_file_w_latest_unix_timestamp(dir)

    df = pd.read_csv(path)

    print_entries_pretty(
        path=None,
        df=df,
        row_ranges=[(0,1),(1600,1601),(1669,1670),(1910,1911)],
        chars_per_row=80,
        space_padding=3,
        values_indentation=12,
        title_divider_char='#',
        title_side_char='#',
        title_line_width=29,
        title_indent=0,
        trunc_str="...(TRUNC.)",
        max_output_len=None
    )