---
id: core-iface-package
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Custom interface package (rosidl_generate_interfaces)"
domain: core
area: core-api
distro: humble
tested: false
audience: dev
summary: "Dedicated ament_cmake package for custom msg/srv/action: example files, CMakeLists, package.xml, build, consumers, pitfalls."
tags: [rosidl_generate_interfaces, custom interfaces, member_of_group, rosidl_default_generators, msg, srv, action]
see: ["[[core-iface-syntax-usage]]", "[[core-pkg-dependencies]]", "[[core-colcon-errors]]", "[[core-action-cli-status]]"]
requires: []
version_notes: []
---
# Custom interface package (rosidl_generate_interfaces)

**TL;DR** Interfaces live in their own **ament_cmake** package, since Python packages cannot generate them. List every file in `rosidl_generate_interfaces`, add `member_of_group`, build, and source the result in EVERY terminal.

## Create
```bash
ros2 pkg create --build-type ament_cmake custom_interfaces --dependencies std_msgs geometry_msgs
mkdir -p custom_interfaces/{msg,srv,action}
```
```
# msg/RoverEvents.msg
std_msgs/String info
geometry_msgs/Pose rover_location
# srv/TextRecognition.srv
string label
---
bool success
int32 start_x
int32 start_y
int32 end_x
int32 end_y
# action/GoToPose.action
float64 x
float64 y
float64 yaw
---
bool success
---
string feedback
```

## CMakeLists.txt
```cmake
find_package(ament_cmake REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/RoverEvents.msg"
  "srv/TextRecognition.srv"
  "action/GoToPose.action"
  DEPENDENCIES std_msgs geometry_msgs        # every pkg used inside the definitions
)
ament_export_dependencies(rosidl_default_runtime)
ament_package()
```

## package.xml
```xml
<buildtool_depend>ament_cmake</buildtool_depend>
<buildtool_depend>rosidl_default_generators</buildtool_depend>
<depend>std_msgs</depend>
<depend>geometry_msgs</depend>
<depend>action_msgs</depend>                 <!-- if any .action -->
<exec_depend>rosidl_default_runtime</exec_depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```
(`<build_depend>rosidl_default_generators</build_depend>` also works.) Keep ALL interface files listed. Never remove existing ones when you add a new one.

## Build & use
```bash
colcon build --packages-select custom_interfaces && source install/setup.bash   # source in EVERY terminal
ros2 interface show custom_interfaces/msg/RoverEvents
```
Consumer package: add `<depend>custom_interfaces</depend>`, plus `find_package` in C++. Importing and filling the types: [[core-iface-syntax-usage]].

## Pitfalls
- Server and client must import the type from the SAME package. Identical definitions in different packages are different types, and they will not connect.
- `ModuleNotFoundError` or an unknown type in `ros2 topic echo` → the terminal was not sourced after building the interface package.
- Changing a published `.msg` is a breaking API change (MAJOR version, [[core-testing-ci-docker]]).
