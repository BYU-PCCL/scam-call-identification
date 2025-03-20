import json

def is_json(myjson):
  try:
    json.loads(myjson)
    return True
  except ValueError:
    return False

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

# Example usage:
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
