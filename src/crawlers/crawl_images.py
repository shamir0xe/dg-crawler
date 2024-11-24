from dataclasses import dataclass
import logging
import io
import requests
import time
from PIL import Image
from typing import List

from selenium.webdriver.chrome.webdriver import WebDriver
from src.helpers.config import Config
from src.actions.get_agent import GetAgent
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
        url = self.product.url
        if url[-1] != "/":
            url += "/"
        url += "#gallery"
        driver = GetDriver.get(instance)
        LOGGER.info(f"going to crawl {url}")
        driver.get(url)
        debug_begin = time.time()
        WebDriverWait(driver, Config.read("main.loading_timelimit")).until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    "//div[@id='modal-root']//div[1]//img[1]",
                )
            )
        )
        time.sleep(3)
        LOGGER.info(f"elapsed time: {time.time() - debug_begin}s")

        for index in range(1, 100):
            try:
                image = self._get_image(index, driver)
                self.product.images += [image]
            except Exception:
                # traceback.print_exc()
                break
        return self.product.images

    def _get_image(self, index: int, driver: WebDriver) -> Image.Image:
        xpath = f"//div[@id='modal-root']//div[{index}]//img[1]"
        element = driver.find_element(
            By.XPATH,
            xpath,
        )
        url = element.get_attribute("src")
        if not url:
            url = ""
        LOGGER.info(f"source of the image: {url}")

        r = requests.get(url, stream=True)
        if r.status_code == 200:
            return Image.open(io.BytesIO(r.content))
        raise Exception("END")
