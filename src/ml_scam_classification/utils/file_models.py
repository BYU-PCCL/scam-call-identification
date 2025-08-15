import os
import re
from dataclasses import dataclass
from functools import cached_property
from typing import List, Union
from src.ml_scam_classification.settings.supported_file_extensions import SUPPORTED_FILE_EXTENSIONS
from src.ml_scam_classification.utils.error_utils import format_context

from src.ml_scam_classification.models.string_models import FormatEnforcedStr

# Examples of defining FormatEnforcedStr class
"""
class PostalCode(FormatEnforcedStr):
    def valid_format_regex_pattern(self):
        return r"\d{5}"  # e.g., '12345'

class ProductCode(FormatEnforcedStr):
    def valid_format_regex_pattern(self):
        return r"[A-Z]{3}-\d{4}"  # e.g., 'ABC-1234'
"""


# utility functions

import json
from typing import List, Union
from src.ml_scam_classification.utils.error_utils import format_context
from src.ml_scam_classification.utils.enforce_fn_properties import enforce_types, ensure_list_param_not_empty


def is_json(myjson):
  try:
    json.loads(myjson)
    return True
  except ValueError:
    return False


@format_context
def assert_is_valid_json(json_obj, context="In assert_is_valid_json"):
    if not is_json(json_obj):
        raise ValueError()


def convert_list_json_str_to_json_list(json_strings):
    """
    Converts a list of JSON strings into a list of JSON objects.
    
    Args:
        json_strings (list of str): A list containing JSON strings.
    
    Returns:
        list: A list of JSON objects (Python dictionaries or lists).
    """
    # Using list comprehension to load each JSON string into a Python object.
    json_list = [json.loads(s) for s in json_strings]
    return json_list


def write_json_to_file(json_obj, output_path):
    """
    Writes a JSON object to a file.
    
    Args:
        json_obj: The JSON object (e.g., list, dict) to write to file.
        output_path (str): The file path where the JSON object will be saved.
    """
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(json_obj, file, indent=4)
    print(f"JSON data has been written to {output_path}")


def file_at_path_has_valid_json(
        filepath: str,
        context: str = "In file_at_path_has_valid_json",
        first_ensure_is_json_file: bool = True
        ):
    
    if first_ensure_is_json_file:
        assert_path_string_has_file_extension(
                path=filepath,
                file_ext=".json",
                ensure_valid_path_str=True,
                ensure_path_exists=True,
                context=context
            )

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except (ValueError, json.JSONDecodeError, OSError):
        return False
    

@format_context
def assert_file_at_path_has_valid_json(
        filepath: str,
        context: str = "In assert_file_at_path_has_valid_json",
        first_ensure_is_json_file: bool = True
    ):
    if not file_at_path_has_valid_json(
        filepath=filepath,
        context=context[:-2], # removes context formatting, it will be added again in this called fn
        first_ensure_is_json_file=first_ensure_is_json_file
        ):
        raise ValueError(f"{context} file does not contain valid json: {filepath}")


def get_json_from_path_str(
        path: str,
        first_ensure_path_and_json_valid=True,
        context="In get_json_from_path_str"
        ):
    
    # perform checks if required
    if first_ensure_path_and_json_valid:
        assert_file_at_path_has_valid_json(
            filepath=path,
            context=context,
            first_ensure_is_json_file=first_ensure_path_and_json_valid
        )

    # Open and read the JSON file
    with open('data.json', 'r') as file:
        data = json.load(file)

    return data





@format_context
@enforce_types
def is_valid_json_navigation_path(
        json_obj,
        check_is_valid_json: bool = True,
        json_navigation_path: List[Union[str, int]] = [],
        context="In is_valid_json_navigation_path"
    ):
    if check_is_valid_json:
        assert_is_valid_json(
            json_obj=json_obj,
            context=context[:-2] # next fn will format it again
        )
    
    if len(json_navigation_path) == 0:
        return False
    
    for el in json_navigation_path:
        if isinstance(el, int):
            if el < 0:
                return False
    
    return True


@format_context
def assert_path_exists(path_str: str, context: str = "") -> None:
    """
    Asserts that `path_str` is both syntactically valid and exists on disk.
    Raises ValueError if either check fails.
    """
    # 1) Syntax check
    assert_is_path_like_string(path_str)

    # 2) Existence check
    if not os.path.exists(path_str):
        raise ValueError(f"{context}Path does not exist: {path_str!r}")


import os
import re
import filetype
import pandas as pd
import soundfile as sf
import numpy as np
from typing import Callable, Any, List, Tuple
from dotenv import load_dotenv
from src.ml_scam_classification.utils.error_utils import format_context
from src.ml_scam_classification.utils.enforce_fn_properties import enforce_types_disallow_none, ensure_list_param_not_empty

def read_file(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        file_contents = file.read()
    return file_contents


def assert_is_path_like_string(path_str: str, name_obj_to_check: str = "Path") -> None:
    """
    Assert that `path_str` is syntactically a path-like string.
    Raises ValueError if not.
    """
    # 1) Type check
    if not isinstance(path_str, str):
        raise ValueError(f"{name_obj_to_check} must be a string, got {type(path_str).__name__!r}")

    # 2) Non-empty
    if not path_str:
        raise ValueError(f"{name_obj_to_check} string is empty")

    # 3) No null or newline chars
    if '\0' in path_str:
        raise ValueError(f"{name_obj_to_check} contains null byte (\\0)")
    if '\n' in path_str or '\r' in path_str:
        raise ValueError(f"{name_obj_to_check} contains newline characters")

    # 4) No other control characters (U+0000–U+001F)
    for ch in path_str:
        if ord(ch) < 32:
            raise ValueError(f"{name_obj_to_check} contains control character U+{ord(ch):04X}")

    # 5) Split on both forward and back slashes, filter out empties
    parts = [p for p in re.split(r'[\\/]', path_str) if p]
    if not parts:
        raise ValueError(f"{name_obj_to_check} contains no valid path components: {path_str!r}")
    
import requests

import os
import sys
import requests
from urllib.parse import urlparse
from pathlib import Path

def show_progress(downloaded: int, total_size: int | None, bar_length: int = 50) -> None:
    """
    Display or update a progress bar in the console. If total_size is unknown, shows downloaded bytes only.

    Args:
        downloaded: Number of bytes downloaded so far.
        total_size: Total file size in bytes, or None if unknown.
        bar_length: Character length of the progress bar.
    """
    if total_size and total_size > 0:
        percent = downloaded / total_size
        filled = int(bar_length * percent)
        bar = '=' * filled + '-' * (bar_length - filled)
        sys.stdout.write(f"\r[{bar}] {percent * 100:6.2f}% ({downloaded}/{total_size} bytes)")
    else:
        # Unknown total size
        sys.stdout.write(f"\rDownloaded {downloaded} bytes")
    sys.stdout.flush()


def download_file_from_url(url: str, destination_folder: str) -> str:
    """
    Download a file from `url` into `destination_folder`, inferring its filename.
    Streams and shows download progress in the console. Supports signed URLs that disallow HEAD.

    Args:
        url: The URL to download.
        destination_folder: Path to an existing directory (slashes of either type are OK).

    Returns:
        The full path to the downloaded file.

    Raises:
        FileNotFoundError: If destination_folder does not exist.
        ValueError: If we cannot infer a filename.
        requests.HTTPError: If the HTTP GET request fails.
    """
    # Normalize and validate destination folder
    destination_folder = os.path.normpath(destination_folder)
    dest_dir = Path(destination_folder)
    if not dest_dir.is_dir():
        raise FileNotFoundError(f"Destination folder not found: {dest_dir}")

    # Perform GET request with streaming
    response = requests.get(url, stream=True, allow_redirects=True)
    response.raise_for_status()

    # Attempt to read total size from GET response headers
    total_size = None
    content_length = response.headers.get('Content-Length')
    if content_length:
        try:
            total_size = int(content_length)
            print(f"File size: {total_size} bytes")
        except ValueError:
            print(f"Unrecognized Content-Length header: {content_length}")

    # Infer filename (Content-Disposition or URL path)
    cd = response.headers.get("content-disposition", "")
    filename = None
    if "filename=" in cd:
        filename = cd.split("filename=")[-1].strip('"; ')
    if not filename:
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
    if not filename:
        raise ValueError(f"Could not determine filename for URL: {url}")

    dest_path = dest_dir / filename
    downloaded = 0
    chunk_size = 8192

    print(f"Downloading to {dest_path}...")

    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if not chunk:
                continue
            f.write(chunk)
            downloaded += len(chunk)
            show_progress(downloaded, total_size)

    # Finish the console line
    sys.stdout.write("\n")
    print(f"Downloaded to {dest_path} successfully.")
    return str(dest_path)


import os
import re
from pathlib import Path

def assert_str_has_valid_path_structure(path: str) -> None:
    """
    Ensure that the provided path is a non-empty string and has a valid filesystem path structure.
    Raises:
        TypeError: If path is not a string.
        ValueError: If path is an empty string or contains null characters.
    """
    if not isinstance(path, str):
        raise TypeError(f"Path must be a string, got {type(path).__name__}")
    if path.strip() == "":
        raise ValueError("Path string is empty or whitespace")
    if "\0" in path:
        raise ValueError("Path string contains null character")


def assert_path_exists(path: str) -> None:
    """
    Ensure that the provided path exists in the filesystem.
    Raises:
        FileNotFoundError: If the path does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No such file or directory: '{path}'")


def assert_path_has_file_extension(path: str, ext: str) -> None:
    """
    Ensure that the provided path ends with the expected file extension.
    Raises:
        ValueError: If the file extension does not match.
    """
    if Path(path).suffix.lower() != ext.lower():
        raise ValueError(f"File '{path}' does not end with '{ext}'")


def assert_file_at_path_loadable(path: str, ext: str) -> str:
    """
    Load the file at the given path and return its contents as a string.
    Currently only supports .txt files.
    Raises:
        NotImplementedError: If ext is not .txt.
        Exception: If loading fails.
    """
    assert_path_has_file_extension(path, ext)
    if ext.lower() != ".txt":
        raise NotImplementedError(f"Loading files with extension '{ext}' is not supported")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Failed to load file '{path}': {e}")


def get_urls_from_text_file(path: str) -> list[str]:
    """
    Extract all URLs starting with http:// or https:// from a text file.
    URLs may be separated by whitespace or newlines; whitespace will be removed.
    Args:
        path (str): Path to the .txt file to process.
    Returns:
        List[str]: A list of extracted URLs.
    Raises:
        Exception: For any assertion failures or load errors.
    """
    # Validate path
    assert_str_has_valid_path_structure(path)
    assert_path_exists(path)
    assert_path_has_file_extension(path, ".txt")

    # Load file contents
    content = assert_file_at_path_loadable(path, ".txt")

    # Find all URL prefixes
    pattern = re.compile(r"https?://")
    matches = list(pattern.finditer(content))

    urls = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        raw_url = content[start:end]
        # Remove whitespace characters
        cleaned_url = "".join(raw_url.split())
        urls.append(cleaned_url)

    return urls


def file_at_filepath_exists(path_str, context, ensure_path_exists=True):
    if ensure_path_exists:
        assert_path_exists(
            path_str=path_str,
            context=context
        )

    return os.path.isfile(path_str)
    

def get_filename_from_path(path=None, assert_path_exists=True):
    """
    Returns the file name from a given file path.
    Does not have to be an existing path
    
    Args:
        path (str): The full file path.
        
    Returns:
        str: The file name at the end of the path.
    """
    assert_is_path_like_string(path)
    if assert_path_exists:
        assert_path_exists(path)

    return os.path.basename(path)


def create_folder_at_path(path=None, folder_name: str = None):
    assert_path_exists(path)

    # Create the directory (and parents if needed)
    os.makedirs(path, exist_ok=False)


def get_paths_to_all_files_in_folder(folder_path: str) -> List[str]:
    """
    Returns a list of absolute or relative paths to every file directly
    contained in `folder_path` (does not recurse into subdirectories).
    
    Raises ValueError if `folder_path` is not a valid path or not a directory.
    """
    # 1) Validate syntax and existence
    assert_path_exists(folder_path)
    
    # 2) Ensure it’s a directory
    if not os.path.isdir(folder_path):
        raise ValueError(f"Not a directory: {folder_path!r}")
    
    # 3) Collect and return all file paths
    file_paths: List[str] = []
    for entry in os.listdir(folder_path):
        full_path = os.path.join(folder_path, entry)
        if os.path.isfile(full_path):
            file_paths.append(full_path)
    
    return file_paths

    
def get_file_extension_from_path_str(file_path):
    """
    Return the file extension (the part after the last dot) of a given path.
    If there is no extension, returns an empty string.

    Examples:
        get_file_type("document.pdf")      -> "pdf"
        get_file_type("/path/to/archive.tar.gz") -> "gz"
        get_file_type("no_extension")      -> ""
    """
    # make sure path is valid
    assert_path_exists(file_path)

    # get the part of the path after the '.' (the file extension)
    _, ext = os.path.splitext(file_path)
    return ext[1:] if ext.startswith('.') else ''

@format_context
def assert_path_string_has_file_extension(path, file_ext, ensure_valid_path_str=True, ensure_path_exists=True, context="In assert_file_extension"):
        # ensure file extension does not start with a dot
        if file_ext[0] != '.':
            raise ValueError(f"{context} passed file extension must begin with a .")
        
        # ensure file extension is alphanumeric
        if not path.isalnum():
            raise ValueError(f"{context} passed file extension is not alphanumeric: {file_ext}")
        
        if ensure_valid_path_str:
            assert_is_path_like_string(path)
        
        if ensure_path_exists:
            assert_path_exists(path, context=context)

        file_ext = get_file_extension_from_path_str(path)

        if not (file_ext == ".json"):
            raise ValueError(f"Attempted to initialize JSONFilePath, but ext of file at path found to not be .json: {path}")


def get_file_size_in_bytes(path, ensure_path_exists=True):
    """
    Returns the size of the file at the given path in bytes.
    Raises FileNotFoundError if the file does not exist.
    """
    if ensure_path_exists:
        assert_path_exists(path)
    
    return os.path.getsize(path)
    

def is_audio_file(filepath):
    """
    Checks if a file is an audio file based on its magic bytes.

    Args:
        filepath: The path to the file.

    Returns:
        True if the file is an audio file, False otherwise.
    """
    if not os.path.isfile(filepath):
        return False

    kind = filetype.guess(filepath)
    if kind is None:
        return False

    return kind.mime.startswith('audio')


def assert_filepath_is_audio_file(filepath):
    if not is_audio_file(filepath):
        raise ValueError(f"{filepath} is not an audio file.")
    

def is_folder(path):
    return os.path.isdir(path)
    

def assert_is_folder(path, err_msg="Error - Non-directory path"):
    if not is_folder(path):
        raise ValueError(f"{err_msg}: {path}")


@enforce_types_disallow_none
def folder_is_empty(
    folder_path: str,
    context: str = "In folder_has_at_least_one_file"
) -> bool:
    """
    Helper: checks if the folder at the given path has no valid files in it
    Checks: Ensures its a valid path first
    If it does, returns True
    If it doesn't, returns false
    """
    files = [
        name for name in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, name))
    ]
    if len(files) > 0:
        raise ValueError(f"No files found in directory: {folder_path!r}")

@enforce_types_disallow_none
def assert_folder_has_at_least_one_file(
        folder_path: str,
        context: str = "In assert_folder_is_valid_and_has_files"
        ) -> None:
    """
    Helper: ensures that folder_path is a directory containing at least one file.
    Raises ValueError if it's not a directory or has no files.
    """
    assert_is_folder(folder_path)
    # List only files (ignore subdirs)
    files = [
        name for name in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, name))
    ]
    if not files:
        raise ValueError(f"No files found in directory: {folder_path!r}")


import os
from typing import Callable, Any, List, Tuple

# assumes these live in the same module or have been imported appropriately:
# from your_module import assert_is_valid_path, get_paths_to_all_files_in_folder

def apply_fn_to_folder(
    folder_path: str,
    fn: Callable[[str], Any]
) -> List[Tuple[str, Any]]:
    """
    Applies `fn` to every file in `folder_path`.

    1. Uses get_paths_to_all_files_in_folder to:
       - assert the path is valid & exists
       - ensure it's a directory
       - collect all immediate files
    2. Fails if no files are found.
    3. Calls fn(path_to_file) for each file and returns
       a list of (file_path, fn_return_value).
    """
    # 1) List & validate files
    file_paths = get_paths_to_all_files_in_folder(folder_path)

    # 2) Ensure at least one file
    if not file_paths:
        raise ValueError(f"No files found in directory: {folder_path!r}")

    # 3) Apply fn
    results: List[Tuple[str, Any]] = []
    for path in file_paths:
        results.append((path, fn(path)))

    return results


def get_dataframe_from_csv_url(url, **kwargs):
    """
    Download CSV directly into pandas DataFrame
    
    Parameters:
        url (str): Direct CSV download URL
        **kwargs: Additional pandas.read_csv() parameters
        
    Returns:
        pd.DataFrame: Contains CSV data
        
    Usage:
        df = get_dataframe_from_csv_url("https://raw.githubusercontent.com/user/repo/file.csv")
    """
    return pd.read_csv(url, **kwargs)


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


import inspect
import os

def get_caller_filename(n=1):
    """
    Returns the filename of the caller n levels up the stack.
    n=1 means the immediate caller, n=2 means the caller's caller, etc.
    """
    stack = inspect.stack()
    # Check if n is within the stack range
    if n < len(stack):
        frame_info = stack[n]
        filename = frame_info.filename
        print(f"returning caller file: {os.path.basename(filename)}")
        return os.path.basename(filename)
    else:
        print(f"returningi caller file: None")
        return None  # Or raise an exception if you prefer


import os
import pandas as pd
import soundfile as sf
import numpy as np
from dotenv import load_dotenv

def parquet_to_audio(
    path_to_parquet: str,
    output_path: str,
    sample_rate: int = 44100,
    output_file_prefix: str = ""
) -> list[str]:
    """
    Convert audio data stored in a Parquet file to individual WAV files.

    Parameters:
        path_to_parquet (str): Path to the input Parquet file.
        output_path (str): Directory where the output WAV files will be stored.
        sample_rate (int): Sample rate for the WAV files (default is 44100 Hz).
        output_file_prefix (str): Optional prefix for the output filenames.

    Returns:
        List[str]: List of generated WAV file paths.
    """
    os.makedirs(output_path, exist_ok=True)

    # Load the Parquet into a DataFrame
    df = pd.read_parquet(path_to_parquet)

    # Verify the audio column
    if 'audio' not in df.columns:
        raise ValueError(f"No audio column found; available columns: {df.columns.tolist()}")

    output_files: list[str] = []
    for idx, raw in enumerate(df['audio']):
        # Handle nested struct types (dict or pyarrow struct) by extracting the 'audio' field
        if isinstance(raw, dict):
            data = raw.get('audio', next(iter(raw.values())))
        else:
            data = raw

        # If this is a PyArrow scalar, convert to Python object
        if hasattr(data, 'as_py'):
            data = data.as_py()

        # Convert bytes payload to numpy array
        if isinstance(data, (bytes, bytearray)):
            audio_array = np.frombuffer(data, dtype=np.int16)
        else:
            # For other array-like types, coerce to numpy
            audio_array = np.asarray(data)

        # Ensure numeric dtype acceptable by soundfile
        if audio_array.dtype == object or audio_array.dtype.kind not in ('i', 'f'):
            # try int16 first, fall back to float32
            try:
                audio_array = audio_array.astype(np.int16)
            except Exception:
                audio_array = audio_array.astype(np.float32)

        # Ensure shape = (n_samples, n_channels)
        audio_array = np.atleast_2d(audio_array).T

        # Write WAV file
        filename = f"{output_file_prefix}_{get_caller_filename(2)}_{idx}.wav"
        dest = os.path.join(output_path, filename)
        sf.write(dest, audio_array, samplerate=sample_rate)
        print(f"Created: {dest}")
        output_files.append(dest)

    return output_files


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

def find_file_path_by_words(words_list):
    return find_file_by_words(words_list)


def get_chatgpt_api_key():
    load_dotenv()
    openai_key = None
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key == "":
        raise ValueError("Please set the OPENAI_API_KEY environment variable")
    return openai_key

class WarningTracker:
    _instance = None  # holds single instance
    _warning_given = False  # Tracks whether the warning has been given

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WarningTracker, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def check_and_warn(self):
        """
        Checks if the warning has already been given. If not, prints the warning
        and marks it as given.
        """
        if not self._warning_given:
            print("\ncout_logGING SET TO TRUE BY DEFAULT")
            print("If you would like to turn off cout_logging, create an environment variable with id \"cout_log\" and set it to \"False\"")
            print("\n-\n")
            self._warning_given = True

def cout_logging_enabled():
    load_dotenv()
    cout_logging_preference = os.getenv("cout_log")
    
    # Get the singleton instance of WarningTracker
    warning_tracker = WarningTracker()

    if not cout_logging_preference or cout_logging_preference is None:
        # Check and warn only if warning hasn't been given
        warning_tracker.check_and_warn()
        return True  # Default cout_logging enabled is true

    if cout_logging_preference.lower() != "true" and cout_logging_preference.lower() != "false":
        raise ValueError("Please set environment variable with id \"cout_log\" to \"True\" or \"False\"")

    if cout_logging_preference.lower() == "true":
        return True

    if cout_logging_preference.lower() == "false":
        return False

    raise ValueError("Critical Error: .env Variable \"cout_log\" exists, but was assigned a value which the function did not account for.")


if __name__ == "__main__":
    print("Testing find_repo_root")
    print(find_repo_root())
    print("-")
    print("Testing find_file_by_words with params: [gemini,key]")
    print(find_file_by_words(["gemini", "key"]))
    print("-")

@dataclass
class FilePath:
    _file_path_str: str
    require_filepath_exists: bool = True

    def __post_init__(self):
        # make sure path is valid path string
        assert_is_path_like_string(self._file_path_str, name_obj_to_check="file_path_str in FilePath instantiation")

        # if required, make sure file exists
        if self.require_filepath_exists and file_at_filepath_exists(
            path_str=self._file_path_str,
            context="Attempting to instantiate FilePath object"
        ):
            raise ValueError(f"Instantiated FilePath with require_path_exists=True, but path does not exist: {self._file_path_str}")

    @cached_property
    def get_extension(self):
        return get_file_extension_from_path_str(self.file_path_str)
    
    # Yields string path when instance is used in str context
    def __str__(self):
        return self._path

    # Yields string path when instance is used in file context
    def __fspath__(self):
        return self._path
    

@dataclass
class JSONNavigationPath:
    json_navigation_path: List[Union[str, int]]

    def __post_init__(self):
        # ensure json navigation path exists in json file

        json_obj = self.json_file_path_obj.get_json_at_json_file_path()

        if not is_valid_json_navigation_path(
            json_obj=json_obj,
            check_is_valid_json=False,
            json_navigation_path=self.json_navigation_path
            ):
            raise ValueError(f"Tried to instantiate JsonNavigationPath with invalid navigation path: {self.json_navigation_path}. JSON navigation path must consist of strings and integers >= 0.")




@dataclass
class JSONFilePath(FilePath):
    def __post_init__(self):
        super().__post_init__()

        # Ensure file is a valid json file
        if not file_at_path_has_valid_json(
            filepath=self,
            context="Trying to instantiate JSONFilePath",
            first_ensure_is_json_file=True
        ):
            raise ValueError(f"Attempted to initalize JSONFilePath object with json file which contains invalid json: {self}")
    
    def get_json_at_json_file_path(self):
        return get_json_from_path_str(
            path=self,
            first_ensure_path_and_json_valid=False, # already did at instantiation
            context="In get_json_obj in instantiated JSONFilePath"
        )
    
    def get_json_value_at_json_navigation_path(self, json_navigation_path: JSONNavigationPath):
        @format_context
        @enforce_types
        def get_json_value_at_json_navigation_path(
                json_navigation_path: JSONNavigationPath,
                json_obj=None,
                json_filepath: JSONFilePath = None,
                ensure_valid_json: bool = True,
                ensure_valid_json_navigation_path: bool = True,
                context: Union[str, None] ="In get_json_value_at_json_navigation_path"
        ):
            # ensure either json_obj or json file path provided
            if json_obj is None and json_filepath is None:
                raise ValueError(f"{context} must provide either json_obj or JSONFilePath obj to navigate")
            
            # if json obj not provided, get it from provided file path
            if json_obj is None:
                json_obj = json_filepath.get_json_at_json_file_path()

            # Perform required checks
            if ensure_valid_json and not is_json(json_obj):
                raise ValueError(f"{context} provided json_obj to navigate is not json")
            
            if ensure_valid_json_navigation_path and not is_valid_json_navigation_path(json_navigation_path):
                raise ValueError(f"{context} provided invalid json navigation path - must be a list with strings and/or integers >= 0")
            
            # Get the value at the json navigation path
            json_sub_object = json_obj
            for key in json_navigation_path:
                try:
                    if isinstance(key, str):
                        json_sub_object = json_sub_object.get(key)
                    if isinstance(key, int):
                        json_sub_object = json_sub_object[key]
                except:
                    raise ValueError(f"{context} json navigation path encountered nonexistent key: {key} when navigating json object with json navigation path: {json_navigation_path}")
                
            return json_sub_object

        get_json_value_at_json_navigation_path(
            json_navigation_path=json_navigation_path,
            json_obj=self.get_json_at_json_file_path(),
            json_filepath=self,
            ensure_valid_json=False, # already passing JSONFilePath obj, which did this after initialization
            context="Getting json valid at navigation path for JSONFilePath obj"
        )


# DUPLICATE - need to fix later
def get_json_value_at_json_navigation_path(self, json_navigation_path: JSONNavigationPath):
    @format_context
    @enforce_types
    def get_json_value_at_json_navigation_path(
            json_navigation_path: JSONNavigationPath,
            json_obj=None,
            json_filepath: JSONFilePath = None,
            ensure_valid_json: bool = True,
            ensure_valid_json_navigation_path: bool = True,
            context: Union[str, None] ="In get_json_value_at_json_navigation_path"
    ):
        # ensure either json_obj or json file path provided
        if json_obj is None and json_filepath is None:
            raise ValueError(f"{context} must provide either json_obj or JSONFilePath obj to navigate")
        
        # if json obj not provided, get it from provided file path
        if json_obj is None:
            json_obj = json_filepath.get_json_at_json_file_path()

        # Perform required checks
        if ensure_valid_json and not is_json(json_obj):
            raise ValueError(f"{context} provided json_obj to navigate is not json")
        
        if ensure_valid_json_navigation_path and not is_valid_json_navigation_path(json_navigation_path):
            raise ValueError(f"{context} provided invalid json navigation path - must be a list with strings and/or integers >= 0")
        
        # Get the value at the json navigation path
        json_sub_object = json_obj
        for key in json_navigation_path:
            try:
                if isinstance(key, str):
                    json_sub_object = json_sub_object.get(key)
                if isinstance(key, int):
                    json_sub_object = json_sub_object[key]
            except:
                raise ValueError(f"{context} json navigation path encountered nonexistent key: {key} when navigating json object with json navigation path: {json_navigation_path}")
            
        return json_sub_object


# Example usage for get-Json_value_at_json_navigation_path:
if __name__ == "__main__":
    # Example list of JSON strings
    json_str_list = [
        '{"name": "Alice", "age": 30}',
        '{"name": "Bob", "age": 25}',
        '{"name": "Charlie", "age": 35}'
    ]
    
    # Convert the list of JSON strings to a list of JSON objects.
    json_objects_list = convert_list_json_str_to_json_list(json_str_list)
    
    # Write the list of JSON objects to a file.
    output_file = "combined.json"
    write_json_to_file(json_objects_list, output_file)




@enforce_types
def get_json_from_path(json_file_path: JSONFilePath):
    get_json_from_path_str(
        path=json_file_path,
        first_ensure_path_and_json_valid=False # only accepted
    )


@dataclass
class FileExtension(FormatEnforcedStr):
    def valid_format_regex_pattern(self):
        return r"^\.(?:{})".format("|".join(map(re.escape, SUPPORTED_FILE_EXTENSIONS)))

@dataclass
class DirPath:
    _dir_path_str: str
    #requirement_settings: DirPathReqs(Enum):
    requirement_settings: str = None,
    
    require_path_exists_on_creation: bool = True
    require_path_exists_on_fn_call: bool = True
    required_file_types: FileExtension = None
    check_file_type_on_creation: bool = True
    check_file_type_on_fn_call: bool = True

    def validate_requirements(self):
        if self.require_path_exists_on_creation:
            assert_is_folder(
                path=self._dir_path_str,
                err_msg="Instantiated DirPath with require_path_exists=True, but path does not exist"
                )
            
        if self.limit_to_file_type is not None:
            # must verify if folder contains any files
            #if folder
            # TODO - finish
            1==1

    def __post_init__(self):
        self.validate_requirements()
            
    @property
    def value(self):
        return self._dir_path_str  # Only a getter, no setter
        
    @cached_property
    def get_end_folder_name(self):
        return os.path.basename(self._dir_path_str)
    
    def assert_path_exists(self):
        assert_is_folder(
            path=self,
            err_msg="Attempted to assert path of DirPath obj exists but it does not"
        )
        # if
        # TODO finish
    
    # Yields string path when instance is used in str context
    def __str__(self):
        return self._path

    # Yields string path when instance is used in file context
    def __fspath__(self):
        return self._path
    

@dataclass
class FilePathAlwaysRequireExists(DirPath):
    @property
    def value(self):
        self.assert_path_exists()
        return self._dir_path_str  # Only a getter, no setter

    @cached_property
    def get_end_folder_name(self):
        self.assert_path_exists()
        return os.path.basename(self._dir_path_str)

    # Yields string path when instance is used in str context
    def __str__(self):
        self.assert_path_exists()
        return self._dir_path_str

    # Yields string path when instance is used in file context
    def __fspath__(self):
        self.assert_path_exists()
        return self._dir_path_str


@dataclass
class AudioFilePath(FilePath):
    def __post_init__(self):
        super().__post_init__()

        # Ensure file is a valid audio file
        assert_filepath_is_audio_file(self)

    @property
    def value(self):
        return self._file_path_str  # Only a getter, no setter


@dataclass
class AudioFilePathAlwaysReqExists(FilePathAlwaysRequireExists):
    def __post_init__(self):
        super().__post_init__()

        # Ensure file is a valid audio file
        assert_filepath_is_audio_file(self)

    @property
    def value(self):
        return self._dir_path_str  # Only a getter, no setter
    
@dataclass
class DirPathAlwaysRequireExists(DirPath):
    @property
    def value(self):
        self.assert_path_exists()
        return self._dir_path_str  # Only a getter, no setter

    @cached_property
    def get_end_folder_name(self):
        self.assert_path_exists()
        return os.path.basename(self._dir_path_str)

    # Yields string path when instance is used in str context
    def __str__(self):
        self.assert_path_exists()
        return self._dir_path_str

    # Yields string path when instance is used in file context
    def __fspath__(self):
        self.assert_path_exists()
        return self._dir_path_str


@dataclass
class NonEmptyDir(DirPath):
    def __post_init__(self):
        super().__post_init__()

        assert_folder_has_at_least_one_file(
            folder_path=self,
            context="Attempted to instantiate NonEmptyDir object, but passed folder path has no files..."
            )



"""
UTILS THAT USE THE OBJECTS
"""


from src.ml_scam_classification.utils.enforce_fn_properties import ensure_list_param_not_empty, enforce_types_disallow_none
from src.ml_scam_classification.utils.file_models import (
    DirPath,
    List,
    FileExtension,
    assert_is_folder,
    assert_path_exists,
    get_file_extension_from_path_str,
    apply_fn_to_folder
)



@enforce_types_disallow_none
@ensure_list_param_not_empty("allowed_types")
def folder_only_has_given_file_types(
    folder_path: DirPath,
    allowed_types: List[FileExtension]
) -> bool:
    """
    Returns True if every file in `folder_path` has an extension
    that is in `allowed_types`, otherwise False. No need to include
    the '.' 
    e.g. input: ['txt', 'md'] (no need for the dot before the
    file extension)
    
    Uses `assert_is_valid_path` to validate the folder path, then
    `apply_fn_to_folder` to check each file.
    """
    assert_is_folder(folder_path)

    # 1) Validate folder exists & is a path, and file types not empty
    assert_path_exists(folder_path)
    if len(allowed_types) == 0:
        raise ValueError("Did not provide any allowed file types... (list empty)")
    
    # 2) Define a checker function for each file
    def _check_type(file_path: str) -> bool:
        file_type = get_file_extension_from_path_str(file_path)
        return file_type in allowed_types
    
    # 3) Apply the checker to every file
    results = apply_fn_to_folder(folder_path, _check_type)
    
    # 4) If any file returned False, the folder fails
    return all(ok for _, ok in results)