---
id: control-controller-config
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Controller YAML: controller_manager, update_rate, controller types, forward_command_controller, joint names"
domain: control
area: setup
distro: jazzy
tested: false
audience: dev
summary: "controller_configuration.yaml: controller_manager update_rate and controller types, forward_command_controller joints/interface_name, trajectory controller block, joint names = URDF."
tags: [controller yaml, controller_manager, ros__parameters, update_rate, type, forward_command_controller, ForwardCommandController, interface_name, joint_trajectory_controller, JointTrajectoryController, joint_state_broadcaster, list_controller_types]
see: ["[[control-jtc-parameters]]", "[[control-urdf-tag]]", "[[control-bringup-sim-launch]]", "[[control-bringup-hardware-launch]]", "[[control-cli-list]]", "[[control-overview]]", "[[core-ros2-control-overview]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: the course's state_publish_rate line is left out (not a Jazzy parameter), goal_time comment corrected, open_loop_control marked — details in control-jtc-parameters (CONTROL-V06, CONTROL-V07, CONTROL-V28)"
  - "jazzy: effort_controllers/JointPositionController is not a ros2_controllers type — https://github.com/ros-controls/ros2_controllers/blob/jazzy/effort_controllers/effort_controllers_plugins.xml (CONTROL-V05)"
  - "jazzy: the course text names the trajectory controller position_trajectory_controller, its YAML joint_trajectory_controller (CONTROL-V02)"
  - "jazzy: the layout is the official Humble demo file; the Jazzy demo puts type in each controller's ros__parameters and passes the file to the spawner — https://github.com/ros-controls/ros2_control_demos/blob/jazzy/example_1/bringup/launch/rrbot.launch.py (CONTROL-V40)"
---
# Controller YAML: controller_manager, update_rate, controller types, forward_command_controller, joint names

**TL;DR** One ROS 2 parameters file configures the controller manager (loop rate and which controllers exist, by name and type) and then each controller under its own name. Joint names must be the names of the URDF joints.

## config/controller_configuration.yaml (two joints)
```yaml
# Controller manager configuration
controller_manager:
  ros__parameters:
    update_rate: 10  # Hz

    ### Controllers to be initialized at startup ###
    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    forward_position_controller:
      type: forward_command_controller/ForwardCommandController

    joint_trajectory_controller:
      type: joint_trajectory_controller/JointTrajectoryController

### Properties of the controllers that we will use and definition of joints to use ###
forward_position_controller:
  ros__parameters:
    joints:
      - joint1
      - joint2
    interface_name: position

joint_trajectory_controller:
  ros__parameters:
    joints:
      - joint1
      - joint2
    command_interfaces:
      - position
    state_interfaces:
      - position
    action_monitor_rate: 20.0 # Defaults to 20
    allow_partial_joints_goal: false # Defaults to false
    open_loop_control: true  # deprecated in Jazzy, removed in Lyrical
    allow_integration_in_goal_trajectories: true
    constraints:
      stopped_velocity_tolerance: 0.01 # Defaults to 0.01
      goal_time: 0.0 # Defaults to 0.0 (no time limit)
```
The course's first version has only `joint1`; the copies of the hardware units name the trajectory controller `position_trajectory_controller` (any name works if both blocks use it). The course text calls it `position_trajectory_controller` here too, but this file defines `joint_trajectory_controller`.

## How it is read
- First line = node name (`controller_manager`), then `ros__parameters:`; `update_rate` is the control loop frequency, one of the values you tune for the behaviour of the actuators.
- Under it, each controller: a free, unique name and its `type`, the name of the controller plugin (`ros2 control list_controller_types` lists the installed ones, [[control-cli-list]]). The course's example `joint1_position_controller` with `type: effort_controllers/JointPositionController` is not a ros2_controllers type: `effort_controllers` has only `JointGroupEffortController`.
- At root level, each controller's own `ros__parameters`. `forward_command_controller` needs `joints` and `interface_name`. Both controllers here claim `joint1/position` and `joint2/position`, so only one can be active at a time.
- The trajectory controller's parameters, and the course lines left out or corrected here (`state_publish_rate`, the `goal_time` comment): [[control-jtc-parameters]].

[≥Jazzy] The official Jazzy demo writes `type` inside each controller's `ros__parameters` and gives the file to the spawner with `--param-file`; the layout above works too.

## Pitfalls
- Joint name not in the URDF (or not in its `<ros2_control>` tag) → the controller cannot claim its interfaces.
- `type` misspelled or package not installed → "Loader for controller '…' (type '…') not found."; a controller without `type` → "The 'type' param was not defined for '…'."
- The file is passed to the gz_ros2_control plugin in simulation ([[control-urdf-tag]]) and to `ros2_control_node` on real hardware ([[control-bringup-hardware-launch]]).
