---
id: core-recipe-laserscan
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "LaserScan geometry, sectors & obstacle avoidance"
domain: core
area: recipes
distro: humble
tested: false
audience: dev
summary: "Index↔angle math for LaserScan, filtering inf/nan, 6-sector minimums, priority-based avoidance and a minimal sense→act node."
tags: [LaserScan, obstacle avoidance, sectors, ranges, Twist, REP 103]
see: ["[[core-topic-pub-sub-py]]", "[[core-recipe-odom-go-to-goal]]", "[[core-learn-unit3-topics]]"]
requires: []
version_notes: []
---
# LaserScan geometry, sectors & obstacle avoidance

**TL;DR** Index `i` is at angle `angle_min + i*angle_increment` (0 = front, + = left). Drop inf/nan before `min()`. Front obstacles take priority, and you keep turning one way until the front is clear.

## LaserScan geometry
```python
import math
n = len(msg.ranges)
angle_i = msg.angle_min + i * msg.angle_increment            # rad, 0 = front, + = left (CCW)
idx = int(round((angle - msg.angle_min) / msg.angle_increment))   # angle -> index
n_expected = int(round((msg.angle_max - msg.angle_min) / msg.angle_increment)) + 1
valid = [r for r in msg.ranges if math.isfinite(r) and msg.range_min <= r <= msg.range_max]   # drop inf/nan
```
Index 0 = `angle_min`, which is the rightmost beam when angle_min < 0. The front is the index where the angle ≈ 0 (the middle, for symmetric scans). `intensities` is empty when the device gives none ([LaserScan.msg](https://github.com/ros2/common_interfaces/blob/humble/sensor_msgs/msg/LaserScan.msg)). Field table and a stop-at-distance node: the ros2-perception skill.

## Sector minimums (6 sectors, right → left)
```python
def sector_minimums(msg, names=('Right_Rear', 'Right', 'Front_Right', 'Front_Left', 'Left', 'Left_Rear')):
    n = len(msg.ranges)
    size = n // len(names)
    out = {}
    for k, name in enumerate(names):
        chunk = msg.ranges[k * size:(k + 1) * size if k < len(names) - 1 else n]
        vals = [r for r in chunk if math.isfinite(r) and r >= msg.range_min]
        out[name] = min(vals) if vals else float('inf')
    return out

d = sector_minimums(msg)
hit = {k: v < 0.8 for k, v in d.items()}          # detection threshold (m)
```
Priority rule: front (both sides → keep turning one way until clear, which avoids left/right oscillation) > sides (go forward + turn slightly away) > rear (go forward) > none (forward).
```python
cmd = Twist()
if hit['Front_Left'] or hit['Front_Right']:
    self.turning = True
    cmd.angular.z = -0.5                     # keep turning right until front clear
else:
    self.turning = False
    if hit['Left']:    cmd.linear.x, cmd.angular.z = 0.2, -0.3
    elif hit['Right']: cmd.linear.x, cmd.angular.z = 0.2, 0.3
    else:              cmd.linear.x = 0.5
self.cmd_pub.publish(cmd)
```
Sign convention (REP 103): `angular.z > 0` = turn LEFT (CCW), `< 0` = RIGHT. Verify it with teleop + `ros2 topic echo /cmd_vel`.

## Minimal sense → act node (front third only)
```python
class Avoider(Node):
    def __init__(self):
        super().__init__('avoider')
        self.sub = self.create_subscription(LaserScan, '/scan', self.on_scan, qos_profile_sensor_data)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

    def on_scan(self, msg):
        cmd = Twist()
        front = [r for r in msg.ranges[len(msg.ranges)//3: 2*len(msg.ranges)//3] if r > msg.range_min]
        if front and min(front) < 0.8:
            cmd.angular.z = -0.5      # turn right
        else:
            cmd.linear.x = 0.3
        self.pub.publish(cmd)
```
Full node structure and `main()`: [[core-topic-pub-sub-py]]. Combining this with a goal: [[core-recipe-odom-go-to-goal]].
