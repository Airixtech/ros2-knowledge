---
id: perception-hsv-color-ranges
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Color spaces and HSV thresholds: why HSV, tuning ranges with a trackbar tool, the course's values"
domain: perception
area: image
distro: humble
tested: false
audience: dev
summary: "RGB vs HSV for segmentation, OpenCV's 8-bit hue scale 0-180, cv2.inRange bounds, range_detector trackbars, orange, yellow and green ranges."
tags: [HSV, RGB, color space, cv2.cvtColor, COLOR_BGR2HSV, cv2.inRange, hue, saturation, value, range_detector, trackbars, H_MIN, color thresholding]
see: ["[[perception-blob-detect]]", "[[perception-line-follower]]", "[[core-recipe-cv-bridge]]", "[[perception-learn-project]]"]
requires: [ros2-core]
version_notes:
  - "opencv 4.x: COLOR_BGR2HSV gives H in 0..180 for 8-bit images (H <- H/2), S and V in 0..255 — https://github.com/opencv/opencv/blob/4.x/modules/imgproc/include/opencv2/imgproc.hpp , https://github.com/opencv/opencv/blob/4.x/modules/imgproc/doc/colors.markdown (PERC-V10)"
---
# Color spaces and HSV thresholds

**TL;DR** Convert BGR to HSV and keep the pixels inside `[H_MIN, S_MIN, V_MIN]`–`[H_MAX, S_MAX, V_MAX]` with `cv2.inRange`. In OpenCV's 8-bit HSV the hue is **degrees / 2** (0–180), saturation and value are 0–255. Tune the bounds on the real camera with a trackbar tool.

## Color spaces
A color space is a mathematical model that writes colors as tuples of numbers (coordinates in a multidimensional space); each one suits different tasks, and the choice changes how well and how fast an image algorithm works. Important ones: RGB (red, green, blue), HSV (hue, saturation, value), HSL (hue, saturation, lightness), YUV/YCbCr (luma, chroma), LAB (CIELAB).
- **RGB**: the common space of digital imaging; each color mixes red, green and blue, each component 0–255 (or 0–1); it matches displays and cameras, which mix light of those three colors.
- **HSV**: separates the color type (**hue**, an angle on the color wheel: red, green, blue…), its intensity or purity (**saturation**: higher = more vivid) and its brightness (**value**). It is closer to how people describe colors. OpenCV stores the 8-bit hue halved: 0–180 instead of 0–360° (PERC-V10).

Why HSV for image processing:
- **Color segmentation**: finding objects or regions of a given color is easier, because ranges and thresholds are set on hue and saturation separately.
- **Color thresholding**: more intuitive than RGB; thresholds on hue and saturation isolate a color while lighting changes matter less.
- **Robustness to illumination**: brightness lives in V, decoupled from the color, so changes in light affect the color less.

## Thresholding in code
```python
hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
lower_orange = np.array([3, 0, 233])
upper_orange = np.array([9, 255, 255])
mask = cv2.inRange(hsv_image, lower_orange, upper_orange)   # 255 where the pixel is inside the range
```

## Tuning the ranges with trackbars
The course gives a tool that opens a `Trackbars` window with six sliders (`H_MIN`, `S_MIN`, `V_MIN`, `H_MAX`, `S_MAX`, `V_MAX`) and a preview of the mask; move them until only the target stays white:
```bash
ros2 run perception_ros2 range_detector --ros-args -p filter:=HSV -p preview:=True
```
(the project copies the same script into its own package: `ros2 run final_project range_detector --ros-args -p filter:=HSV -p preview:=True`, [[perception-learn-project]]). A C++ trackbar tuner is in the ros2-cpp skill (`cpp-recipe-cv-bridge`).

Ranges the course found in its simulation:
| Target | H_MIN | S_MIN | V_MIN | H_MAX | S_MAX | V_MAX | Used by |
|---|---|---|---|---|---|---|---|
| orange marker (exit door) | 3 | 0 | 233 | 9 | 255 | 255 | [[perception-blob-detect]], [[perception-door-follower]] |
| yellow line | 20 | 100 | 100 | 40 | 255 | 255 | [[perception-line-follower]] |
| green marker (door) | 34 | 255 | 0 | 82 | 255 | 255 | [[perception-door-follower]] |

The project's purple line: tune it against **blue and red**, its neighbors in HSV, and minimize overlaps so that only the line is detected; the same steps give the four area colors ([[perception-learn-project]]).

## Pitfalls
- Hue ranges copied from a 0–360 color picker do not work in OpenCV: halve them (PERC-V10).
- Red wraps around 0/180: one range covers only one side; combine two masks with `cv2.bitwise_or` for all reds.
- Ranges tuned in simulation rarely survive real lighting: retune on the robot's camera.
