import logging
import threading
from typing import List
from ulid import ULID
from random import shuffle
from src.helpers.config import Config
from src.orchestrators.crawl_all_products import CrawlAllProducts
from src.crawlers.crawl_images import CrawlImages
from src.orchestrators.check_image_possibilities import CheckImagePossibilities
from src.orchestrators.save_image import SaveImage
from pylib_0xe.string.hash_generator import HashGenerator


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

LOGGER = logging.getLogger(__name__)


def run_chunk(products: List, instance: int):
    LOGGER.info("Run chunks")
    LOGGER.info(products)
    for product in products:
        CrawlImages(product=product).crawl(instance)
        count = 0
        for img in product.images:
            possible = CheckImagePossibilities(image=img).check()
            if possible:
                SaveImage(image=img).save(
                    name=f"{ULID().generate() + HashGenerator.generate()}#{count+1:02d}"
                )
                count += 1


def main():
    """
    Consists of 3 stages:
        1) Crawl all of the product URLs in the list-page
        2) For each URL, crawl all of the images
        3) Run YOLO on each image, and tag it if there contains
        an suspicious text-box
    """
    products = CrawlAllProducts().crawl()
    shuffle(products)
    thread_count = int(Config.read("main.thread_count"))
    batch_size = (len(products) + 1) // thread_count
    product_chunks = []
    cur_chunk = []
    index = 0
    for i, product in enumerate(products):
        cur_chunk += [product]
        if i // batch_size != index:
            product_chunks.append(cur_chunk)
            cur_chunk = []
            index = i // batch_size
            LOGGER.info(f"#{i} chunk#{index}")
    if cur_chunk:
        product_chunks.append(cur_chunk)

    LOGGER.info("chunks:")
    LOGGER.info(product_chunks)

    thread_pool = []
    for i in range(len(product_chunks)):
        thread = threading.Thread(
            target=run_chunk,
            args=(
                product_chunks[i],
                i + 1,
            ),
        )
        thread.start()
        thread_pool += [thread]

    for thread in thread_pool:
        thread.join()


if __name__ == "__main__":
    main()
