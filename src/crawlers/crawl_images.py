from dataclasses import dataclass
import logging
import io
import requests
import time
from PIL import Image
from typing import List, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from src.actions.get_agent import GetAgent
from src.helpers.config import Config
from src.actions.get_driver import GetDriver
from src.models.product import Product
from src.crawlers.base_crawler import BaseCrawler
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


LOGGER = logging.getLogger(__name__)


@dataclass
class CrawlImages(BaseCrawler):
    product: Product

    def crawl(self, instance: int) -> List[Image.Image]:
        self.instance = instance
        self.user_agent = GetAgent.get()
        base_url = Config.read("main.base_url")
        url = base_url + self.product.url
        if url[-1] != "/":
            url += "/"
        url += "#gallery"
        driver = GetDriver.get(instance)
        # LOGGER.info(f"going to crawl {url}")
        driver.get(url)
        debug_begin = time.time()
        if not self._wait(driver):
            LOGGER.info("Empty IMGS")
            return []
        # LOGGER.info(f"elapsed time: {time.time() - debug_begin}s")
        try:
            images = self._get_image(driver)
            self.product.images += images
        except Exception:
            LOGGER.info("Exception Occured => End.")
        return self.product.images

    def _get_image(self, driver: WebDriver) -> List[Image.Image]:
        xpath = "//div[@id='modal-root']//img[1]"
        elements = driver.find_elements(
            By.XPATH,
            xpath,
        )
        images = []
        for element in elements:
            url = element.get_attribute("src")
            if not url:
                url = ""
            # LOGGER.info(f"source of the image: {url}")
            image = self._retry_image(url)
            if image:
                images += [image]
        if not images:
            raise Exception("END")
        return images

    def _retry_image(self, url: str, count=5) -> Optional[Image.Image]:
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
            WebDriverWait(driver, Config.read_env("times.short_delay")).until(
                EC.presence_of_all_elements_located(
                    (
                        By.XPATH,
                        "//div[@id='modal-root']//img[1]",
                    )
                )
            )
            if count != 5:
                LOGGER.info(f"[{self.instance}] Resolved!")
            return True
        except TimeoutException:
            self._refresh(driver)
            return self._wait(driver, count - 1)

    def _refresh(self, driver: WebDriver) -> None:
        LOGGER.info(f"[{self.instance}] Refreshing")
        driver.refresh()
        time.sleep(Config.read_env("times.short_delay"))
        driver.refresh()
