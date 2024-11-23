from typing import List
import logging
from src.models.product import Product

LOGGER = logging.getLogger(__name__)


class ChunkProducts:
    @staticmethod
    def chunk(products: List[Product], chunk_count: int) -> List[List[Product]]:
        batch_size = (len(products) + 1) // chunk_count
        product_chunks = []
        cur_chunk = []
        index = 0
        for i, product in enumerate(products):
            cur_chunk += [product]
            if i // batch_size != index:
                product_chunks.append(cur_chunk)
                cur_chunk = []
                index = i // batch_size
                LOGGER.info(f"#{i} chunk#{index}")
        if cur_chunk:
            product_chunks.append(cur_chunk)

        assert len(product_chunks) == chunk_count

        LOGGER.info("chunks:")
        LOGGER.info(product_chunks)
        return product_chunks
