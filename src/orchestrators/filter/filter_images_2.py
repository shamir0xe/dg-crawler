from typing import List

from PIL import Image
from src.orchestrators.filter.base_filter import BaseFilter
from src.helpers.config import Config
from src.helpers.decorators.singleton import singleton
from src.models.product import Product


@singleton
class FilterImages2(BaseFilter):
    def __init__(self) -> None:
        self.min_width = Config.read_env("img.min_width")
        self.min_height = Config.read_env("img.min_height")
        self.transform_width = Config.read_env("img.transform_width")

    def filter(self, obj: Product) -> List[Image.Image]:
        result = []
        for image in obj.images:
            good = True
            good &= self._condition1(image)
            if good:
                image = image.resize(
                    (
                        self.transform_width,
                        int(1.0 * image.height / image.width * self.transform_width),
                    )
                )
                result += [image]
        return result

    def _condition1(self, image: Image.Image) -> bool:
        return image.width >= self.min_width and image.height >= self.min_height
