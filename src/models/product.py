from typing import List
from pydantic import BaseModel


class Product(BaseModel):
    name: str
    url: str
    images: List[str]
