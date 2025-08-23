import os
import pickle

import os
import pickle

def make_pkl_file(path: str, data) -> None:
    """
    Creates a pickle file at the given path with the provided data.
    
    Parameters:
        path (str): Full path to the .pkl file to create. Directory must exist.
        data (Any): The Python object to serialize.
    
    Raises:
        FileNotFoundError: If the directory part of `path` does not exist.
    """
    # Split into directory and file basename
    directory, filename = os.path.split(path)
    
    if not directory:
        directory = "."  # default to current directory if no dir given
    
    # Ensure directory exists
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Directory does not exist: {directory}")
    
    # Construct full path with basename inside that directory
    full_path = os.path.join(directory, filename)
    
    # Write pickle file
    with open(full_path, "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_pkl(
        path_to_pkl
):
    if not os.path.exists(path_to_pkl):
        raise FileNotFoundError(f"Could not find provided path to .pkl: {path_to_pkl}")

    with open(path_to_pkl, 'rb') as file:
        data = pickle.load(file)

    return data


def overwrite_pkl(path: str, new_data) -> None:
    """
    Overwrites the contents of the pkl file at the given path with the inputted data
    """
    # make sure pkl exists, as we are overwriting it
    if not os.path.exists(path):
        raise FileNotFoundError(f"Attempted to overwrite .pkl file at non-existent path:\n{path}")

    with open('data.pkl', 'wb') as file:
        pickle.dump(new_data, file)
