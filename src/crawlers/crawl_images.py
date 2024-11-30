from dataclasses import dataclass
import logging
import io
import httpx
from PIL import Image
from typing import List, Optional

from pylib_0xe.json.json_helper import JsonHelper
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from src.orchestrators.send_request import SendRequest
from src.actions.go_to_url import GoToUrl
from src.actions.get_agent import GetAgent
from src.helpers.config import Config
from src.actions.get_driver import GetDriver
from src.models.product import Product
from src.crawlers.base_crawler import BaseCrawler


LOGGER = logging.getLogger("CrawlProductImages")

RETRY_CNT = 5


@dataclass
class CrawlImages(BaseCrawler):
    product: Product
    instance: int

    def crawl(self) -> List[Image.Image]:
        urls_v1 = self._v1_urls()
        urls_v2 = self._v2_urls()

        diffs = self._diff(urls_v1, urls_v2)
        if not diffs:
            return []

        if len(diffs) > 1:
            LOGGER.info("SPECIAL ONE")
            self.product.name = f"FFFFFFFF-{self.product.name}"

        self.user_agent = GetAgent.get()
        self.image_query_timeout = Config.read_env("times.short_delay")
        # LOGGER.info(urls)
        try:
            for url_ in diffs:
                image = self._retry_image(url_)
                if image:
                    self.product.images += [image]
        except Exception as e:
            LOGGER.info(f"Exception Occured: {str(e)[:22]}")
        return self.product.images

    def _retry_image(self, url: str, count: int = RETRY_CNT) -> Optional[Image.Image]:
        if count == 0:
            LOGGER.info(f"[{self.instance}] Cant fetch the image, giving up: {url}")
            return None
        try:
            with httpx.Client(
                timeout=self.image_query_timeout,
                headers={"User-Agent": self.user_agent},
            ) as client:
                response = client.get(url, follow_redirects=True)

                # Check HTTP status code
                if response.status_code == 200:
                    if count != RETRY_CNT:
                        LOGGER.info(f"[{self.instance}] Resolved!")
                    content_type = response.headers.get("Content-Type", "")
                    if "image" not in content_type.lower():
                        # It's not an image, move on
                        return None
                    img = Image.open(io.BytesIO(response.content))
                    return img
        except Exception:
            pass
        LOGGER.info(f"[{self.instance}] Retrying")
        return self._retry_image(url, count - 1)

    def _v1_urls(self) -> List[str]:
        target_url = self.product.url
        product_data = SendRequest.send(target_url, self.instance)
        if not product_data:
            LOGGER.info("EMPTY")
            return []

        urls = []
        main_url = JsonHelper.selector_get_value(
            product_data, "data.product.images.main"
        )
        if main_url:
            urls += [main_url]
        list_urls = JsonHelper.selector_get_value(
            product_data, "data.product.images.image_list"
        )
        if list_urls:
            urls += list_urls
        urls = sorted(urls)
        return urls

    def _v2_urls(self) -> List[str]:
        target_url = f"https://api.digikala.com/v2/product/{self.product.id}/"
        product_data = SendRequest.send(target_url, self.instance)
        if not product_data:
            LOGGER.info("EMPTY")
            return []
        urls = [
            JsonHelper.selector_get_value(product_data, "data.product.images.main.url")
        ]
        urls += JsonHelper.selector_get_value(
            product_data, "data.product.images.list.*.url"
        )
        result = []
        for url_ in urls:
            if len(url_) > 0:
                result += [url_[0]]
        result = sorted(result)
        return result

    def _diff(self, urls_1: List[str], urls_2: List[str]) -> List[str]:
        m1 = [self._remove(t) for t in urls_1]
        m2 = [self._remove(t) for t in urls_2]
        diff = (set(m1) - set(m2)) | (set(m2) - set(m1))
        return list(diff)

    def _remove(self, url: str) -> str:
        patterns = ["/resize", "/quality"]
        idx = int(1e9)
        for pattern in patterns:
            i = url.find(pattern)
            if i == -1:
                continue
            idx = min(idx, i)
        if idx < 1e5:
            url = url[:idx]
        return url
