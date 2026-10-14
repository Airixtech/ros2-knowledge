---
id: nav2-multirobot-single-launch
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "One XML launch for multi-robot localization, planning and RViz"
domain: nav2
area: multi-robot
distro: humble
tested: false
audience: dev
summary: "multi_main.launch.xml includes multi_localization, multi_pathplanner and start_rviz.launch.py (rviz_config_dir, use_sim_time args); install .launch.xml files."
tags: [multi-robot, launch xml, multi_main.launch.xml, include, find-pkg-share, start_rviz.launch.py, DeclareLaunchArgument, LaunchConfiguration]
see: ["[[nav2-multirobot-planning-launch]]", "[[nav2-multirobot-localization]]", "[[core-launch-args-include]]", "[[core-launch-basics]]"]
requires: [ros2-core]
version_notes: []
---
# One XML launch for multi-robot localization, planning and RViz

**TL;DR** To start everything with one command, write an XML launch that includes the multi-robot localization, the multi-robot path planning and an RViz launch with the right config.

## path_planner_server/launch/multi_main.launch.xml
```xml
<?xml version='1.0' ?>
<launch>
  <include file="$(find-pkg-share localization_server)/launch/multi_localization.launch.py"/>
  <include file="$(find-pkg-share path_planner_server)/launch/multi_pathplanner.launch.py"/>
  <include file="$(find-pkg-share cartographer_slam)/launch/start_rviz.launch.py">
    <arg name="use_sim_time" value="true"/>
    <arg name="rviz_config_dir" value="$(find-pkg-share cartographer_slam)/rviz/tb3_1_and_2.rviz" />
  </include>
</launch>
```

## cartographer_slam/launch/start_rviz.launch.py
Starts RViz2 without terminal commands:
```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    rviz_config_dir = LaunchConfiguration("rviz_config_dir")

    return LaunchDescription([
        DeclareLaunchArgument("rviz_config_dir", default_value="", description="TRviz"),
        DeclareLaunchArgument('use_sim_time', default_value='false',
                              description='Use simulation (Gazebo) clock if true'),
        Node(package='rviz2', executable='rviz2', name='rviz2',
             arguments=['-d', rviz_config_dir],
             parameters=[{'use_sim_time': use_sim_time}],
             output='screen'),
    ])
```
Launch arguments and includes in Python and XML: [[core-launch-args-include]].

## Run
```bash
cd ~/ros2_ws
source install/setup.bash
colcon build
source install/setup.bash
ros2 launch path_planner_server multi_main.launch.xml
```
You get the same result as launching the three parts in three terminals.

## Pitfalls
- The `setup.py` glob `launch/*.launch.py` does not install `.launch.xml` files: use `glob('launch/*.launch.*')` or add the XML explicitly ([[core-pkg-ament-python]]).
- `rviz_config_dir` empty (default) → RViz opens with an empty default config.
