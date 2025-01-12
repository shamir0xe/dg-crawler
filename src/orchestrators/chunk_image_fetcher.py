import logging
import time
from random import random
from typing import List

from actions.image_convertor import ImageConvertor
from src.factories.image_generator import ImageGenerator
from src.orchestrators.process_image import ProcessImage
from src.helpers.config import Config
from src.factories.image_filter_factory import ImageFilterFactory
from src.actions.get_driver import GetDriver
from src.orchestrators.product_manager import ProductManager
from src.actions.save_product_images import SaveProductImages
from src.crawlers.crawl_images import CrawlImages

LOGGER = logging.getLogger(__name__)


class ChunkImageFetcher:
    @staticmethod
    def fetch(
        product_manager: ProductManager, img_gen: ImageGenerator, instance: int
    ) -> None:
        LOGGER.info(f"Instanciate #{instance}")
        img_gen_cfg = Config.read_env("image_gen")
        sleep_time = Config.read("main.cm.sleep")
        image_filter = ImageFilterFactory().create()
        time.sleep(sleep_time * random())
        while True:
            product = product_manager.get_one()
            if not product:
                time.sleep(sleep_time * random())
                continue
            try:
                CrawlImages(product=product, instance=instance).crawl()
                # if not product.images:
                #     raise Exception()
                product_manager.resolve(product)
            except Exception:
                product_manager.failure(product)
                GetDriver().revoke(instance)
                continue
            try:
                # Convert images to RGB
                for i, image in enumerate(product.images):
                    try:
                        image = ImageConvertor(image).convert("RGB")
                    except Exception:
                        continue
                    if image:
                        product.images[i] = image

                # Filter the images based on the provided sample image
                product.images = image_filter.filter(obj=product)
                if product.images:
                    # Crop the image and add it to img_gen
                    for image in product.images:
                        cropped_img = ProcessImage(image, cfg=img_gen_cfg).process()
                        if cropped_img:
                            img_gen.add_one(img=cropped_img, product=product)
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
            CrawlImages(product=product, instance=instance).crawl()
