from concurrent.futures import ThreadPoolExecutor, wait
import os
import json
import logging
import time
from random import random
from typing import List

from pylib_0xe.file.file import File
from src.helpers.config import Config
from src.orchestrators.crawl_manager import CrawlManager
from src.actions.cat_url_builder import CatUrlBuilder
from src.orchestrators.send_request import SendRequest
from src.models.category import Category

LOGGER = logging.getLogger("[FLC]")


class FindLeafCategories:
    @staticmethod
    def find(cat: str) -> List[Category]:
        categories = []
        cat_manager = CrawlManager[str]()
        cat_manager.add_one(cat)
        # thread_count = Config.read_env("thread_cnt")
        thread_count = 8
        with ThreadPoolExecutor() as executor:
            futures = []
            for i in range(thread_count):
                futures += [
                    executor.submit(
                        FindLeafCategories.fn, cat_manager, (i % thread_count) + 1
                    )
                ]
            wait(futures)
            for future in futures:
                categories += future.result()
        # Save the output
        File.write_file(
            os.path.join(Config.read("main.urls_path"), "categories.json"),
            json.dumps({cat.id: cat.model_dump() for cat in categories}),
        )
        LOGGER.info("Done & Dusted ;)")
        return categories

    @staticmethod
    def fn(cat_manager: CrawlManager, instance: int) -> List[Category]:
        env = Config.read_env("env")
        result = []
        sleep_time = Config.read("main.cm.sleep")
        time.sleep(sleep_time * random())
        LOGGER.info(f"Instanciate #{instance}")
        cnt = 0
        while not cat_manager.eof():
            if env == "debug" and cnt > 3:
                break

            cat = cat_manager.get_one()
            LOGGER.info(f"{cat} is assigned to {instance}")
            if not cat:
                time.sleep(sleep_time * random())
                continue
            url = CatUrlBuilder.build(cat)
            data = SendRequest.send(url, instance)
            if not data or not "data" in data:
                cat_manager.retry(cat)
                time.sleep(sleep_time * random())
                continue
            try:
                if (
                    "sub_categories_best_selling" not in data["data"]
                    or not data["data"]["sub_categories_best_selling"]
                ):
                    cnt += 1
                    result += [
                        Category(
                            id=data["data"]["category"]["id"],
                            name=cat,
                            url=url,
                            page_cnt=data["data"]["pager"]["total_pages"],
                        )
                    ]
                    LOGGER.info(f"LEAF!")
                else:
                    LOGGER.info(f"NOT LEAF!")
                    sub_cats = data["data"]["sub_categories_best_selling"]
                    # LOGGER.info("")
                    for sub_cat in sub_cats:
                        # LOGGER.info(f"{cat}->{sub_cat['code']}")
                        cat_manager.add_one(sub_cat["code"])
            except Exception:
                pass
            cat_manager.resolve(cat)
        LOGGER.info(f"Instance #{instance} Ended")
        return result

    @staticmethod
    def is_char(char: str) -> bool:
        return ord("a") <= ord(char) <= ord("z")
