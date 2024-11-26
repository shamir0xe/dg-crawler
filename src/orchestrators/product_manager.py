from dataclasses import dataclass, field
from typing import Dict, Optional, Set
from ulid import ULID
import threading
import logging

from src.models.product import Product

lock = threading.Lock()

LOGGER = logging.getLogger(__name__)


@dataclass
class ProductManager:
    products: Set[Product]
    pendings: Dict[str, Product] = field(default_factory=dict)

    def get_one(self) -> Optional[Product]:
        with lock:
            if self.have_any():
                product = self.products.pop()
                if product.id is None:
                    product.id = ULID().generate()
                self.pendings[product.id] = product
                return product
            else:
                return None

    def have_any(self) -> bool:
        return len(self.products) > 0

    def resolve(self, product: Product) -> None:
        LOGGER.info(f"[PM] Success {product.id}")
        if product.id:
            self.pendings.pop(product.id)

    def failure(self, product: Product) -> None:
        LOGGER.info(f"[PM] Failure {product.id}, Go back to Q")
        if product.id:
            self.pendings.pop(product.id)
        self.products.add(product)
