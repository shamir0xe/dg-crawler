from dataclasses import dataclass, field
from typing import Dict, Optional
import threading
import logging

from src.datastructure.trees.avl_node import AvlNode
from src.datastructure.trees.avl_tree import AvlTree
from src.models.product import Product

lock = threading.Lock()

LOGGER = logging.getLogger(__name__ + "[PM]")


@dataclass
class ProductManager:
    tree: AvlTree[Product, int] = field(
        default=AvlTree[Product, int](
            lambda node: node.data.page * 100000000 + int(node.data.id)
        )
    )
    pendings: Dict[int, Product] = field(default_factory=dict)

    def add_one(self, p: Product) -> None:
        with lock:
            v = self.tree.find(AvlNode(p))
            if v:
                return
            self.tree.insert(AvlNode(p))

    def get_one(self) -> Optional[Product]:
        with lock:
            if self.have_any():
                node = self.tree.get_minimum()
                if not node:
                    return None
                product = node.data
                self.tree.remove(node)
                self.pendings[product.id] = product
                return product
            else:
                return None

    def have_any(self) -> bool:
        return self.tree.get_size() > 0

    def resolve(self, product: Product) -> None:
        LOGGER.info(f"Success #{product.id} // P#{product.page}")
        self.pendings.pop(product.id)

    def failure(self, product: Product) -> None:
        LOGGER.info(f"Failure {product.id}, Go back to Q")
        self.pendings.pop(product.id)
        self.tree.insert(AvlNode(product))

    def eof(self) -> bool:
        return self.tree.get_size() == 0 and len(self.pendings) == 0
