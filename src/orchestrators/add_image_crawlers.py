from concurrent.futures import Future, ThreadPoolExecutor, wait
from dataclasses import dataclass
from typing import List

from src.helpers.config import Config
from src.orchestrators.chunk_image_fetcher import ChunkImageFetcher
from src.orchestrators.product_manager import ProductManager


@dataclass
class AddImageCrawlers:
    executor: ThreadPoolExecutor
    pm: ProductManager

    def listen(self) -> List[Future]:
        # thread_count = Config.read_env("thread_cnt")
        futures = []
        thread_cnt = min(4, Config.read_env("thread_cnt"))
        max_threads = Config.read_env("thread_cnt")
        for i in range(thread_cnt, max_threads):
            futures += [self.executor.submit(ChunkImageFetcher.fetch, self.pm, i + 1)]
        return futures
