from dataclasses import dataclass
from PIL import Image


@dataclass
class ImageConvertor:
    img: Image.Image

    def convert(self, kind: str) -> Image.Image:
        return self.img.convert(kind)
