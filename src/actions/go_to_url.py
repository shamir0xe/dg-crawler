from dataclasses import dataclass
import logging

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LOGGER = logging.getLogger(__name__)


@dataclass
class GoToUrl:
    driver: WebDriver
    timeout: float

    def go(self, url: str, xpath: str) -> None:
        if url:
            self.driver.get(url)
        if xpath:
            WebDriverWait(driver=self.driver, timeout=self.timeout).until(
                EC.presence_of_all_elements_located(
                    (
                        By.XPATH,
                        xpath,
                    )
                )
            )
