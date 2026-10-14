---
id: nav2-plugin-test-launch
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Path planning launch and setup.py used to test custom Nav2 plugins"
domain: nav2
area: plugins
distro: humble
tested: false
audience: dev
summary: "Launch file to test a custom plugin (map server, AMCL, servers, bt_navigator, RViz, lifecycle) and setup.py for each config folder."
tags: [pathplanner_custom_costmap_plugin.launch.py, path planning launch, plugin test launch, setup.py, data_files, default_nav_to_pose_bt_xml, behavior_server, lifecycle_manager, neobotix_area.yaml]
see: ["[[nav2-costmap-plugin-config]]", "[[nav2-planner-plugin-config]]", "[[nav2-controller-plugin-config]]", "[[nav2-path-planning-launch]]", "[[nav2-bt-navigator]]"]
requires: [ros2-core]
version_notes:
  - "humble: the course passes the BT as default_bt_xml_filename, a Foxy name Humble ignores; use default_nav_to_pose_bt_xml — https://github.com/ros-navigation/navigation2/blob/humble/nav2_bt_navigator/src/navigators/navigate_to_pose.cpp (NAV2-V51)"
---
# Path planning launch and setup.py used to test custom Nav2 plugins

**TL;DR** Each plugin example of the course gets its own launch file, a copy of this one (written for the costmap plugin, Example 3.1) where only the YAML paths change, and one more `data_files` line in `setup.py`. The planner and controller examples change `planner_yaml` or `controller_yaml` ([[nav2-planner-plugin-config]], [[nav2-controller-plugin-config]]).

## launch/pathplanner_custom_costmap_plugin.launch.py
```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # Custom Plugin
    controller_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'custom_costmap', 'controller.yaml')
    default_bt_xml_path = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'low_battery.xml')
    # Custom Plugin
    planner_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'custom_costmap', 'planner_server.yaml')
    recovery_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'recovery.yaml')
    bt_navigator_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'bt_navigator.yaml')
    nav2_yaml = os.path.join(get_package_share_directory('localization_server'), 'config', 'amcl_config.yaml')
    map_file = os.path.join(get_package_share_directory('map_server'), 'maps', 'neobotix_area.yaml')
    rviz_config_file_path = os.path.join(get_package_share_directory('path_planner_server'), 'rviz_config', 'nav2.rviz')

    return LaunchDescription([
        Node(package='nav2_map_server', executable='map_server', name='map_server', output='screen',
             parameters=[{'use_sim_time': True}, {'yaml_filename': map_file}]),
        Node(package='nav2_amcl', executable='amcl', name='amcl', output='screen', parameters=[nav2_yaml]),
        Node(package='nav2_controller', executable='controller_server', name='controller_server',
             output='screen', parameters=[controller_yaml]),
        Node(package='nav2_planner', executable='planner_server', name='planner_server',
             output='screen', parameters=[planner_yaml]),
        Node(package='nav2_behaviors', executable='behavior_server', name='behavior_server',
             output='screen', parameters=[recovery_yaml]),
        Node(package='nav2_bt_navigator', executable='bt_navigator', name='bt_navigator', output='screen',
             parameters=[bt_navigator_yaml, {'default_nav_to_pose_bt_xml': default_bt_xml_path}]),  # course: default_bt_xml_filename
        Node(package='rviz2', executable='rviz2', output='screen', name='rviz2_node',
             parameters=[{'use_sim_time': True}], arguments=['-d', rviz_config_file_path]),
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager', name='lifecycle_manager',
             output='screen',
             parameters=[{'use_sim_time': True}, {'autostart': True},
                         {'node_names': ['map_server', 'amcl', 'controller_server', 'planner_server',
                                         'behavior_server', 'bt_navigator']}])
    ])
```
Only `controller_yaml` and `planner_yaml` change with respect to the normal launch. `low_battery.xml` is the tree of [[nav2-bt-battery-abort]]; with the course's `default_bt_xml_filename` it is never loaded (NAV2-V51).

## setup.py
To find the new **config/custom_costmap** folder and its files, add it to `setup.py`:
```python
from setuptools import setup
import os
from glob import glob

package_name = 'path_planner_server'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'rviz_config'), glob('rviz_config/*')),
        (os.path.join('share', package_name, 'config/custom_costmap'), glob('config/custom_costmap/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='you@example.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [],
    },
)
```
The line `(os.path.join('share', package_name, 'config/custom_costmap'), glob('config/custom_costmap/*.yaml')),` installs the folder and its files.
