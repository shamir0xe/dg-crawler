from typing import List, Optional
from src.facades.cats import Cats
from src.models.category import Category


class CategoryFinder:
    @staticmethod
    def by_name(name: str) -> Optional[Category]:
        name = name.lower()
        cats = Cats().categories
        for cat in cats:
            if cat.name == name:
                return cat
        for cat in cats:
            if cat.name in name:
                return cat
        return None

    @staticmethod
    def read_ids(ids: List[int]) -> List[Category]:
        check_set = set(ids)
        result = []
        for cat in Cats().categories:
            if cat.id in check_set:
                result += [cat]
        return result
