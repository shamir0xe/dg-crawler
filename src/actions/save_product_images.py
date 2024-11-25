from dataclasses import dataclass

from src.models.product import Product
from src.orchestrators.check_image_possibilities import CheckImagePossibilities
from src.orchestrators.save_image import SaveImage


@dataclass
class SaveProductImages:
    product: Product

    def save(self) -> None:
        count = 0
        for img in self.product.images:
            possible = CheckImagePossibilities(image=img).check()
            if possible:
                SaveImage(image=img).save(
                    name=f"{self.product.name}-{self.product.id}-#{count+1:02d}"
                )
                count += 1
