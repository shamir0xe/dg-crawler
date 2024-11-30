from typing import Dict
from src.helpers.config import Config
from src.helpers.decorators.singleton import singleton
from src.models.category import Category


@singleton
class Cats:
    def __init__(self) -> None:
        self.categories = []

    def add(self, cat: Category) -> None:
        self.categories += [cat]

    def load(self, data: Dict) -> None:
        if "data" not in data:
            raise Exception("Bad Category Data Provided")
        page_size = Config.read("main.page_size")
        cats_data = data["data"]
        for cat_data in cats_data:
            try:
                self.add(
                    Category(
                        id=int(cat_data["id"]),
                        name=cat_data["code"],
                        fa_name=cat_data["title_fa"],
                        page_cnt=(cat_data["products_count"] - 1) // page_size,
                        url=f"https://sirius.digikala.com/v1/category/{int(cat_data["id"])}/",
                    )
                )
            except Exception:
                pass
