from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from tqdm import tqdm
import time
from random import random
import logging
from typing import List, Tuple

from selenium.webdriver.chrome.webdriver import WebDriver
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
class UrlCrawler2(BaseCrawler):
    url: str
    section: int

    def crawl(self) -> List[Product]:
        self._base_time = Config.read_env("times.base")
        products = []
        total_pages, _ = self._fetch_info()
        thread_cnt = Config.read_env("thread_cnt")
        participants = Config.read_env("participants")
        length = (total_pages - 1) // participants + 1
        with ThreadPoolExecutor(max_workers=thread_cnt) as executor:
            futures = []
            for i in range(thread_cnt):
                futures += [
                    executor.submit(
                        self._products_page,
                        (self.section - 1) * length + 1 + i,
                        min(self.section * length, total_pages),
                        thread_cnt,
                    )
                ]
            for i, future in enumerate(futures):
                try:
                    LOGGER.info(f"[THREAD #{i:01d}] Merge the results")
                    products += future.result()
                except Exception:
                    LOGGER.info(f"[THREAD #{i:01d}] Cannot get the result")
        LOGGER.info(f"product total length = {len(products)}")
        return products

    def _fetch_info(self) -> Tuple[int, int]:
        """
        Returns (Total Pages, Total Products)
        """
        LOGGER.info("Fetching info")
        url = ModifyUrlPerPage.modify(url=self.url, page=1)
        data = SendRequest.send(url)
        if not data:
            raise Exception("Cannot fetch info")
        total_pages = int(
            JsonHelper.selector_get_value(data, "data.pager.total_pages")  # type:ignore
        )
        total_products = int(
            JsonHelper.selector_get_value(data, "data.pager.total_items")  # type:ignore
        )
        total_pages = min(total_pages, Config.read_env("max_search_page"))
        if Config.read_env("debug"):
            total_pages = 10
        LOGGER.info(f"pages, products = ({total_pages}, {total_products})")
        return total_pages, total_products

    def _products_page(self, residual: int, max_page: int, steps: int) -> List[Product]:
        result: List[Product] = []
        page = residual
        gen_list = range(residual, max_page + 1, steps)
        if residual % steps == 1:
            gen_list = tqdm(gen_list)
        for page in gen_list:
            time.sleep(self._base_time + self._base_time * random())
            url = ModifyUrlPerPage.modify(url=self.url, page=page)
            # LOGGER.info(f"[#{residual}] Send {url}")
            data = SendRequest.send(url)
            # LOGGER.info(f"[#{residual}] Got Result!")
            if not data:
                LOGGER.info(f"[#{residual}] Cannot fetch page #{page}")
                continue
            products = JsonHelper.selector_get_value(data, "data.products")
            if not products:
                LOGGER.info(f"[#{residual}] EMPTY!")
                # LOGGER.info(data)
                # LOGGER.info(f"[#{residual}] len(products)={len(products)}")
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
                result += [Product(id=str(id), url=url, name=name, images=[])]
            # LOGGER.info(f"[#{residual}] Loop through baby!")
        return result
