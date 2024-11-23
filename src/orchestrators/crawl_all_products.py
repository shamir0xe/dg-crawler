from typing import List
import logging
from src.helpers.config import Config
from src.crawlers.url_crawler import UrlCrawler
from src.models.product import Product
from src.crawlers.base_crawler import BaseCrawler

LOGGER = logging.getLogger(__name__)


class CrawlAllProducts(BaseCrawler):
    def crawl(self) -> List[Product]:
        products = UrlCrawler(Config.read("main.url")).crawl()
        LOGGER.info(products)
        return products
