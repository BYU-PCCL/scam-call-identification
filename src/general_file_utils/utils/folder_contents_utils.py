import os

from src.general_file_utils.utils.path_checks import assert_path_exists

def get_subfolder_names(path):
    """
    Gets the names of the subdirectories (not files) at the given path

    Input: 
    path - the path at which to retrieve the names of the subdirectories

    Output:
    list of names (NOT full paths) of subdirectories at input path
    """
    # Ensure path exists
    assert_path_exists(path)

    # Get subfolder names
    subfolders = [child for child in os.listdir(path) if os.path.isdir(os.path.join(path, child))]
    return subfolders


def get_subfolder_paths(path):
    """
    Gets the full paths to all of the subdirectories at the given path

    Inputs:
    path - The path at which to obtain the subdirectories whose paths will be retrieved

    Outputs:
    list of paths to each subdirectory at the input path
    """
    # ensure the path exists first
    assert_path_exists(path)

    # get the paths to subdirectories
    subfolder_names = get_subfolder_names(path)
    subfolder_paths = [os.path.join(path, subfolder_name) for subfolder_name in subfolder_names]
    return subfolder_paths

def apply_fn_to_each_subfolder_path(path, fn):
    subfolder_paths = get_subfolder_paths(path)
    results = [fn(subfolder_path) for subfolder_path in subfolder_paths]
    return results

if __name__ == "__main__":
    print("running")
    print(get_subfolder_paths("."))
