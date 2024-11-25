import logging
import time
from random import random
from typing import List

from src.actions.get_driver import GetDriver
from src.orchestrators.product_manager import ProductManager
from src.actions.save_product_images import SaveProductImages
from src.crawlers.crawl_images import CrawlImages

LOGGER = logging.getLogger(__name__)


class ChunkImageFetcher:
    @staticmethod
    def fetch(product_manager: ProductManager, instance: int) -> None:
        time.sleep(5 * random())
        LOGGER.info(f"Instanciate #{instance}")
        while product_manager.have_any():
            product = product_manager.get_one()
            if not product:
                break
            try:
                CrawlImages(product=product).crawl(instance)
                if not product.images:
                    raise Exception()
                product_manager.resolve(product)
            except Exception:
                product_manager.failure(product)
                continue
            try:
                SaveProductImages(product=product).save()
            except Exception:
                import traceback

                traceback.print_exc()
        LOGGER.info(f"Instance #{instance} going to die")
        GetDriver.get(instance).close()

    @staticmethod
    def run(products: List, instance: int):
        time.sleep(5 * random())
        LOGGER.info(f"Run chunk #{instance}")
        # LOGGER.info(products)
        for product in products:
            CrawlImages(product=product).crawl(instance)
