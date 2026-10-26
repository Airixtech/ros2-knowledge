---
id: core-launch-xml-yaml
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "XML and YAML launch files (same launch as Python)"
domain: core
area: build-run
distro: humble
tested: false
audience: dev
summary: "ROS 2 XML and YAML launch syntax: arg, $(var), $(find-pkg-share), include with args, group with push-ros-namespace, node params."
tags: [launch xml, launch yaml, $(var), $(find-pkg-share), push-ros-namespace, include, group, param, launch.xml, launch.yaml]
see: ["[[core-launch-substitutions]]", "[[core-launch-args-include]]", "[[core-learn-inter-unit4-launch-formats]]", "[[core-param-yaml-cli]]"]
requires: []
version_notes:
  - "all: push-ros-namespace and push_ros_namespace are both accepted (Humble to Lyrical) — https://github.com/ros2/launch_ros/blob/humble/launch_ros/launch_ros/actions/push_ros_namespace.py (V15)"
---
# XML and YAML launch files (same launch as Python)

**TL;DR** XML and YAML launch files do what [[core-launch-substitutions]] does in Python, with `$(var name)` for arguments and `$(find-pkg-share pkg)` for paths. Formats mix freely: XML or YAML can include a Python launch file. They pass `param` to nodes, not command-line arguments, so the node must declare those parameters (`move_robot_with_params.py` in [[core-learn-inter-unit4-launch-formats]]). Install them with `glob('launch/*')` in `setup.py`.

## XML: main launch
```xml
<launch>
  <arg name="turning_speed" default="0.2"/>
  <arg name="forward_speed" default="0.1"/>
  <arg name="rviz_config_file_name" default="launch_part.rviz"/>
  <arg name="custom_namespace" default="gypsi_danger"/>

  <include file="$(find-pkg-share launch_tests_pkg)/launch/start_rviz_with_arguments.launch.py">
    <arg name="rviz_config_file_name" value="$(var rviz_config_file_name)"/>
  </include>

  <group>
    <push-ros-namespace namespace="$(var custom_namespace)"/>
    <include file="$(find-pkg-share launch_tests_pkg)/launch/move_with_arguments.launch.xml">
      <arg name="turning_speed" value="$(var turning_speed)"/>
      <arg name="forward_speed" value="$(var forward_speed)"/>
    </include>
  </group>
</launch>
```

## XML: node with parameters (`move_with_arguments.launch.xml`)
```xml
<launch>
  <arg name="turning_speed" default="6.0"/>
  <arg name="forward_speed" default="0.1"/>
  <node pkg="launch_tests_pkg" exec="move_robot_with_params_exe" name="move_robot_node">
    <param name="turning_speed" value="$(var turning_speed)"/>
    <param name="forward_speed" value="$(var forward_speed)"/>
  </node>
</launch>
```
The syntax resembles ROS 1 XML; the difference is that arguments are read with `$(var argument_name)`. Porting ROS 1 files: [launch files migration guide](https://docs.ros.org/en/humble/How-To-Guides/Launch-files-migration-guide.html).

## YAML: main launch
```yaml
launch:

# args that can be set from the command line or a default will be used
- arg:
    name: "turning_speed"
    default: "0.0"
- arg:
    name: "forward_speed"
    default: "0.0"
- arg:
    name: "rviz_config_file_name"
    default: "launch_part.rviz"
- arg:
    name: "custom_namespace"
    default: "crimson_typhoon"

- include:
    file: "$(find-pkg-share launch_tests_pkg)/launch/start_rviz_with_arguments.launch.py"
    arg:
      - name: "rviz_config_file_name"
        value: "$(var rviz_config_file_name)"

- group:
    - push-ros-namespace:
        namespace: "$(var custom_namespace)"
    - include:
        file: "$(find-pkg-share launch_tests_pkg)/launch/move_with_arguments.launch.yaml"
        arg:
          - name: "turning_speed"
            value: "$(var turning_speed)"
          - name: "forward_speed"
            value: "$(var forward_speed)"
```

## YAML: node with parameters (`move_with_arguments.launch.yaml`)
```yaml
launch:

# args that can be set from the command line or a default will be used
- arg:
    name: "turning_speed"
    default: "0.0"
- arg:
    name: "forward_speed"
    default: "0.0"

- node:
    pkg: "launch_tests_pkg"
    exec: "move_robot_with_params_exe"
    name: "move_robot_node"
    param:
      - name: "turning_speed"
        value: "$(var turning_speed)"
      - name: "forward_speed"
        value: "$(var forward_speed)"
```
YAML uses the same substitutions as XML. A `group` holds a list of actions.

## Run
```bash
ros2 launch launch_tests_pkg xml_main.launch.xml turning_speed:=5.0 forward_speed:=0.0
ros2 launch launch_tests_pkg yaml_main.launch.yaml turning_speed:=1.0 forward_speed:=1.0 rviz_config_file_name:=launch_part_2.rviz
```

## Pitfalls
- `exec` (not `executable`) and `pkg` (not `package`) are the XML/YAML attribute names.
- A launch file that is not in `data_files` is not installed: `glob('launch/*.launch.py')` skips `.xml` and `.yaml` files.
- Without a matching `declare_parameter()` in the node, the `param` values are ignored.
- XML and YAML can log: `LogInfo` is exposed as `<log message="turning_speed: $(var turning_speed)"/>` and `- log: {message: "…"}` (the C++ course says XML cannot, CPP-V53). `emulate_tty="true"` is a valid `<node>` attribute too.
