from dataclasses import dataclass, field
from typing import List
from PIL.Image import Image
from ulid import ULID


@dataclass
class Product:
    name: str
    url: str
    page: int
    category_id: int
    id: str = field(default_factory=ULID().generate)
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
        return self.id

    def __hash__(self) -> int:
        return hash(self.url)

    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, Product):
            return False
        return self.id == value.id
