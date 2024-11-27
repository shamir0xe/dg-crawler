from dataclasses import dataclass
from typing import List, Optional
from PIL.Image import Image


@dataclass
class Product:
    name: str
    url: str
    page: int
    images: List[Image]
    id: Optional[str] = None

    def __lt__(self, obj) -> bool:
        if isinstance(obj, Product) and self.page < obj.page:
            return True
        return False

    def __hash__(self) -> int:
        return hash(self.url)

    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, Product):
            return False
        return self.url == value.url
