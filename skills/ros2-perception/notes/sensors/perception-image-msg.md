---
id: perception-image-msg
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "sensor_msgs/Image fields, the byte layout of data and a center-pixel color detector"
domain: perception
area: sensors
distro: humble
tested: false
audience: dev
summary: "Image height, width, encoding (bgr8, rgb8, mono8), step and data bytes; index a pixel by hand; RGB color thresholds."
tags: [sensor_msgs/Image, Image, encoding, bgr8, rgb8, mono8, step, data, pixel index, image_raw, color_detector.py, detect_color]
see: ["[[perception-opencv-cv-bridge]]", "[[perception-hsv-color-ranges]]", "[[perception-rviz-sensors]]", "[[core-recipe-cv-bridge]]"]
requires: [ros2-core]
version_notes:
  - "humble: `step` is the 'Full row length in bytes' and `data` holds step * rows bytes — https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs/msg/Image.msg (PERC-V01, PERC-V06)"
  - "course: the center index was always a multiple of 3, so only the first of three branches ran and blue was read from the previous pixel (center_index - 1); fixed to R, G, B = i, i+1, i+2 with the row stride `msg.step` (PERC-V06)"
  - "course: `heigth` and `b0gr8` were typos of height and bgr8 (PERC-V05)"
---
# sensor_msgs/Image and a center-pixel color detector

**TL;DR** An `Image` is a grid of pixels flattened into one byte array `data`, row after row; `step` is the length of one row in bytes, `encoding` says what each byte is. Pixel `(u, v)` of an 8-bit 3-channel image starts at `v * step + u * 3`. Most nodes let cv_bridge do this ([[perception-opencv-cv-bridge]]).

## The message
`sensor_msgs/Image` is the camera's snapshot of the world: robots use it to "see" and recognize objects, faces and patterns (computer vision). Main fields ([Image.msg](https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs/msg/Image.msg)):
- `height` = number of rows, `width` = number of columns.
- `encoding`: the format of the data. Common values: `bgr8` (3 bytes per pixel: blue, green, red), `rgb8` (same with the order red, green, blue), `mono8` (1 byte per pixel: gray intensity).
- `step`: bytes of one row (the row length in bytes).
- `data`: the raw image as an **array of bytes**, not of pixels; each byte is one component, in the order the encoding gives.
- The origin (0, 0) is the **top-left corner**, as in computer graphics and in most image software.

Example: a 2 × 2 `bgr8` image. B1, G1, R1 are the components of pixel (0,0), B2, G2, R2 of pixel (1,0), and so on. Each pixel has 3 bytes and each row 2 pixels, so `step = width * byte_depth = 2 * 3 = 6`:
- `height` = 2, `width` = 2, `encoding` = bgr8, `step` = 6
- `data` = [B1, G1, R1, B2, G2, R2, B3, G3, R3, B4, G4, R4]

Each component ranges from 0 (no intensity) to 255 (maximum). The course camera (`/deepmind_robot1/deepmind_robot1_camera/image_raw`, found with `ros2 topic echo /deepmind_robot1/deepmind_robot1_camera/image_raw`) gives `height` = 480, `width` = 640, `encoding` = rgb8.

## Example: color of the center pixel (`color_detector.py`)
Subscribe to the camera, read the three components of the center pixel, and print which of four colors (orange, yellow, green, blue) it shows. Each color is a **range** because lighting changes the values.
```bash
cd ~/ros2_ws/
touch src/basics_sensor_data/basics_sensor_data/color_detector.py
chmod +x src/basics_sensor_data/basics_sensor_data/color_detector.py
```
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image


class ColorDetector(Node):

    def __init__(self) -> None:
        super().__init__('color_detector')
        self.subscription = self.create_subscription(Image, '/deepmind_robot1/deepmind_robot1_camera/image_raw', self.image_callback, 10)

    def image_callback(self, msg: Image) -> None:
        """
        Callback function to process image data
        """
        # Retrieve image properties
        height = msg.height
        width = msg.width
        data = msg.data
        byte_depth = 3  # Each pixel consists of 3 bytes (RGB)

        # Calculate center pixel index (rows are msg.step bytes long, PERC-V06)
        center_index = (height // 2) * msg.step + (width // 2) * byte_depth

        # Calculate color component indices based on center pixel (rgb8: R, G, B, PERC-V06)
        red_component_index = center_index
        green_component_index = center_index + 1
        blue_component_index = center_index + 2

        # Print RGB values of center pixel
        print(f'\nRGB({data[red_component_index]}, {data[green_component_index]}, {data[blue_component_index]}) ')

        # Detect colors based on RGB values
        self.detect_color(data[red_component_index], data[green_component_index], data[blue_component_index])

    def detect_color(self, red: int, green: int, blue: int) -> None:
        """
        Detects color based on RGB values
        """
        if (240 <= red <= 255) and (55 <= green <= 80) and (0 <= blue <= 10):
            print(f'ORANGE COLOR DETECTED ....')
        if (220 <= red <= 255) and (190 <= green <= 255) and (0 <= blue <= 10):
            print(f'YELLOW COLOR DETECTED ....')
        if (0 <= red <= 10) and (230 <= green <= 255) and (0 <= blue <= 10):
            print(f'GREEN COLOR DETECTED ....')
        if (10 <= red <= 40) and (90 <= green <= 125) and (130 <= blue <= 185):
            print(f'BLUE COLOR DETECTED ....')


def main(args=None) -> None:
    rclpy.init(args=args)
    color_detector = ColorDetector()
    rclpy.spin(color_detector)
    color_detector.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
Byte depth is 3 because the encoding is `rgb8`. The course computed `center_index = ((height // 2) * width + (width // 2)) * byte_depth` and then three branches on `center_index % byte_depth` (`== 0`: red = i, green = i + 1, blue = i − 1; `== 1` and `== 2`: the other two orders). That index is always a multiple of 3, so only the first branch ran, and its "blue" was the last byte of the previous pixel: correct on uniform areas only (PERC-V06). `detect_color()` gets the three values of the center pixel and checks them against the ranges, so the robot can react to the colors its camera sees.

Run, then drive around the museum with teleop and tilt the head toward the floor (course tools: [[perception-learn-start-here]]):
```bash
cd ~/ros2_ws/
colcon build;source install/setup.bash
ros2 run basics_sensor_data color_detector
```

## Pitfalls
- Hand indexing with `width * 3` breaks when a driver pads rows: always use `msg.step` (PERC-V06).
- Assuming `rgb8`: check `msg.encoding`; a `bgr8` camera swaps red and blue. With cv_bridge, ask for the encoding you want ([[perception-opencv-cv-bridge]]).
- RGB thresholds depend on lighting; HSV ranges are more robust ([[perception-hsv-color-ranges]]).
