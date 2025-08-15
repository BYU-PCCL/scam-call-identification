# Install dependencies as needed:
# pip install kagglehub[pandas-datasets]
import kagglehub
import pandas as pd
from kagglehub import KaggleDatasetAdapter

if __name__ == "__main__":
    DATA_WRITE_PATH = "src/ml_scam_detector/data/youtube_scam_calls_1/raw_data/YT_scams_1.csv"

    kaggle_rel_file_path = "FullTranscriptData.csv"

    # Load the latest version
    df = kagglehub.load_dataset(
    KaggleDatasetAdapter.PANDAS,
    "rivalcults/youtube-scam-phone-call-transcripts",
    kaggle_rel_file_path,
    # Provide any additional arguments like 
    # sql_query or pandas_kwargs. See the 
    # documenation for more information:
    # https://github.com/Kaggle/kagglehub/blob/main/README.md#kaggledatasetadapterpandas
    )

    print("First 5 records:", df.head())

    df.to_csv(DATA_WRITE_PATH)
