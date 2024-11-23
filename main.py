import logging
from concurrent.futures import ThreadPoolExecutor
from random import shuffle
from src.orchestrators.chunk_products import ChunkProducts
from src.helpers.config import Config
from src.orchestrators.crawl_all_products import CrawlAllProducts
from src.orchestrators.chunk_image_fetcher import ChunkImageFetcher


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
    products = CrawlAllProducts().crawl()
    shuffle(products)
    thread_count = Config.read("main.thread_count")
    product_chunks = ChunkProducts.chunk(products=products, chunk_count=thread_count)

    # 2
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
