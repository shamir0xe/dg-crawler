from dataclasses import dataclass
import logging
import io
import requests
import time
from PIL import Image
from typing import List, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from src.actions.go_to_url import GoToUrl
from src.actions.get_agent import GetAgent
from src.helpers.config import Config
from src.actions.get_driver import GetDriver
from src.models.product import Product
from src.crawlers.base_crawler import BaseCrawler
from selenium.webdriver.common.by import By


LOGGER = logging.getLogger(__name__)


@dataclass
class CrawlImages(BaseCrawler):
    product: Product

    def crawl(self, instance: int) -> List[Image.Image]:
        self.instance = instance
        self.user_agent = GetAgent.get()
        self.bad_strings = Config.read("main.bad_strings")
        base_url = Config.read("main.base_url")
        url = base_url + self.product.url
        if url[-1] != "/":
            url += "/"
        url += "#gallery"
        driver = GetDriver.get(instance)

        try:
            driver.get(url)
        except Exception:
            LOGGER.info(f"[{self.instance}] Cannot fetch the URL")
            return self.product.images

        if not self._wait(driver):
            LOGGER.info(f"[{self.instance}] Empty IMGS")
            return self.product.images

        try:
            images = self._get_image(driver)
            self.product.images += images
        except Exception as e:
            LOGGER.info(f"Exception Occured: {str(e)[:22]}")
        return self.product.images

    def _get_image(self, driver: WebDriver) -> List[Image.Image]:
        xpath = "//div[@id='modal-root']//img[1]"
        elements = driver.find_elements(
            By.XPATH,
            xpath,
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

    def _retry_image(self, url: str, count: int = 5) -> Optional[Image.Image]:
        if count == 0:
            LOGGER.info(f"[{self.instance}] Cant fetch the image, giving up: {url}")
            return None
        try:
            r = requests.get(
                url,
                stream=True,
                timeout=Config.read_env("times.short_delay"),
                headers={"User-Agent": self.user_agent},
            )
            if r.status_code == 200:
                if count != 5:
                    LOGGER.info(f"[{self.instance}] Resolved!")
                return Image.open(io.BytesIO(r.content))
        except Exception:
            pass
        time.sleep(Config.read_env("times.short_delay"))
        LOGGER.info(f"[{self.instance}] Retrying")
        return self._retry_image(url, count - 1)

    def _wait(self, driver: WebDriver, count: int = 5):
        if count == 0:
            return False
        try:
            GoToUrl(driver=driver, timeout=Config.read_env("times.short_delay")).go(
                url="", xpath="//div[@id='modal-root']//picture[1]/img[1]"
            )
            if count != 5:
                LOGGER.info(f"[{self.instance}] Resolved!")
            return True
        except TimeoutException:
            self._refresh(driver)
            return self._wait(driver, count - 1)

    def _refresh(self, driver: WebDriver) -> None:
        LOGGER.info(f"[{self.instance}] Refreshing")
        try:
            LOGGER.info(f"[{self.instance}] Going to dummy url")
            GoToUrl(driver=driver, timeout=Config.read_env("times.short_delay")).go(
                url=Config.read("main.dummy_url"), xpath=Config.read("main.dummy_xpath")
            )
            LOGGER.info(f"[{self.instance}] We are dummied :)")
        except Exception:
            import traceback

            traceback.print_exc()
            # time.sleep(Config.read_env("times.short_delay"))
        driver.back()
        driver.refresh()
