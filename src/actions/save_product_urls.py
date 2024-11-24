from typing import List
import json
from os import path
from pylib_0xe.file.file import File

from src.helpers.config import Config


class SaveProductUrls:
    @staticmethod
    def save(output: List) -> None:
        dir = Config.read("main.urls_path")
        File.write_file(path.join(dir, "product-urls.json"), json.dumps(output))
