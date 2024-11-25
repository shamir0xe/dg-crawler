from __future__ import annotations
import requests
import time
from src.actions.get_agent import GetAgent
from src.helpers.config import Config
from random import random


class SendRequest:
    @staticmethod
    def send(url: str) -> str:
        retry_count = Config.read_env("retry_count")
        retry_bak = retry_count
        base_time = Config.read_env("times.base")
        while retry_count > 0:
            try:
                return SendRequest.trying(url)
            except Exception:
                pass
            retry_count -= 1
            time.sleep(base_time * (retry_bak - retry_count) + base_time * random())

        return ""

    @staticmethod
    def trying(url: str) -> str:
        headers = {"User-Agent": GetAgent.get()}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
