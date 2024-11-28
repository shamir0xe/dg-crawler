import logging
import time
from random import random
from typing import List

from src.helpers.config import Config
from src.factories.image_filter_factory import ImageFilterFactory
from src.actions.get_driver import GetDriver
from src.orchestrators.product_manager import ProductManager
from src.actions.save_product_images import SaveProductImages
from src.crawlers.crawl_images import CrawlImages

LOGGER = logging.getLogger(__name__)


class ChunkImageFetcher:
    @staticmethod
    def fetch(product_manager: ProductManager, instance: int) -> None:
        LOGGER.info(f"Instanciate #{instance}")
        sleep_time = Config.read("main.cm.sleep")
        image_filter = ImageFilterFactory().create()
        time.sleep(sleep_time * random())
        while True:
            product = product_manager.get_one()
            if not product:
                time.sleep(sleep_time * random())
                continue
            try:
                CrawlImages(product=product).crawl(instance)
                if not product.images:
                    raise Exception()
                product_manager.resolve(product)
            except Exception:
                product_manager.failure(product)
                GetDriver().revoke(instance)
                continue
            try:
                # Filter the images based on the provided sample image
                product.images = image_filter.filter(obj=product)
                if product.images:
                    # Save the filtered images if exists any
                    SaveProductImages(product=product).save()
            except Exception:
                import traceback

                traceback.print_exc()
            del product
        LOGGER.info(f"Instance #{instance} going to die")
        GetDriver().get(instance).close()

    @staticmethod
    def run(products: List, instance: int):
        time.sleep(5 * random())
        LOGGER.info(f"Run chunk #{instance}")
        for product in products:
            CrawlImages(product=product).crawl(instance)
