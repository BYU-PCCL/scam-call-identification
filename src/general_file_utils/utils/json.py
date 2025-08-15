import json

from src.general_file_utils.utils.path_checks import assert_path_exists

def load_json_from_path(path):
    assert_path_exists(path)

    with open(path, 'r') as file:
        data = json.load(file)

    return data

if __name__ == "__main__":
    load_json_from_path("temp_test/test.json")
