import logging
import os

from PIL import Image
from src.actions.save_product_images import SaveProductImages
from src.orchestrators.filter_images import FilterImages
from src.models.product import Product
from pylib_0xe.file.file import File

LOGGER = logging.getLogger(__name__)


class TestFilter:
    def test_filter(self):
        images_dir = "/home/shamir0xe/Downloads/Telegram Desktop/#_(/#:("
        product = Product(name="test-product", url="/", page=1, images=[], id="14")
        for file in File.get_all_files(images_dir, ext="jpg"):
            image_path = os.path.join(images_dir, file)
            image = Image.open(image_path)
            cp_image = image.copy()
            image.close()
            product.images += [cp_image]
        product.images = FilterImages().filter(product)
        SaveProductImages(product).save()
        assert 1 == 1
