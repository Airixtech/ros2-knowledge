---
id: perception-pointcloud2-msg
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "sensor_msgs/PointCloud2 fields and the binary layout of one point (offsets, datatype, point_step)"
domain: perception
area: sensors
distro: humble
tested: false
audience: dev
summary: "PointCloud2 height, width, fields (name, offset, datatype, count), point_step, row_step, binary data, is_dense; read x, y, z with sensor_msgs_py."
tags: [sensor_msgs/PointCloud2, PointCloud2, PointField, FLOAT32, point_step, row_step, is_dense, is_bigendian, depth camera, 3D lidar, sensor_msgs_py, read_points_numpy]
see: ["[[perception-pointcloud-markers]]", "[[perception-cloud-to-base-link]]", "[[perception-rviz-sensors]]", "[[core-perception-basics]]"]
requires: [ros2-core]
version_notes:
  - "humble: field comments, `is_dense` = 'True if there are no invalid points', PointField datatypes 1-8 — https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs/msg/PointCloud2.msg , https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs/msg/PointField.msg (PERC-V01, PERC-V08)"
  - "humble: sensor_msgs_py.point_cloud2.read_points / read_points_numpy(cloud, field_names, skip_nans) read any layout and byte order; same API on jazzy — https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs_py/sensor_msgs_py/point_cloud2.py (PERC-V08)"
---
# sensor_msgs/PointCloud2 and the layout of one point

**TL;DR** A `PointCloud2` is a binary blob of `width * height` points, each `point_step` bytes long; `fields` say at which byte offset each attribute starts and its type (7 = FLOAT32). Read it with `sensor_msgs_py.point_cloud2` instead of slicing bytes by hand.

## The message
`sensor_msgs/PointCloud2` is the robot's 3D scanner: points in 3D space from 3D lidars or depth cameras, each with x, y, z and maybe intensity, color or other values. It is used for 3D maps, object recognition, exploration and navigation in complex spaces (from autonomous drones to warehouse robots). Main fields ([PointCloud2.msg](https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs/msg/PointCloud2.msg)):
- `height`, `width`: the 2D structure, like an image; total points = `height * width` (an unordered cloud has `height` 1).
- `fields`: the attributes of each point (`name`, `offset` in bytes from the start of the point, `datatype`, `count`).
- `point_step`: size of one point in bytes; `row_step`: length of a row in bytes.
- `data`: the raw points in **binary** form, a one-dimensional byte array of size `row_step * height`.
- `is_bigendian`: byte order of the values; `is_dense`: true if there are no invalid points.

`datatype` values ([PointField.msg](https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs/msg/PointField.msg)): INT8 = 1, UINT8 = 2, INT16 = 3, UINT16 = 4, INT32 = 5, UINT32 = 6, FLOAT32 = 7, FLOAT64 = 8.

## Example: the course depth camera
```bash
ros2 topic echo /deepmind_robot1_depth_sensor/points
```
```text
- 0
- 0
- '...'
is_dense: true
---
header:
  stamp:
    sec: 414
    nanosec: 253000000
  frame_id: deepmind_robot1_camera_depth_optical_frame
height: 1
width: 307200
fields:
- name: x
  offset: 0
  datatype: 7
  count: 1
- name: y
  offset: 4
  datatype: 7
  count: 1
- name: z
  offset: 8
  datatype: 7
  count: 1
- name: rgb
  offset: 16
  datatype: 7
  count: 1
is_bigendian: false
point_step: 32
row_step: 9830400
data:
- 20
- 159
- 146
- 191
```
`data` is printed as 1-byte integers; each group of bytes is a value of the field's `datatype`. Here every field is `datatype` 7 (**float32**, 4 bytes) and `point_step` = 32, so one point is:
- bytes 0–3: **x** (float32) · bytes 4–7: **y** · bytes 8–11: **z** · bytes 16–19: **rgb** (packed color as a float32)
- bytes 12–15 and 20–31 are unused. The layout repeats for every point (`row_step` 9,830,400 = 307,200 points × 32 bytes).

The `offset` tells where a field starts inside the point; the `datatype` tells how to read its bytes.

## Read the points (official helper)
```python
from sensor_msgs_py import point_cloud2

xyz = point_cloud2.read_points_numpy(msg, field_names=('x', 'y', 'z'), skip_nans=True)  # (N, 3) array
```
`read_points` returns a structured array with every field; `read_points_numpy` an unstructured one (all requested fields must share one datatype). Both follow `point_step`, the offsets and `is_bigendian`, and `skip_nans` drops invalid points of a non-dense cloud. Add `<exec_depend>sensor_msgs_py</exec_depend>` to `package.xml`.

## Pitfalls
- Reading `x` at byte 0 of every `point_step` assumes this layout: take the offsets from `msg.fields` (other sensors put intensity or ring fields in between).
- A depth camera's cloud can hold NaN points when `is_dense` is false: skip them before computing minimums or centroids.
- The cloud is in the sensor's optical frame (z forward): transform it before reasoning in `base_link` ([[perception-cloud-to-base-link]], [[core-perception-basics]]).
