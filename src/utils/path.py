import os
from pathlib import Path


def get_project_root() -> Path:
    current_path = Path(__file__)
    return current_path.resolve().parent.parent.parent


def get_absolute_path(*path: str) -> Path:
    return get_project_root().joinpath(*path)
