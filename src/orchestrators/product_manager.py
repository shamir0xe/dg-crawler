from dataclasses import dataclass, field
from typing import Deque, Dict, Optional
import threading
import logging

from src.models.product import Product

lock = threading.Lock()

LOGGER = logging.getLogger(__name__ + "[PM]")


@dataclass
class ProductManager:
    products: Deque[Product]
    pendings: Dict[str, Product] = field(default_factory=dict)

    def get_one(self) -> Optional[Product]:
        with lock:
            if self.have_any():
                product = self.products.popleft()
                self.pendings[product.id] = product
                return product
            else:
                return None

    def have_any(self) -> bool:
        return len(self.products) > 0

    def resolve(self, product: Product) -> None:
        LOGGER.info(f"Success #{product.id} // P#{product.page}")
        self.pendings.pop(product.id)

    def failure(self, product: Product) -> None:
        LOGGER.info(f"Failure {product.id}, Go back to Q")
        self.pendings.pop(product.id)
        self.products.appendleft(product)

    def eof(self) -> bool:
        return len(self.products) == 0 and len(self.pendings) == 0
