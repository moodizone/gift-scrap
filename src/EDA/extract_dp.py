import os
import json
import sys

from mamad.test import name


# [1.json, 10.json, 3.json] => [1.json, 3.json, 10.json]
def sort_based_on_name_ascending(name: str) -> int:
    truncated_name = name.split(".")[0]
    convert_to_int = int(truncated_name)
    return convert_to_int


print(__name__)
print(sys.path)

current_dir = os.path.dirname(__file__)
data_dir = os.path.join(current_dir, "art_and_crafts")
file_list = sorted(os.listdir(data_dir), key=sort_based_on_name_ascending)
data = []
for index, file_name in enumerate(file_list):
    file_path = os.path.join(data_dir, file_name)

    if os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            content = json.load(file)
            count = content["count"]
            details = content["details"]

            if count > 0:
                data += details
