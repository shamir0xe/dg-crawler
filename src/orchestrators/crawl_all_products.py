from concurrent.futures import ThreadPoolExecutor
from random import shuffle
from tqdm import tqdm
from dataclasses import dataclass
from typing import List, Set
import logging
from src.orchestrators.product_manager import ProductManager
from src.models.category import Category
from src.crawlers.find_leaf_categories import FindLeafCategories
from src.crawlers.url_crawler_3 import UrlCrawler3
from src.helpers.config import Config
from src.crawlers.url_crawler import UrlCrawler

# from src.crawlers.url_crawler_2 import UrlCrawler2
from src.models.product import Product
from src.crawlers.base_crawler import BaseCrawler

LOGGER = logging.getLogger(__name__)


@dataclass
class CrawlAllProducts(BaseCrawler):
    leaf_categories: List[Category]
    player_number: int
    executor: ThreadPoolExecutor

    def crawl(self, pm: ProductManager) -> None:
        for category in self.leaf_categories:
            UrlCrawler3(
                category, self.player_number, pm=pm, executor=self.executor
            ).crawl()

    def crawl_old(self) -> List[Product]:
        urls = Config.read_env("urls")
        products: Set[Product] = set()
        thread_cnt = Config.read_env("thread_cnt")
        with ThreadPoolExecutor(max_workers=thread_cnt) as executor:
            futures = []
            for i, url in enumerate(urls):
                futures += [
                    executor.submit(UrlCrawler(url).crawl, (i % thread_cnt) + 1)
                ]
            for i, future in enumerate(futures):
                try:
                    LOGGER.info(f"[THREAD #{i:01d}] Merge the results")
                    products |= set(future.result())
                except Exception:
                    LOGGER.info(f"[THREAD #{i:01d}] Cannot get the result")
        LOGGER.info(products)
        return list(products)
