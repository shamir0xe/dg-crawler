import logging
import os
from PIL import Image
from pylib_0xe.file.file import File
from src.orchestrators.process_image import ProcessImage
from src.helpers.config import Config

LOGGER = logging.getLogger(__name__)


class TestImageGen:
    def test_image_gen(self):
        img_gen_cfg = Config.read_env("image_gen")
        images_dir = "/home/shamir0xe/Documents/Projects/Crawlers/digikala-bounty-hunter/outputs5"
        for file in File.get_all_files(images_dir, ext="jpg"):
            image_path = os.path.join(images_dir, file)
            image = Image.open(image_path)
            gen_img = ProcessImage(image, img_gen_cfg).process()
            if gen_img:
                LOGGER.info(f"We Got The Image: {file}")
                gen_img.save(f"outputs/{file}.jpg")
            image.close()
