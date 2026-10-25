---
id: control-diff-drive-controller
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "diff_drive_controller: wheel joints with velocity interfaces, YAML parameters, TwistStamped cmd_vel, odometry and TF"
domain: control
area: controllers
distro: jazzy
tested: false
audience: dev
summary: "diff_drive_controller: TwistStamped on ~/cmd_vel to two wheel velocity interfaces, odometry on ~/odom and TF, wheel YAML, limits, cmd_vel_timeout."
tags: [diff_drive_controller, DiffDriveController, differential drive, cmd_vel, TwistStamped, odom, nav_msgs/Odometry, odom_frame_id, base_frame_id, wheel_separation, wheel_radius, open_loop, enable_odom_tf, cmd_vel_timeout, use_stamped_vel, has_velocity_limits, max_jerk, publish_rate]
see: ["[[control-urdf-tag]]", "[[control-controller-config]]", "[[control-builtin-forward]]", "[[control-learn-unit6-diffbot]]", "[[control-humble-to-jazzy]]", "[[control-jazzy-to-lyrical]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: the course YAML is the Humble example_2 file plus use_stamped_vel; the Jazzy demo drops the has_* and jerk lines — https://github.com/ros-controls/ros2_control_demos/blob/jazzy/example_2/bringup/config/diffbot_controllers.yaml (CONTROL-V68)"
  - "humble: use_stamped_vel default true; false subscribes Twist on ~/cmd_vel_unstamped; jazzy: removed, TwistStamped on ~/cmd_vel only — https://github.com/ros-controls/ros2_controllers/blob/humble/diff_drive_controller/src/diff_drive_controller.cpp (CONTROL-V67)"
  - "jazzy: has_*_limits deprecated (false sets the limits to NaN), min_acceleration deprecated and not read; kilted/lyrical: removed, so max_jerk 0.0 becomes a jerk limit of 0 and the speed never rises from 0 [verify] — https://github.com/ros-controls/control_toolbox/blob/master/control_toolbox/include/control_toolbox/rate_limiter.hpp (CONTROL-V68)"
  - "lyrical: publish_rate removed — https://github.com/ros-controls/ros2_controllers/blob/master/doc/release_notes.rst (CONTROL-V69)"
  - "jazzy: open_loop true computes odometry from the commands, not from the wheel states — https://github.com/ros-controls/ros2_controllers/blob/jazzy/diff_drive_controller/src/diff_drive_controller_parameter.yaml (CONTROL-V70)"
  - "jazzy: ros2 topic pub -1 sends one message; the controller brakes after cmd_vel_timeout — https://github.com/ros2/ros2cli/blob/jazzy/ros2topic/ros2topic/verb/pub.py (CONTROL-V54)"
  - "kilted/lyrical: wheel min/max ±1 rad/s clamp the commands (enforce_command_limits true) [verify] (CONTROL-V64)"
---
# diff_drive_controller: wheel joints with velocity interfaces, YAML parameters, TwistStamped cmd_vel, odometry and TF

**TL;DR** A plane has three degrees of freedom (x, y, rotation about z), so a mobile base is commanded with a **twist**: linear plus angular velocity. `diff_drive_controller` takes one twist and turns it into the velocities of the left and right wheels: one controller for all wheels. It also estimates the robot's position and velocity, publishes `nav_msgs/Odometry` and the `odom → base_link` transform. It has no closed velocity loop of its own: on a real robot use actuators with on-board velocity control, or write a controller with one.

## Wheels in `<ros2_control>`
The wheels are driven through **velocity** command interfaces:
```xml
<ros2_control name="diff_drive" type="system">
  <hardware>
    <plugin>gz_ros2_control/GazeboSimSystem</plugin>
  </hardware>
  <joint name="left_wheel_joint">
    <command_interface name="velocity">
      <param name="min">-1</param>
      <param name="max">1</param>
    </command_interface>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
    <state_interface name="effort"/>
  </joint>
  <joint name="right_wheel_joint">
    <command_interface name="velocity">
      <param name="min">-1</param>
      <param name="max">1</param>
    </command_interface>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
    <state_interface name="effort"/>
  </joint>
</ros2_control>
```
The `min`/`max` are wheel velocities in rad/s: ±1 rad/s on a 0.015 m wheel is 0.015 m/s. Jazzy does not apply them by default; [changed in Kilted: `enforce_command_limits` defaults to `true` and the robot crawls [verify]] ([[control-urdf-tag]]). The YAML below goes into the gz_ros2_control `<parameters>` in simulation.

## config/diff_drive_controller_config.yaml (Jazzy form)
```yaml
controller_manager:
  ros__parameters:
    update_rate: 10  # Hz

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    diffbot_base_controller:
      type: diff_drive_controller/DiffDriveController

diffbot_base_controller:
  ros__parameters:
    left_wheel_names: ["left_wheel_joint"]
    right_wheel_names: ["right_wheel_joint"]

    wheel_separation: 0.10
    #wheels_per_side: 1  # actually 2, but both are controlled by 1 signal
    wheel_radius: 0.015

    wheel_separation_multiplier: 1.0
    left_wheel_radius_multiplier: 1.0
    right_wheel_radius_multiplier: 1.0

    publish_rate: 50.0  # odometry and TF; removed in Lyrical
    odom_frame_id: odom
    base_frame_id: base_link
    pose_covariance_diagonal : [0.001, 0.001, 0.001, 0.001, 0.001, 0.01]
    twist_covariance_diagonal: [0.001, 0.001, 0.001, 0.001, 0.001, 0.01]

    open_loop: true
    enable_odom_tf: true

    cmd_vel_timeout: 0.5
    #publish_limited_velocity: true
    #velocity_rolling_window_size: 10

    # Velocity and acceleration limits
    # Whenever a min_* is unspecified, default to -max_*
    linear.x.max_velocity: 1.0
    linear.x.min_velocity: -1.0
    linear.x.max_acceleration: 1.0
    angular.z.max_velocity: 1.0
    angular.z.min_velocity: -1.0
    angular.z.max_acceleration: 1.0
```
- `wheel_separation` and `wheel_radius` in m; the multipliers correct a measured robot without changing the nominal values.
- `open_loop: true`: odometry is computed from the **commanded** velocities, not from the wheel states (wheel slip is invisible); `false` uses the wheels' position/velocity states.
- `cmd_vel_timeout`: with no new command for this long the controller brakes ("Velocity command timed out. Braking."); 0.0 disables it.
- An unset limit (NaN) means no limit.

The course's file has these lines more. They are the Humble form ([Humble: `has_*_limits` default `false`, so the limits apply only with them]); leave them out on Jazzy and later:
```yaml
    use_stamped_vel: false
    linear.x.has_velocity_limits: true
    linear.x.has_acceleration_limits: true
    linear.x.has_jerk_limits: false
    linear.x.max_jerk: 0.0
    linear.x.min_jerk: 0.0
    angular.z.has_velocity_limits: true
    angular.z.has_acceleration_limits: true
    angular.z.has_jerk_limits: false
    angular.z.min_acceleration: -1.0
    angular.z.max_jerk: 0.0
    angular.z.min_jerk: 0.0
```
- [Humble] `use_stamped_vel: false` makes the controller listen to `geometry_msgs/msg/Twist` on `~/cmd_vel_unstamped`: the course's TwistStamped on `~/cmd_vel` then reaches nobody. Keep the default (`true`) on Humble. [changed in Jazzy: removed; only TwistStamped on `~/cmd_vel`].
- [changed in Jazzy: `has_*_limits` deprecated with a warning (`false` sets those limits to NaN); `min_acceleration` deprecated and not read, the limiter uses −`max_acceleration`, the same −1.0]. [changed in Kilted: `has_*_limits` removed, so `max_jerk: 0.0` and `min_jerk: 0.0` become a jerk limit of 0 and the speed never rises from 0: the robot does not move [verify]. Delete the jerk lines or set them to `.NAN`].

## Topics
| Topic | Type | |
|---|---|---|
| `~/cmd_vel` | `geometry_msgs/msg/TwistStamped` | a zero stamp is replaced by the receive time (warned once); messages older than `cmd_vel_timeout` are ignored |
| `~/odom` | `nav_msgs/msg/Odometry` | in `odom_frame_id` |
| `/tf` | `odom → base_link` | with `enable_odom_tf: true` |

Drive in a circle, publishing until Ctrl+C:
```bash
ros2 topic pub --rate 30 /diffbot_base_controller/cmd_vel geometry_msgs/msg/TwistStamped "header:
  stamp:
    sec: 0
    nanosec: 0
  frame_id: ''
twist:
  linear:
    x: 0.2
    y: 0.0
    z: 0.0
  angular:
    x: 0.0
    y: 0.0
    z: 1.0"
```
The course adds `-1` (`--once`): that sends one message, and the robot stops 0.5 s later (`cmd_vel_timeout`).

## Pitfalls
- Humble with `use_stamped_vel: false` → commands on the wrong topic, the robot does not move.
- Kilted/Lyrical with the course's jerk lines → the robot does not move, without an error [verify].
- Real robot: the controller only forwards wheel velocities; without a velocity loop in the actuators the robot does not follow the twist.
