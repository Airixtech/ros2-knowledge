---
id: control-custom-config-launch
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Use the custom controller: YAML type rrbot_controller/RRBotController, gz_ros2_control <parameters>, launch with a delayed spawner"
domain: control
area: controllers
distro: jazzy
tested: false
audience: dev
summary: "rrbot_controllers_custom.yaml with type rrbot_controller/RRBotController, install config, Gazebo <parameters> path, rrbot_with_rrbot_controller.launch.py: OnExecutionComplete + TimerAction spawners."
tags: [custom controller, rrbot_controllers_custom.yaml, rrbot_controller/RRBotController, install config, gz_ros2_control, parameters, rrbot.xacro, rrbot_with_rrbot_controller.launch.py, OnExecutionComplete, TimerAction, LogInfo, OnProcessExit, spawner]
see: ["[[control-controller-config]]", "[[control-bringup-sim-launch]]", "[[control-urdf-tag]]", "[[control-custom-package-build]]", "[[control-learn-unit7-custom]]", "[[control-cli-state-changes]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: for a process action, OnExecutionComplete fires when the process has exited; the spawners start 10 s after create exits — https://github.com/ros2/launch/blob/jazzy/launch/launch/actions/execute_local.py (CONTROL-V78)"
  - "jazzy: same YAML layout as unit 2 (type under controller_manager) — https://github.com/ros-controls/ros2_control_demos/blob/jazzy/example_1/bringup/launch/rrbot.launch.py (CONTROL-V40)"
---
# Use the custom controller: YAML type rrbot_controller/RRBotController, gz_ros2_control <parameters>, launch with a delayed spawner

**TL;DR** The custom controller is configured and started like any other: a YAML whose `type` is the plugin name of its XML, the YAML path in the gz_ros2_control plugin of the robot description, and a spawner. A launch file is optional: the `ros2 control` CLI can load and start it too ([[control-cli-state-changes]]).

## config/rrbot_controllers_custom.yaml
```bash
mkdir ~/ros2_ws/src/rrbot_controller/config
touch ~/ros2_ws/src/rrbot_controller/config/rrbot_controllers_custom.yaml
```
```yaml
# Controller manager configuration
controller_manager:
  ros__parameters:
    update_rate: 50  # Hz

    # Define a name for controllers that we plan to use
    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    rrbot_controller:
      type: rrbot_controller/RRBotController

# Properties of the custom controler and definition of joints to use
rrbot_controller:
  ros__parameters:
    joints:
      - joint1
      - joint2
    interface_name: position
```
The layout is the one of unit 2 ([[control-controller-config]]); `joints` and `interface_name` are the parameters declared in `on_init()` ([[control-custom-init]]). Install the folder: add to `CMakeLists.txt`, after the install of `include/` ([[control-custom-package-build]]):
```cmake
install(
  DIRECTORY config
  DESTINATION share/${PROJECT_NAME}/
)
```

## The Gazebo plugin
In `rrbot.xacro` of `rrbot_unit2`, point the gz_ros2_control plugin at the new file; the `<ros2_control>` tags of unit 2 stay ([[control-urdf-tag]]):
```xml
<!-- Gazebo's ros2_control plugin -->
<gazebo>
  <plugin filename="gz_ros2_control-system" name="gz_ros2_control::GazeboSimROS2ControlPlugin">
    <parameters>$(find rrbot_controller)/config/rrbot_controllers_custom.yaml</parameters>
  </plugin>
</gazebo>
```

## launch/rrbot_with_rrbot_controller.launch.py (in my_robot_bringup)
The file is `my_robot.launch.py` of unit 2 ([[control-bringup-sim-launch]]) with these differences:
```python
# the two import lines that change (the other imports as in my_robot.launch.py)
from launch.actions import ExecuteProcess, IncludeLaunchDescription, RegisterEventHandler, TimerAction, LogInfo
from launch.event_handlers import OnProcessExit, OnExecutionComplete
```
- In `gz_spawn_entity`, the entity name is `"-name", "rrobot"` (unit 2: `"robot"`).
- The second spawner starts the custom controller:
```python
    robot_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["rrbot_controller", "-c", "/controller_manager"],
    )
```
- The first event handler waits 10 s more before the broadcaster spawner (the second handler, `OnProcessExit` from the broadcaster spawner to `robot_controller_spawner`, is unchanged):
```python
        RegisterEventHandler(
            OnExecutionComplete(
                target_action=gz_spawn_entity,
                on_completion=[
                    LogInfo(msg='Spawn finished, waiting 10 seconds to start controllers.'),
                    TimerAction(
                        period=10.0,
                        actions=[joint_state_broadcaster_spawner],
                    )
                ]
            )
        ),
```
For a process such as `create`, `OnExecutionComplete` fires when the process has exited, as `OnProcessExit` does; the timer then adds 10 s. `ExecuteProcess`, `IncludeLaunchDescription` and `PythonLaunchDescriptionSource` (imported as in unit 2) are not used.

## Pitfalls
- YAML `type` different from the XML `name` (`rrbot_controller/RRBotController`) → "Loader for controller … not found".
- `config/` not installed, or the package not rebuilt after editing the YAML → the plugin reads the old file or none.
- The robot from an earlier run still in Gazebo → the new `<parameters>` path is not used: delete the model and spawn again.
