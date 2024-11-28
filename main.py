import logging
from src.crawlers.crawl_all_images import CrawlAllImages
from src.orchestrators.send_request import SendRequest
from src.actions.initialize import Initialize
from src.actions.save_product_urls import SaveProductUrls
from src.orchestrators.crawl_all_products import CrawlAllProducts
from src.helpers.config import Config
from pylib_0xe.argument.argument_parser import ArgumentParser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)5s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

LOGGER = logging.getLogger("main")


def main():
    """
    Consists of 3 stages:
        1) Crawl all of the product URLs in the list-page
        2) For each URL, crawl all of the images
        3) Run YOLO on each image, and tag it if there contains
        an suspicious text-box
    """
    Initialize()

    # 1
    if not ArgumentParser.is_option("n"):
        raise Exception("Provide which part is yours (1-#participants_cnt)")
    player_number = ArgumentParser.get_value("n")
    if not player_number:
        raise Exception("Option is not valid")
    player_number = int(player_number)
    assert 1 <= player_number <= Config.read_env("participants")

    #####
    if ArgumentParser.is_option("img"):
        if not ArgumentParser.is_option("i"):
            raise Exception("Provide instance number")
    #####

    products = CrawlAllProducts(player_number=player_number).crawl()
    for product in products:
        LOGGER.info(f"[#{product.page:05d} -- {product.name} -- {product.category_id}]")

    # 1.5
    product_list = []
    for product in products:
        product_list += [
            {
                "id": product.id,
                "name": product.name,
                "url": product.url,
                "page": product.page,
                "category_id": product.category_id,
            }
        ]
    SaveProductUrls.save(product_list)

    # 2
    CrawlAllImages(products).crawl()


def url_builder(page: int, sort: int) -> str:
    # url = "https://api.digikala.com/v1/categories/suspension-systems-and-component/search/"
    # url = "https://api.digikala.com/v1/categories/girls-headwear/search/"
    # url = "https://api.digikala.com/v1/categories/rural-tea/search/"
    # url = "https://api.digikala.com/v1/categories/religious-printed-book/search/"
    # url = "https://api.digikala.com/v1/categories/medical-Insoles/search/"
    # url = "https://api.digikala.com/v1/categories/punching-bag/search/"
    # url = "https://api.digikala.com/v1/categories/bowl/search/"
    url = "https://api.digikala.com/v1/categories/electric-massager/search/"
    url += f"?sort={sort}"
    url += f"&page={page}"
    return url


def examine():
    from tqdm import tqdm

    sort_set = [
        # {"id": 22, "title_fa": "مرتبط‌ترین"},        # 64,   21, 11, 1,  1,  1, 39
        {"id": 4, "title_fa": "پربازدیدترین"},  # N,    52, 40, 1,  1,  7, 82
        {"id": 1, "title_fa": "جدیدترین"},  # 15,   11, 3,  94, 46, 1, 9
        {"id": 7, "title_fa": "پرفروش‌ترین‌"},  # N,    45, 23, 2,  1,  N, 54
        {"id": 20, "title_fa": "ارزان‌ترین"},  # 39,   36, 46, 40, 19, 8, 100
        {"id": 21, "title_fa": "گران‌ترین"},  # N,    37, 4,  N,  54, 1, 2
        {"id": 25, "title_fa": "سریع‌ترین ارسال"},  # 51,   54, 11, 16, 11, 2, 83
        # {"id": 27, "title_fa": "پیشنهاد خریداران"}, # N,    38, N,  31, 12, 6, 51
        # {"id": 29, "title_fa": "منتخب"},            # N,    52, N,  19, 1,  7, 82
    ]
    # target_id = 17320403
    # target_id = 17360539
    # target_id = 16919467
    # target_id = 8625255
    # target_id = 4463244
    # target_id = 17168537
    # target_id = 16689506
    target_id = 13181766
    for st in sort_set:
        found = False
        for page in tqdm(range(0, 100)):
            url = url_builder(page + 1, st["id"])
            data = SendRequest.send(url)
            if not data:
                LOGGER.info(f"error occured {st['title_fa']}")
                continue
            products = data["data"]["products"]
            ids = [product["id"] for product in products]
            if target_id in ids:
                LOGGER.info(f"{st['title_fa']}: {page+1}")
                found = True
                break
        if not found:
            LOGGER.info(f"{st['id']} not found")


if __name__ == "__main__":
    examine()
    # main()
