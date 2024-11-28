from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Generic, Optional, Set, TypeVar
import threading
import logging

lock = threading.Lock()

LOGGER = logging.getLogger("[CM]")

T = TypeVar("T")
MAX_RETRY = 10


@dataclass
class CrawlManager(Generic[T]):
    """
    T should have __repr__
    T should have __hash__
    T should have __eq__
    """

    whole: Deque[T] = field(default_factory=deque)
    pendings: Dict[str, T] = field(default_factory=dict)
    history: Dict[str, int] = field(default_factory=dict)

    def get_one(self) -> Optional[T]:
        with lock:
            if self.have_any():
                next = self.whole.popleft()
                self.pendings[str(next)] = next
                return next
            else:
                return None

    def add_one(self, obj: T) -> None:
        with lock:
            if str(obj) in self.history:
                return
            self.history[str(obj)] = 1
            self.whole.append(obj)

    def have_any(self) -> bool:
        return len(self.whole) > 0

    def resolve(self, obj: T) -> None:
        LOGGER.info(f"Success {str(obj)}")
        self.pendings.pop(str(obj))

    def failure(self, obj: T) -> None:
        LOGGER.info(f"Failure {str(obj)}, Go back to Q")
        self.pendings.pop(str(obj))
        self.whole.append(obj)

    def retry(self, obj: T) -> None:
        with lock:
            if str(obj) not in self.history:
                return
            self.history[str(obj)] += 1
            if self.history[str(obj)] > MAX_RETRY:
                LOGGER.info(f"Max retry occures for {obj}")
                self.pendings.pop(str(obj))
            else:
                self.failure(obj)

    def eof(self) -> bool:
        # LOGGER.info(f"{len(self.whole)}  {len(self.pendings)}")
        # if len(self.pendings) == 1:
        #     LOGGER.info(self.pendings.keys())
        with lock:
            return len(self.whole) == 0 and len(self.pendings) == 0
