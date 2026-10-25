---
id: gazebo-tf-follow-frame
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Move a model to follow a TF frame: TF listener plus the /world/<world>/set_pose service (SetEntityPose)"
domain: gazebo
area: plugins
distro: jazzy
tested: false
audience: dev
summary: "Follow a TF frame: lookup_transform each tick, then move the model with /world/<world>/set_pose (SetEntityPose) and a rotated offset."
tags: [set_pose, SetEntityPose, ros_gz_interfaces, Entity, UserCommands, service bridge, parameter_bridge, TF listener, lookup_transform, follow frame, cam_bot_follower, move_generic_model.py, quaternion rotation]
see: ["[[core-tf-listener]]", "[[gazebo-ros-gz-bridge]]", "[[gazebo-world-sdf]]", "[[gazebo-sim-overview]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy/harmonic: the UserCommands world system offers the Gazebo service /world/<world>/set_pose; a ROS client reaches it through ros_gz_bridge with ros_gz_interfaces/srv/SetEntityPose (request entity + pose, response success) — https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md, https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/systems/user_commands/UserCommands.cc (TF-V24)"
  - "humble/fortress: SetEntityPose exists and the bridge lists it — https://github.com/gazebosim/ros_gz/blob/humble/ros_gz_bridge/README.md (TF-V24)"
  - "jazzy: ros_gz_interfaces/msg/Entity defines MODEL = 2 — https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_interfaces/msg/Entity.msg (TF-V24)"
  - "humble/jazzy: get_logger().warn() is a deprecated alias; lyrical: removed, use warning() (V22) (TF-V36)"
  - "TF course: the same program is turtle_tf_3d_ros2/cam_bot_follower.py (unit 2) and move_generic_model.py (unit 3) (TF-V10)"
---
# Move a model to follow a TF frame (Gazebo Sim)

**TL;DR** TF tells a node *where* a frame is; Gazebo only has to *move the model there*. On every timer tick, look up `fixed_frame → target_frame`, rotate an offset given in the target frame by the target's orientation, and call the world service `/world/<world>/set_pose` (`ros_gz_interfaces/srv/SetEntityPose`). The ROS service exists only when ros_gz_bridge bridges it.

## Bridge the service
```bash
ros2 run ros_gz_bridge parameter_bridge /world/default/set_pose@ros_gz_interfaces/srv/SetEntityPose
```
`default` is the world name (the `world` parameter below must match). Gazebo's UserCommands system, loaded by default in a world without `<plugin>` elements ([[gazebo-world-sdf]]), provides the Gazebo side. Without the bridge the node stops at `Waiting for service /world/default/set_pose ...`.

## `move_generic_model.py`
```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener
from ros_gz_interfaces.srv import SetEntityPose


def quat_mult(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (
        aw*bx + ax*bw + ay*bz - az*by,
        aw*by - ax*bz + ay*bw + az*bx,
        aw*bz + ax*by - ay*bx + az*bw,
        aw*bw - ax*bx - ay*by - az*bz,
    )


def rotate_vec(v, q):
    # v' = q * (v,0) * q_conj
    x, y, z = v
    qx, qy, qz, qw = q
    qc = (-qx, -qy, -qz, qw)
    vq = (x, y, z, 0.0)
    t = quat_mult(q, vq)
    r = quat_mult(t, qc)
    return (r[0], r[1], r[2])


class CamBotFollower(Node):
    def __init__(self):
        super().__init__("cam_bot_follower")

        # Parameters
        self.declare_parameter("world", "default")
        self.declare_parameter("model_name", "cam_bot")
        self.declare_parameter("fixed_frame", "odom")          # TF parent frame
        self.declare_parameter("target_frame", "my_front_turtle_frame")
        self.declare_parameter("offset_xyz", [0.0, 0.0, 0.0])  # offset in target frame
        self.declare_parameter("rate_hz", 30.0)

        self.world = self.get_parameter("world").value
        self.model_name = self.get_parameter("model_name").value
        self.fixed_frame = self.get_parameter("fixed_frame").value
        self.target_frame = self.get_parameter("target_frame").value
        self.offset_xyz = self.get_parameter("offset_xyz").value
        rate_hz = float(self.get_parameter("rate_hz").value)

        # TF
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Service client
        srv = f"/world/{self.world}/set_pose"
        self.cli = self.create_client(SetEntityPose, srv)
        self.get_logger().info(f"Waiting for service {srv} ...")
        self.cli.wait_for_service()

        # Entity type enum: read your constant if you want; 2 commonly corresponds to MODEL
        self.ENTITY_MODEL = 2

        self.timer = self.create_timer(1.0 / rate_hz, self.tick)

    def tick(self):
        try:
            tf = self.tf_buffer.lookup_transform(
                self.fixed_frame,
                self.target_frame,
                rclpy.time.Time()
            )
        except Exception as e:
            self.get_logger().warning(f"TF lookup failed: {e}")
            return

        tx = tf.transform.translation.x
        ty = tf.transform.translation.y
        tz = tf.transform.translation.z

        qx = tf.transform.rotation.x
        qy = tf.transform.rotation.y
        qz = tf.transform.rotation.z
        qw = tf.transform.rotation.w
        q = (qx, qy, qz, qw)

        # Offset defined in target frame so it stays "above" even when robot turns
        ox, oy, oz = self.offset_xyz
        rox, roy, roz = rotate_vec((ox, oy, oz), q)

        req = SetEntityPose.Request()
        req.entity.name = self.model_name
        req.entity.type = self.ENTITY_MODEL  # MODEL enum

        req.pose.position.x = tx + rox
        req.pose.position.y = ty + roy
        req.pose.position.z = tz + roz

        req.pose.orientation.x = qx
        req.pose.orientation.y = qy
        req.pose.orientation.z = qz
        req.pose.orientation.w = qw

        self.cli.call_async(req)


def main():
    rclpy.init()
    node = CamBotFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
```
`2` is `Entity.MODEL` of `ros_gz_interfaces/msg/Entity` (`from ros_gz_interfaces.msg import Entity`). The course's version logs with `warn()`; `warning()` works in every distro.

## How it works
- `Buffer` + `TransformListener` fill the buffer from `/tf` and `/tf_static` ([[core-tf-listener]]).
- `lookup_transform(fixed_frame, target_frame, Time())` asks "where is `target_frame` with respect to `fixed_frame` right now?": translation = position of the target, rotation = its orientation. If the transform is missing the node logs and retries on the next tick.
- The offset (for example 60 cm above the robot) is defined in the **target** frame, so it is rotated by the target's quaternion (`v' = q (v, 0) q*`) and stays in place when the robot turns.
- The request moves the model `model_name` to that pose; the model pose is set in the Gazebo world, so `fixed_frame` must coincide with the world origin (in the course `world → odom` is the identity).

| Parameter | Default | Course (unit 2) |
|---|---|---|
| `world` | `default` | — |
| `model_name` | `cam_bot` | `cam_bot` |
| `fixed_frame` | `odom` | `world` |
| `target_frame` | `my_front_turtle_frame` | `turtle_attach_frame` |
| `offset_xyz` | `[0.0, 0.0, 0.0]` | `"[0.0, 0.0, 0.0]"` |
| `rate_hz` | 30.0 | 30.0 |

## Pitfalls
- No bridge for `set_pose` or a wrong `world` name → the node waits forever for the service.
- `TF lookup failed` every tick → the target frame is not published (a static broadcaster that was stopped, a separate tree).
- `call_async` without waiting is fire-and-forget: failed requests are not reported.
