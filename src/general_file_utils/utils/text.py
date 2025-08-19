def get_text_from_txt_file(file_path):
    """
    Reads and returns the full text content from a .txt file.
    
    Parameters:
    file_path (str): The path to the text file.
    
    Returns:
    str: The text content of the file.
    
    Raises:
    FileNotFoundError: If the file does not exist at the given path.
    IOError: If there is an issue reading the file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    except FileNotFoundError:
        raise FileNotFoundError(f"The file at {file_path} was not found.")
    except IOError as e:
        raise IOError(f"An error occurred while reading the file: {e}")
