from dataclasses import dataclass
import logging
import io
import httpx
from PIL import Image
from typing import List, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
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

    def crawl(self, instance: int) -> List[Image.Image]:
        self.instance = instance
        self.user_agent = GetAgent.get()
        self.bad_strings = Config.read("main.bad_strings")
        self.wait_xpath = Config.read("main.wait_xpath")
        self.imgs_xpath = Config.read("main.imgs_xpath")
        self.image_query_timeout = Config.read_env("times.short_delay")

        base_url = Config.read("main.base_url")
        url = base_url + self.product.url
        if url[-1] != "/":
            url += "/"
        url += "#gallery"
        driver = GetDriver().get(instance)

        try:
            driver.get(url)
        except Exception:
            LOGGER.info(f"[{self.instance}] Cannot fetch the URL")
            return self.product.images

        if not self._wait(driver):
            LOGGER.info(f"[{self.instance}] Empty IMGS")
            return self.product.images

        try:
            images = self._get_images(driver)
            self.product.images += images
        except Exception as e:
            LOGGER.info(f"Exception Occured: {str(e)[:22]}")
        return self.product.images

    def _get_images(self, driver: WebDriver) -> List[Image.Image]:
        elements = driver.find_elements(
            By.XPATH,
            self.imgs_xpath,
        )
        images = []
        for element in elements:
            url = ""
            try:
                url = element.get_attribute("src")
            except Exception:
                pass
            if not url or self._find(url.lower(), self.bad_strings):
                continue
            if "http" not in url[:11].lower():
                continue
            image = self._retry_image(url)
            if image:
                images += [image]
        # if not images:
        #     raise Exception("END")
        return images

    def _find(self, string: str, bad_strings: List[str]) -> bool:
        for temp in bad_strings:
            if temp in string:
                return True
        return False

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

    def _wait(self, driver: WebDriver, count: int = RETRY_CNT) -> bool:
        if count == 0:
            return False
        try:
            GoToUrl(driver=driver, timeout=self.image_query_timeout).go(
                url="", xpath=self.wait_xpath
            )
            if count != RETRY_CNT:
                LOGGER.info(f"[{self.instance}] Resolved!")
            return True
        except Exception:
            self._refresh(driver)
            return self._wait(driver, count - 1)

    def _refresh(self, driver: WebDriver) -> None:
        LOGGER.info(f"[{self.instance}] Refreshing")
        try:
            LOGGER.info(f"[{self.instance}] Going to dummy url")
            GoToUrl(driver=driver, timeout=self.image_query_timeout).go(
                url=Config.read("main.dummy_url"), xpath=Config.read("main.dummy_xpath")
            )
            LOGGER.info(f"[{self.instance}] We are dummies :)")
        except Exception:
            pass
        driver.back()
        driver.refresh()
