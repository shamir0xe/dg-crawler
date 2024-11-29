from typing import List

from PIL import Image
from src.orchestrators.filter.base_filter import BaseFilter
from src.helpers.config import Config
from src.helpers.decorators.singleton import singleton
from src.models.product import Product


@singleton
class FilterImages3(BaseFilter):
    def __init__(self) -> None:
        self.hex_color = Config.read_env("box_color")

    def filter(self, obj: Product) -> List[Image.Image]:
        return obj.images
