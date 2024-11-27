import logging
from collections import deque
from typing import List
from src.actions.cat_url_builder import CatUrlBuilder
from src.orchestrators.send_request import SendRequest
from src.models.category import Category

LOGGER = logging.getLogger(__name__)


class FindLeafCategories:
    @staticmethod
    def find(cat: str) -> List[Category]:
        result = []
        q = deque([])
        q.append(cat)
        while True:
            try:
                cat = q.popleft()
            except Exception:
                break
            url = CatUrlBuilder.build(cat)
            data = SendRequest.send(url)
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
                    q.append(sub_cat["code"])
        return result
