---
id: moveit-cpp-package-setup
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "moveit2_scripts package: dependencies, launch file with MoveItConfigsBuilder, CMakeLists entries, build and run order"
domain: moveit
area: planning
distro: humble
tested: false
audience: dev
summary: "ros2 pkg create moveit2_scripts with MoveIt dependencies; launch passing robot_description, semantic, kinematics, use_sim_time; CMake add_executable, install; run order."
tags: [moveit2_scripts, ros2 pkg create, moveit_ros_planning_interface, moveit_core, MoveItConfigsBuilder, robot_description, robot_description_semantic, robot_description_kinematics, use_sim_time, add_executable, ament_target_dependencies, target_link_libraries, install, launch file, colcon build]
see: ["[[moveit-cpp-move-group-interface]]", "[[moveit-cpp-joint-space-goal]]", "[[moveit-move-group-launch-sim]]", "[[cpp-pkg-cmake]]", "[[cpp-launch-cpp-nodes]]"]
requires: [ros2-core, ros2-cpp]
version_notes:
  - "lyrical: ament_target_dependencies removed (deprecated in Kilted); link moveit_ros_planning_interface::moveit_move_group_interface and ::moveit_planning_scene_interface, valid on Humble too (ament_export_targets defaults to ${PROJECT_NAME}::) — https://github.com/ament/ament_cmake/blob/humble/ament_cmake_export_targets/cmake/ament_export_targets.cmake (MOVEIT-V17)"
  - "humble: the MoveGroupInterface constructor throws 'Unable to construct robot model…' without the description parameters and waits for the move_group action servers (wait_for_servers default -1 = no timeout) — https://github.com/moveit/moveit2/blob/humble/moveit_ros/planning_interface/move_group_interface/src/move_group_interface.cpp (MOVEIT-V48)"
  - "humble: Node(name=…) adds -r __node:=<name>, which renames every node of the process (both nodes of these programs) [verify]; dict parameters go to /** — https://github.com/ros2/launch_ros/blob/humble/launch_ros/launch_ros/actions/node.py (MOVEIT-V18)"
---
# The `moveit2_scripts` package

**TL;DR** One ament_cmake package holds all the course's C++ programs. Each program gets a launch file that loads the MoveIt configuration with `MoveItConfigsBuilder` and passes the robot description, the SRDF and the kinematics (plus `use_sim_time`) to the program, and a CMake entry. Run order: `move_group` → (RViz2) → the program.

## Create the package
```bash
cd ~/ros2_ws/src
ros2 pkg create moveit2_scripts --dependencies rclcpp rclcpp_action moveit_core moveit_ros_planning moveit_ros_planning_interface interactive_markers geometric_shapes control_msgs moveit_msgs
cd ~/ros2_ws/src/moveit2_scripts/src
touch joint_space_trajectory.cpp
cd ~/ros2_ws/src/moveit2_scripts
mkdir launch
touch launch/joint_space_trajectory.launch.py
```

## Launch file (one per program)
`launch/joint_space_trajectory.launch.py`:
```python
from launch import LaunchDescription
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("name", package_name="my_moveit_config").to_moveit_configs()

    # MoveItCpp demo executable
    moveit_cpp_node = Node(
        name="joint_space_trajectory",
        package="moveit2_scripts",
        executable="joint_space_trajectory",
        output="screen",
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            {'use_sim_time': True},
        ],
    )

    return LaunchDescription([moveit_cpp_node])
```
(The course's files also import `os`, `ExecuteProcess` and `get_package_share_directory`, unused.) The program needs the robot description, the semantic description and the kinematics; `use_sim_time` because the robot is simulated ([[moveit-move-group-launch-sim]]). For another program, copy the file (`cp launch/joint_space_trajectory.launch.py launch/goal_pose_trajectory.launch.py`) and change `name` and `executable`. The dict parameters are written for `/**`, so the program's second node (`move_group_node`) receives them too; `name=` renames every node of the process, so both nodes are called `joint_space_trajectory` (MOVEIT-V18 [verify]); leaving `name` out keeps their own names.

## CMakeLists.txt entries
```cmake
# Generate the executable
add_executable(joint_space_trajectory
  src/joint_space_trajectory.cpp)
target_include_directories(joint_space_trajectory
  PUBLIC include)
ament_target_dependencies(joint_space_trajectory
  ament_cmake
  rclcpp
  rclcpp_action
  moveit_core
  moveit_ros_planning_interface
  interactive_markers
  moveit_ros_planning
  control_msgs)

# Install the executable
install(TARGETS
  joint_space_trajectory
  DESTINATION lib/${PROJECT_NAME})

# Install the launch file
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME})
```
Every later program repeats the `add_executable` / `target_include_directories` / `ament_target_dependencies` block with its name and is added to the one `install(TARGETS …)`, e.g.:
```cmake
install(TARGETS
  joint_space_trajectory
  goal_pose_trajectory
  DESTINATION lib/${PROJECT_NAME})
```
(The course repeats `install(TARGETS …)` and `install(DIRECTORY launch …)` per program; once is enough.) [changed in Lyrical: `ament_target_dependencies` is removed (deprecated in Kilted); use `target_link_libraries(joint_space_trajectory moveit_ros_planning_interface::moveit_move_group_interface moveit_ros_planning_interface::moveit_planning_scene_interface rclcpp::rclcpp)`, which works on Humble too] (MOVEIT-V17 [verify] the exact list; general rule: [[cpp-pkg-cmake]]).

| Program | Exercise | Note |
|---|---|---|
| `joint_space_trajectory` | 3.1, 3.3 | [[moveit-cpp-joint-space-goal]] |
| `goal_pose_trajectory` | 3.2 | [[moveit-cpp-pose-goal]] |
| `double_motion_trajectory` | 3.4 | [[moveit-learn-unit2-3]] |
| `gripper_control` | 3.5 | [[moveit-cpp-gripper]] |
| `approach_retreat_trajectory` | 3.6 | [[moveit-approach-retreat]] |
| `cartesian_trajectory` | 4.1 | [[moveit-cpp-cartesian-path]] |
| `draw_x_cartesian_trajectory` | 4.2 | [[moveit-learn-unit4]] |
| `kinematics_plugin_trajectory` | 4.3 | [[moveit-kinematics-plugins]] |
| `pick_and_place_trajectory` | 4.4 | [[moveit-pick-and-place]] |

## Build and run
```bash
cd ~/ros2_ws
colcon build --packages-select moveit2_scripts
source install/setup.bash
```
Before any program: `move_group` (and optionally RViz2 for watching) must run, each in its own terminal:
```bash
ros2 launch my_moveit_config move_group.launch.py
ros2 launch my_moveit_config moveit_rviz.launch.py
ros2 launch moveit2_scripts joint_space_trajectory.launch.py
```

## Pitfalls
- Started without `move_group`: the `MoveGroupInterface` constructor waits for the `move_group` action servers, with no timeout by default (MOVEIT-V48).
- The program's node lacks the description parameters (launch without them, or no `automatically_declare_parameters_from_overrides`) → exception `Unable to construct robot model. Please make sure all needed information is on the parameter server.` (MOVEIT-V48).
- New file in `launch/` or a new executable → rebuild before `ros2 launch` finds it (or use `--symlink-install` for the launch files).
