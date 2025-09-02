import os
import pandas as pd

from src.general_file_utils.utils.path_checks import assert_path_exists

if __name__ == "__main__":
    # write transcript data to destination
    youtube_scam_calls_1 = "src\\ml_scam_classification\\data\\youtube_scam_calls_1"
    DEFAULT_DATA_PATH = os.path.join(youtube_scam_calls_1, "raw_data\\FullTranscriptData.csv")

    DEFAULT_WRITE_PATH = "src\\ml_scam_classification\\data\\youtube_scam_calls_1\\processed"

    assert_path_exists(DEFAULT_DATA_PATH)

        # Read data, just get transcripts
    df = pd.read_csv(DEFAULT_DATA_PATH)
    transcripts_df = df[["Content"]]
    n_transcripts = len(transcripts_df)

    # create destination
    full_destination_path = os.path.join(DEFAULT_WRITE_PATH, "transcripts.csv")
    if not os.path.exists(DEFAULT_WRITE_PATH):
        os.makedirs(DEFAULT_WRITE_PATH)
    assert_path_exists(os.path.join("src\\ml_scam_classification\\data\\youtube_scam_calls_1\\processed"))

    # if path already existed with a csv, make sure either empty or has all transcripts
    # otherwise, incomplete loading and will need to clear it and start over
    if os.path.exists(full_destination_path):
        initial_transcripts_df = pd.read_csv(full_destination_path)
        # need to erase if partially loaded
        if not len(initial_transcripts_df) == 0:
            # not empty
            has_all_transcripts = len(initial_transcripts_df) - 1 == n_transcripts
            if has_all_transcripts:
                # have already extracted all transcripts, no work to do
                exit()
            else:
                # isn't empty but doesn't have all transcripts, clear in preparation to re-extract them all
                os.remove(full_destination_path)

    # write transcripts to new location
    print(transcripts_df)
    transcripts_df.to_csv(full_destination_path, index=False)

    print("\nComplete!")
