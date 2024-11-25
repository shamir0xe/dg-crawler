import logging
import time
from random import random
from typing import List

from pylib_0xe.string.hash_generator import HashGenerator
from ulid import ULID

from src.crawlers.crawl_images import CrawlImages
from src.orchestrators.check_image_possibilities import CheckImagePossibilities
from src.orchestrators.save_image import SaveImage

LOGGER = logging.getLogger(__name__)


class ChunkImageFetcher:
    @staticmethod
    def run(products: List, instance: int):
        time.sleep(5 * random())
        LOGGER.info(f"Run chunk #{instance}")
        # LOGGER.info(products)
        for product in products:
            CrawlImages(product=product).crawl(instance)
            count = 0
            for img in product.images:
                possible = CheckImagePossibilities(image=img).check()
                if possible:
                    SaveImage(image=img).save(name=f"{product.name}#{count+1:02d}")
                    count += 1
