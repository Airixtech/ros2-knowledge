---
id: gazebo-multi-robot
type: reference
owner: equipo-ros2
updated: 2026-10-21
review_by: 2027-04-19
source: manual
confidentiality: internal
title: "Several robots in one world: per-robot spawn, plugin topics/frames via xacro, bridge"
domain: gazebo
area: plugins
distro: jazzy
tested: false
audience: dev
summary: "Two robots in Gazebo: namespaced robot_state_publisher with frame_prefix, xacro robot_name for plugin topics, create per robot, per-robot bridge."
tags: [multi-robot, namespace, frame_prefix, robot_name, xacro arg, ros_gz_sim create, robot_description, bridge, cmd_vel, odom, joint_states, teleop remap, rqt_tf_tree]
see: ["[[core-multi-robot-namespacing]]", "[[gazebo-joint-state-diffdrive]]", "[[gazebo-ros-gz-bridge]]", "[[gazebo-spawn-urdf]]", "[[urdf-xacro-macros]]", "[[gazebo-learn-unit7-xacro]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy/harmonic: two create nodes named my_robot_spawn in the same namespace are duplicate node names; give each its own name (GZ-V42)"
  - "humble/fortress: $(arg robot_name) without <xacro:arg> fails when the arg is not passed (URDF-V11)"
  - "jazzy/harmonic: per-robot topics and frames through a xacro parameter, RSP frame_prefix, one bridge (GZ-V43) — https://github.com/ros/robot_state_publisher/blob/jazzy/src/robot_state_publisher.cpp"
---
# Several robots in one world: per-robot spawn, plugin topics/frames via xacro, bridge

**TL;DR** Spawning the same model twice is not enough: both robots would use the same command topic, sensor topics, TF frames and node names. Give each robot a name and use it everywhere: robot_state_publisher namespace and `frame_prefix`, the Gazebo plugin topics and odometry frames (a xacro parameter), the spawn topic, and the bridge.

## Plugin topics and frames from a xacro parameter
In `box_bot.gazebo.xacro` the macro gets a parameter and uses it in the plugins:
```xml
<xacro:macro name="gazebo_elements" params="robot_name">
  …
  <topic>${robot_name}/joint_states</topic>                 <!-- JointStatePublisher -->
  …
  <topic>${robot_name}/cmd_vel</topic>                      <!-- DiffDrive -->
  <odom_topic>${robot_name}/odom</odom_topic>
  <tf_topic>tf</tf_topic>
  <frame_id>${robot_name}/odom</frame_id>
  <child_frame_id>${robot_name}/base_link</child_frame_id>
</xacro:macro>
```
In the main `box_bot.xacro`, right below `<robot …>`, and at the call:
```xml
<xacro:arg name="robot_name" default="robot1"/>   <!-- the course omits this declaration -->
<xacro:property name="robot_name" value="$(arg robot_name)"/>
…
<xacro:gazebo_elements robot_name="$(arg robot_name)"/>
```

## box_bot_spawn_two_robots.launch.py (part after starting Gazebo)
Gazebo start, resource path and imports as in [[gazebo-start-sim]] (plus `from launch.substitutions import Command`):
```python
    # Define the robot model files to be used
    robot_desc_file = "box_bot.xacro"
    robot_desc_path = os.path.join(pkg_box_bot_description, "urdf", robot_desc_file)

    robot_name_1 = "robot1"
    robot_name_2 = "robot2"

    # Load Robot State Publisher 1
    rsp_robot1 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        namespace=robot_name_1,
        parameters=[{'frame_prefix': robot_name_1 + '/',
                     'robot_description': Command(['xacro ', robot_desc_path, ' robot_name:=', robot_name_1])}],
        output="screen")
    # Load Robot State Publisher 2: the same with robot_name_2

    # Spawn Robot 1
    spawn_robot1 = Node(
        package="ros_gz_sim",
        executable="create",
        name="my_robot_spawn",
        arguments=["-name", robot_name_1, "-allow_renaming", "true",
                   "-topic", robot_name_1 + "/robot_description",
                   "-x", "0.0", "-y", "-0.5", "-z", "0.2", "-Y", "3.14"],
        output="screen",
    )
    # Spawn Robot 2: the same with robot_name_2 at "-y", "0.5"

    # ROS-Gazebo Bridge
    gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="gz_bridge",
        arguments=[
            "/clock" + "@rosgraph_msgs/msg/Clock" + "[gz.msgs.Clock",
            "/tf" + "@tf2_msgs/msg/TFMessage" + "[gz.msgs.Pose_V",
            "/robot1/cmd_vel" + "@geometry_msgs/msg/Twist" + "@gz.msgs.Twist",
            "/robot2/cmd_vel" + "@geometry_msgs/msg/Twist" + "@gz.msgs.Twist",
            "/robot1/odom" + "@nav_msgs/msg/Odometry" + "[gz.msgs.Odometry",
            "/robot2/odom" + "@nav_msgs/msg/Odometry" + "[gz.msgs.Odometry",
            "/robot1/joint_states" + "@sensor_msgs/msg/JointState" + "[gz.msgs.Model",
            "/robot2/joint_states" + "@sensor_msgs/msg/JointState" + "[gz.msgs.Model",
        ],
        remappings=[
            # there are no remappings for this robot description
        ],
        output="screen",
    )

    # Create and Return the Launch Description Object #
    return LaunchDescription([
        # Sets use_sim_time for all nodes started below (Gazebo itself is not a ROS node) #
        SetParameter(name="use_sim_time", value=True),
        gz_sim, rsp_robot1, rsp_robot2, spawn_robot1, spawn_robot2, gz_bridge,
    ])
```
- `Command(['xacro ', path, ' robot_name:=', name])` expands the same file per robot, and also accepts a plain `.urdf` path.
- Both robots publish TF on the shared `/tf` with prefixed frames (`robot1/odom → robot1/base_link → robot1/chassis → …`, the same for `robot2/`): option (b) of [[core-multi-robot-namespacing]].

## Check and drive
```bash
ros2 topic list            # /robot1/cmd_vel, /robot1/joint_states, /robot1/odom, /robot1/robot_description, same for robot2
ros2 run rqt_tf_tree rqt_tf_tree    # two trees: robot1/odom …, robot2/odom …
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/robot1/cmd_vel
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/robot2/cmd_vel
```

## Pitfalls
- Both spawn nodes are named `my_robot_spawn` in the same namespace: give them different names (`robot1_spawn`, `robot2_spawn`) to avoid duplicate node names.
- After adding `$(arg robot_name)`, the single-robot launch must pass `robot_name` too (or the arg needs a default); with a default the single robot's topics become `<default>/cmd_vel`, so update its bridge.
- `frame_prefix` without the trailing `/` → frames like `robot1base_link`.
