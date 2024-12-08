import os
import json

from pathlib import Path
from utils.path import get_absolute_path
from scripts.amazon import extract_dp


# [1.json, 10.json, 3.json] => [1.json, 3.json, 10.json]
def sort_based_on_name_ascending(name: str) -> int:
    truncated_name = name.split(".")[0]
    convert_to_int = int(truncated_name)
    return convert_to_int


def main():
    back_up_dir = get_absolute_path("backup/amazon")
    category_list = os.listdir(back_up_dir)
    sum_ = 0

    # iterate over directories
    for category_name in category_list:
        category_path = Path.joinpath(back_up_dir, category_name)
        json_list = sorted(os.listdir(category_path), key=sort_based_on_name_ascending)
        data = []
        index = 0

        # iterate over json files in each directory
        for json_name in json_list:
            json_path = Path.joinpath(category_path, json_name)

            if os.path.isfile(json_path):
                with open(json_path, "r", encoding="utf-8") as file:
                    content = json.load(file)
                    count = content["count"]

                    if count > 0:

                        for info in content["details"]:

                            # some of data miss 'dp' property (the unique product key in aws)
                            if not "dp" in info:
                                info["dp"] = extract_dp(info["url"])
                            info["id"] = index
                            index += 1

                        data += content["details"]

        with open(f"data/{category_name}.json", "w", encoding="utf-8") as output:
            json.dump(data, output, ensure_ascii=False, indent=2)
