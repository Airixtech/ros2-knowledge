---
id: core-iface-std-types
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Interface CLI & standard message packages"
domain: core
area: communication
distro: humble
tested: false
audience: dev
summary: "ros2 interface list/show/proto and the standard msg/srv/action packages with the fields of the most used types."
tags: [ros2 interface, std_msgs, geometry_msgs, sensor_msgs, nav_msgs, std_srvs, example_interfaces]
see: ["[[core-iface-syntax-usage]]", "[[core-iface-package]]", "[[core-topic-cli]]", "[[core-action-cli-status]]"]
requires: []
version_notes:
  - "lyrical: action_tutorials_interfaces removed in Kilted; demos use example_interfaces/action/Fibonacci (feedback field 'sequence') — https://github.com/ros2/demos/tree/kilted/action_tutorials (V29)"
---
# Interface CLI & standard message packages

**TL;DR** Prefer existing interfaces, and create a custom one only if nothing fits. Run `ros2 interface show <pkg>/<msg|srv|action>/<Type>` before writing code against a type.

## CLI
```bash
ros2 interface list            # -m msgs | -s srvs | -a actions
ros2 interface package std_msgs
ros2 interface show geometry_msgs/msg/Twist
ros2 interface show std_srvs/srv/SetBool          # request --- response
ros2 interface show action_tutorials_interfaces/action/Fibonacci   # goal --- result --- feedback
ros2 interface proto std_srvs/srv/Trigger         # request template ("{}")
```

## Common packages
| Pkg | Types |
|---|---|
| `std_msgs` | String, Bool, Int32, Float64, Header, Empty (prefer semantic msgs) |
| `geometry_msgs` | Twist, Pose, PoseStamped, Point, Quaternion, Vector3, TransformStamped, PoseWithCovarianceStamped |
| `sensor_msgs` | LaserScan, Image, CompressedImage, Imu, PointCloud2, JointState, CameraInfo |
| `nav_msgs` | Odometry, Path, OccupancyGrid |
| `std_srvs` | Empty, Trigger{→success,message}, SetBool{data→success,message} |
| `example_interfaces` | AddTwoInts srv; Fibonacci action (`order` → `sequence`, feedback `sequence`) |
| `action_tutorials_interfaces` | Fibonacci action (feedback `partial_sequence`) [Humble, Jazzy] [changed in Lyrical: removed in Kilted] |
| `action_msgs` | GoalStatus (STATUS_SUCCEEDED=4, CANCELED=5, ABORTED=6) |

## Fields of frequent types
`std_msgs/String{data}` · `geometry_msgs/Twist{linear,angular:Vector3}` · `geometry_msgs/Pose{position:Point, orientation:Quaternion}` · `nav_msgs/Odometry{header, child_frame_id, pose.pose, twist.twist}` · `sensor_msgs/LaserScan{angle_min, angle_max, angle_increment, range_min, range_max, ranges[]}` · `sensor_msgs/Image` (use cv_bridge, [[core-recipe-cv-bridge]]).

## Pitfalls
- `int32` is a primitive field type, and `std_msgs/Int32` is a message with a `.data` field ([[core-iface-syntax-usage]]).
- `ros2 interface show` fails for a custom type until its package is built and the terminal is sourced ([[core-iface-package]]).
- For code that must run on Humble through Lyrical, use `example_interfaces/action/Fibonacci`. Note its feedback field is `sequence`, not `partial_sequence`.
