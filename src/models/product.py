from dataclasses import dataclass, field
from random import randint
from typing import List
from PIL.Image import Image


@dataclass
class Product:
    name: str
    url: str
    page: int
    category_id: int
    id: int = field(default=randint(int(1e6), int(1e10)))
    images: List[Image] = field(default_factory=list)

    def __lt__(self, obj) -> bool:
        """
        page INC
        id DESC
        """
        if isinstance(obj, Product):
            if self.page < obj.page or (self.page == obj.page and self.id > obj.id):
                return True
        return False

    def __repr__(self) -> str:
        return str(self.id)

    def __hash__(self) -> int:
        return hash(self.url)

    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, Product):
            return False
        return self.id == value.id
