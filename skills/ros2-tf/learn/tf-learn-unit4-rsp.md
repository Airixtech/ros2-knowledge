---
id: tf-learn-unit4-rsp
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "TF unit 4: spawn the unicycle with and without robot_state_publisher"
domain: tf
area: learn
distro: jazzy
tested: false
audience: students
summary: "TF unit 4: example 4.1.1 spawns from -file without robot_state_publisher; 4.2.1 spawn.launch.py with it, remapped description, two /tf publishers."
tags: [unit 4, example 4.1.1, example 4.2.1, robot_state_publisher, joint_state_publisher, unicycle, unicycle_robot_pkg, spawn.launch.py, spawn_without_robot_state_publisher.launch.py, ros_gz_sim create, ros_gz_bridge, /unicycle_bot_robot_description, ros2 topic info -v, ros2 node info]
see: ["[[tf-learn-start-here]]", "[[core-robot-state-publisher]]", "[[urdf-frames-rviz]]", "[[tf-rviz]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy: ros_gz_sim create -file takes a file path (Load XML from a file); -string takes the XML text — https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_sim/src/create.cpp (TF-V07, TF-V25)"
  - "course: RViz is told to read /unicycle_robot_description, the launch remaps to /unicycle_bot_robot_description (TF-V08); its explained snippet names the path urdf instead of urdf_path (TF-V17)"
  - "jazzy: the joint_state_publisher node publishes default positions, not simulated ones; with Gazebo use the JointStatePublisher system + bridge (TF-V15, GZ-V04)"
  - "humble: the topic info and node info outputs have no 'Topic type hash' lines and no get_type_description service (TF-V28) — https://github.com/ros2/rclpy/blob/humble/rclpy/rclpy/topic_endpoint_info.py"
---
# TF unit 4: robot_state_publisher

**TL;DR** Spawn the same robot twice in an empty sand world: first straight from its URDF file (only the DiffDrive system's `odom → unicycle_base_link` reaches TF, and there is no `/robot_description`), then with robot_state_publisher, which publishes the description and the transforms of every link. Conclusion of the unit: you need the Robot State Publisher to see all the robot's body parts in RViz.

## What robot_state_publisher does (4.3)
It takes the URDF or xacro model as input, publishes it on `/robot_description` (other tools such as Gazebo or RViz read it there), and publishes the transforms between all links: **fixed** joints straight from the URDF (on `/tf_static`), **movable** joints (wheels, heads, arms, grippers) from the angles or positions on `/joint_states`. Real robots get `/joint_states` from their controllers; in Gazebo Sim the robot's JointStatePublisher system publishes them and the bridge brings them to ROS, as in this robot. The `joint_state_publisher` node is not a substitute in simulation: it publishes default positions (0 or mid-range), not the simulated ones. Without a simulator or controllers, add it to a Python launch file like this:
```python
joint_state_publisher_node = Node(
    package='joint_state_publisher',
    executable='joint_state_publisher',
    name='joint_state_publisher')
# ...
return LaunchDescription([
    # ...
    joint_state_publisher_node,
    robot_state_publisher_node,
    # ...
])
```
This robot does not need it: its model has the Gazebo JointStatePublisher system. Details: [[core-robot-state-publisher]], [[urdf-frames-rviz]].

## Example 4.1.1: without robot_state_publisher
```bash
cd ~/ros2_ws/src/my_tf_ros2_course_pkg/launch
touch spawn_without_robot_state_publisher.launch.py
touch spawn.launch.py          # example 4.2.1
```
`launch/spawn_without_robot_state_publisher.launch.py` is the file below without the `robot_state_publisher_node` and without `xacro`; it spawns from the file: `"-file", urdf_path` (a path, not the URDF text). Then RViz with Fixed Frame `odom` and a TF display shows only two frames, `odom` and `unicycle_base_link`, from the DiffDrive system; a RobotModel cannot use Topic as Description Source because no node publishes `/robot_description`. `ros2 topic info /tf --verbose` lists one publisher, `gz_bridge`. Driving works: `ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=unicycle_cmd_vel` (keep the focus on that terminal).

## Example 4.2.1: `launch/spawn.launch.py`
```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro


def generate_launch_description():

    urdf_file = 'unicycle.urdf'
    package_description = 'unicycle_robot_pkg'
    urdf_path = os.path.join(get_package_share_directory(package_description), 'urdf', urdf_file)
    robot_desc = xacro.process_file(urdf_path)
    xml = robot_desc.toxml()

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='unicycle_robot_state_publisher',
        emulate_tty=True,
        parameters=[{'use_sim_time': True, 'robot_description': xml}],
        remappings=[("/robot_description", "/unicycle_bot_robot_description")],
        output="screen"
    )

    # Spawn Robot In Gazebo
    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        name="my_robot_spawn",
        arguments=[
            "-name", "my_robot",
            "-allow_renaming", "true",
            "-topic", "/unicycle_bot_robot_description",
            "-Y", "3.14",
        ],
        output="screen",
    )

    # ROS-Gazebo Bridge
    gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="gz_bridge",
        arguments=[
            "/clock" + "@rosgraph_msgs/msg/Clock" + "[gz.msgs.Clock",
            "/unicycle_cmd_vel" + "@geometry_msgs/msg/Twist" + "@gz.msgs.Twist",
            "/tf" + "@tf2_msgs/msg/TFMessage" + "[gz.msgs.Pose_V",
            "/unicycle_odom" + "@nav_msgs/msg/Odometry" + "[gz.msgs.Odometry",
            "/joint_states" + "@sensor_msgs/msg/JointState" + "[gz.msgs.Model"
        ],
        remappings=[
            # there are no remappings for this robot description
        ],
        output="screen",
    )

    return LaunchDescription([
        robot_state_publisher_node,
        spawn_robot,
        gz_bridge,
    ])
```
The Gazebo part is the same as in 4.1.1, except that the robot is read from the topic. The description goes to `/unicycle_bot_robot_description` instead of `/robot_description`. Restart the simulation first (Ctrl+C on it and start it again) for a clean state, then build and launch.

In RViz: Fixed Frame `odom` (the dropdown now lists many more frames, published by robot_state_publisher), a RobotModel on **`/unicycle_bot_robot_description`** (the course text says `/unicycle_robot_description`, which does not exist), a TF display with Marker Scale 5. Everything moves correctly with the teleop.

## Checking who publishes
`ros2 topic info /tf --verbose` → `Publisher count: 2`: `unicycle_robot_state_publisher` and `gz_bridge` (the DiffDrive transform), each with `Topic type hash: RIHS01_…`, plus one subscription `transform_listener_impl_…` (RViz). `ros2 node info /unicycle_robot_state_publisher`:
```text
/unicycle_robot_state_publisher
  Subscribers:
    /clock: rosgraph_msgs/msg/Clock
    /joint_states: sensor_msgs/msg/JointState
    /parameter_events: rcl_interfaces/msg/ParameterEvent
  Publishers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
    /tf: tf2_msgs/msg/TFMessage
    /tf_static: tf2_msgs/msg/TFMessage
    /unicycle_bot_robot_description: std_msgs/msg/String
```
Input `joint_states`; outputs `/tf`, `/tf_static` (fixed joints) and the description topic. Its service list also has `get_type_description` (Jazzy; not in Humble).
