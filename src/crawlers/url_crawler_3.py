from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from tqdm import tqdm
import time
from random import random
import logging
from typing import List, Tuple

from selenium.webdriver.chrome.webdriver import WebDriver
from src.models.category import Category
from src.actions.modify_url_per_page import ModifyUrlPerPage
from src.orchestrators.send_request import SendRequest
from src.models.product import Product
from src.helpers.config import Config
from src.actions.get_driver import GetDriver
from src.actions.get_agent import GetAgent
from src.crawlers.base_crawler import BaseCrawler

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pylib_0xe.json.json_helper import JsonHelper


LOGGER = logging.getLogger(__name__)


@dataclass
class UrlCrawler3(BaseCrawler):
    category: Category
    player_number: int

    def crawl(self) -> List[Product]:
        self._base_time = Config.read_env("times.base")
        products = []
        thread_cnt = Config.read_env("thread_cnt")
        participants = Config.read_env("participants")
        with ThreadPoolExecutor(max_workers=thread_cnt) as executor:
            futures = []
            for i in range(thread_cnt):
                futures += [
                    executor.submit(
                        self._products_page,
                        self.player_number,
                        participants,
                        i,
                        thread_cnt,
                    )
                ]
            for i, future in enumerate(futures):
                try:
                    # LOGGER.info(f"[THREAD #{i:01d}] Merge the results")
                    products += future.result()
                except Exception:
                    LOGGER.info(f"[THREAD #{i:01d}] Cannot get the result")
        products = self.make_uniques(products)
        # LOGGER.info(f"product total length = {len(products)}")
        return products

    def _products_page(
        self, start_idx: int, participants: int, thread_number: int, thread_cnt: int
    ) -> List[Product]:
        result: List[Product] = []
        pages = []
        cur_idx = start_idx
        max_search_page = Config.read_env("max_search_page")
        while cur_idx <= min(max_search_page, self.category.page_cnt):
            pages += [cur_idx]
            cur_idx += participants
        base_search_cnt = Config.read_env("base_search_cnt")
        base_sort_numbers = Config.read_env("base_sort_numbers")
        best_sort_number = Config.read_env("best_sort_number")
        max_res = Config.read_env("max_res_per_cat")

        for i, page in enumerate(pages):
            if len(result) >= max_res:
                break
            if i % thread_cnt == thread_number:
                # Do Crawl
                urls = []
                if i < base_search_cnt:
                    for sort_number in base_sort_numbers:
                        url = ModifyUrlPerPage.modify(
                            url=self.category.url, page=page, sort_number=sort_number
                        )
                        urls += [url]
                else:
                    urls += [
                        ModifyUrlPerPage.modify(
                            url=self.category.url,
                            page=page,
                            sort_number=best_sort_number,
                        )
                    ]
                # LOGGER.info(f"[#{thread_number}] URLs: {urls}")
                for url in urls:
                    # LOGGER.info(f"[#{thread_number}] going to fetch {url}")
                    data = SendRequest.send(url, instance=thread_number + 1)
                    if not data:
                        LOGGER.info(f"[#{thread_number}] Cannot fetch page #{page}")
                        continue
                    products = JsonHelper.selector_get_value(data, "data.products")
                    if not products:
                        LOGGER.info(f"[#{thread_number}] EMPTY!")
                    for product in products:
                        id = 0
                        url = ""
                        name = ""
                        try:
                            id = product["id"]
                        except:
                            pass
                        try:
                            url = product["url"]["uri"]
                        except:
                            pass
                        try:
                            name = product["title_fa"]
                        except:
                            pass
                        result += [
                            Product(
                                id=str(id),
                                url=url,
                                name=name,
                                page=page,
                                category_id=self.category.id,
                                images=[],
                            )
                        ]
        return result

    def make_uniques(self, products: List[Product]):
        products = sorted(products)
        unique = []
        for product in products:
            if len(unique) == 0 or not (product == unique[-1]):
                unique += [product]
        return unique
