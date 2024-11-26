from dataclasses import dataclass

from selenium.webdriver.chrome.webdriver import WebDriver


@dataclass
class ClearDriverCookies:
    driver: WebDriver

    def clear(self) -> None:
        self.driver.delete_all_cookies()
