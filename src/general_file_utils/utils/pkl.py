import os
import pickle

def load_pkl(
        path_to_pkl
):
    if not os.path.exists(path_to_pkl):
        raise FileNotFoundError(f"Could not find provided path to .pkl: {path_to_pkl}")

    with open(path_to_pkl, 'rb') as file:
        data = pickle.load(file)

    return data
