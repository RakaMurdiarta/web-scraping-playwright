import os
import json


def merge_json_files(folder_path, output_file_path):
    # Get a list of all JSON files in the folder
    json_files = [file for file in os.listdir(folder_path) if file.endswith(".json")]

    merged_data = {}

    # Read and merge the contents of each JSON file
    for file in json_files:
        file_path = os.path.join(folder_path, file)
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
            # merged_data.extend(data)
            merged_data.update(data)

    # Write the merged data to the output file
    with open(output_file_path, "w") as output_file:
        json.dump(merged_data, output_file, indent=4)


# Example usage
folder_path = "./output"  # Replace with the path to your folder
output_file_path = "./data-nik/koperasi-uuid.json"  # Replace with the desired output file path

merge_json_files(folder_path, output_file_path)
