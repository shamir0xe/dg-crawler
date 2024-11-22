from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseCrawler(ABC, Generic[T]):
    @abstractmethod
    def crawl(self) -> T:
        pass
