from __future__ import annotations
from dataclasses import dataclass
import subprocess
import httpx
import logging
import json
from typing import Dict, Optional
import requests
import time

from selenium.webdriver.common.by import By
from src.actions.get_driver import GetDriver
from src.actions.go_to_url import GoToUrl
from src.actions.get_agent import GetAgent
from src.helpers.config import Config
from random import random

logging.getLogger("httpx").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)


@dataclass
class SendRequest:
    instance: int

    @staticmethod
    def send(url: str, instance: int = 2) -> Optional[Dict]:
        retry_count = Config.read_env("retry_count")
        retry_bak = retry_count
        base_time = Config.read_env("times.base")
        send_req = SendRequest(instance)
        while retry_count > 0:
            try:
                return send_req.trying(url)
            except Exception:
                pass
            retry_count -= 1
            time.sleep(base_time * (retry_bak - retry_count) + base_time * random())

        return None

    def trying(self, url: str) -> Dict:
        driver = GetDriver().get(self.instance)
        GoToUrl(driver, 10).go(url, "//body//pre")
        element = driver.find_element(By.XPATH, "//body//pre")
        str_data = element.get_attribute("innerHTML")
        if not str_data:
            raise Exception()
        data = json.loads(str_data)
        if not data:
            raise Exception()
        return data
