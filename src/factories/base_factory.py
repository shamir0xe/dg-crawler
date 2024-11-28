from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseFactory(ABC, Generic[T]):
    @abstractmethod
    def create(self) -> T:
        pass
