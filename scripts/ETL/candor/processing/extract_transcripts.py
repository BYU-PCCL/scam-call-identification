import os
import pandas as pd

from src.general_file_utils.utils.path_checks import assert_path_exists
from src.general_file_utils.utils.json import load_json_from_path
from src.general_file_utils.utils.folder_contents_utils import get_subfolder_paths
from src.general_file_utils.utils.csv_utils import append_df_rows_to_csv

if __name__ == "__main__":
    """
    Gets the candor datasets transcripts json (from the expected location), extracts the transcripts, and writes them to a csv. It creates the new location for the csv if not already created (the extracted_features folder).
    """

    CANDOR_FOLDER_PATH = "src\\ml_scam_classification\\data\\candor"
    DEFAULT_CANDOR_DATA_PATH = os.path.join(CANDOR_FOLDER_PATH, "raw_data")
    DEFAULT_CANDOR_TRANSCRIPT_WRITE_PATH = "src\\ml_scam_classification\\data\\candor\\processed"

    assert_path_exists(DEFAULT_CANDOR_DATA_PATH)

    # get list of paths to jsons of transcript info
    candor_download_subdir_paths = get_subfolder_paths(DEFAULT_CANDOR_DATA_PATH)
    CANDOR_JSON_REL_PATH = "transcription\\transcribe_output.json"
    candor_json_paths = [os.path.join(subdir_path, CANDOR_JSON_REL_PATH) for subdir_path in candor_download_subdir_paths]
    
    # TEST ONE
    """
    data = load_json_from_path(candor_json_paths[0])
    print(data["results"]["transcripts"][0]["transcript"])
    print(len(data["results"]["transcripts"]))
    print(data)
    exit()
    """

    # create destination
    destination_dir = os.path.join(CANDOR_FOLDER_PATH, "processed")
    full_destination_path = os.path.join(destination_dir, "transcripts.csv")
    # TODO REMOVE following line once works and leave space
    assert full_destination_path == "src\\ml_scam_classification\\data\\candor\\processed\\transcripts.csv"
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    assert_path_exists(os.path.join("src\\ml_scam_classification\\data\\candor\\processed"))

    # load jsons...
    transcripts = []
    n_json_paths = len(candor_json_paths)
    print("\nLOADING RAW TRANSCRIPTS\n")
    for i, path in enumerate(candor_json_paths):
        print(f" ... loading data in raw data file {i + 1}/{n_json_paths} ... ")
        data = load_json_from_path(path)
        transcripts += [t["transcript"] for t in data["results"]["transcripts"]]
    n_transcripts = len(transcripts)

    # create folder if does not exist
    dir_present = os.path.exists(destination_dir)
    if not dir_present:
        os.makedirs(destination_dir)
    assert_path_exists("src/ml_scam_classification/data/candor/processed")

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
    t_1 = pd.DataFrame({"transcript": [transcripts[0]]})
    t_1.to_csv(full_destination_path, index=False)

    print("\nEXTRACTING TRANSCRIPTS\n")
    for i, t in enumerate(transcripts):
        print(f"    ... Extracting transcript {i + 1}/{n_transcripts} ...")
        append_df_rows_to_csv(full_destination_path, pd.DataFrame({"transcript": [t]}))

    print("\nComplete!")
