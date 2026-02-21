import os

import yaml

from src.config import CONFIG_FILE_NAME, CONFIG_DIR

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_yaml(folder: str = CONFIG_DIR, filename: str = CONFIG_FILE_NAME):
    filepath = os.path.join(folder, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)