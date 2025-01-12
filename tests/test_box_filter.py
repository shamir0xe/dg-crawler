import logging
import os

from PIL import Image
from src.orchestrators.filter.box_filter import BoxFilter
from src.actions.save_product_images import SaveProductImages
from src.orchestrators.filter.filter_images import FilterImages
from src.models.product import Product
from pylib_0xe.file.file import File
import matplotlib.pyplot as plt
from unittest.mock import patch

LOGGER = logging.getLogger(__name__)


class _TestBoxFilter:
    def test_box_filter(self):
        images_dir = "./outputs"
        product = Product(
            name="test-product", url="/", page=1, images=[], id=1, category_id=123
        )

        cnt = 25
        for file in File.get_all_files(images_dir, ext="jpg"):
            cnt -= 1
            if not cnt:
                break

            image_path = os.path.join(images_dir, file)
            image = Image.open(image_path)
            temp = image.copy()
            product.images += [temp]
            image.close()
        for i, img in enumerate(product.images):
            tmp = BoxFilter().filter(img)
            if tmp:
                product.images[i] = tmp

        for i, image in enumerate(product.images):
            image.save(f"output-test/{i}.jpg")
        assert 1 == 1
