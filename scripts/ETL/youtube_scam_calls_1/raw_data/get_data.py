# Install dependencies as needed:
# pip install kagglehub[pandas-datasets]
import kagglehub
import pandas as pd
from kagglehub import KaggleDatasetAdapter

from src.ml_scam_detector.utils.file_utils import make_dir_rec

if __name__ == "__main__":
    PATH_TO_WRITE_DATA = "src/ml_scam_detector/data/youtube_scam_calls_1/raw_data/YT_scams_1.csv"

    # path to kaggle
    kaggle_dataset_rel_path = "FullTranscriptData.csv"

    # Load the latest version
    df = kagglehub.load_dataset(
    KaggleDatasetAdapter.PANDAS,
    "rivalcults/youtube-scam-phone-call-transcripts",
    kaggle_dataset_rel_path,
    # Provide any additional arguments like 
    # sql_query or pandas_kwargs. See the 
    # documenation for more information:
    # https://github.com/Kaggle/kagglehub/blob/main/README.md#kaggledatasetadapterpandas
    )

    print("First 5 records:", df.head())

    # make dirs where needed 
    make_dir_rec(PATH_TO_WRITE_DATA)

    df.to_csv(PATH_TO_WRITE_DATA)
