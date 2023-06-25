import os
import json

folder_path = './output'


def read_all_json():
    json_files = [file for file in os.listdir(
        folder_path) if file.endswith('.json')]
    state = {}
    for file in json_files:
        file_path = os.path.join(folder_path, file)
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            state[file.replace(".json", "").replace(
                "koperasi_nik_", "")] = len(data)
    return state


print(read_all_json())
