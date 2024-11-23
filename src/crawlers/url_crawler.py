from dataclasses import dataclass
import time
from random import random
import traceback
import logging
from typing import List, Tuple

from selenium.webdriver.chrome.webdriver import WebDriver
from src.models.product import Product
from src.helpers.config import Config
from src.actions.get_driver import GetDriver
from src.actions.get_agent import GetAgent
from src.crawlers.base_crawler import BaseCrawler

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


LOGGER = logging.getLogger(__name__)


@dataclass
class UrlCrawler(BaseCrawler):
    url: str

    def crawl(self, instance: int) -> List[Product]:
        wrappers: List[Product] = []
        try:
            user_agent = GetAgent.get()
            LOGGER.info(f"user-agent: {user_agent}")
            driver = GetDriver(user_agent).get(instance)
            LOGGER.info(f"going to crawl {self.url}")
            driver.get(self.url)
            debug_begin = time.time()
            element = WebDriverWait(
                driver, Config.read("main.loading_timelimit")
            ).until(
                EC.presence_of_all_elements_located(
                    (
                        By.XPATH,
                        "//div[@id='ProductListPagesWrapper']//div[1]//a[1]",
                    )
                )
            )
            time.sleep(3)
            LOGGER.info(f"elapsed time: {time.time() - debug_begin}s")

            driver.execute_script("window.scrollTo(0, 0);")
            self.current_scroll = 0
            self.scroll_step = 100  # Number of pixels to scroll per step

            loop = True
            while loop:
                loop = False
                # Slowly scroll to the bottom
                scroll_height = driver.execute_script(
                    "return document.body.scrollHeight"
                )  # Get the full scroll height
                while self.current_scroll < scroll_height:
                    loop = True
                    self._step_scroll(driver)
                    time.sleep(0.1 + 0.1 * random())

                # DEBUG:
                # break

            i = 1
            while True:
                try:
                    url, name = self._get_info(i, driver)
                    wrappers += [Product(name=name, url=url, images=[])]
                    LOGGER.info(f"#{i}: {name} - {url}")
                    i += 1
                except Exception:
                    LOGGER.info("we've reached the end of it")
                    traceback.print_exc()
                    break

            LOGGER.info(f"length of wrappers: {len(wrappers)}")
            LOGGER.info("Done!")
            time.sleep(5)
        except Exception:
            traceback.print_exc()
            LOGGER.info("whAT")
        return wrappers

    def _get_info(self, index: int, driver: WebDriver) -> Tuple[str, str]:
        xpath = f"//div[@id='ProductListPagesWrapper']//div[{index}]//a[1]"
        element = driver.find_element(
            By.XPATH,
            xpath,
        )
        url = element.get_attribute("href")
        if not url:
            url = ""
        LOGGER.info(f"url: {url}")
        inner_child = element.find_element(By.XPATH, "//h3[1]")
        name = inner_child.text
        return url, name

    def _step_scroll(self, driver: WebDriver):
        self.current_scroll += self.scroll_step
        driver.execute_script(f"window.scrollTo(0, {self.current_scroll});")
