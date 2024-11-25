from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Set
import logging
from src.helpers.config import Config
from src.crawlers.url_crawler import UrlCrawler
from src.crawlers.url_crawler_2 import UrlCrawler2
from src.models.product import Product
from src.crawlers.base_crawler import BaseCrawler

LOGGER = logging.getLogger(__name__)


@dataclass
class CrawlAllProducts(BaseCrawler):
    section: int

    def crawl(self) -> List[Product]:
        urls = Config.read_env("urls")
        return UrlCrawler2(urls[0], self.section).crawl()

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
