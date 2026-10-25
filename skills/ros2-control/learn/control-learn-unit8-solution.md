---
id: control-learn-unit8-solution
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Unit 8 solution: ros2_control xacro macro for 8 joints, JTC YAML, start_controllers launch, run"
domain: control
area: learn
distro: jazzy
tested: false
audience: students
summary: "Unit 8 solution: my_quadruped_bringup, joint_trajectory_controller choice, xacro actuator macro with GazeboSimSystem, solo8_controller_config.yaml, start_controllers.launch.py, run."
tags: [unit 8, course project, solution, my_quadruped_bringup, solo_system_quadruped.ros2_control.xacro, xacro macro, GazeboSimSystem, gz_ros2_control, solo8_controller_config.yaml, position_trajectory_controller, start_controllers.launch.py, spawner]
see: ["[[control-learn-unit8-project]]", "[[control-jtc-commands]]", "[[control-jtc-parameters]]", "[[control-urdf-tag]]", "[[control-controller-config]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: the solution page's first snippet uses plugin names that gz_ros2_control does not provide and another YAML package; the complete file is right — https://github.com/ros-controls/gz_ros2_control/blob/jazzy/gz_ros2_control/src/gz_system.cpp (CONTROL-V60)"
  - "jazzy: state_publish_rate left out, goal_time comment corrected, open_loop_control marked (CONTROL-V06, CONTROL-V07, CONTROL-V28); list_controllers in columns (CONTROL-V10)"
---
# Unit 8 solution: ros2_control xacro macro for 8 joints, JTC YAML, start_controllers launch, run

**TL;DR** Try the project yourself first ([[control-learn-unit8-project]]). The solution adds the `<ros2_control>` tags for the eight joints with a xacro macro, uses a joint trajectory controller named like the test script expects, and starts it with two spawners.

## 1. Package
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type=ament_cmake my_quadruped_bringup --dependencies urdf xacro robot_state_publisher
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

## 2. Controller choice
The test script publishes `trajectory_msgs/msg/JointTrajectory` on `/position_trajectory_controller/joint_trajectory`, the message a joint trajectory controller takes: run the script and check with `ros2 topic list` and `ros2 topic info` ([[control-jtc-commands]]).

## 3–4. Robot description and Gazebo
Only `solo_system_quadruped.ros2_control.xacro` changes. The solution page first shows a short snippet with other plugin names and the YAML in another package; it contradicts the complete file, which is the one for Gazebo Sim:
```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Using xacro you we create a macro for one joint -->
  <xacro:macro name="solo_system_quadruped_actuator" params="name">
    <joint name="${name}">
      <command_interface name="position">
        <param name="min">-10</param>
        <param name="max">10</param>
      </command_interface>
      <command_interface name="velocity">
        <param name="min">-1000</param>
        <param name="max">1000</param>
      </command_interface>
      <command_interface name="effort">
        <param name="min">-1000</param>
        <param name="max">1000</param>
      </command_interface>
      <state_interface name="position"/>
      <state_interface name="velocity"/>
      <state_interface name="effort"/>
    </joint>
  </xacro:macro>

  <xacro:macro name="solo_system_quadruped" params="name">
    <ros2_control name="${name}" type="system">
      <hardware>
        <plugin>gz_ros2_control/GazeboSimSystem</plugin>
      </hardware>
      <!-- Use macro defined earlier to create the command and state interfaces on each joint -->

      <!-- Forward Left Hip -->
      <xacro:solo_system_quadruped_actuator name="FL_HFE" />
      <!-- Forward Left Knee -->
      <xacro:solo_system_quadruped_actuator name="FL_KFE"/>
      <!-- Forward Right Hip -->
      <xacro:solo_system_quadruped_actuator name="FR_HFE"/>
      <!-- Forward Right Knee -->
      <xacro:solo_system_quadruped_actuator name="FR_KFE"/>
      <!-- Hind Left Hip -->
      <xacro:solo_system_quadruped_actuator name="HL_HFE"/>
      <!-- Hind Left Knee -->
      <xacro:solo_system_quadruped_actuator name="HL_KFE"/>
      <!-- Hind Right Hip -->
      <xacro:solo_system_quadruped_actuator name="HR_HFE"/>
      <!-- Hind Right Knee -->
      <xacro:solo_system_quadruped_actuator name="HR_KFE"/>
    </ros2_control>

    <!-- Gazebo's ros2_control plugin -->
    <gazebo>
      <plugin filename="gz_ros2_control-system" name="gz_ros2_control::GazeboSimROS2ControlPlugin">
        <!-- If you are using a different package name or .yaml name update the line below accordingly -->
        <parameters>$(find my_quadruped_bringup)/config/solo8_controller_config.yaml</parameters>
      </plugin>
    </gazebo>
  </xacro:macro>
</robot>
```
The main file already calls `<xacro:solo_system_quadruped name="SoloSystemQuadruped" />`.

## 5. config/solo8_controller_config.yaml (in my_quadruped_bringup)
```yaml
controller_manager:
  ros__parameters:
    update_rate: 50  # Hz

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    position_trajectory_controller:
      type: joint_trajectory_controller/JointTrajectoryController

position_trajectory_controller:
  ros__parameters:
    joints:
      - FL_HFE
      - FL_KFE
      - FR_KFE
      - HL_HFE
      - HR_HFE
      - FR_HFE
      - HL_KFE
      - HR_KFE
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
The order of `joints` does not matter: the controller matches the trajectory's joints by name. The course's `state_publish_rate: 200.0` is left out and the `goal_time` comment corrected ([[control-jtc-parameters]]).

## 6. launch/start_controllers.launch.py
```bash
cd ~/ros2_ws/src/my_quadruped_bringup
mkdir launch
cd launch
touch start_controllers.launch.py
chmod +x start_controllers.launch.py
```
```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "-c", "/controller_manager"],
    )

    joint_trajectory_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["position_trajectory_controller", "-c", "/controller_manager"],
    )

    return LaunchDescription([
        joint_state_broadcaster_spawner,
        joint_trajectory_controller_spawner,
    ])
```
The course's file also imports `os`, `get_package_share_directory`, `ExecuteProcess`, `IncludeLaunchDescription`, `RegisterEventHandler`, `OnProcessExit`, `PythonLaunchDescriptionSource` and `xacro`, none of them used. The two spawners need no ordering here: the robot is already spawned. Install both folders (end of `CMakeLists.txt`) and build:
```cmake
install(
  DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}/
)
```
```bash
cd ~/ros2_ws
colcon build --symlink-install
source ~/ros2_ws/install/setup.bash
```

## Run it
```bash
ros2 launch spawn_solo spawn_solo.launch.py
ros2 launch my_quadruped_bringup start_controllers.launch.py
ros2 control list_controllers
ros2 launch joint_trajectory_publisher joint_trajectory_solo_push-ups.launch.py
```
`list_controllers` shows `joint_state_broadcaster` and `position_trajectory_controller` as `active` (columns: name, type, state); then the test makes the robot do push-ups.
