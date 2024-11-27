from concurrent.futures import ThreadPoolExecutor, wait
import os
import json
import logging
import time
from random import random
from typing import List

from pylib_0xe.file.file import File
from src.actions.get_driver import GetDriver
from src.helpers.config import Config
from src.orchestrators.crawl_manager import CrawlManager
from src.actions.cat_url_builder import CatUrlBuilder
from src.orchestrators.send_request import SendRequest
from src.models.category import Category

LOGGER = logging.getLogger(__name__)


class FindLeafCategories:
    @staticmethod
    def fn(cat_manager: CrawlManager, instance: int) -> List[Category]:
        result = []
        # time.sleep(5/ * random())
        if instance > 1:
            time.sleep(instance)
        LOGGER.info(f"Instanciate #{instance}")
        while cat_manager.have_any():
            cat = cat_manager.get_one()
            if not cat:
                time.sleep(0.5 * random())
                continue
            if cat_manager.eof():
                break
            url = CatUrlBuilder.build(cat)
            data = SendRequest.send(url, instance)
            if not data:
                continue
            if (
                "sub_categories_best_selling" not in data["data"]
                or not data["data"]["sub_categories_best_selling"]
            ):
                result += [
                    Category(
                        id=data["data"]["category"]["id"],
                        name=cat,
                        url=url,
                        page_cnt=data["data"]["pager"]["total_pages"],
                    )
                ]
                LOGGER.info(f"LEAF! {cat}")
            else:
                LOGGER.info(f"NOT LEAF! {cat}")
                sub_cats = data["data"]["sub_categories_best_selling"]
                for sub_cat in sub_cats:
                    cat_manager.add_one(sub_cat["code"])
            cat_manager.resolve(cat)
        LOGGER.info(f"Instance #{instance} Ended")
        return result

    @staticmethod
    def find(cat: str) -> List[Category]:
        categories = []
        cat_manager = CrawlManager[str]()
        cat_manager.add_one(cat)
        thread_count = Config.read_env("thread_cnt")
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
