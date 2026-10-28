---
id: moveit-architecture
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "What MoveIt 2 is and its architecture: move_group, robot interface, configuration data, user interfaces"
domain: moveit
area: config
distro: humble
tested: false
audience: dev
summary: "MoveIt 2 motion planning framework: move_group node, robot interface (joint states, TF, point clouds, controllers), URDF/SRDF config package, C++/Python/RViz interfaces."
tags: [MoveIt 2, MoveIt, move_group, motion planning, architecture, SRDF, URDF, config package, Setup Assistant, MoveGroupInterface, moveit_py, RViz MotionPlanning, robot interface]
see: ["[[moveit-setup-assistant-model]]", "[[moveit-cpp-move-group-interface]]", "[[moveit-config-controllers-yaml]]", "[[core-moveit2-overview]]"]
requires: [ros2-core]
version_notes:
  - "humble: moveit_py (Python API) is released as ros-humble-moveit-py 2.5.10, also on Jazzy, Kilted, Lyrical; the course says MoveIt 2 has no Python API — https://github.com/ros/rosdistro/blob/master/humble/distribution.yaml (MOVEIT-V02)"
---
# What MoveIt 2 is and its architecture

**TL;DR** MoveIt 2 is the ROS 2 version of MoveIt, a motion planning framework: it plans a motion of a robot (an arm, a gripper) from A to B without colliding with anything, and sends the result to the robot's controllers. Before you use it you build a **MoveIt configuration package** for your robot (configuration and launch files), usually with the MoveIt Setup Assistant ([[moveit-setup-assistant-model]]), which makes a complex task easy. RViz2 offers a GUI to plan and execute ([[moveit-rviz-motion-planning]]).

## Architecture
The four parts of the course's architecture figure (redrawn from its description):

```
 (4) user interfaces                        (3) configuration data
     C++ MoveGroupInterface, moveit_py,         URDF, SRDF, config/*.yaml of the
     RViz MotionPlanning plugin                 MoveIt package (joint limits, kinematics,
            |  actions / services                perception, end effector, controllers)
            v                                          |  parameters
     +------------------------------------------------------+
     |              (1) move_group node                     |
     +------------------------------------------------------+
            ^  joint states, TF, point clouds        |  trajectories to the controllers
            |                                        v
     (2) robot interface: a simulated or a real robot
```

1. **`move_group`** is the heart of MoveIt: it integrates the robot's components and offers actions and services (plan, execute, IK, FK, pick and place) to the user.
2. **Robot interface**: `move_group` collects robot data from it: point clouds, the robot's joint states, its controllers and its transforms (TF). The same interface fits a simulated robot or a real one.
3. **Configuration data**: the robot description (URDF), the semantic description (SRDF, Semantic Robot Description Format) and configuration files with joint limits, perception, the robot's kinematics and the end effector. The SRDF and the configuration files are generated with the MoveIt package; they live in its `config/` folder.
4. **User interfaces**: once `move_group` has all this, you command it from a program, with the C++ API ([[moveit-cpp-move-group-interface]]) or the Python API (`moveit_py`, released for Humble and later distros, MOVEIT-V02), or from the RViz motion planning plugin.

Planners available in Humble (OMPL, Pilz, CHOMP), Servo and the octomap perception pipeline: [[core-moveit2-overview]].

## Pitfalls
- No MoveIt package, no planning: `move_group` needs the URDF, the SRDF and the YAML files of the package; build it first ([[moveit-setup-assistant-controllers]]).
- The robot interface must deliver joint states with the right clock: a simulated robot needs `use_sim_time` on `move_group` ([[moveit-move-group-launch-sim]]).
- Executing needs the controllers named in `moveit_controllers.yaml` to match the robot's action servers ([[moveit-config-controllers-yaml]]).
