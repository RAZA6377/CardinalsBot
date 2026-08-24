from pathlib import Path
from handlers._printer import ColorPrint
import json
from typing import Dict


class DataManager:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def get_data_dir(self):
        return self.data_dir

    def get_data_files(self):
        files = list()
        for file in self.get_data_dir.iterdir():
            files.append(file)
        return files

    def read_file(self, file_path: Path):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except Exception as e:
            ColorPrint().failed(f"Error while reading {file_path} : {e}")
            data = {}
        return data

    def save_file(self, file: Path, data: Dict):
        with open(file, "w") as f:
            json.dump(data, f, indent=4)
