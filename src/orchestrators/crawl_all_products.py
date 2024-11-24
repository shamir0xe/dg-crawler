from concurrent.futures import ThreadPoolExecutor
from typing import List, Set
import logging
from src.helpers.config import Config
from src.crawlers.url_crawler import UrlCrawler
from src.models.product import Product
from src.crawlers.base_crawler import BaseCrawler

LOGGER = logging.getLogger(__name__)


class CrawlAllProducts(BaseCrawler):
    def crawl(self) -> List[Product]:
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
