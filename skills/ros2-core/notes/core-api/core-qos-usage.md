---
id: core-qos-usage
title: "QoS in code, per-data-type choices & diagnosis"
domain: core
area: core-api
distro: humble
tested: false
audience: dev
summary: "Creating QoSProfile in rclpy/rclcpp (sensor, latched map), recommended QoS per data type, diagnosing QoS mismatch, RViz settings."
tags: [QoS, QoSProfile, SensorDataQoS, transient_local, ros2 topic info, RViz]
see: ["[[core-qos-policies]]", "[[core-topic-cli]]", "[[core-debug-tools]]", "[[core-message-filters]]"]
requires: []
version_notes: []
---
# QoS in code, per-data-type choices & diagnosis

**TL;DR** Sensors use `qos_profile_sensor_data` / `SensorDataQoS()`. Latched data (`/map`, `/tf_static`, `/robot_description`) uses RELIABLE + TRANSIENT_LOCAL with depth 1. When a topic is silent, check `ros2 topic info -v` first.

## Python
```python
from rclpy.qos import (DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy,
                       qos_profile_sensor_data)

self.create_subscription(LaserScan, '/scan', self.on_scan, qos_profile_sensor_data)

reliable_10 = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)   # course LaserScan sub
map_qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                     durability=DurabilityPolicy.TRANSIENT_LOCAL, history=HistoryPolicy.KEEP_LAST)
self.map_pub = self.create_publisher(OccupancyGrid, '/map', map_qos)
```
## C++
```cpp
sub_ = create_subscription<sensor_msgs::msg::LaserScan>("scan", rclcpp::SensorDataQoS(), cb);
auto map_qos = rclcpp::QoS(rclcpp::KeepLast(1)).reliable().transient_local();
pub_ = create_publisher<nav_msgs::msg::OccupancyGrid>("map", map_qos);
```

## Recommended per data type
| Data | Reliability | Durability | Depth |
|---|---|---|---|
| Camera raw / PointCloud2 / LaserScan | BEST_EFFORT | VOLATILE | 1–5 |
| IMU | BEST_EFFORT | VOLATILE | 10–50 |
| `/cmd_vel`, `/odom` | RELIABLE | VOLATILE | 10 |
| `/tf` | RELIABLE | VOLATILE | 100 |
| `/tf_static`, `/map`, `/robot_description` | RELIABLE | TRANSIENT_LOCAL | 1 |

## Diagnose
```bash
ros2 topic info /scan --verbose                          # QoS of every pub/sub endpoint
ros2 topic echo /scan --qos-reliability best_effort      # also --qos-profile sensor_data, --qos-depth N
ros2 topic echo /map --qos-durability transient_local
ros2 doctor --report                                     # QOS COMPATIBILITY LIST section
```
RViz2: set Display → Topic → Reliability Policy = Best Effort for sensor topics. The RViz defaults may not match ([[core-debug-tools]]).

## Pitfalls
- RELIABLE for high-rate sensors over Wi-Fi → latency and lag. Use BEST_EFFORT.
- TRANSIENT_LOCAL on high-rate streams wastes memory.
- message_filters synchronizers: all subscribers need the same compatible QoS ([[core-message-filters]]).
