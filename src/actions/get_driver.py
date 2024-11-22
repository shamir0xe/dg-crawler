from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from src.actions.get_agent import GetAgent


@dataclass
class GetDriver:
    user_agent: str

    def get(self) -> WebDriver:
        user_agent = GetAgent.get()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("user-agent={}".format(user_agent))
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--window-size=1920x1080")
        return webdriver.Chrome(
            service=Service(executable_path="/usr/local/bin/chromedriver"),
            options=chrome_options,
        )
