from collections import deque
from concurrent.futures import ThreadPoolExecutor, wait
from dataclasses import dataclass
import logging
from typing import List

from src.helpers.config import Config
from src.orchestrators.chunk_image_fetcher import ChunkImageFetcher
from src.orchestrators.product_manager import ProductManager
from src.models.product import Product

LOGGER = logging.getLogger(__name__)


@dataclass
class CrawlAllImages:
    products: List[Product]

    def crawl(self):
        thread_count = Config.read_env("thread_cnt")
        pm = ProductManager(deque(self.products))
        with ThreadPoolExecutor() as executor:
            futures = []
            for i in range(thread_count):
                futures += [
                    executor.submit(ChunkImageFetcher.fetch, pm, (i % thread_count) + 1)
                ]
            wait(futures)
            LOGGER.info("Done & Dusted ;)")
