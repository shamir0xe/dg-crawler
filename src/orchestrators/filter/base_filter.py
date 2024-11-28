from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")
K = TypeVar("K")


class BaseFilter(ABC, Generic[T, K]):
    @abstractmethod
    def filter(self, obj: T) -> K:
        pass
