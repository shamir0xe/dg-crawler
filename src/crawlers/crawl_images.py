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
        # target_url = f"https://api.digikala.com/v2/product/{self.product.id}/"
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
        self.user_agent = GetAgent.get()
        self.image_query_timeout = Config.read_env("times.short_delay")
        # LOGGER.info(urls)
        try:
            for url_ in urls:
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
