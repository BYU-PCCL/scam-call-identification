import os

import pandas as pd

from src.general_file_utils.utils.text import get_text_from_txt_file

if __name__ == "__main__":
    # NOTE: iS is short for "Internet Search" here. First letter kept lowecase to not have ambiguity with the word "is"

    iS_TRANSCRIPTS_DIRPATH = "src\\ml_scam_classification\\data\\calls_from_internet_search\\individual_transcripts_parsed"
    iS_TRANSCRIPTS_EXTRACTED_DATA_SAVE_LOCATION = "src\\ml_scam_classification\\data\\calls_from_internet_search\\processed\\data.csv"

    # Build paths for each transcript txt file in dir
    iS_transcripts_rel_paths = os.listdir(iS_TRANSCRIPTS_DIRPATH)
    iS_transcripts_full_paths = [os.path.join(iS_TRANSCRIPTS_DIRPATH, rel_path) for rel_path in iS_transcripts_rel_paths]

    # Get text from each transcript file
    texts_of_iS_transcripts = [get_text_from_txt_file(path) for path in iS_transcripts_full_paths]

    # Form dataframe where each instance is a transcript, save in IS transcripts save location
    df = pd.DataFrame({"Transcript": texts_of_iS_transcripts})
    df.to_csv(iS_TRANSCRIPTS_EXTRACTED_DATA_SAVE_LOCATION, index=False)

    # Check
    stored_df = pd.read_csv(iS_TRANSCRIPTS_EXTRACTED_DATA_SAVE_LOCATION)
    print(stored_df)
