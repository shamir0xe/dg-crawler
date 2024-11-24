import logging

from random import shuffle
from concurrent.futures import ThreadPoolExecutor
from src.actions.save_product_urls import SaveProductUrls
from src.orchestrators.crawl_all_products import CrawlAllProducts
from src.helpers.config import Config
from src.orchestrators.chunk_image_fetcher import ChunkImageFetcher
from src.orchestrators.chunk_products import ChunkProducts
from pylib_0xe.argument.argument_parser import ArgumentParser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

LOGGER = logging.getLogger(__name__)


def main():
    """
    Consists of 3 stages:
        1) Crawl all of the product URLs in the list-page
        2) For each URL, crawl all of the images
        3) Run YOLO on each image, and tag it if there contains
        an suspicious text-box
    """
    # 1
    if not ArgumentParser.is_option("n"):
        raise Exception("Provide which part is yours (1-#participants_cnt)")
    player_number = ArgumentParser.get_value("n")
    if not player_number:
        raise Exception("Option is not valid")
    player_number = int(player_number)
    assert 1 <= player_number <= Config.read_env("participants")
    products = CrawlAllProducts(section=player_number).crawl()

    # 1.5
    product_urls = []
    for product in products:
        product_urls += [
            {
                "name": product.name,
                "url": product.url,
                "id": product.id,
            }
        ]
    SaveProductUrls.save(product_urls)

    # 2
    shuffle(products)
    thread_count = Config.read_env("thread_cnt")
    product_chunks = ChunkProducts.chunk(products=products, chunk_count=thread_count)
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = []
        for i in range(len(product_chunks)):
            futures += [
                executor.submit(
                    ChunkImageFetcher.run, product_chunks[i], (i % thread_count) + 1
                )
            ]


if __name__ == "__main__":
    main()
