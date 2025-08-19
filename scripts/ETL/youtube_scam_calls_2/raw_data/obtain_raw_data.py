import os
import pandas as pd

from src.ml_scam_classification.utils.ETL.hugging_face import get_store_HF_ds_all_splits

if __name__ == "__main__":
    # write transcript data to destination
    DEFAULT_DATA_PATH = "src\\ml_scam_classification\\data\\youtube_scam_calls_2"
    CSV_WRITEPATH = os.path.join(DEFAULT_DATA_PATH, 'raw_data\\data.csv')


    # Read dataset from HuggingFace, puts all splits into csv and stores
    get_store_HF_ds_all_splits(
        dataset_name="BothBosu/youtube-scam-conversations",
        out_csv_path=CSV_WRITEPATH,
        streaming=True
    )
