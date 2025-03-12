import os

def find_repo_root():
    """
    Determine the repository root by trying two approaches:
    1. Use the script's location (__file__) and go one level up.
    2. Fall back to the current working directory.
    In either case, verify that the "api_keys" folder exists.
    """
    # Approach 1: Based on the script's location.
    repo_root = None
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidate = os.path.abspath(os.path.join(script_dir, os.pardir))
        if os.path.isdir(os.path.join(candidate, "api_keys")):
            repo_root = candidate
    except NameError:
        # __file__ may not be defined (e.g., in interactive mode)
        pass

    # Approach 2: Use the current working directory if the first approach didn't yield a valid repo root.
    if repo_root is None:
        cwd = os.getcwd()
        if os.path.isdir(os.path.join(cwd, "api_keys")):
            repo_root = cwd

    if repo_root is None:
        raise FileNotFoundError("Could not find the repository root containing the 'api_keys' folder.")

    return repo_root


def find_file_by_words(words):
    """
    Search through all files in the repository (determined by find_repo_root())
    and return the path of the file whose name contains every word in 'words'
    (case-insensitive). Raises an error if multiple matches or no match is found.
    
    Parameters:
        words (list): List of words that must all be present in the file name.
    
    Returns:
        str: Full path to the matching file.
    """
    repo_root = find_repo_root()
    matches = []
    
    for root, dirs, files in os.walk(repo_root):
        for file in files:
            # Check if every word (case-insensitive) is found in the file name.
            if all(word.lower() in file.lower() for word in words):
                matches.append(os.path.join(root, file))
    
    if not matches:
        raise FileNotFoundError(f"No file found in the repository containing all words: {words}")
    elif len(matches) > 1:
        raise ValueError(f"Multiple files found matching the criteria: {matches}")
    else:
        return matches[0]

def get_gemini_key_path():
    return find_file_by_words(["gemini", "key"])


if __name__ == "__main__":
    print("Testing find_repo_root")
    print(find_repo_root())
    print("-")
    print("Testing find_file_by_words with params: [gemini,key]")
    print(find_file_by_words(["gemini", "key"]))
    print("Testing get_gemini_key_path:")
    print("(note that it will only work if the fileanme contains the words \"gemini\" and \"key\")")
    print(get_gemini_key_path())