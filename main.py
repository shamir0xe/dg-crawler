import logging
from src.orchestrators.crawl_all_products import CrawlAllProducts
from src.orchestrators.crawl_images import CrawlImages
from src.orchestrators.check_image_possibilities import CheckImagePossibilities
from src.orchestrators.save_image import SaveImage


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main():
    """
    Consists of 3 stages:
        1) Crawl all of the product URLs in the list-page
        2) For each URL, crawl all of the images
        3) Run YOLO on each image, and tag it if there contains
        an suspicious text-box
    """
    products = CrawlAllProducts().crawl()
    for product in products:
        images = CrawlImages(product=product).crawl()
        count = 0
        for img in images:
            possible = CheckImagePossibilities(image=img).check()
            if possible:
                SaveImage(image=img).save(name=f"{product.name}#{count+1:02d}")
                count += 1


if __name__ == "__main__":
    main()
