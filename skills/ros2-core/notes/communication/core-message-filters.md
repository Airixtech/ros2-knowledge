---
id: core-message-filters
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Multi-sensor time sync (message_filters)"
domain: core
area: communication
distro: humble
tested: false
audience: dev
summary: "Synchronize image + point cloud (or any sensors) with ApproximateTimeSynchronizer; slop rule, QoS, sync quality hierarchy."
tags: [message_filters, ApproximateTimeSynchronizer, TimeSynchronizer, slop, sensor sync]
see: ["[[core-qos-usage]]", "[[core-perception-basics]]", "[[core-tf-listener]]"]
requires: []
version_notes:
  - "jazzy: new C++ policies ApproximateEpsilonTime and LatestTime (Iron) — https://docs.ros.org/en/rolling/Releases/Release-Iron-Irwini.html (V72)"
---
# Multi-sensor time sync (message_filters)

**TL;DR** Wrap each topic in a `message_filters.Subscriber` and feed them to an `ApproximateTimeSynchronizer(queue_size, slop)`. The callback receives one message per topic with close stamps. All subscribers need the same compatible QoS.

## Python
```python
from message_filters import ApproximateTimeSynchronizer, Subscriber
img_sub = Subscriber(self, Image, '/camera/image_raw', qos_profile=qos_profile_sensor_data)
pc_sub = Subscriber(self, PointCloud2, '/lidar/points', qos_profile=qos_profile_sensor_data)
self.sync = ApproximateTimeSynchronizer([img_sub, pc_sub], queue_size=10, slop=0.05)
self.sync.registerCallback(self.on_pair)        # on_pair(self, img, cloud)
```
- `TimeSynchronizer` = identical stamps only (e.g. stereo pairs).
- `slop ≈ 1/(2·f_min)`. Example: 30 Hz camera + 10 Hz lidar → 0.05. Use the same QoS on all subscribers.
- [≥Jazzy (since Iron), C++: `ApproximateEpsilonTime` (exact time within an epsilon) and `LatestTime` (up to 9 msgs, zero-order-hold upsampling)]

## Sync quality (best → worst)
Hardware trigger (<1 µs) > PTP (sub-µs, wired) > NTP (ms) > software (`ApproximateTimeSynchronizer`). Stamp as close to the hardware as possible ([[core-perception-basics]]).

## Pitfalls
- Messages without a `header.stamp`, or stamped with arrival time instead of capture time, sync poorly or never.
- A RELIABLE `Subscriber` on a BEST_EFFORT publisher never connects, so the synchronizer callback never fires. Use sensor QoS on every input.
