from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Generic, Optional, Set, TypeVar
import threading
import logging

lock = threading.Lock()

LOGGER = logging.getLogger("[CM]")

T = TypeVar("T")


@dataclass
class CrawlManager(Generic[T]):
    """
    T should have __repr__
    T should have __hash__
    T should have __eq__
    """

    whole: Deque[T] = field(default_factory=deque)
    pendings: Dict[str, T] = field(default_factory=dict)
    history: Set[str] = field(default_factory=set)

    def get_one(self) -> Optional[T]:
        with lock:
            if self.have_any():
                next = self.whole.popleft()
                self.pendings[str(next)] = next
                return next
            else:
                return None

    def add_one(self, obj: T) -> None:
        if str(obj) in self.history:
            return
        self.history.add(str(obj))
        self.whole.append(obj)

    def have_any(self) -> bool:
        return len(self.whole) > 0

    def resolve(self, obj: T) -> None:
        LOGGER.info(f"Success {str(obj)}")
        self.pendings.pop(str(obj))

    def failure(self, obj: T) -> None:
        LOGGER.info(f"Failure {str(obj)}, Go back to Q")
        with lock:
            self.pendings.pop(str(obj))
            self.whole.append(obj)

    def eof(self) -> bool:
        return len(self.whole) == 0 and len(self.pendings) == 0
