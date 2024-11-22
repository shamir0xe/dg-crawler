from dataclasses import dataclass
from PIL.Image import Image
from typing import List
from src.models.product import Product
from src.crawlers.base_crawler import BaseCrawler


@dataclass
class CrawlImages(BaseCrawler):
    product: Product

    def crawl(self) -> List[Image]:
        return []
