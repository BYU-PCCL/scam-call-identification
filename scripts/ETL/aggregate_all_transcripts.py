import os
import time
import pandas as pd
from pathlib import Path

#=============================#
#       MASTER SETTINGS       #
#=============================#

BASE_DATA_DIRPATH = "src/ml_scam_classification/data"
STORAGE_PATH = f"src/ml_scam_classification/data/compiled/transcripts_compiled__{time.time_ns()}.csv"

# ----------------------------#

class transcript_csv:
    rel_path: Path
    scam_call_onehot: int
    legitimate_call_onehot: int
    _full_path: Path

    def __init__(self, rel_path, scam_call_onehot, legitimate_call_onehot):
        s = scam_call_onehot if scam_call_onehot else not legitimate_call_onehot
        l = legitimate_call_onehot if legitimate_call_onehot else not scam_call_onehot

        if not ((s == 1 or s == 0) and (l == 1 or l == 0)):
            raise ValueError("Attempted to instantiate transcript obj with non-0-or-1 passed onehot attribute value...")
        
        full_path = os.path.join(BASE_DATA_DIRPATH, rel_path)
        
        if not os.path.exists(full_path):
            raise ValueError("Attempted to instantiate transcript obj with rel path which does not exist")
        
        self.rel_path = rel_path
        self.scam_call_onehot = scam_call_onehot
        self.legitimate_call_onehot = legitimate_call_onehot
        self._full_path = Path(full_path)


TRANSCRIPT_CSVs = [
    transcript_csv(
        rel_path="calls_from_internet_search/processed/data.csv",
        scam_call_onehot=0,
        legitimate_call_onehot=1
    ),
    transcript_csv(
        rel_path="candor/processed/transcripts.csv",
        scam_call_onehot=0,
        legitimate_call_onehot=1
    ),
    transcript_csv(
        rel_path="youtube_scam_calls_1/extracted_features/transcripts.csv",
        scam_call_onehot=1,
        legitimate_call_onehot=0
    ),
    transcript_csv(
        rel_path="youtube_scam_calls_2/processed/transcripts.csv",
        scam_call_onehot=1,
        legitimate_call_onehot=0
    )
]

TRANSCRIPT_SOURCE_FILEPATHS = [transcript._full_path for transcript in TRANSCRIPT_CSVs]

#============================#
#         MAIN BLOCK         #
#============================#

if __name__ == "__main__":
    print(TRANSCRIPT_SOURCE_FILEPATHS)

    dfs = [pd.read_csv(transcript_path) for transcript_path in TRANSCRIPT_SOURCE_FILEPATHS]

    combined_df = pd.DataFrame()
    for t_csv in TRANSCRIPT_CSVs:
        df = pd.read_csv(t_csv._full_path)
        print(df)
        df.columns.values[0] = 'transcripts'
        df['call_is_scam__onehot'] = t_csv.scam_call_onehot
        df['call_is_legitimate__onehot'] = t_csv.legitimate_call_onehot
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    
    combined_df.to_csv(STORAGE_PATH, index=False)

    # verify ok by printing every 10 entires
    stored_df = pd.read_csv(STORAGE_PATH)
    for i, row in enumerate(stored_df.iterrows()):
        if i%10 == 0:
            print(row[:50])
