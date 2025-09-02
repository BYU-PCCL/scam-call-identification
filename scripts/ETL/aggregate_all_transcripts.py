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

    # new one-hots for source
    source_internet_search: int
    source_candor: int
    source_youtube1: int
    source_youtube2: int

    def __init__(self, rel_path, scam_call_onehot, legitimate_call_onehot,
                 source_internet_search=0, source_candor=0, source_youtube1=0, source_youtube2=0, source_my_recorded_calls=0):

        # scam/legit validation
        s = scam_call_onehot if scam_call_onehot else not legitimate_call_onehot
        l = legitimate_call_onehot if legitimate_call_onehot else not scam_call_onehot
        if not ((s in [0, 1]) and (l in [0, 1])):
            raise ValueError("Attempted to instantiate transcript obj with non-0-or-1 passed onehot attribute value...")

        # source validation
        srcs = [source_internet_search, source_candor, source_youtube1, source_youtube2, source_my_recorded_calls]
        if not all(x in [0, 1] for x in srcs):
            raise ValueError("Source one-hot values must be 0 or 1.")
        if sum(srcs) != 1:
            raise ValueError("Exactly one source must be 1, rest 0.")

        full_path = os.path.join(BASE_DATA_DIRPATH, rel_path)
        if not os.path.exists(full_path):
            raise ValueError("Attempted to instantiate transcript obj with rel path which does not exist")

        self.rel_path = rel_path
        self.scam_call_onehot = scam_call_onehot
        self.legitimate_call_onehot = legitimate_call_onehot
        self._full_path = Path(full_path)

        # assign sources
        self.source_internet_search = source_internet_search
        self.source_candor = source_candor
        self.source_youtube1 = source_youtube1
        self.source_youtube2 = source_youtube2
        self.source_my_recorded_calls = source_my_recorded_calls


TRANSCRIPT_CSVs = [
    transcript_csv(
        rel_path="calls_from_internet_search/processed/data.csv",
        scam_call_onehot=0,
        legitimate_call_onehot=1,
        source_internet_search=1
    ),
    transcript_csv(
        rel_path="candor/processed/transcripts.csv",
        scam_call_onehot=0,
        legitimate_call_onehot=1,
        source_candor=1
    ),
    transcript_csv(
        rel_path="youtube_scam_calls_1/extracted_features/transcripts.csv",
        scam_call_onehot=1,
        legitimate_call_onehot=0,
        source_youtube1=1
    ),
    transcript_csv(
        rel_path="youtube_scam_calls_2/processed/transcripts.csv",
        scam_call_onehot=1,
        legitimate_call_onehot=0,
        source_youtube2=1
    ),
    transcript_csv(
        rel_path="my_recorded_calls/processed/transcripts_txts.csv",
        scam_call_onehot=0,
        legitimate_call_onehot=1,
        source_my_recorded_calls=1
    )
]

TRANSCRIPT_SOURCE_FILEPATHS = [transcript._full_path for transcript in TRANSCRIPT_CSVs]

#============================#
#         MAIN BLOCK         #
#============================#

if __name__ == "__main__":
    print(TRANSCRIPT_SOURCE_FILEPATHS)

    combined_df = pd.DataFrame()
    
    for t_csv in TRANSCRIPT_CSVs:
        df = pd.read_csv(t_csv._full_path)

        # 0) strip whitespace and drop index-like junk columns
        df.columns = df.columns.str.strip()
        df = df.loc[:, ~df.columns.str.match(r'(?i)^Unnamed:')]

        # 1) If a 'transcripts' column already exists, keep it.
        #    Otherwise, rename the first column to 'transcripts'.
        first_col = df.columns[0]
        if 'transcripts' not in df.columns:
            df = df.rename(columns={first_col: 'transcripts'})

        # 2) Ensure column names are unique (keep the first occurrence)
        if df.columns.duplicated().any():
            # If duplicates exist, drop later duplicates
            df = df.loc[:, ~df.columns.duplicated(keep='first')]

        # 3) add labels
        df['call_is_scam__onehot'] = int(bool(t_csv.scam_call_onehot))
        df['call_is_legitimate__onehot'] = int(bool(t_csv.legitimate_call_onehot))

        # 4) add sources
        df['source_internet_search__onehot'] = t_csv.source_internet_search
        df['source_candor__onehot'] = t_csv.source_candor
        df['source_youtube1__onehot'] = t_csv.source_youtube1
        df['source_youtube2__onehot'] = t_csv.source_youtube2
        df['source_myrecordedcalls__onehot'] = t_csv.source_my_recorded_calls

        combined_df = pd.concat([combined_df, df], ignore_index=True)


    combined_df.to_csv(STORAGE_PATH, index=False)

    # verify ok by printing every 10 entries
    stored_df = pd.read_csv(STORAGE_PATH)
    for i, row in enumerate(stored_df.iterrows()):
        if i % 10 == 0:
            print(row[:50])
