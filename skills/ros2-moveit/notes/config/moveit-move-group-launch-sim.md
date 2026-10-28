---
id: moveit-move-group-launch-sim
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "move_group launch for a simulated robot: use_sim_time, execution duration scaling, publish the SRDF"
domain: moveit
area: config
distro: humble
tested: false
audience: dev
summary: "Execution ABORTED, 'couldn't receive full current joint state within 1s': give move_group use_sim_time; generated launch vs Node launch."
tags: [move_group.launch.py, generate_move_group_launch, MoveItConfigsBuilder, moveit_configs_utils, use_sim_time, trajectory_execution.allowed_execution_duration_scaling, publish_robot_description_semantic, moveit_ros_move_group, ABORTED, couldn't receive full current joint state, SetParameter, simulation]
see: ["[[moveit-rviz-motion-planning]]", "[[moveit-architecture]]", "[[core-time-timers]]", "[[core-launch-basics]]"]
requires: [ros2-core]
version_notes:
  - "humble: execution validation calls waitForCurrentState(node_->now()) and logs 'Failed to validate trajectory: couldn't receive full current joint state within 1s' — https://github.com/moveit/moveit2/blob/humble/moveit_ros/planning/trajectory_execution_manager/src/trajectory_execution_manager.cpp (MOVEIT-V20)"
  - "humble: allowed_execution_duration_scaling default 1.1, allowed_goal_duration_margin 0.5 s — https://github.com/moveit/moveit2/blob/humble/moveit_ros/planning/trajectory_execution_manager/src/trajectory_execution_manager.cpp (MOVEIT-V21)"
  - "humble: generate_move_group_launch already sets publish_robot_description_semantic and the publish_* scene parameters; no generator handles use_sim_time (also jazzy, main) — https://github.com/moveit/moveit2/blob/humble/moveit_configs_utils/moveit_configs_utils/launches.py (MOVEIT-V19)"
  - "humble: MoveItConfigsBuilder(robot_name, package_name) finds config/<robot_name>.urdf.xacro and the .setup_assistant file — https://github.com/moveit/moveit2/blob/humble/moveit_configs_utils/moveit_configs_utils/moveit_configs_builder.py (MOVEIT-V27)"
---
# move_group for a simulated robot: `use_sim_time`

**TL;DR** The launch files the Setup Assistant generates never set `use_sim_time`. With a simulated robot, **Execute** then aborts: `move_group` compares wall-clock time with the simulation stamps of `/joint_states`. Start `move_group` with `use_sim_time: True` (and `False` on a real robot).

## Symptom
Plan works, Execute does not move the robot, and the `move_group` log shows:
```
[move_group-1] Check clock synchronization if your are running ROS across multiple machines!
[move_group-1] [WARN] [1700227282.168744312] [moveit_ros.trajectory_execution_manager]: Failed to validate trajectory: couldn't receive full current joint state within 1s
[move_group-1] [INFO] [1700227282.168787188] [moveit_move_group_default_capabilities.execute_trajectory_action_capability]: Execution completed: ABORTED
```
Before executing, MoveIt waits for a joint state at least as new as `node->now()`; with wall time "now" is decades ahead of the simulation stamps, so the wait fails (MOVEIT-V20; the first line, typo included, comes from MoveIt's state monitor).

## The generated launch
```python
from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_move_group_launch


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("name", package_name="my_moveit_config").to_moveit_configs()
    return generate_move_group_launch(moveit_config)
```
- `MoveItConfigsBuilder("name", package_name="my_moveit_config")` loads the package's configuration into `moveit_config`; `"name"` is the robot's name (it finds `config/name.urdf.xacro` and the `.setup_assistant` file, MOVEIT-V27).
- `generate_move_group_launch()` (from `moveit_configs_utils`, which generates all MoveIt launch files) builds the `move_group` node from that data; nothing in it sets `use_sim_time`.

## The course's fix: start `move_group` yourself
```python
from moveit_configs_utils import MoveItConfigsBuilder
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("name", package_name="my_moveit_config").to_moveit_configs()

    # Move Group Node
    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            {"trajectory_execution.allowed_execution_duration_scaling": 2.0,},
            {"publish_robot_description_semantic": True},
            {"use_sim_time": True},
        ],
    )

    return LaunchDescription([move_group_node])
```
(The course file also imports `generate_move_group_launch`, unused here.)
- `trajectory_execution.allowed_execution_duration_scaling: 2.0`: an execution may take twice the planned time before MoveIt cancels it (default 1.1, plus a 0.5 s margin, MOVEIT-V21), to avoid timeouts in simulation.
- `publish_robot_description_semantic: True`: publish the semantic description (SRDF); the course sets it so RViz2 shows the robot properly.
- `use_sim_time: True`: use the simulation clock. **On a real robot set it to `False`.**

Rebuild (`cd ~/ros2_ws && colcon build && source install/setup.bash`), start `ros2 launch my_moveit_config move_group.launch.py` again (it ends with `You can start planning now!`) and RViz2 ([[moveit-rviz-motion-planning]]). A successful execution logs:
```
[move_group-1] [INFO] [1700229599.034172961] [moveit_ros.trajectory_execution_manager]: Completed trajectory execution with status SUCCEEDED ...
[move_group-1] [INFO] [1700229599.034286615] [moveit_move_group_default_capabilities.execute_trajectory_action_capability]: Execution completed: SUCCEEDED
```

## Keep the generated settings instead (alternative, `[verify]`)
The hand-written node loses what `generate_move_group_launch` adds besides the SRDF flag: `publish_planning_scene`, `publish_geometry_updates`, `publish_state_updates`, `publish_transforms_updates` (true there, false by default), `allow_trajectory_execution`, `capabilities`, `disable_capabilities`, `monitor_dynamics` and a `debug` argument (MOVEIT-V19). `SetParameter` gives `use_sim_time` to every node of the launch scope:
```python
from launch import LaunchDescription
from launch_ros.actions import SetParameter
from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_move_group_launch


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("name", package_name="my_moveit_config").to_moveit_configs()
    generated = generate_move_group_launch(moveit_config)
    return LaunchDescription([SetParameter(name="use_sim_time", value=True), *generated.entities])
```
Not built or run yet [verify].

## Pitfalls
- Every node that talks to the simulated robot needs the same clock: the course's C++ programs get `{'use_sim_time': True}` too ([[moveit-cpp-package-setup]]); clock rules: [[core-time-timers]].
- `use_sim_time: True` with no simulation running: the node's time stays 0 until a `/clock` message arrives ([[core-time-timers]]).
