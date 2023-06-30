import os
import json


def joinfile(folder, output):
    list_file = [file for file in os.listdir(folder) if file.endswith(".json")]
    print(list_file)
    merge = {}
    for file in list_file:
        join_file = os.path.join(folder, file)
        with open(join_file, "r") as outfile:
            data = json.load(outfile)
            merge.update(data)
    
    with open(f"{output}/games.json", "w") as games:
        json.dump(merge, games)


path = "./checkpoint"
output = "output"

joinfile(folder=path, output=output)
