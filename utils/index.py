import os
import json


def save_file(data, path: str):
    # ensure the directory exists
    directory = os.path.dirname(f"data/amazon/{path}")
    if not os.path.exists(directory):
        os.makedirs(directory)

    # pick last segment as file name
    segment = path.split("/")

    # write the data to a JSON file
    with open(f"{directory}/{segment[-1]}.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
