import os
import traceback
import pandas as pd

if __name__ == "__main__":
    dir_w_my_transcripts = "src/ml_scam_classification/data/my_recorded_calls/raw/transcripts/"

    paths_to_transcript_dirs = [os.path.join(dir_w_my_transcripts, dirname) for dirname in os.listdir(dir_w_my_transcripts) if str.isnumeric(dirname[:6])]

    paths_to_txt_transcripts = []

    for path_to_transcript_dir in paths_to_transcript_dirs:
        filenams_in_dir = os.listdir(path_to_transcript_dir)
        for filename in filenams_in_dir:
            if filename[-4:] == '.txt':
                paths_to_txt_transcripts.append(os.path.join(path_to_transcript_dir, filename))

    transcripts_txts = []

    for path_to_txt_transcript in paths_to_txt_transcripts:
        try:
            with open(path_to_txt_transcript, 'r') as file:
                content = file.read()  # reads the entire file content as a string
                transcripts_txts.append(content)
        except Exception as e:
            print("Exception occurred:", e)
            traceback.print_exc()

    df = pd.DataFrame({"transcripts": transcripts_txts})
    
    df.to_csv("src/ml_scam_classification/data/my_recorded_calls/processed/transcripts_txts.csv")
