import logging
import threading
from ulid import ULID
from random import shuffle
from src.helpers.config import Config
from src.orchestrators.crawl_all_products import CrawlAllProducts
from src.crawlers.crawl_images import CrawlImages
from src.orchestrators.check_image_possibilities import CheckImagePossibilities
from src.orchestrators.save_image import SaveImage


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def run_chunk(products):
    for product in products:
        CrawlImages(product=product).crawl()
        count = 0
        for img in product.images:
            possible = CheckImagePossibilities(image=img).check()
            if possible:
                SaveImage(image=img).save(name=f"{ULID().generate()}#{count+1:02d}")
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
    thread_num = Config.read("main.thread_count")
    product_chunks = []
    cur_chunk = []
    index = 0
    for i, product in enumerate(products):
        cur_chunk += [product]
        if i // thread_num != index:
            product_chunks += cur_chunk
            cur_chunk = []
            index += 1
    if cur_chunk:
        product_chunks += cur_chunk

    thread_pool = []
    for i in range(thread_num):
        thread = threading.Thread(target=run_chunk, args=(product_chunks[i],))
        thread.start()
        thread_pool += [thread]

    for thread in thread_pool:
        thread.join()


if __name__ == "__main__":
    main()
