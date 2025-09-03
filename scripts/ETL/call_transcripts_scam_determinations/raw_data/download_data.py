import kaggle

from src.data_processing.kaggle_downloads import download_csv_from_kaggle

if __name__ == "__main__":
    path = download_csv_from_kaggle(
        kaggle_url="https://www.kaggle.com/datasets/mealss/call-transcripts-scam-determinations",
        save_dir="src/ml_scam_classification/data/",
        *,
        create_path: bool = True,
        overwrite: bool = True,
        download_all_csvs: bool = False,
        interactive_auth_retry: bool = True,
    )
    # Download latest version
    path = kaggle.dataset_download("mealss/call-transcripts-scam-determinations")
    print(path)
    exit()

    print("Path to dataset files:", path)