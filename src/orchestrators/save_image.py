from dataclasses import dataclass

from PIL.Image import Image

from src.helpers.config import Config


@dataclass
class SaveImage:
    image: Image

    def save(self, name: str) -> None:
        output_dir = Config.read("main.output_dir")
        self.image.save(output_dir.format(name, ".jpg"))
        self.image.close()
