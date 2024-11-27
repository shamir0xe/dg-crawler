from dataclasses import dataclass, field
from typing import Dict, Generic, Optional, Set, TypeVar
import threading
import logging

lock = threading.Lock()

LOGGER = logging.getLogger(__name__ + " [CM]")

T = TypeVar("T")


@dataclass
class CrawlManager(Generic[T]):
    """
    T should have __repr__
    T should have __hash__
    T should have __eq__
    """

    whole: Set[T] = field(default_factory=set)
    pendings: Dict[str, T] = field(default_factory=dict)

    def get_one(self) -> Optional[T]:
        with lock:
            if self.have_any():
                next = self.whole.pop()
                self.pendings[str(next)] = next
                return next
            else:
                return None

    def add_one(self, obj: T) -> None:
        self.whole.add(obj)

    def have_any(self) -> bool:
        return len(self.whole) > 0

    def resolve(self, obj: T) -> None:
        LOGGER.info(f"Success {str(obj)}")
        self.pendings.pop(str(obj))

    def failure(self, obj: T) -> None:
        LOGGER.info(f"Failure {str(obj)}, Go back to Q")
        self.pendings.pop(str(obj))
        self.whole.add(obj)

    def eof(self) -> bool:
        return len(self.whole) == 0 and len(self.pendings) == 0
