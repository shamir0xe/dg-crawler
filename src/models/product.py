from dataclasses import dataclass
from typing import List, Optional
from PIL.Image import Image


@dataclass
class Product:
    name: str
    url: str
    images: List[Image]
    id: Optional[str] = None

    def __hash__(self) -> int:
        return hash(self.url)

    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, Product):
            return False
        return self.url == value.url
