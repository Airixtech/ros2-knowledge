---
id: core-recipe-odom-go-to-goal
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Odometry yaw & go-to-goal controller (geofence)"
domain: core
area: recipes
distro: humble
tested: false
audience: dev
summary: "Yaw from quaternion without deps, angle normalization, turn-then-drive P controller to (x, y), return-home geofence."
tags: [odometry, yaw, quaternion, go-to-goal, geofence, tf_transformations]
see: ["[[core-recipe-laserscan]]", "[[core-recipe-command-goals]]", "[[core-tf-basics]]"]
requires: []
version_notes:
  - "jazzy: pip3 install blocked by PEP 668 on Ubuntu 24.04; use apt python3-transforms3d — https://peps.python.org/pep-0668/ (V42)"
---
# Odometry yaw & go-to-goal controller (geofence)

**TL;DR** Read the pose from `nav_msgs/Odometry` and compute yaw from the quaternion. First rotate in place until the heading error is under 0.1 rad, then drive with a small P correction.

## Odometry: position, yaw, distance
```python
def yaw_from_quaternion(q):
    # no external deps; equals tf_transformations.euler_from_quaternion(...)[2]
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))

def on_odom(self, msg):                                  # nav_msgs/Odometry
    self.x = msg.pose.pose.position.x
    self.y = msg.pose.pose.position.y
    self.yaw = yaw_from_quaternion(msg.pose.pose.orientation)
    self.dist_origin = math.hypot(self.x, self.y)

def normalize_angle(a):                                  # -> [-pi, pi]
    return (a + math.pi) % (2.0 * math.pi) - math.pi
```
With tf_transformations (`sudo apt install ros-humble-tf-transformations && pip3 install transforms3d`):
`roll, pitch, yaw = tf_transformations.euler_from_quaternion([q.x, q.y, q.z, q.w])` · `qx, qy, qz, qw = tf_transformations.quaternion_from_euler(0, 0, yaw)`.
[changed in Jazzy: Ubuntu 24.04 blocks `pip3 install` into the system Python (PEP 668) → `sudo apt install python3-transforms3d`]

## Go-to-goal (turn-then-drive P controller)
```python
def drive_to(self, gx, gy, tol=0.1):
    """Return Twist toward (gx, gy); zero Twist when within tol."""
    cmd = Twist()
    dx, dy = gx - self.x, gy - self.y
    if math.hypot(dx, dy) < tol:
        return cmd                                       # arrived -> stop
    yaw_err = normalize_angle(math.atan2(dy, dx) - self.yaw)
    if abs(yaw_err) > 0.1:                               # rad
        cmd.angular.z = 0.5 if yaw_err > 0 else -0.5     # rotate in place
    else:
        cmd.linear.x = min(0.5, math.hypot(dx, dy))
        cmd.angular.z = 0.8 * yaw_err                    # small heading correction
    return cmd
```
- Return home / geofence: in `on_odom`, `if self.dist_origin > R: self.returning = True`, and `elif self.returning and self.dist_origin <= R: self.returning = False`. In the control callback: `if self.returning: publish(drive_to(0, 0))`, else explore.
- Combine with obstacle avoidance: if the front is blocked → avoidance Twist ([[core-recipe-laserscan]]), else `drive_to`.

## Pitfalls
- Forgetting `normalize_angle` makes the robot spin the long way around when the error crosses ±π.
- `odom` drifts. For goals in a map frame, use Nav2 ([[core-nav2-python-client]]).
