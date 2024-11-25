from dataclasses import dataclass
from functools import lru_cache

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from src.helpers.config import Config
from src.actions.get_agent import GetAgent


@dataclass
class GetDriver:

    @lru_cache
    @staticmethod
    def get(i: int) -> WebDriver:
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
