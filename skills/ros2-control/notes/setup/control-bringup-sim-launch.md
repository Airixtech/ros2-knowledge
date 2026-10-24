---
id: control-bringup-sim-launch
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Bringup package and Gazebo Sim launch: xacro, robot_state_publisher, ros_gz_sim create, chained spawners"
domain: control
area: setup
distro: jazzy
tested: false
audience: dev
summary: "my_robot_bringup package, launch: xacro to robot_description, robot_state_publisher, ros_gz_sim create, spawners chained with OnProcessExit, install launch/config."
tags: [bringup, my_robot_bringup, launch, xacro, robot_state_publisher, robot_description, ros_gz_sim, create, spawner, OnProcessExit, RegisterEventHandler, joint_state_broadcaster, forward_position_controller, install DIRECTORY]
see: ["[[control-controller-config]]", "[[control-urdf-tag]]", "[[control-services-spawner]]", "[[control-bringup-hardware-launch]]", "[[control-learn-unit2-setup]]", "[[core-robot-state-publisher]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: joint_state_broadcaster publishes /joint_states and /dynamic_joint_states (the course says /rrbot_controller/state) — https://github.com/ros-controls/ros2_controllers/blob/jazzy/joint_state_broadcaster/src/joint_state_broadcaster.cpp (CONTROL-V03)"
  - "jazzy/harmonic: -allow_renaming is a gflags bool: the flag alone enables renaming [verify] — https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_sim/src/create.cpp (CONTROL-V32)"
  - "humble/fortress: same launch; gz_ros2_control reads robot_description from the node robot_state_publisher, the default name used here — ros2-gazebo skill (GZ-V29)"
  - "jazzy: the explained snippet names the node robot_state_pub_node with output both; the launch code wins (CONTROL-V44)"
---
# Bringup package and Gazebo Sim launch: xacro, robot_state_publisher, ros_gz_sim create, chained spawners

**TL;DR** Keep ros2_control configuration and launch files in their own package (modular, fewer dependencies per package). The launch file publishes the description, spawns the robot (whose `<gazebo>` plugin starts the controller manager) and then spawns the controllers in order with `OnProcessExit`.

## Package
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type=ament_cmake my_robot_bringup --dependencies urdf xacro robot_state_publisher
cd my_robot_bringup && mkdir config launch   # config/controller_configuration.yaml, launch/my_robot.launch.py
```
At the end of `CMakeLists.txt`, so that `colcon build` copies (or links) both folders to the share directory, where `ros2 launch` looks:
```cmake
install(
  DIRECTORY
    launch
    config
  DESTINATION
    share/${PROJECT_NAME}/
)
```

## launch/my_robot.launch.py
```python
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    rrbot_description_path = os.path.join(get_package_share_directory('rrbot_unit2'))

    xacro_file = os.path.join(rrbot_description_path, 'urdf', 'rrbot.xacro')
    doc = xacro.parse(open(xacro_file))
    xacro.process_doc(doc)
    robot_description_config = doc.toxml()
    robot_description = {'robot_description': robot_description_config}

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    gz_spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        name="my_robot_spawn",
        arguments=[
            "-name", "robot",
            "-allow_renaming", "true",
            "-topic", "robot_description",
            "-x", "0.0",
            "-y", "0.0",
            "-z", "0.0",
            "-Y", "0.0",
        ],
        output="screen",
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    robot_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["forward_position_controller", "-c", "/controller_manager"],
    )

    return LaunchDescription([
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=gz_spawn_entity,
                on_exit=[joint_state_broadcaster_spawner],
            )
        ),
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[robot_controller_spawner],
            )
        ),
        gz_spawn_entity,
        node_robot_state_publisher,
    ])
```
The course's file also imports `ExecuteProcess`, `IncludeLaunchDescription` and `PythonLaunchDescriptionSource`, which it never uses (left out). Gazebo Sim with a world must already be running (ros2-gazebo skill, `gazebo-start-sim`).

## What each part does
- `xacro.parse` + `process_doc` expands the xacro in the launch file; `robot_state_publisher` publishes it on `/robot_description` and turns `/joint_states` into `/tf` and `/tf_static` ([[core-robot-state-publisher]]).
- `ros_gz_sim create -topic robot_description` spawns that description; its `gz_ros2_control-system` plugin starts the controller manager inside Gazebo ([[control-urdf-tag]]).
- `spawner` (package `controller_manager`) loads, configures and activates one controller ([[control-services-spawner]]); `--controller-manager` and `-c` are the same option.
- The two `OnProcessExit` handlers start the broadcaster spawner when `create` exits (the robot and its controller manager exist) and the controller spawner when the broadcaster spawner exits.
- `joint_state_broadcaster` publishes `sensor_msgs/JointState` on `/joint_states` (and `control_msgs/DynamicJointState` on `/dynamic_joint_states`).

## Build and test
```bash
cd ~/ros2_ws && colcon build && source install/setup.bash
ros2 launch my_robot_bringup my_robot.launch.py
ros2 topic list    # /forward_position_controller/commands
ros2 topic pub /forward_position_controller/commands std_msgs/msg/Float64MultiArray "data:
- 1.57
- -1.57" -1
```
One value per joint, in the order of `joints` in the YAML, in radians for these rotary joints; `-1` publishes once.

## Pitfalls
- Remove the old robot from Gazebo before launching again: with `-allow_renaming` a second robot is spawned under another name and the old one stays.
- Spawner: "Could not contact service /controller_manager/…" → the robot was not spawned or its plugin failed (Gazebo log).
- Only `joint1` in the YAML and `<ros2_control>` → the second segment is not held and swings down (the course's starting point).
