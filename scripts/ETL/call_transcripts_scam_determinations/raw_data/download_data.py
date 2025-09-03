import kagglehub

from src.data_processing.kaggle_downloads import download_csv_from_kaggle

if __name__ == "__main__":
    path = download_csv_from_kaggle(
        kaggle_url="https://www.kaggle.com/datasets/mealss/call-transcripts-scam-determinations?select=BETTER30.csv",
        save_dir="src/ml_scam_classification/data/call_transcripts_scam_determinations/raw_data/BETTER30.csv",
        create_path=True, # Create the paths
        overwrite=True, # Want to overwrite with latest version if/where applicable
        download_all_csvs=False, # only expecting one...
        interactive_auth_retry=True, # Allow retry
    )
    print(path)
    import pandas as pd
    print(pd.read_csv(path).head())
