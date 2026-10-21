---
id: urdf-joint-state-publisher
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "joint_state_publisher(_gui): /joint_states, sliders, mimic, conflicts"
domain: urdf
area: workflow
distro: humble
tested: false
audience: dev
summary: "robot_state_publisher vs joint_state_publisher; joint_state_publisher_gui sliders, /joint_states, parameters rate/source_list/zeros/use_mimic_tags, who else publishes joint states."
tags: [joint_state_publisher, joint_state_publisher_gui, joint_states, sensor_msgs/JointState, sliders, source_list, zeros, rate, use_mimic_tags, use_smallest_joint_limits, robot_state_publisher]
see: ["[[core-robot-state-publisher]]", "[[urdf-frames-rviz]]", "[[urdf-joint-extras]]", "[[urdf-joints]]"]
requires: [ros2-core]
version_notes:
  - "humble: no slider for fixed, floating and planar joints; mimic joints follow their leader; parameters rate (10), source_list, use_mimic_tags (true), use_smallest_joint_limits (true), zeros.<joint> — https://github.com/ros/joint_state_publisher/blob/humble/joint_state_publisher/joint_state_publisher/joint_state_publisher.py (URDF-V06, URDF-V21, URDF-V23)"
---
# joint_state_publisher(_gui): /joint_states, sliders, mimic, conflicts

**TL;DR** robot_state_publisher knows the shape of the robot but not where its movable joints are: something must publish `sensor_msgs/msg/JointState` on `/joint_states` (angles for continuous/revolute, meters for prismatic). On a desk that is `joint_state_publisher_gui` (sliders); on a robot it is the driver, `joint_state_broadcaster` or the simulator.

## Two nodes that get confused
| Node | Reads | Publishes |
|---|---|---|
| `robot_state_publisher` | `robot_description`, `/joint_states` | `/robot_description`, `/tf_static`, `/tf` |
| `joint_state_publisher` / `_gui` | `robot_description` | `/joint_states` (default or slider values) |

```bash
ros2 run joint_state_publisher_gui joint_state_publisher_gui   # window with one slider per movable joint
ros2 run joint_state_publisher joint_state_publisher           # same values without a window
```
- Fixed (and floating/planar) joints get no slider: with only a fixed joint the window is empty.
- Continuous joints get a −π…π slider; revolute and prismatic use `lower`/`upper`, narrowed to `soft_lower_limit`/`soft_upper_limit` when a `<safety_controller>` is present.
- Mimic joints get no slider: their value is computed from the leader ([[urdf-joint-extras]]).
- Change a joint from `fixed` to `continuous` without starting the GUI → RViz2 shows the child link with an error until a joint state arrives ([[urdf-frames-rviz]]).

## Parameters (joint_state_publisher)
| Parameter | Default | Use |
|---|---|---|
| `rate` | 10 | publish rate (Hz) |
| `source_list` | `[]` | other `JointState` topics to merge (e.g. a gripper driver) |
| `zeros.<joint>` | — | start value of a joint instead of 0 |
| `use_mimic_tags` | true | apply `<mimic>` |
| `use_smallest_joint_limits` | true | use the soft limits of `<safety_controller>` |

## Who publishes joint states
- Desk or teaching: `joint_state_publisher_gui`.
- Real robot: the hardware driver or ros2_control's `joint_state_broadcaster`.
- Simulator: the simulator's joint state plugin, bridged to ROS, or `joint_state_broadcaster` under gz_ros2_control (ros2-gazebo skill).

## Pitfalls
- Two publishers on `/joint_states` (the GUI plus a broadcaster) → links jump between values ([[core-robot-state-publisher]]).
- joint_state_publisher is not a stand-in for simulated joints: it publishes slider or default values, not what the simulator does.
- No `/joint_states` at all → movable links have no TF; RViz2 RobotModel reports them as missing.
