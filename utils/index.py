import os
import json
from playwright.async_api import Page
from datetime import datetime, timedelta


def save_file(data, path: str):
    # ensure the directory exists
    directory = os.path.dirname(f"data/{path}")
    if not os.path.exists(directory):
        os.makedirs(directory)

    # pick last segment as file name
    segment = path.split("/")

    # write the data to a JSON file
    with open(f"{directory}/{segment[-1]}.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


def absolute_url(page: Page, relative_url: str):
    if relative_url == None:
        return None
    return page.url + relative_url


def convert_persian_to_english(persian_number: str):
    # translation table: Persian digits to English digits
    translation_table = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
    # replace commas, percent and translate digits
    return persian_number.translate(translation_table).replace(",", "").replace("٪", "")


def generate_dates(start_date: str, end_date: str):
    # convert strings to datetime objects
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # check if dates are valid
    if start > end:
        raise ValueError("Start date must be before end date")

    # loop through each day
    current = start
    while current <= end:
        yield current.strftime("%Y-%m-%d")
        current += timedelta(days=1)
