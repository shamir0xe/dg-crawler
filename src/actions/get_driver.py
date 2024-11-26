from typing import Dict

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from src.helpers.decorators.singleton import singleton
from src.helpers.config import Config
from src.actions.get_agent import GetAgent


@singleton
class GetDriver:

    def __init__(self) -> None:
        self.drivers: Dict[int, WebDriver] = {}

    def revoke(self, i: int) -> WebDriver:
        self.drivers[i] = self.build_one(i)
        return self.drivers[i]

    def build_one(self, i: int) -> WebDriver:
        user_agent = GetAgent.get()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("user-agent={}".format(user_agent))
        if Config.read_env("headless"):
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--window-size=1920x1080")
        exec_path = Config.read_env("executable_path").format(i)
        driver = webdriver.Chrome(
            service=Service(executable_path=exec_path),
            options=chrome_options,
        )
        driver.set_page_load_timeout(Config.read_env("times.page_timeout"))
        return driver

    def get(self, i: int) -> WebDriver:
        if i in self.drivers:
            return self.drivers[i]
        return self.revoke(i)
