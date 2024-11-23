import logging
from src.models.product import Product
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


def main():
    """
    Consists of 3 stages:
        1) Crawl all of the product URLs in the list-page
        2) For each URL, crawl all of the images
        3) Run YOLO on each image, and tag it if there contains
        an suspicious text-box
    """
    products = CrawlAllProducts().crawl()

    # products = []
    # products += [
    #     Product(
    #         name="باتری قلمی سونی مدل AAx2 بسته چهار عددی",
    #         url="https://www.digikala.com/product/dkp-12429438/%D8%A8%D8%A7%D8%AA%D8%B1%DB%8C-%D9%82%D9%84%D9%85%DB%8C-%D8%B3%D9%88%D9%86%DB%8C-%D9%85%D8%AF%D9%84-aax2-%D8%A8%D8%B3%D8%AA%D9%87-%DA%86%D9%87%D8%A7%D8%B1-%D8%B9%D8%AF%D8%AF%DB%8C/",
    #         images=[],
    #     )
    # ]
    # products += [
    #     Product(
    #         name=" محافظ صفحه نمایش ژینوس مدل SIMPLX مناسب برای گوشی موبایل سونی Xperia Z1",
    #         url="https://www.digikala.com/product/dkp-13707907/%D9%85%D8%AD%D8%A7%D9%81%D8%B8-%D8%B5%D9%81%D8%AD%D9%87-%D9%86%D9%85%D8%A7%DB%8C%D8%B4-%DA%98%DB%8C%D9%86%D9%88%D8%B3-%D9%85%D8%AF%D9%84-simplx-%D9%85%D9%86%D8%A7%D8%B3%D8%A8-%D8%A8%D8%B1%D8%A7%DB%8C-%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%DB%8C%D9%84-%D8%B3%D9%88%D9%86%DB%8C-xperia-z1/",
    #         images=[],
    #     )
    # ]

    for product in products:
        CrawlImages(product=product).crawl()
        count = 0
        for img in product.images:
            possible = CheckImagePossibilities(image=img).check()
            if possible:
                SaveImage(image=img).save(
                    name=f"{HashGenerator.generate(10)}#{count+1:02d}"
                )
                count += 1


if __name__ == "__main__":
    main()
