---
id: gazebo-learn-unit5-moving
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Unit 5: plugins, laser prismatic + rotating model, launch chain, final URDF"
domain: gazebo
area: learn
distro: jazzy
tested: false
audience: students
summary: "Unit 5: JointStatePublisher and DiffDrive, bridge and teleop, prismatic laser via ros2_control, move_laser.py, lidar model spun by velocity."
tags: [course, unit 5, box_bot_physcal_control.urdf, box_bot_control_complete.urdf, box_bot_control_complete_velocity.urdf, control.launch.py, move_laser.py, velocity_controller, teleop_twist_keyboard]
see: ["[[gazebo-learn-start-here]]", "[[gazebo-learn-unit4-sim]]", "[[gazebo-joint-state-diffdrive]]", "[[gazebo-ros-gz-bridge]]", "[[gazebo-ros2-control-urdf]]", "[[gazebo-ros2-control-controllers]]", "[[gazebo-jtc-action-client]]", "[[gazebo-velocity-control]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "jazzy: DiffDrive publish_odom/publish_odom_tf/publish_wheel_tf are ignored (GZ-V03); controller YAML keys interface_name, command_interfaces under the velocity controller are ignored (GZ-V06, GZ-V07)"
  - "humble: with gz_ros2_control on Humble add <robot_param_node>robot_state_publisher_node</robot_param_node> (GZ-V29)"
---
# Unit 5: plugins, laser prismatic + rotating model, launch chain, final URDF

**TL;DR** Three steps on top of `box_bot_physical_properties.urdf` (unit 4): drive the base with Gazebo systems, move a lidar mount with ros2_control by position, then spin the lidar model by velocity. Each step copies the previous URDF and launch files under a new name; only the new parts are listed here.

## 1. Drive the base (5.3–5.4)
- New files: `my_box_bot_description/urdf/box_bot_physcal_control.urdf` (the course's file name), `my_box_bot_description/launch/urdf_visualize_control.launch.py`, `my_box_bot_gazebo/launch/spawn_robot_ros2_control.launch.xml` (the two-include pattern of [[gazebo-spawn-urdf]]).
- URDF: add the JointStatePublisher and DiffDrive blocks before `</robot>` ([[gazebo-joint-state-diffdrive]]).
- First run: Gazebo shows the robot, teleop does nothing. Add the bridge node with `/clock`, `/cmd_vel`, `/tf`, `/odom`, `/joint_states` to `spawn_robot_description.launch.py` and to its `LaunchDescription` ([[gazebo-ros-gz-bridge]]).
```bash
ros2 launch my_box_bot_gazebo start_world.launch.py                     # terminal 1
ros2 launch my_box_bot_gazebo spawn_robot_ros2_control.launch.xml       # terminal 2
ros2 run teleop_twist_keyboard teleop_twist_keyboard                     # terminal 3
```
RViz2: Fixed Frame `odom`; all TFs and joint states arrive.

## 2. Laser up and down by position (5.6–5.7)
- New files: `my_box_bot_gazebo/launch/control.launch.py`, `my_box_bot_gazebo/launch/spawn_robot_ros2_control_complete.launch.xml`, `my_box_bot_description/config/controller_position.yaml`, `my_box_bot_description/launch/urdf_visualize_control_complete.launch.py`, `my_box_bot_description/urdf/box_bot_control_complete.urdf` (copy of the step-1 URDF).
- URDF: add before `</robot>` the laser links below, then the `<ros2_control>` block and the `gz_ros2_control-system` plugin ([[gazebo-ros2-control-urdf]]). Copy your lidar mesh to `meshes/sensors/rplidar.dae`.
  ```xml
  <!-- Laser Position Control -->
  <link name="laser_scan_link">
    <visual>
      <origin rpy="0 0 0" xyz="0 0 0"/>
      <geometry><mesh filename="package://my_box_bot_description/meshes/sensors/rplidar.dae" scale="1.0 1.0 1.0"/></geometry>
    </visual>
    <collision>
      <origin rpy="0 0 0" xyz="0 0 0.0204"/>
      <geometry><box size="0.074986 0.074935 0.0408"/></geometry>   <!-- simple shape that fits the mesh -->
    </collision>
    <inertial>
      <mass value="0.01"/>
      <origin rpy="0 0 0" xyz="0 0 0.0204"/>
      <inertia ixx="6.066578520833334e-06" ixy="0" ixz="0" iyy="6.072950163333333e-06" iyz="0" izz="9.365128684166666e-06"/>
    </inertial>
  </link>
  <joint name="laser_scan_link_joint" type="prismatic">
    <origin rpy="0 0 0" xyz="0.0 0.0 0.05"/>
    <parent link="chassis"/>
    <child link="laser_scan_link"/>
    <axis xyz="0 0 1"/>
    <limit lower="-0.1" upper="0.0" effort="20.0" velocity="2.0"/>   <!-- effort/velocity found by trying -->
    <dynamics damping="0.1" friction="1.0"/>                          <!-- keeps the joint from running wild -->
  </joint>
  <link name="laser_scan_frame"></link>   <!-- where the sensor's center is -->
  <joint name="laser_scan_frame_joint" type="fixed">
    <origin rpy="0 0 0" xyz="0 0 0.03"/>
    <parent link="laser_scan_link"/>
    <child link="laser_scan_frame"/>
  </joint>
  ```
- YAML and spawners: [[gazebo-ros2-control-controllers]] (position-only file and `control.launch.py`). Add `config` to the install rule of `my_box_bot_description`: `install(DIRECTORY urdf rviz launch meshes config DESTINATION share/${PROJECT_NAME}/)`.
- Script `my_box_bot_gazebo/scripts/move_laser.py` ([[gazebo-jtc-action-client]]). `my_box_bot_gazebo/CMakeLists.txt` then reads:
```cmake
cmake_minimum_required(VERSION 3.8)
project(my_box_bot_gazebo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(my_box_bot_description REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

install(
  DIRECTORY launch worlds models
  DESTINATION share/${PROJECT_NAME}/
)
install(PROGRAMS scripts/move_laser.py DESTINATION lib/${PROJECT_NAME})

ament_package()
```
```bash
ros2 launch my_box_bot_gazebo spawn_robot_ros2_control_complete.launch.xml
ros2 run my_box_bot_gazebo move_laser.py 0.0      # up
ros2 run my_box_bot_gazebo move_laser.py -0.05    # down
```

## 3. Spin the lidar model by velocity (5.8)
- New files: `control_position_velocity.launch.py`, `spawn_robot_ros2_control_velocity.launch.xml` (gazebo package), `controller_position_velocity.yaml`, `urdf_visualize_control_velocity.launch.py`, `box_bot_control_complete_velocity.urdf` (description package).
- URDF: `laser_scan_link` becomes the small box, add `laser_scan_model_link` and its continuous joint, a second `<ros2_control>` joint with a `velocity` interface, and point `<parameters>` to `controller_position_velocity.yaml` ([[gazebo-velocity-control]]).
- Launch chain and YAML with the third spawner: [[gazebo-ros2-control-controllers]]. Send velocities with `ros2 topic pub /velocity_controller/commands …` while `move_laser.py` still works.

Final URDF of the unit = unit 4 physical file + both plugin blocks + the three laser links + `<ros2_control>` with both joints + the plugin with `controller_position_velocity.yaml`.
