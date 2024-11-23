from dataclasses import dataclass
from typing import List
from PIL.Image import Image
from pydantic import BaseModel


@dataclass
class Product:
    name: str
    url: str
    images: List[Image]
