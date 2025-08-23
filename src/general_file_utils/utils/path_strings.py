import os
import re


def parse_ints_from_filename(filename: str) -> list[int]:
    """
    Extract all contiguous digit groups from a filename as integers.
    Raises ValueError if no digit groups are found.
    """
    matches = re.findall(r"\d+", filename)
    if not matches:
        raise ValueError(f"No integers found in filename: {filename}")
    return [int(m) for m in matches]


def get_path_of_file_w_latest_unix_timestamp(dir_path: str) -> str:
    """
    Given a directory, find the file whose name contains the latest unix timestamp
    (defined as an integer between 10 and 20 digits, inclusive).
    
    Rules:
    - dir_path must exist and be a directory.
    - Only files directly inside dir_path are considered (subdirectories ignored).
    - Each filename must contain exactly ONE integer in the 10–20 digit range.
      - If none found -> error
      - If more than one found -> error
    - All timestamps must have lengths that differ by at most 1 digit,
      and only 2 consecutive lengths are allowed.
    - If two files have identical timestamps -> error
    - Returns the full path (string) of the file with the largest timestamp.
    """
    if not os.path.isdir(dir_path):
        raise NotADirectoryError(f"Not a valid directory: {dir_path}")

    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    if not files:
        raise FileNotFoundError(f"No files found in directory: {dir_path}")

    timestamps = {}
    lengths = set()

    for fname in files:
        ints_in_file = parse_ints_from_filename(fname)
        valid_candidates = [num for num in ints_in_file if 10 <= len(str(num)) <= 20]

        if len(valid_candidates) == 0:
            raise ValueError(f"File '{fname}' does not contain a valid unix timestamp (10–20 digits).")
        if len(valid_candidates) > 1:
            raise ValueError(f"File '{fname}' contains multiple 10–20 digit integers, ambiguous timestamp.")

        ts = valid_candidates[0]
        if ts in timestamps:
            raise ValueError(f"Duplicate timestamp {ts} found in files '{timestamps[ts]}' and '{fname}'.")

        timestamps[ts] = fname
        lengths.add(len(str(ts)))

    # Check consistency of digit lengths
    if len(lengths) > 2:
        raise ValueError(f"Timestamps differ by more than 1 digit length: {lengths}")
    if len(lengths) == 2:
        if max(lengths) - min(lengths) > 1:
            raise ValueError(f"Timestamps differ by more than 1 digit length: {lengths}")

    # Select latest timestamp
    latest_ts = max(timestamps.keys())
    latest_file = timestamps[latest_ts]
    return os.path.join(dir_path, latest_file)
