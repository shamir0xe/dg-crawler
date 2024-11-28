from src.factories.base_factory import BaseFactory
from src.helpers.config import Config
from src.orchestrators.filter.base_filter import BaseFilter
from src.orchestrators.filter.filter_images import FilterImages
from src.orchestrators.filter.filter_images_2 import FilterImages2


class ImageFilterFactory(BaseFactory):
    def create(self) -> BaseFilter:
        method = Config.read_env("filter.method")
        if method == 1:
            return FilterImages()
        if method == 2:
            return FilterImages2()
        raise Exception("Filter Not Implemented")