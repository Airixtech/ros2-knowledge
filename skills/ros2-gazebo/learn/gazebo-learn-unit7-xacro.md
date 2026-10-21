---
id: gazebo-learn-unit7-xacro
type: reference
owner: equipo-ros2
updated: 2026-10-21
review_by: 2027-04-19
source: manual
confidentiality: internal
title: "Unit 7: box_bot.xacro step by step, gazebo macro file, two robots"
domain: gazebo
area: learn
distro: jazzy
tested: false
audience: students
summary: "Unit 7: box_bot.xacro (properties, wheel macro), box_bot_xacro.launch.py with Gazebo and bridge, box_bot.gazebo.xacro macro, two robots with robot_name."
tags: [course, unit 7, xacro, box_bot.xacro, box_bot.gazebo.xacro, box_bot_xacro.launch.py, gazebo_elements, wheel macro, exercise 7.7.1, two robots]
see: ["[[gazebo-learn-start-here]]", "[[urdf-xacro-workflow]]", "[[urdf-xacro-macros]]", "[[gazebo-multi-robot]]", "[[gazebo-urdf-sim-tags]]", "[[gazebo-joint-state-diffdrive]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "humble/fortress: the macro call must match params (the course's first wheel example fails); args are read with $(arg) (URDF-V09, URDF-V10)"
  - "jazzy/harmonic: the prose names spawn_entity.py, which is not a ros_gz tool; the code uses ros_gz_sim create (GZ-V09)"
  - "humble/fortress: the stray word 'Exercise' inside the course's box_bot.xacro is an export artefact (URDF-V44)"
---
# Unit 7: box_bot.xacro step by step, gazebo macro file, two robots

**TL;DR** Rewrite box_bot as `my_box_bot_description/urdf/box_bot.xacro`: properties for sizes, a macro for the wheels, the Gazebo tags in an included macro file, and finally a `robot_name` parameter so two robots can share one world. Each step is checked in Gazebo with `box_bot_xacro.launch.py`.

## Steps (only what changes)
1. **Minimal file** (7.1.1): header with `xmlns:xacro`, empty `base_link`, fixed joint, `chassis` box. Expand it by hand with `xacro box_bot.xacro > converted_box_bot_file.urdf` (7.2.1) ([[urdf-xacro-workflow]]).
2. **Launch in Gazebo** (7.4): `my_box_bot_description/launch/box_bot_xacro.launch.py` (below; the first version has no bridge). `ros2 launch my_box_bot_description box_bot_xacro.launch.py` shows the cube.
3. **Properties** (7.4.1): `body_width`, `body_lenght`, `body_height` for the chassis box: the example of [[urdf-xacro-workflow]].
4. **Wheels and casters** (7.4.2): properties `wheel_width` (0.001) and `wheel_radius` (0.035) in the wheel cylinders; the four caster links and joints as in unit 4 (collision + inertial, no materials). Check the wheels in RViz2 with `joint_state_publisher_gui`.
5. **Wheel macro** (7.5.1): the `wheel` macro and its two calls of [[urdf-xacro-macros]]; the wheel joints stay outside the macro.
6. **Gazebo tags in their own file** (7.7.1): `box_bot.gazebo.xacro` with a macro `gazebo_elements` (below); in `box_bot.xacro` add `<xacro:include filename="$(find my_box_bot_description)/urdf/box_bot.gazebo.xacro"/>` after `<robot …>`, the chassis visual becomes the `cute_cube.dae` mesh, and `<xacro:gazebo_elements/>` goes before `</robot>`. Add the bridge to the launch file; teleop drives the robot.
7. **Two robots** (7.9): `robot_name` parameter, `box_bot_spawn_two_robots.launch.py`: [[gazebo-multi-robot]].

## box_bot.gazebo.xacro (7.7.1)
```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
  <xacro:macro name="gazebo_elements">
    <gazebo reference="left_wheel">
      <collision>
        <surface>
          <friction><ode><mu>10.0</mu><mu2>10.0</mu2></ode></friction>
          <contact><ode><kp>10000000.0</kp><kd>10000000.0</kd></ode></contact>
        </surface>
      </collision>
      <visual>
        <material>
          <!-- Red -->
          <ambient>1 0 0 1</ambient>
          <diffuse>1 0 0 1</diffuse>
          <specular>0 0 0 1</specular>
          <emissive>0 0 0 1</emissive>
        </material>
      </visual>
    </gazebo>
    <!-- right_wheel: same friction, Green 0 1 0 1 · front_pitch_link: mu/mu2 0.5, Purple 1 0 1 1 ·
         back_pitch_link: mu/mu2 0.5, Yellow 1 1 0 1 · front_yaw_link, back_yaw_link: color only, Blue 0 0 1 1 ·
         front_roll_link, back_roll_link: color only, Red 1 0 0 1 (ambient = diffuse = the color, specular and emissive 0 0 0 1) -->

    <!-- PLUGINS: the JointStatePublisher and DiffDrive blocks -->
  </xacro:macro>
</robot>
```
The two plugin blocks are those of [[gazebo-joint-state-diffdrive]]; friction values and colors: [[gazebo-urdf-sim-tags]].

## box_bot_xacro.launch.py (final, 7.8)
```python
import os
from ament_index_python.packages import get_package_prefix, get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import SetParameter, Node
import xacro


# ROS2 Launch System will look for this function definition #
def generate_launch_description():
    # Get Package Directory #
    pkg_box_bot_gazebo = get_package_share_directory('my_box_bot_gazebo')
    pkg_box_bot_description = get_package_share_directory('my_box_bot_description')
    gz_sim_pkg = get_package_share_directory("ros_gz_sim")

    # Set the Path to Robot Mesh Models for Loading in Gazebo Sim #
    # NOTE: Do this BEFORE launching Gazebo Sim #
    install_dir_path_gazebo = (get_package_prefix('my_box_bot_gazebo') + "/share")
    install_dir_path_description = (get_package_prefix('my_box_bot_description') + "/share")
    gazebo_models_path = os.path.join(pkg_box_bot_gazebo, "models")
    description_meshes_path = os.path.join(pkg_box_bot_description, "meshes")
    gazebo_resource_paths = [install_dir_path_gazebo, install_dir_path_description,
                             gazebo_models_path, description_meshes_path]
    if "GZ_SIM_RESOURCE_PATH" in os.environ:
        for resource_path in gazebo_resource_paths:
            if resource_path not in os.environ["GZ_SIM_RESOURCE_PATH"]:
                os.environ["GZ_SIM_RESOURCE_PATH"] += (':' + resource_path)
    else:
        os.environ["GZ_SIM_RESOURCE_PATH"] = (':'.join(gazebo_resource_paths))

    # Setup to launch the simulator and Gazebo world
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gz_sim_pkg, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': ['-r ',  # <-- start unpaused
                                      PathJoinSubstitution([pkg_box_bot_gazebo, 'worlds', 'box_bot_empty.world'])]}.items(),
    )

    # convert XACRO file into URDF
    xacro_file = os.path.join(pkg_box_bot_description, 'urdf', 'box_bot.xacro')
    doc = xacro.parse(open(xacro_file))
    xacro.process_doc(doc)
    params = {'robot_description': doc.toxml()}
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        output="screen",
        parameters=[params])

    # Spawn the Robot
    gz_spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        name="my_robot_spawn",
        arguments=["-name", "my_robot", "-allow_renaming", "true",
                   "-topic", "robot_description",
                   "-x", "0.0", "-y", "0.0", "-z", "0.2", "-Y", "3.14"],
        output="screen",
    )

    # ROS-Gazebo Bridge
    gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="gz_bridge",
        arguments=[
            "/clock" + "@rosgraph_msgs/msg/Clock" + "[gz.msgs.Clock",
            "/cmd_vel" + "@geometry_msgs/msg/Twist" + "@gz.msgs.Twist",
            "/tf" + "@tf2_msgs/msg/TFMessage" + "[gz.msgs.Pose_V",
            "/odom" + "@nav_msgs/msg/Odometry" + "[gz.msgs.Odometry",
            "/joint_states" + "@sensor_msgs/msg/JointState" + "[gz.msgs.Model",
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
        gz_sim,
        robot_state_publisher_node,
        gz_spawn_entity,
        gz_bridge,
    ])
```
One file starts Gazebo, publishes the expanded xacro and spawns the robot. With the `robot_name` arg of step 7, pass a value here too (`xacro.process_doc(doc, mappings={'robot_name': '…'})`) and adapt the bridged topics ([[gazebo-multi-robot]]).
