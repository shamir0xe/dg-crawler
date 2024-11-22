from dataclasses import dataclass
from PIL.Image import Image


@dataclass
class CheckImagePossibilities:
    image: Image

    def check(self) -> bool:
        return True
