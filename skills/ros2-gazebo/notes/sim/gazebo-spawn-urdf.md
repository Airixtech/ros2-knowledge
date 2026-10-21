---
id: gazebo-spawn-urdf
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Spawn a URDF with ros_gz_sim create; URDF to SDF conversion rules"
domain: gazebo
area: sim
distro: jazzy
tested: false
audience: dev
summary: "ros_gz_sim create -topic robot_description -name -allow_renaming -x -y -z -Y; spawn file; URDF to SDF: massless links, fixed-joint lumping, preserveFixedJoint."
tags: [ros_gz_sim, create, spawn, robot_description, -topic, -file, -string, -param, -allow_renaming, urdf2sdf, fixed joint lumping, preserveFixedJoint, inertial]
see: ["[[gazebo-start-sim]]", "[[gazebo-urdf-sim-tags]]", "[[gazebo-ros-gz-bridge]]", "[[urdf-description-package]]", "[[urdf-inertia]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy: create flags -world -file -param -string -topic -name -allow_renaming -x -y -z -R -P -Y (same in humble and lyrical) — https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_sim/src/create.cpp (GZ-V09, GZ-V18)"
  - "jazzy: a massless link (no <inertial>) is an urdf2sdf error unless its fixed parent joint is lumped; fixed joints are lumped unless <preserveFixedJoint> — https://github.com/gazebosim/sdformat/blob/sdf14/src/parser_urdf.cc (GZ-V19, GZ-V46)"
  - "jazzy: the Gazebo Classic spawner spawn_entity.py does not apply to Gazebo Sim (GZ-V09)"
---
# Spawn a URDF with ros_gz_sim create; URDF to SDF conversion rules

**TL;DR** robot_state_publisher publishes the URDF on `/robot_description`; the `ros_gz_sim create` node reads it (`-topic robot_description`), and Gazebo converts it to SDF and inserts it into the running world. Movable joints have no TF until something publishes joint states ([[gazebo-joint-state-diffdrive]]).

## spawn_robot_description.launch.py
```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, SetParameter


# ROS2 Launch System will look for this function definition #
def generate_launch_description():
    # Spawn the Robot #
    declare_spawn_model_name = DeclareLaunchArgument("model_name", default_value="my_robot", description="Model Spawn Name")
    declare_spawn_x = DeclareLaunchArgument("x", default_value="0.0", description="Model Spawn X Axis Value")
    declare_spawn_y = DeclareLaunchArgument("y", default_value="0.0", description="Model Spawn Y Axis Value")
    declare_spawn_z = DeclareLaunchArgument("z", default_value="0.2", description="Model Spawn Z Axis Value")
    declare_spawn_yaw = DeclareLaunchArgument("yaw", default_value="3.14", description="Model Spawn Yaw Value")
    gz_spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        name="my_robot_spawn",
        arguments=[
            "-name", LaunchConfiguration("model_name"),
            "-allow_renaming", "true",
            "-topic", "robot_description",
            "-x", LaunchConfiguration("x"),
            "-y", LaunchConfiguration("y"),
            "-z", LaunchConfiguration("z"),
            "-Y", LaunchConfiguration("yaw"),
        ],
        output="screen",
    )

    # Create and Return the Launch Description Object #
    return LaunchDescription([
        # Sets use_sim_time for all nodes started below (Gazebo itself is not a ROS node) #
        SetParameter(name="use_sim_time", value=True),
        declare_spawn_model_name,
        declare_spawn_x,
        declare_spawn_y,
        declare_spawn_z,
        declare_spawn_yaw,
        gz_spawn_entity,
    ])
```
A launch XML puts the pieces together (Gazebo already running from [[gazebo-start-sim]]):
```xml
<?xml version='1.0' ?>
<launch>
  <!-- Publish URDF file in robot_description topic -->
  <include file="$(find-pkg-share my_box_bot_description)/launch/urdf_visualize_meshes_collisions_inertias.launch.py"/>
  <!-- Read robot_description and spawn in gazebo running sim -->
  <include file="$(find-pkg-share my_box_bot_gazebo)/launch/spawn_robot_description.launch.py"/>
</launch>
```
The first include is the RViz launch file of [[urdf-description-package]] with the simulation URDF.

## create flags
| Flag | Meaning |
|---|---|
| `-topic` / `-file` / `-string` / `-param` | where the XML comes from (a `std_msgs/String` topic, a file, a string, a ROS parameter) |
| `-name` | model name in Gazebo; `-allow_renaming` renames it if the name is taken |
| `-x -y -z` (m), `-R -P -Y` (rad) | initial pose; spawn above the ground (`-z 0.2`) so it does not start inside it |
| `-world` | target world; empty = the first world the running server reports |

## URDF → SDF rules
- Links joined by **fixed** joints are merged into their parent link (lumping), with mass and inertia combined; an empty frame link (`laser_scan_frame`) is fine there. Keep one as a separate link with `<gazebo reference="joint_name"><preserveFixedJoint>true</preserveFixedJoint></gazebo>`.
- A link on a **movable** joint needs `<inertial>` with mass > 0, else "urdf2sdf: link[…] has no <inertial> block defined" and its joint is dropped.
- URDF material colors become SDF visual colors unless a `<gazebo reference>` block sets them ([[gazebo-urdf-sim-tags]]).
- Meshes must be on `GZ_SIM_RESOURCE_PATH` ([[gazebo-start-sim]]).

## Pitfalls
- RViz shows no TF for the wheels after spawning → expected: no joint states yet (no GUI in simulation; the simulator publishes them once a plugin is added).
- `create` repeats "Requesting list of world names." → Gazebo is not running. It prints "Waiting messages on topic [robot_description]." → nothing publishes the description (it subscribes Transient Local), or it is under a namespace: `-topic robot1/robot_description`.
- Robot spawned inside the floor or flipped → adjust `-z` and the yaw.
