from dataclasses import dataclass, field
from typing import List
from PIL.Image import Image
from ulid import ULID


@dataclass
class Product:
    name: str
    url: str
    page: int
    images: List[Image]
    category_id: int
    id: str = field(default_factory=ULID().generate)

    def __lt__(self, obj) -> bool:
        if isinstance(obj, Product) and self.page < obj.page:
            return True
        return False

    def __repr__(self) -> str:
        return self.id

    def __hash__(self) -> int:
        return hash(self.url)

    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, Product):
            return False
        return self.url == value.url
