import os
import pandas as pd

from datasets import load_dataset

from src.general_file_utils.utils.path_checks import assert_path_exists
from src.general_file_utils.utils.json import load_json_from_path
from src.general_file_utils.utils.folder_contents_utils import get_subfolder_paths
from src.general_file_utils.utils.csv_utils import append_df_rows_to_csv

if __name__ == "__main__":
    # write transcript data to destination
    youtube_scam_calls_2 = "src\\ml_scam_classification\\data\\youtube_scam_calls_2"
    DEFAULT_DATA_PATH = os.path.join(youtube_scam_calls_2, "raw_data")

    # Read dataset from HuggingFace
    ds = load_dataset("BothBosu/youtube-scam-conversations")

    # Convert all splits into DataFrames and add a "split" column
    dfs = []
    for split_name in ds.keys():
        df_split = ds[split_name].to_pandas()
        df_split["split"] = split_name  # track where each row came from
        dfs.append(df_split)

    # combine into one df
    df = pd.concat(dfs, ignore_index=True)

    # store raw data in storage location
    df.to_csv(os.path.join(DEFAULT_DATA_PATH, 'datatest.csv'))
    # TODO - implement overwrite if anything already present with confirmation prompt

    print("\nComplete!")
