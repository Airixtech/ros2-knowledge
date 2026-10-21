---
id: urdf-learn-unit8-quadruped
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Unit 8: quadruped exported from Onshape, launch and RViz"
domain: urdf
area: learn
distro: humble
tested: false
audience: students
summary: "Unit 8: quadruped_description package, onshape-to-robot export of a 4-leg assembly, mesh path fix, quadruped.launch.py, start_rviz.launch.py, joint sliders."
tags: [course, unit 8, quadruped, quadruped_description, onshape-to-robot, config.json, robot.urdf, quadruped.launch.py, start_rviz.launch.py, ParameterValue]
see: ["[[urdf-learn-start-here]]", "[[urdf-onshape-export]]", "[[urdf-description-package]]", "[[urdf-frames-rviz]]"]
requires: [ros2-core]
version_notes:
  - "humble: install onshape-to-robot with pipx or in a venv (URDF-V12); the course's last config.json misses a comma (URDF-V13)"
  - "all: current onshape-to-robot writes the XML declaration itself, so the course's 'add the format shebang' step is not needed (URDF-V47)"
---
# Unit 8: quadruped exported from Onshape, launch and RViz

**TL;DR** Export a public four-legged assembly from Onshape into a new package, fix the mesh paths with `packageName`, and show the model in RViz2 with joint sliders. Tool details: [[urdf-onshape-export]].

## Steps
1. **Onshape account** (free for public documents) and **API keys**, exported from a `keys.sh` you source (`echo $ONSHAPE_ACCESS_KEY` to check).
2. **Package**:
   ```bash
   cd ~/ros2_ws/src
   ros2 pkg create --build-type ament_cmake quadruped_description --dependencies urdf xacro
   cd quadruped_description && mkdir quadruped launch rviz && touch quadruped/config.json
   ```
   Install `rviz launch quadruped` in `CMakeLists.txt` ([[urdf-description-package]]).
3. **config.json** with the assembly: the course uses a prepared public assembly `quadruped_v1` (copy it in Onshape to edit it). First version (course keys):
   ```json
   {"documentId": "<document-id>", "outputFormat": "urdf", "assemblyName": "quadruped_v1"}
   ```
4. **Export**: `pipx install onshape-to-robot`, open a new terminal, then `onshape-to-robot quadruped` in the package folder → `quadruped/robot.urdf` and the STL meshes.
5. **Fix the mesh paths**: the first export writes `package:///assets/torso_quadruped.stl`. Add (with commas)
   ```json
   "packageName": "quadruped_description/quadruped",
   "robotName": "quadruped_robot"
   ```
   and export again → `package://quadruped_description/quadruped/assets/torso_quadruped.stl`.
6. **Result**: links `torso_quadruped`, `shoulder`…`shoulder_4`, `upperlimb`…`upperlimb_4`, `lowerlimb`…`lowerlimb_4`; revolute joints `shoulder1`–`4` (±0.785 rad), `upperlimb1`–`4` (−1.222…0), `lowerlimb1`–`4` (−1.396…0), all `effort="10" velocity="10"`; masses and inertias from the CAD materials.

## Launch files
`launch/quadruped.launch.py` publishes the model (note `ParameterValue`):
```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


# this is the function launch system will look for
def generate_launch_description():
    ####### DATA INPUT ##########
    urdf_file = 'robot.urdf'
    package_description = "quadruped_description"
    ####### DATA INPUT END ##########
    print("Fetching URDF ==>")
    robot_desc_path = os.path.join(get_package_share_directory(package_description), "quadruped", urdf_file)

    # Run xacro at launch and force the result to be treated as a string
    robot_description_content = Command(['xacro ', robot_desc_path])
    robot_description = ParameterValue(robot_description_content, value_type=str)

    # Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        emulate_tty=True,
        parameters=[{'use_sim_time': True, 'robot_description': robot_description}],
        output="screen")

    # create and return launch description object
    return LaunchDescription([robot_state_publisher_node])
```
`launch/start_rviz.launch.py` is the `rviz_node` part of the RViz launch file in [[urdf-description-package]] with `package_description = "quadruped_description"` and `rviz/quadruped.rviz`. Save that config from RViz2 with Fixed Frame `torso_quadruped`, a RobotModel on `/robot_description` (Transient Local) and a TF display ([[urdf-frames-rviz]]); the course ships a ready-made file.

```bash
cd ~/ros2_ws && colcon build --packages-select quadruped_description && source install/setup.bash
ros2 launch quadruped_description quadruped.launch.py           # terminal 1
ros2 launch quadruped_description start_rviz.launch.py          # terminal 2
ros2 run joint_state_publisher_gui joint_state_publisher_gui    # terminal 3: move the legs
```
