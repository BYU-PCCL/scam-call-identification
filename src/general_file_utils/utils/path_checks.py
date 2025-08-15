import os

def assert_path_exists(path):
    """
    Ensures the specified path exists. Otherwise, raises an error.

    Input: 
    path - The path whose existence will be asserted

    Output:
    (none)
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Attempted to assert existence of non-existent path: {path}")