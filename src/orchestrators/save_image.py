from dataclasses import dataclass
import re

from PIL.Image import Image

from src.helpers.config import Config

BAD_CHARS = r'[<>:"/\\|?*\']'


@dataclass
class SaveImage:
    image: Image

    def save(self, name: str) -> None:
        output_dir = Config.read("main.output_dir")
        name = re.sub(BAD_CHARS, "", name)
        self.image.save(output_dir.format(name, "jpg"))
        self.image.close()
