import logging
from typing import Optional
from PIL import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from .base_filter import BaseFilter

LOGGER = logging.getLogger(__name__)


class BoxFilter(BaseFilter):
    def filter(self, obj: Image.Image) -> Optional[Image.Image]:
        np_img = np.array(obj)
        image = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)

        # Load and preprocess the image
        # image = cv2.imread(
        #     "digik/پا رکابی خودرو پژو مدل P67 بسته 4 عددی-16327437-#03.jpg"
        # )
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # Reduce blur for finer edges
        edges = cv2.Canny(blurred, 50, 150)

        # Detect line segments using HoughLinesP (probabilistic Hough transform)
        lines = cv2.HoughLinesP(
            edges, 1, np.pi / 180, threshold=80, minLineLength=20, maxLineGap=50
        )

        horizontal_segments = []
        vertical_segments = []

        if lines is not None:
            for x1, y1, x2, y2 in lines[:, 0]:
                dx = x2 - x1
                dy = y2 - y1
                angle = np.arctan2(dy, dx) * 180 / np.pi  # Calculate angle in degrees

                # Ensure angles are between 0° and 180°
                if angle < 0:
                    angle += 180

                # Detect horizontal segments (within 10 degrees tolerance)
                if (
                    abs(angle) < 5 or abs(angle) > 175
                ):  # Horizontal segments (including perfect horizontal)
                    horizontal_segments.append((x1, y1, x2, y2))
                # Detect vertical segments (within 10 degrees tolerance)
                elif (
                    85 < abs(angle) < 95
                ):  # Vertical segments (including perfect vertical)
                    vertical_segments.append((x1, y1, x2, y2))

        # Merge close segments (if they are close enough in the same direction)
        def merge_segments(segments, threshold=10):
            merged_segments = []
            for segment in segments:
                x1, y1, x2, y2 = segment
                merged = False
                for i, merged_segment in enumerate(merged_segments):
                    mx1, my1, mx2, my2 = merged_segment
                    # Check if the segment is close to an existing segment (same direction)
                    if (
                        abs(x1 - mx1) < threshold
                        and abs(y1 - my1) < threshold
                        and abs(x2 - mx2) < threshold
                        and abs(y2 - my2) < threshold
                    ):
                        # Merge the segments by averaging the coordinates
                        merged_segments[i] = (
                            (mx1 + x1) // 2,
                            (my1 + y1) // 2,
                            (mx2 + x2) // 2,
                            (my2 + y2) // 2,
                        )
                        merged = True
                        break
                if not merged:
                    merged_segments.append(segment)
            return merged_segments

        # Merge horizontal and vertical segments
        merged_horizontal = merge_segments(horizontal_segments)
        merged_vertical = merge_segments(vertical_segments)

        # Extend segments by 10%
        def extend_segment(x1, y1, x2, y2, extension_factor=0.1):
            # Calculate the segment length
            dx, dy = x2 - x1, y2 - y1
            length = np.sqrt(dx**2 + dy**2)

            # Extend the segment by the given factor
            dx_extended = dx * extension_factor
            dy_extended = dy * extension_factor

            # Extend both ends of the segment
            x1_extended = int(x1 - dx_extended)
            y1_extended = int(y1 - dy_extended)
            x2_extended = int(x2 + dx_extended)
            y2_extended = int(y2 + dy_extended)

            return x1_extended, y1_extended, x2_extended, y2_extended

        # Extend horizontal and vertical segments
        extended_horizontal = [
            extend_segment(x1, y1, x2, y2) for x1, y1, x2, y2 in merged_horizontal
        ]
        extended_vertical = [
            extend_segment(x1, y1, x2, y2) for x1, y1, x2, y2 in merged_vertical
        ]

        # Step 4: Find all possible intersections of extended horizontal and vertical segments
        def find_intersections(horizontal_segments, vertical_segments):
            intersections = []

            # Loop through each pair of horizontal and vertical lines
            for hx1, hy1, hx2, hy2 in horizontal_segments:
                for vx1, vy1, vx2, vy2 in vertical_segments:
                    # Check if the horizontal line intersects with the vertical line
                    if min(hx1, hx2) <= vx1 <= max(hx1, hx2) and min(
                        vy1, vy2
                    ) <= hy1 <= max(vy1, vy2):
                        # Intersection occurs when the point is inside both line segments
                        intersection_x = vx1
                        intersection_y = hy1
                        intersections.append((intersection_x, intersection_y))

            return intersections

        # Find intersections of extended lines
        intersections = find_intersections(extended_horizontal, extended_vertical)

        # Step 5: Refined rectangle detection logic based on Manhattan distance
        def find_rectangle(intersections, threshold=10):
            rectangles = []

            # Loop over each pair of intersection points
            for i in range(len(intersections)):
                for j in range(i + 1, len(intersections)):
                    x1, y1 = intersections[i]
                    x2, y2 = intersections[j]
                    point1 = False
                    point2 = False
                    for k in range(len(intersections)):
                        # Check if (x1, y2) exists in the intersections
                        if (
                            abs(intersections[k][0] - x1)
                            + abs(intersections[k][1] - y2)
                            < threshold
                        ):
                            point1 = True
                        if (
                            abs(intersections[k][0] - x2)
                            + abs(intersections[k][1] - y1)
                            < threshold
                        ):
                            point2 = True
                    if point1 and point2:
                        rectangles.append([x1, y1, x2, y2])
            return rectangles

        # Find rectangles from intersections
        rectangles = find_rectangle(intersections)

        # Step 6: Find the largest rectangle by area
        def find_largest_rectangle(rectangles):
            largest_area = 0
            largest_rectangle = None
            for rectangle in rectangles:
                # Calculate area: width * height
                width = abs(rectangle[0] - rectangle[2])
                height = abs(rectangle[1] - rectangle[3])
                area = width * height
                if area > largest_area:
                    largest_area = area
                    largest_rectangle = rectangle
            return largest_rectangle

        largest_rectangle = find_largest_rectangle(rectangles)

        # Step 7: Visualization
        plt.figure(figsize=(18, 6))

        # Plot 1: Detected Segments
        ax1 = plt.subplot(1, 3, 1)
        ax1.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        ax1.set_title("Detected Segments")

        # Plot horizontal and vertical segments
        for segment in merged_horizontal:
            ax1.plot(
                [segment[0], segment[2]],
                [segment[1], segment[3]],
                color="b",
                linewidth=2,
            )

        for segment in merged_vertical:
            ax1.plot(
                [segment[0], segment[2]],
                [segment[1], segment[3]],
                color="g",
                linewidth=2,
            )

        # Plot 2: Detected Intersections
        ax2 = plt.subplot(1, 3, 2)
        ax2.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        ax2.set_title("Detected Intersections")

        # Plot intersections as green dots
        for intersection in intersections:
            ax2.plot(intersection[0], intersection[1], "go", markersize=5)

        # Plot 3: Detected Rectangles
        ax3 = plt.subplot(1, 3, 3)
        ax3.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        ax3.set_title("Detected Rectangles")

        # Plot the largest rectangle if available
        if largest_rectangle:
            x1, y1, x2, y2 = largest_rectangle
            ax3.add_patch(
                Rectangle(
                    (x1, y1),
                    x2 - x1,
                    y2 - y1,
                    linewidth=3,
                    edgecolor="b",
                    facecolor="none",
                )
            )

        plt.tight_layout()
        plt.show()
        # t = input(" [.] ")
        LOGGER.info("next")
        # Convert BGR (OpenCV) to RGB (Pillow)
        # rgb_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)

        # Create a Pillow image
        LOGGER.info(image.shape)
        LOGGER.info(largest_rectangle)
        if largest_rectangle:
            largest_rectangle = (
                min(largest_rectangle[0], largest_rectangle[2]),
                min(largest_rectangle[1], largest_rectangle[3]),
                max(largest_rectangle[0], largest_rectangle[2]),
                max(largest_rectangle[1], largest_rectangle[3]),
            )
            return obj.crop(largest_rectangle)
        return None
        pillow_image = Image.fromarray(rgb_image)
