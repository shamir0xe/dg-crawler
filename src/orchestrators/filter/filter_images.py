from random import randint
from PIL import Image
import math
from typing import List, Tuple
from src.orchestrators.filter.base_filter import BaseFilter
from src.helpers.config import Config
from src.models.product import Product
from src.helpers.decorators.singleton import singleton


@singleton
class FilterImages(BaseFilter):
    def __init__(self) -> None:
        self.sample_image = Image.open(Config.read("main.base_image.path"))
        self.sample_image = self.sample_image.convert("RGB")
        self.width = self.sample_image.width
        self.height = self.sample_image.height
        self.n = Config.read("main.base_image.sample_cnt")
        self.threshold = Config.read_env("image_similarity_threshold")
        self.max_distance = Config.read_env("diff_color_max_distance")
        self.sample_points: List[Tuple[int, int]] = [
            (randint(0, self.width - 1), randint(0, self.height - 1))
            for _ in range(self.n)
        ]
        self.sample_values = [
            self.sample_image.getpixel(self.sample_points[i]) for i in range(self.n)
        ]

    def filter(self, obj: Product) -> List[Image.Image]:
        result = []
        for image in obj.images:
            if self._match(image):
                result += [image]
        return result

    def _match(self, image: Image.Image) -> bool:
        image = image.convert("RGB")
        if image.width != self.width or image.height != self.height:
            image = image.resize((self.width, self.height))
        values = [image.getpixel(self.sample_points[i]) for i in range(self.n)]
        cnt = 0
        for i in range(self.n):
            cnt += 1 if self._kinda_close(self.sample_values[i], values[i]) else 0
        return 1.0 * cnt / self.n >= self.threshold

    def _kinda_close(self, c1, c2) -> bool:
        close_enough = True
        for i in range(3):
            close_enough &= math.fabs(c1[i] - c2[i]) <= self.max_distance
        return close_enough
