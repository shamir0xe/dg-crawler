from dataclasses import dataclass
import time
import logging
import numpy as np
from typing import Any, Dict, Optional, Tuple

from PIL import Image

LOGGER = logging.getLogger("[IP]")


@dataclass
class ProcessImage:
    image: Image.Image
    cfg: Dict[str, Any]

    def process(self) -> Optional[Image.Image]:
        width = 444
        min_width = 200
        min_height = 100
        img = self.image.resize(
            (
                width,
                int(1.0 * self.image.height / self.image.width * width),
            ),
            resample=Image.Resampling.LANCZOS,
        )
        begin = time.time()
        rgb_color = self._to_rgb(self.cfg["box_color"])

        min_x, max_x = 333333, -1
        data = np.asarray(img)
        fq_x: Dict[int, int] = {}
        fq_y: Dict[int, int] = {}
        if data.shape[2] != 3:
            return None

        for i in range(data.shape[0]):
            min_y, max_y = 333333, -1
            for j in range(data.shape[1]):
                if self._kinda_close(data[i, j], rgb_color):
                    min_y = min(min_y, j)
                    max_y = max(max_y, j)
            if max_y < 0:
                continue
            delta = max_y - min_y
            if delta not in fq_x:
                fq_x[delta] = 1
            else:
                fq_x[delta] += 1
        for j in range(data.shape[1]):
            min_x, max_x = 333333, -1
            for i in range(data.shape[0]):
                if self._kinda_close(data[i, j], rgb_color):
                    min_x = min(min_x, i)
                    max_x = max(max_x, i)
            if max_x < 0:
                continue
            delta = max_x - min_x
            if delta not in fq_y:
                fq_y[delta] = 1
            else:
                fq_y[delta] += 1

        LOGGER.info(fq_x.values())
        LOGGER.info("")
        LOGGER.info("")
        LOGGER.info("")
        LOGGER.info(fq_y.values())
        if not fq_x or not fq_y:
            return None
        max_fq_x = max(fq_x.values())
        max_fq_y = max(fq_y.values())
        LOGGER.info(f"MAX FQ X: {max_fq_x}")
        LOGGER.info(f"MAX FQ Y: {max_fq_y}")
        if min(max_fq_x, max_fq_y) < self.cfg["min_fq_threshold"]:
            return None
        delta_x, delta_y = -1, -1
        for key, value in fq_x.items():
            if max_fq_x == value:
                delta_y = key
                break
        for key, value in fq_y.items():
            if max_fq_y == value:
                delta_x = key
                break

        LOGGER.info(f"DELTA X: {delta_x}")
        LOGGER.info(f"DELTA Y: {delta_y}")
        box_x = (333333, -1)
        for i in range(data.shape[0]):
            min_y, max_y = 333333, -1
            for j in range(data.shape[1]):
                if self._kinda_close(data[i, j], rgb_color):
                    min_y = min(min_y, j)
                    max_y = max(max_y, j)
            if max_y - min_y == delta_y:
                box_x = (min(i, box_x[0]), max(i, box_x[1]))
        box_y = (333333, -1)
        for j in range(data.shape[1]):
            min_x, max_x = 333333, -1
            for i in range(data.shape[0]):
                if self._kinda_close(data[i, j], rgb_color):
                    min_x = min(min_x, i)
                    max_x = max(max_x, i)
            if max_x - min_x == delta_x:
                box_y = (min(j, box_y[0]), max(j, box_y[1]))

        LOGGER.info(f"BOX X: {box_x}")
        LOGGER.info(f"BOX Y: {box_y}")

        if box_y[1] - box_y[0] < min_width:
            delta = min_width - (box_y[1] - box_y[0])
            box_y = (box_y[0] - delta, box_y[1] + delta)
        if box_x[1] - box_x[0] < min_height:
            delta = min_height - (box_x[1] - box_x[0])
            box_x = (box_x[0] - delta, box_x[1] + delta)

        LOGGER.info(f"elapsed time: {time.time() - begin}")
        try:
            gen_img = img.crop((box_y[0], box_x[0], box_y[1], box_x[1]))
        except Exception:
            import traceback

            traceback.print_exc()
            return None
        LOGGER.info(f"elapsed time: {time.time() - begin}")
        return gen_img

    def _kinda_close(
        self, color: Tuple[int, ...], target_color: Tuple[int, ...]
    ) -> bool:
        for i in range(3):
            if abs(color[i] - target_color[i]) > self.cfg["distance_threshold"]:
                return False
        return True

    def _to_rgb(self, hex: str) -> Tuple[int, ...]:
        hex = hex.lstrip("#")
        return tuple(int(hex[i : i + 2], 16) for i in (0, 2, 4))
