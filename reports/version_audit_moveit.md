# Version audit — ros2-moveit (Phase 1)

> Date: 2026-10-27. Scope: every version-dependent or checkable statement of the manipulation course (course wiki,
> not published; units 1–5, C++ with `MoveGroupInterface`) that lands in `ros2-moveit`: the MoveIt Setup Assistant
> and the generated configuration package (`joint_limits.yaml`, `moveit_controllers.yaml`, `kinematics.yaml`, the
> `move_group` launch), motion planning in RViz2, the Move Group C++ interface (joint-space, pose, named, gripper and
> Cartesian goals, plan / execute / move), kinematics plugins, pick and place, and object detection with
> `simple_grasping` (`find_objects` action, `grasping_msgs`, a C++ action client). The course robot is a UR3e with a
> Robotiq 85 gripper. Section IDs = the course's section numbers.
> Baseline: **Humble is canonical** (decision of 2026-10-27: the course targets Humble and its code builds on the
> Humble API). Jazzy, Kilted and Lyrical are annotated. Simulation versions are distro + Gazebo pairs. Generic ROS 2
> rows are in [version_audit.md](version_audit.md) (`Vnn`).

## Method
- Primary sources, read on the matching branch with grep: `moveit/moveit2` (humble, jazzy, main = Kilted/Lyrical
  release line; tags 2.10.0, 2.12.0, 2.12.4): `move_group_interface.h/.hpp` and `.cpp`, `cartesian_interpolator.cpp`,
  `robot_model_loader.cpp`, `trajectory_execution_manager.cpp`, `current_state_monitor.cpp`,
  `planning_scene_monitor.cpp`, `move_group.cpp`, `execute_trajectory_action_capability.cpp`,
  `moveit_simple_controller_manager.cpp`, `action_based_controller_handle.h`, `moveit_configs_utils` (`launches.py`,
  `moveit_configs_builder.py`), the Setup Assistant sources (`srdf_config.cpp`, `default_collisions_widget.cpp`,
  `compute_default_collisions.cpp`, `start_screen_widget.cpp`, `group_edit_widget.cpp`, `moveit_controllers.hpp`,
  `controllers.cpp`), `moveit_kinematics/*_description.xml`, `motion_planning_frame.cpp`, CMakeLists and CHANGELOGs;
  `moveit/moveit2_tutorials` (humble: `move_group_interface_tutorial.cpp` and its launch file);
  `ros-controls/ros2_controllers` (humble: `gripper_controllers`, `rqt_joint_trajectory_controller/setup.py`);
  `ros-controls/control_msgs` (humble: `GripperCommand`); `ros2/launch_ros` (humble: `node.py`, `set_parameter.py`);
  `ros2/rclcpp` (humble: `parameter_value.hpp`); `ament/ament_cmake` (humble: `ament_export_targets.cmake`);
  `ros2/common_interfaces` (humble: `SolidPrimitive.msg`); `mikeferguson/simple_grasping` (branches `ros2` and
  `jazzy`: `basic_grasping_perception.cpp`, `object_support_segmentation.cpp`, `README.md`, `CHANGELOG.rst`);
  `mikeferguson/grasping_msgs` (`ros2`); `gazebosim/gz-sim` (`ign-gazebo6`, `gz-sim8`: `SdfEntityCreator.cc`,
  `Changelog.md`); `gazebosim/ros_gz` (`create.cpp`, via ros2-gazebo's GZ-V09); `PointCloudLibrary/pcl` (`CHANGES.md`);
  `ros/rosdistro` (released versions); the ROS apt indexes (`packages.ros.org`, jammy, noble, resolute) and the Ubuntu
  archive indexes (PCL).
- Origin of the course code: the C++ programs follow the official Humble tutorial
  [move_group_interface_tutorial.cpp][tut-h] (same node options, executor thread, comments such as "Raw pointers are
  frequently used to refer to the planning group for improved performance", `eef_step` 0.01 and `jump_threshold` 0.0;
  the course's comment "more efficient method than std::copy() method used in the docs" points at it). The course
  wraps the steps in classes and creates **two** nodes per program; the tutorial creates one. Object detection uses a
  modified copy of `simple_grasping` given in the course (repository of the course platform, commit 2023-09-19,
  changelog at 0.3.1); it was diffed token by token against the released `jazzy` branch (0.5.0, released for Humble
  and Jazzy) and `ros2` (0.6.0, Kilted and Lyrical).
- Course logic was reviewed too: each variable followed from the code that writes it to the code that reads it, the
  return values that are ignored, index assumptions, empty results, the order of the course commands, explanations
  and outputs against their code. Contradictions are **fix** rows ("course mistake").
- Actions: **keep** = correct for Humble · **annotate** = correct, add marks (Jazzy, Lyrical) or a precise wording ·
  **fix** = wrong for Humble itself. Confidence: High (read in code or the official file) · Medium (docs, or
  inferred) · `[verify]` (needs a run).

## Baseline
| | Humble | Jazzy | Kilted | Lyrical |
|---|---|---|---|---|
| Ubuntu / EOL | 22.04 jammy / May 2027 | 24.04 noble / May 2029 | 24.04 noble / Dec 2026 | 26.04 resolute / May 2031 |
| Gazebo pair | Fortress | Harmonic | Ionic | Jetty |
| MoveIt 2 release (rosdistro, apt) | 2.5.10 | 2.12.4 | 2.14.3 | 2.15.2 |
| `moveit_py` (Python API) binary | `ros-humble-moveit-py` 2.5.10 | 2.12.4 | 2.14.3 | 2.15.2 |
| MoveIt C++ headers | `.h` only | `.hpp`; every `.h` is a wrapper with `#pragma message(".h header is obsolete…")` (MoveIt 2.12.0, [#3113][hpp-pr]) | same | same |
| `computeCartesianPath(…, jump_threshold, …)` | current API | `[[deprecated("Drop jump_threshold")]]` (2.12.0; absent in 2.10.0) | same | same |
| `ament_target_dependencies` | ✓ | ✓ | deprecated | removed (core V09) |
| `ros2_controllers` (`gripper_controllers`, `rqt_joint_trajectory_controller`) | 2.54.1 | 4.43.0 | 5.18.0 | 6.10.0 |
| `simple_grasping` / `grasping_msgs` (apt) | 0.5.0 / 0.4.0 | 0.5.0 / 0.5.0 | 0.6.0 / 0.5.0 | 0.6.0 / 0.5.0 |
| `ros_gz` (`ros_gz_sim create`) | 0.244.27 | 1.0.25 | 2.1.19 | 3.0.12 |
| `perception_pcl` / `libpcl-dev` (Ubuntu) | 2.4.5 / 1.12.1 | 2.6.5 / 1.14.0 | 2.10.0 / 1.14.0 | 2.10.0 / 1.15.1 |

## Real Humble errors (fix)
| ID | Section | Origin | Error | Correct statement |
|---|---|---|---|---|
| MOVEIT-V01 | 3.3, 3.9 | course mistake (explanation) | "we copy the values of the variable `joint_model_group_robot_` (which contains the position value of each joint) into the vector"; "Here we are creating a ROS2 node as a shared pointer from a ROS2 base node" | A `JointModelGroup` holds the group's model (joint names, bounds), not values: `current_state_robot_->copyJointGroupPositions(joint_model_group_robot_, joint_group_positions_robot_)` copies the **current state's** positions of that group's joints. `move_group_node_` is a second, separate node (the base node is never spun); the official tutorial creates only one ([tutorial][tut-h]). |
| MOVEIT-V02 | 3.1, 2.14 | course mistake (outdated, self-contradiction) | "MoveIt2 does not yet have a Python API at the time of writing"; 2.14: "You can use C++ (you will see it in chapter 4) or Python MoveIt APIs" | `moveit_py` is released for Humble (`ros-humble-moveit-py` 2.5.10) and every later distro ([humble distribution.yaml][distro-h]; core's V59). The C++ interface is taught in unit 3, not 4. |
| MOVEIT-V03 | 3.5 | course mistake | "`move` will execute a random plan that it calculates" | `move()` plans **and** executes in one call: "This call is always blocking (waits for the execution of the trajectory to complete)"; nothing is random, but you cannot inspect or choose the plan before it runs. `plan()` + `execute()` lets you check the result first ([move_group_interface.h][mgi-h]); the official tutorial adds that `move()` "requires a controller to be active and report success on execution" ([tutorial][tut-h]). |
| MOVEIT-V04 | 3.5, 3.6, 3.9, 3.10, 4.2–4.5 | course mistake (logic) | `execute_trajectory_kinematics()` / `execute_trajectory_gripper()`: `move_group_robot_->execute(plan); RCLCPP_INFO(LOGGER, "Robot Kinematics Trajectory Success !");` | `execute()` returns a `moveit::core::MoveItErrorCode` ("execute it while waiting for completion", [header][mgi-h]); the course ignores it and logs "Success" whenever **planning** succeeded, also when execution was ABORTED (e.g. the sim-time case of 2.13). Check `== moveit::core::MoveItErrorCode::SUCCESS`, and stop the sequence on failure. |
| MOVEIT-V05 | 4.2, 4.3, 4.5 | course mistake (logic) | `if (plan_fraction_robot_ >= 0.0) { // 0.0 to 1.0 = success and -1.0 = failure` then `execute(cartesian_trajectory_plan_)` | `computeCartesianPath` returns "a value that is between 0.0 and 1.0 indicating the fraction of the path achieved … -1.0 in case of error" ([header][mgi-h]): 0.3 means only 30 % of the path was computed, and the course executes that partial path. Execute only when the fraction is 1.0 (or above a threshold you choose) and log it, as the tutorial does (`%.2f%% achieved`). |
| MOVEIT-V06 | 3.10, 5.7 | course mistake (physics) | `grasp_box.urdf`: box 0.04 × 0.04 × 0.08 m, 0.5 kg, `ixx = iyy = izz = 0.000133333333333`; `grasp_box2.urdf`: cube 0.1 m, 0.5 kg, the same three values | Box inertia: `ixx = m(y²+z²)/12`, `iyy = m(x²+z²)/12`, `izz = m(x²+y²)/12` ([URDF tutorial][urdf-tut-h]; ros2-urdf's `urdf-inertia`). grasp_box: `ixx = iyy = 0.000333333`, `izz = 0.000133333`; grasp_box2: `0.000833333` for all three. The course's value is that of a 0.04 m cube. |
| MOVEIT-V07 | 5.5 | course mistake (explanation vs code) | "subscribe to the PointCloud of the Depth Camera, which is published in the `/wrist_camera/depth/points` topic" under a fragment that subscribes `/wrist_rgbd_depth_sensor/points`; the `cloud_callback` fragment shows `boost::make_shared<pcl::PointCloud<pcl::PointXYZRGB>>()` | The code wins: the course copy subscribes `/wrist_rgbd_depth_sensor/points` (the released package: `/head_camera/depth_registered/points`, MOVEIT-V44) and creates the cloud with `std::make_shared`. Since PCL 1.11 `PointCloud::Ptr` is a `std::shared_ptr` ([PCL CHANGES][pcl-changes]; Humble's Ubuntu ships 1.12.1), so the `boost::make_shared` line of the walk-through does not compile there. |
| MOVEIT-V08 | 5.6 | course mistake (logic) | `get_object_pose_action_client.cpp`: `action_result.result->objects[0].object.primitive_poses[0].position.x` right after `SUCCEEDED` | With no detected object (or an object without primitives) `operator[]` reads past the end of an empty vector (undefined behavior, usually a crash). Check `objects.empty()` and `primitive_poses.empty()` first. |
| MOVEIT-V09 | 5.7 (both updated clients) | course mistake (logic) | inside `for (auto object : action_result.result->objects)` the position is printed from `action_result.result->objects[0].object.primitive_poses[0]` | Every iteration prints the **first** object's position next to the current object's type and size: the filtered box gets the wrong position whenever it is not first. Use `object.object.primitive_poses[0]`. |
| MOVEIT-V10 | 5.6 (solution) | course mistake | the client's `CMakeLists.txt` ends with `install(DIRECTORY launch DESTINATION share/${PROJECT_NAME}/)`, and `find_package(std_msgs)` / `find_package(geometry_msgs)`; the package was created with `--dependencies grasping_msgs rclcpp rclcpp_action` | The package has no `launch/` folder (none is created), so the install step fails `[verify]`; drop the line or create the folder. `std_msgs` and `geometry_msgs` are found in CMake but missing from `package.xml` (rosdep cannot install them); the client uses neither directly. |
| MOVEIT-V12 | 2.5 | course mistake (explanation) | "the Setup Assistant automatically defines pairs of links that don't need to be considered … For instance, because they are adjacent links, they will always collide" | The Setup Assistant disables pairs for separate reasons: **Adjacent** (connected by a joint), **Always** (in collision in at least the chosen share of sampled states, the "Min. collisions for "always"-colliding pairs" value), **Never** (never in collision while sampling), **Default** (in collision in the default state) and **User** ([compute_default_collisions.cpp][sa-cdc-h]). |
| MOVEIT-V13 | 3.7 | course mistake (old name) | "The **Joint State Controller** provides the joint states of the robot" | In ros2_control the `joint_state_broadcaster` publishes `/joint_states` ([ros2_controllers humble][jsb-h]; ros2-control skill). |
| MOVEIT-V15 | 3.3 | course mistake (link) | the `MoveGroupInterface` API is linked to the API pages of an old MoveIt release that is not MoveIt 2 | Read the Humble header [move_group_interface.h][mgi-h] (Jazzy and later: [move_group_interface.hpp][mgi-j]); docs site `moveit.picknik.ai/humble`. |

## Full table
| # | Section | Statement | Humble | Jazzy | Lyrical | Action | Source | Confidence |
|---|---|---|---|---|---|---|---|---|
| MOVEIT-V01 | 3.3, 3.9 | joint model group "contains the position values"; a node "from a base node" | ✗ see fix table | ✗ same | ✗ same | **fix** | [tut-h] | High |
| MOVEIT-V02 | 3.1, 2.14 | no Python API; C++ "in chapter 4" | ✗ `moveit_py` 2.5.10 released; C++ is unit 3 | ✗ 2.12.4 | ✗ 2.15.2 | **fix** | [distro-h], apt indexes | High |
| MOVEIT-V03 | 3.5 | `move()` executes "a random plan" | ✗ plan + execute in one blocking call | ✗ same | ✗ same | **fix** | [mgi-h], [tut-h] | High |
| MOVEIT-V04 | 3.5–4.5 | "Success !" logged without checking `execute()` | ✗ check the returned `MoveItErrorCode` | ✗ same | ✗ same | **fix** | [mgi-h] | High |
| MOVEIT-V05 | 4.2–4.5 | executes when fraction ≥ 0.0 | ✗ partial paths executed; require 1.0 | ✗ same | ✗ same | **fix** | [mgi-h], [tut-h] | High |
| MOVEIT-V06 | 3.10, 5.7 | box inertia 0.000133 for both boxes | ✗ 0.000333/0.000333/0.000133 and 0.000833 | ✗ same | ✗ same | **fix** | [urdf-tut-h] | High |
| MOVEIT-V07 | 5.5 | camera topic `/wrist_camera/depth/points`; `boost::make_shared` cloud | ✗ code subscribes `/wrist_rgbd_depth_sensor/points`, uses `std::make_shared` (PCL ≥ 1.11) | ✗ same (PCL 1.14) | ✗ same (PCL 1.15) | **fix** | course copy, [pcl-changes] | High |
| MOVEIT-V08 | 5.6 | `objects[0]` read without a size check | ✗ undefined behavior when nothing is found | ✗ same | ✗ same | **fix** | C++ `std::vector::operator[]` | High |
| MOVEIT-V09 | 5.7 | loop prints `objects[0]`'s position for every object | ✗ use the loop variable | ✗ same | ✗ same | **fix** | course code | High |
| MOVEIT-V10 | 5.6 | `install(DIRECTORY launch …)` without a launch folder; deps missing in package.xml | ✗ install fails `[verify]`; add `<depend>` or drop | ✗ same | ✗ same | **fix** | course code | Medium |
| MOVEIT-V11 | 2.12 | `max_velocity: 100` must become `100.0`; `max_acceleration: 0` → `0.0`; add `has_position_limits`, `min_position`, `max_position` | ✓ the Setup Assistant writes `static_cast<double>` values through yaml-cpp, which prints `100` and `0` ([srdf_config.cpp][srdfcfg-h]); `move_group` declares parameters from overrides, so they stay integers, and `robot_model_loader` reads `robot_description_planning.joint_limits.<joint>.max_velocity` as a double: rclcpp throws "expected [double] got [integer]" ([parameter_value.hpp][rclcpp-pv-h]), MoveIt logs "When getting the parameter …" and skips the rest of that joint's limits ([robot_model_loader.cpp][rml-h]). `max_acceleration` is read only when `has_acceleration_limits` is true (here false). `max_position`/`min_position` are read directly and set the position limit themselves (`has_position_limits` is not read); continuous joints reject them | ✓ same writer and reader | ✓ same | annotate | [srdfcfg-h], [rml-h], [rclcpp-pv-h] | High |
| MOVEIT-V12 | 2.5 | adjacent links "always collide" | ✗ separate reasons Adjacent / Always / Never / Default / User | ✗ same | ✗ same | **fix** | [sa-cdc-h] | High |
| MOVEIT-V13 | 3.7 | "Joint State Controller" | ✗ `joint_state_broadcaster` | ✗ same | ✗ same | **fix** | [jsb-h] | High |
| MOVEIT-V14 | 3.3–5.8 | `#include <moveit/move_group_interface/move_group_interface.h>`, `planning_scene_interface.h` | ✓ only `.h` exists | ✓ builds with a `#pragma message` per header; use `.hpp` [≥Jazzy] | ✓ same | annotate | [mgi-j], [hpp-pr] | High |
| MOVEIT-V15 | 3.3 | API link to an old MoveIt release | ✗ link the Humble header | ✗ `.hpp` | ✗ same | **fix** | [mgi-h] | High |
| MOVEIT-V16 | 4.2 | `computeCartesianPath(waypoints, 0.01, 0.0, trajectory)`: 1 cm interpolation, `jump_threshold` 0.0 "basically disabling it" | ✓ a 0.0 factor skips the relative jump check ([cartesian_interpolator.cpp][ci-h]); the tutorial warns: "disabling the jump threshold while operating real hardware can cause large unpredictable motions of redundant joints and could be a safety issue" ([tutorial][tut-h]) | ✓ the overload is `[[deprecated("Drop jump_threshold")]]` since 2.12.0: call `computeCartesianPath(waypoints, eef_step, trajectory)` | ✓ same | annotate | [mgi-h], [mgi-j], [ci-h], [tut-h] | High |
| MOVEIT-V17 | 3.3–4.5 | CMake `ament_target_dependencies(<exe> ament_cmake rclcpp rclcpp_action moveit_core moveit_ros_planning_interface interactive_markers moveit_ros_planning control_msgs)` | ✓ | ✓ | ✗ removed in Lyrical (deprecated in Kilted): `target_link_libraries(<exe> moveit_ros_planning_interface::moveit_move_group_interface rclcpp::rclcpp)`; the namespaced target exists on Humble too (`ament_export_targets` defaults to `${PROJECT_NAME}::`) | annotate | [pi-cmake-j], [aet-h], core V09 | High |
| MOVEIT-V18 | 3.3 launch files | `Node(name="joint_space_trajectory", …)` for a program that creates two nodes | ✓ launch_ros passes `-r __node:=joint_space_trajectory` ([node.py][node-h]); a remap without a node prefix applies to every node of the process ([Node arguments][nodeargs-h], [CLI design][cliargs]), so `move_group_node` gets the same name `[verify]` (duplicate-name warning); dict parameters go to `/**` because no namespace is given, which is why `move_group_node` receives `robot_description` | ✓ same | ✓ same | annotate | [node-h], [nodeargs-h] | Medium |
| MOVEIT-V19 | 2.13 | the hand-written `move_group.launch.py` (`to_dict()` + `allowed_execution_duration_scaling` 2.0 + `publish_robot_description_semantic` + `use_sim_time`) | ✓ fixes the sim-time abort; but `generate_move_group_launch` already sets `publish_robot_description_semantic: True` and also sets `publish_planning_scene`, `publish_geometry_updates`, `publish_state_updates`, `publish_transforms_updates` (true), `allow_trajectory_execution`, `capabilities`, `disable_capabilities`, `monitor_dynamics` and a `debug` argument ([launches.py][launches-h]); the hand-written node loses them (the scene monitor's defaults are false, [planning_scene_monitor.cpp][psm-h]); none of the generators handles `use_sim_time`. Keeping the generated launch: `SetParameter(name="use_sim_time", value=True)` before its entities sets it for the nodes of that scope ([set_parameter.py][setparam-h]) `[verify]` | ✓ same (`launches.py` jazzy has no `use_sim_time`) | ✓ same | annotate | [launches-h], [psm-h], [setparam-h] | Medium |
| MOVEIT-V20 | 2.13 | the ABORTED execution with `use_sim_time` false | ✓ execution validation calls `waitForCurrentState(node_->now())` and logs "Failed to validate trajectory: couldn't receive full current joint state within 1s" ([trajectory_execution_manager.cpp][tem-h]): `now()` is wall time while the joint states carry simulation stamps; "Check clock synchronization if your are running ROS across multiple machines!" (typo in MoveIt) comes from [current_state_monitor.cpp][csm-h]; "Execution completed: " from the execute capability | ✓ | ✓ | keep | [tem-h], [csm-h] | High |
| MOVEIT-V21 | 2.13 | `trajectory_execution.allowed_execution_duration_scaling: 2.0` "to avoid timeout issues" | ✓ default 1.1, plus `allowed_goal_duration_margin` 0.5 s after scaling ([trajectory_execution_manager.cpp][tem-h]) | ✓ | ✓ | annotate | [tem-h] | High |
| MOVEIT-V22 | 2.3–2.11 | Setup Assistant: `setup_assistant.launch.py`, "Create New MoveIt Configuration Package", Sampling Density, "Min. collisions for "always"-colliding pairs", "Generate Collision Matrix", "Add Kin. Chain", "Auto Add FollowJointsTrajectory Controllers For Each Planning Group", "Edit Existing MoveIt Configuration Package" | ✓ the labels exist in the Humble sources ([start screen][sa-start-h], [collisions][sa-coll-h], [group edit][sa-group-h], [controllers][sa-ctrl-h]); Auto Add names each controller `<group>_controller` ([controllers.cpp][sa-ctrl-src-h]), hence `ur_manipulator_controller`; the ROS 2 Controllers tab has its own "Auto Add JointTrajectoryController Controllers For Each Planning Group" (writes `ros2_controllers.yaml`) | ✓ | ✓ | keep | listed | High |
| MOVEIT-V23 | 2.10, 2.12 | `moveit_controllers.yaml`: the action is `/<name>/<action_ns>`; `FollowJointTrajectory` for the arm, `GripperCommand` with `action_ns: gripper_cmd` for the gripper | ✓ `getActionName()` = `name + "/" + action_ns` ([action_based_controller_handle.h][abch-h]); `GripperCommand` controllers also read optional `max_effort` (default 0.0), `parallel`, `allow_failure`; `default` marks the controller to use for its joints ([moveit_simple_controller_manager.cpp][smcm-h]) | ✓ | ✓ | keep | [abch-h], [smcm-h] | High |
| MOVEIT-V24 | 3.8 | `ros2 action send_goal /gripper_controller/gripper_cmd control_msgs/action/GripperCommand` with `position` 0.0 (open) / 0.8 (close), `max_effort` 0.0 | ✓ goal = `GripperCommand command` (`position`, `max_effort`); the controller serves `~/gripper_cmd`; with a position interface the goal position is written to the joint as is (here the knuckle angle; the message comment says "gap size (in meters)") and `max_effort` is not used by that adapter ([gripper_action_controller_impl.hpp][gripper-h], [hardware_interface_adapter.hpp][gripper-adapter-h], [GripperCommand.msg][gcmd-h]); the export collapsed the YAML: `"{command: {position: 0.0, max_effort: 0.0}}"` | ✓ | ✓ | annotate | [gripper-h], [gcmd-h] | High |
| MOVEIT-V25 | 3.9 | `setup_joint_value_gripper()`: `joint_group_positions_gripper_[2] = angle` | ✓ compiles; index 2 assumes the third variable of the `gripper` group is the driven knuckle (the group's joints were shown only in a figure) `[verify]`; by name: `setJointValueTarget("robotiq_85_left_knuckle_joint", angle)` ([header][mgi-h], line 405) | ✓ | ✓ | annotate | [mgi-h] | Medium |
| MOVEIT-V26 | 3.3–4.5 | MoveGroupInterface calls: `setJointValueTarget(vector)`, `setPoseTarget(Pose)`, `setNamedTarget`, `setStartStateToCurrentState`, `getCurrentState(10)`, `getCurrentPose().pose`, `plan(...) == MoveItErrorCode::SUCCESS` | ✓ all in the Humble header; `getCurrentState(double wait = 1)`; `MoveItErrorCode` has `operator==(int)`; defaults: planning time 5 s, 1 attempt, end effector = last link of a chain group, pose reference frame = model frame, scaling factors from `robot_description_planning.default_*_scaling_factor` or 0.1 ([move_group_interface.cpp][mgi-cpp-h]) | ✓ | ✓ | keep | [mgi-h], [mgi-cpp-h] | High |
| MOVEIT-V27 | 2.13, 3.3 | `MoveItConfigsBuilder("name", package_name="my_moveit_config")` | ✓ the first argument is the robot name: the builder looks for `config/<name>.urdf.xacro` and reads the URDF and SRDF paths from `.setup_assistant`; without `package_name` it looks for `<name>_moveit_config` ([moveit_configs_builder.py][builder-h]) | ✓ | ✓ | keep | [builder-h] | High |
| MOVEIT-V28 | 2.13 | "You can start planning now!"; `<random valid>` goal state | ✓ ([move_group.cpp][mg-h], [motion_planning_frame.cpp][mpf-h]) | ✓ | ✓ | keep | listed | High |
| MOVEIT-V29 | 2.11 Note 3, 4.4 | "If you modify your MoveIt package, you will need to restart the simulation"; rebuild and restart MoveIt after editing `kinematics.yaml` | ✓ the configuration is read when `move_group` (and RViz2, the C++ programs) start: rebuild (installed copies) and restart those; the simulation itself does not read it | ✓ | ✓ | annotate | [launches-h] | Medium |
| MOVEIT-V30 | 4.4 | default `kdl_kinematics_plugin/KDLKinematicsPlugin`; switch to `lma_kinematics_plugin/LMAKinematicsPlugin`; `kinematics_solver_search_resolution`, `kinematics_solver_timeout` 0.005 | ✓ both plugins in `moveit_kinematics` (also `cached_ik_kinematics_plugin/CachedKDLKinematicsPlugin`, `srv_kinematics_plugin/SrvKinematicsPlugin`) ([moveit_kinematics][kin-h]) | ✓ | ✓ | keep | [kin-h] | High |
| MOVEIT-V31 | 3.7 | `ros2 run rqt_joint_trajectory_controller rqt_joint_trajectory_controller` | ✓ console script of the package ([setup.py][rqtjtc-h]), released 2.54.1 | ✓ 4.43.0 | ✓ 6.10.0 | keep | [rqtjtc-h] | High |
| MOVEIT-V32 | 3.7 | `ros2 run tf2_ros tf2_echo base_link tool0`; `/joint_states` order differs from the controller's (`wrist_2`, `wrist_3`, `wrist_1`) | ✓ `tf2_echo` usage as in ros2-tf (TF-V21); the course output is shortened; read joint values by name, not by index | ✓ | ✓ | annotate | ros2-tf | Medium |
| MOVEIT-V33 | 3.10, 4.5, 5.3, 5.7 | `ros2 run gazebo_ros spawn_entity.py -file … -x … -y … -z 0.1 -entity grasp_box` | ✗ `spawn_entity.py` is not a ros_gz tool (GZ-V09): Gazebo Sim spawns with `ros2 run ros_gz_sim create -file <path> -name grasp_box -x 0.34 -y 0.13 -z 0.1` (same flags on Humble + Fortress) | ✓ same, Jazzy + Harmonic | ✓ same, Lyrical + Jetty | annotate | [gz-create-j], GZ-V09 | High |
| MOVEIT-V34 | 3.10, 5.7 | `<gazebo reference="grasp_box_base_link">` with `kp`, `kd`, `mu1`, `mu2` and `<material>Gazebo/Red</material>` | ✓ the short contact and friction tags are converted (GZ-V16); a `Gazebo/…` material name: gz-sim 6 (Fortress) has no lookup for it (ignored `[verify]` which color is shown) | ✓ gz-sim 8 (Harmonic) reads `Gazebo/*` names from an internal `gazebo.material` with a warning ([SdfEntityCreator.cc][gzsim8-sec]; fix in 8.6.0) | ✓ | annotate | [gzsim6-sec], [gzsim8-sec], GZ-V16 | Medium |
| MOVEIT-V35 | 3.10 | pose `(-1, 0, 0, 0)` above the box; IK makes "overly complex motions" | ✓ quaternion x = −1, w = 0 is a half turn about X of the planning frame; each pose goal is solved by the group's IK plugin, which may return another arm configuration, and the joint-space planner then moves to it (the course's explanation) | ✓ | ✓ | keep | [mgi-h] | Medium |
| MOVEIT-V36 | 3.6 | `double_motion_trajectory.cpp` second motion logs "Planning/Executing Joint Value Trajectory 1..." and keeps an unused `setup_goal_pose_target` | ✓ course typo (the second log should say 2) | ✓ | ✓ | annotate | course code | High |
| MOVEIT-V37 | 5.2, 5.4, 5.5 | the course's `simple_grasping` copy: node `basic_grasping_perception_node`, `debug_topics`, `frame_id` `base_link`, `find_objects` | ✓ the released package (`sudo apt install ros-humble-simple-grasping`, 0.5.0) has the same executable, parameters and action ([README][sg-j-readme], [basic_grasping_perception.cpp][sg-j-node]); the course copy differs in: the subscribed topic (`/wrist_rgbd_depth_sensor/points` vs `/head_camera/depth_registered/points`), `voxel_limit_min` default −1.0 (release 0.0, [object_support_segmentation.cpp][sg-j-seg]), no `continuous_detection` parameter and no QoS overrides (added in 0.5.0, [CHANGELOG][sg-changelog]). With the release: `--ros-args -p debug_topics:=true -p voxel_limit_min:=-1.0 -r /head_camera/depth_registered/points:=/wrist_rgbd_depth_sensor/points` `[verify]` | ✓ 0.5.0 | ✓ 0.6.0 (`ament_target_dependencies` replaced) | annotate | [sg-j-node], [sg-j-seg], [sg-changelog] | High |
| MOVEIT-V38 | 5.4, 5.5 | the debug clouds need **Best Effort** in RViz2 | ✓ publishers `rclcpp::QoS qos(1); qos.best_effort();`, cloud subscription depth 10 best effort ([basic_grasping_perception.cpp][sg-j-node]); a reliable subscriber gets nothing from a best-effort publisher (core QoS notes) | ✓ | ✓ | keep | [sg-j-node] | High |
| MOVEIT-V39 | 5.4 | topics `/object_cloud` and `/support_cloud` | ✓ the code publishes `object_cloud` and `support_cloud`; the package README calls the second one `surface_cloud` (README error) | ✓ | ✓ | annotate | [sg-j-node], [sg-j-readme] | High |
| MOVEIT-V40 | 5.5 | `execute()` waits up to 3 s for a cloud ("Failed to get camera data in allotted time."); `find_objects_` set by the action thread and cleared by the cloud callback | ✓ timeout 3.0 s; the course copy prints "alloted", the release "allocated"; `find_objects_` is a plain `bool` shared by two threads (no `std::atomic`), a data race in C++ terms | ✓ | ✓ | annotate | [sg-j-node] | High |
| MOVEIT-V41 | 5.4, 5.6 | `ros2 interface show` of `FindGraspableObjects`, `GraspableObject`, `Object` | ✓ identical to `grasping_msgs` (`ros2` branch) ([grasping_msgs][gm-ros2]) | ✓ | ✓ | keep | [gm-ros2] | High |
| MOVEIT-V42 | 5.7 | `ros2 interface show shape_msgs/msg/SolidPrimitive` lists BOX…CONE | ✓ Humble's file also has `PRISM=5` and a `polygon` field ([SolidPrimitive.msg][solid-h]): the course output comes from an older distro | ✓ | ✓ | annotate | [solid-h] | High |
| MOVEIT-V43 | 5.4, 5.7 | the result output (stamp 2021, a primitive of 9.57 × 4.96 × 0.008 m at y = −2.08) and "one of the objects detected is way bigger than this (0.19x0.12x0.29)" | ✓ neither matches the course scene (a 0.04 × 0.04 × 0.08 m box at x 0.5 and a 0.1 m cube): outputs from other scenes `[verify]` | ✓ | ✓ | annotate | course setup | Medium |
| MOVEIT-V44 | 5.6 | the client spins with `while (!is_goal_done()) rclcpp::spin_some(action_client);`; `goal_handle_future` unused; continues after "Action Client is Not Initialized" | ✓ works; the loop never sleeps (one core busy while waiting); `spin_until_future_complete` or a sleep avoids it; the unused future and the missing `return` are course leftovers | ✓ | ✓ | annotate | course code | High |
| MOVEIT-V45 | 5.2–5.7 | exercise numbering ("Exercise 5.2" twice, "End Exercise 5.1.2", "5.1.3"); "update the code in `get_pose_client.cpp`" (the file is `get_object_pose_action_client.cpp`); 3.9 repeats "create a new package named moveit2_scripts" | ✓ course typos; the learn notes keep the course's exercise titles and use the real file names | ✓ | ✓ | annotate | course text | High |
| MOVEIT-V46 | 3.3 | the programs follow the official Humble tutorial | ✓ origin [tutorial][tut-h] and its launch ([launch][tut-launch-h]); the course adds a class, a second node and `use_sim_time` | ✓ | ✓ | keep | [tut-h] | High |
| MOVEIT-V47 | 2.11 Data, 3.3 (found in Phase 2) | the SRDF `home` of the course: `shoulder_pan` 0, `shoulder_lift` −2.5, `elbow` 1.5, `wrist_1` −1.5, `wrist_2` −1.55, `wrist_3` 0; the programs call the joint target (0, −2.3562, 1.5708, −1.5708, −1.5708, 0) "the home position" | ✓ two slightly different poses share the name; `setNamedTarget("home")` uses the SRDF one | ✓ | ✓ | annotate | course text and code | High |
| MOVEIT-V48 | 3.3 (beyond source, Phase 2) | what happens when `move_group` is not running or the description parameters are missing | ✓ the `MoveGroupInterface` constructor throws "Unable to construct robot model. Please make sure all needed information is on the parameter server." without a robot model, and waits for the `move_group` action servers with `wait_for_servers` default −1 (no timeout) ([move_group_interface.cpp][mgi-cpp-h], [header][mgi-h]) | ✓ | ✓ | keep | [mgi-cpp-h] | High |

## Canonical alternatives (features of a later distro)
None needed: every API the notes use exists in Humble. The Jazzy forms (`.hpp` headers, `computeCartesianPath` without
`jump_threshold`) are later spellings of the same calls; `target_link_libraries` with
`moveit_ros_planning_interface::moveit_move_group_interface` already works on Humble.

## Open `[verify]` (Phase 5 or a real machine)
- MOVEIT-V10: `colcon build` of the client package with `install(DIRECTORY launch …)` and no `launch/` folder.
- MOVEIT-V18: two nodes in one process renamed by `Node(name=…)` (duplicate-name warning, any effect on MoveGroupInterface).
- MOVEIT-V19: `SetParameter(name="use_sim_time", value=True)` + the generated move_group launch.
- MOVEIT-V25: the variable order of the `gripper` group (is index 2 the driven knuckle?).
- MOVEIT-V34: the color Gazebo Fortress shows for `<material>Gazebo/Red</material>`.
- MOVEIT-V37: the released `simple_grasping` with the topic remap and `voxel_limit_min:=-1.0` in the course scene.
- MOVEIT-V43: the real `find_objects` result for the course boxes.

## Sources
[tut-h]: https://github.com/moveit/moveit2_tutorials/blob/humble/doc/examples/move_group_interface/src/move_group_interface_tutorial.cpp
[tut-launch-h]: https://github.com/moveit/moveit2_tutorials/blob/humble/doc/examples/move_group_interface/launch/move_group_interface_tutorial.launch.py
[mgi-h]: https://github.com/moveit/moveit2/blob/humble/moveit_ros/planning_interface/move_group_interface/include/moveit/move_group_interface/move_group_interface.h
[mgi-j]: https://github.com/moveit/moveit2/blob/jazzy/moveit_ros/planning_interface/move_group_interface/include/moveit/move_group_interface/move_group_interface.hpp
[mgi-cpp-h]: https://github.com/moveit/moveit2/blob/humble/moveit_ros/planning_interface/move_group_interface/src/move_group_interface.cpp
[hpp-pr]: https://github.com/moveit/moveit2/pull/3113
[ci-h]: https://github.com/moveit/moveit2/blob/humble/moveit_core/robot_state/src/cartesian_interpolator.cpp
[rml-h]: https://github.com/moveit/moveit2/blob/humble/moveit_ros/planning/robot_model_loader/src/robot_model_loader.cpp
[srdfcfg-h]: https://github.com/moveit/moveit2/blob/humble/moveit_setup_assistant/moveit_setup_framework/src/srdf_config.cpp
[tem-h]: https://github.com/moveit/moveit2/blob/humble/moveit_ros/planning/trajectory_execution_manager/src/trajectory_execution_manager.cpp
[csm-h]: https://github.com/moveit/moveit2/blob/humble/moveit_ros/planning/planning_scene_monitor/src/current_state_monitor.cpp
[psm-h]: https://github.com/moveit/moveit2/blob/humble/moveit_ros/planning/planning_scene_monitor/src/planning_scene_monitor.cpp
[mg-h]: https://github.com/moveit/moveit2/blob/humble/moveit_ros/move_group/src/move_group.cpp
[launches-h]: https://github.com/moveit/moveit2/blob/humble/moveit_configs_utils/moveit_configs_utils/launches.py
[builder-h]: https://github.com/moveit/moveit2/blob/humble/moveit_configs_utils/moveit_configs_utils/moveit_configs_builder.py
[smcm-h]: https://github.com/moveit/moveit2/blob/humble/moveit_plugins/moveit_simple_controller_manager/src/moveit_simple_controller_manager.cpp
[abch-h]: https://github.com/moveit/moveit2/blob/humble/moveit_plugins/moveit_simple_controller_manager/include/moveit_simple_controller_manager/action_based_controller_handle.h
[sa-start-h]: https://github.com/moveit/moveit2/blob/humble/moveit_setup_assistant/moveit_setup_core_plugins/src/start_screen_widget.cpp
[sa-coll-h]: https://github.com/moveit/moveit2/blob/humble/moveit_setup_assistant/moveit_setup_srdf_plugins/src/default_collisions_widget.cpp
[sa-cdc-h]: https://github.com/moveit/moveit2/blob/humble/moveit_setup_assistant/moveit_setup_srdf_plugins/src/compute_default_collisions.cpp
[sa-group-h]: https://github.com/moveit/moveit2/blob/humble/moveit_setup_assistant/moveit_setup_srdf_plugins/src/group_edit_widget.cpp
[sa-ctrl-h]: https://github.com/moveit/moveit2/blob/humble/moveit_setup_assistant/moveit_setup_controllers/include/moveit_setup_controllers/moveit_controllers.hpp
[sa-ctrl-src-h]: https://github.com/moveit/moveit2/blob/humble/moveit_setup_assistant/moveit_setup_controllers/src/controllers.cpp
[kin-h]: https://github.com/moveit/moveit2/tree/humble/moveit_kinematics
[mpf-h]: https://github.com/moveit/moveit2/blob/humble/moveit_ros/visualization/motion_planning_rviz_plugin/src/motion_planning_frame.cpp
[pi-cmake-j]: https://github.com/moveit/moveit2/blob/jazzy/moveit_ros/planning_interface/CMakeLists.txt
[aet-h]: https://github.com/ament/ament_cmake/blob/humble/ament_cmake_export_targets/cmake/ament_export_targets.cmake
[rclcpp-pv-h]: https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/parameter_value.hpp
[node-h]: https://github.com/ros2/launch_ros/blob/humble/launch_ros/launch_ros/actions/node.py
[setparam-h]: https://github.com/ros2/launch_ros/blob/humble/launch_ros/launch_ros/actions/set_parameter.py
[nodeargs-h]: https://docs.ros.org/en/humble/How-To-Guides/Node-arguments.html
[cliargs]: https://design.ros2.org/articles/ros_command_line_arguments.html
[gripper-h]: https://github.com/ros-controls/ros2_controllers/blob/humble/gripper_controllers/include/gripper_controllers/gripper_action_controller_impl.hpp
[gripper-adapter-h]: https://github.com/ros-controls/ros2_controllers/blob/humble/gripper_controllers/include/gripper_controllers/hardware_interface_adapter.hpp
[gcmd-h]: https://github.com/ros-controls/control_msgs/blob/humble/control_msgs/msg/GripperCommand.msg
[rqtjtc-h]: https://github.com/ros-controls/ros2_controllers/blob/humble/rqt_joint_trajectory_controller/setup.py
[jsb-h]: https://github.com/ros-controls/ros2_controllers/tree/humble/joint_state_broadcaster
[sg-j-node]: https://github.com/mikeferguson/simple_grasping/blob/jazzy/src/basic_grasping_perception.cpp
[sg-j-seg]: https://github.com/mikeferguson/simple_grasping/blob/jazzy/src/object_support_segmentation.cpp
[sg-j-readme]: https://github.com/mikeferguson/simple_grasping/blob/jazzy/README.md
[sg-changelog]: https://github.com/mikeferguson/simple_grasping/blob/ros2/CHANGELOG.rst
[gm-ros2]: https://github.com/mikeferguson/grasping_msgs/tree/ros2
[solid-h]: https://github.com/ros2/common_interfaces/blob/humble/shape_msgs/msg/SolidPrimitive.msg
[pcl-changes]: https://github.com/PointCloudLibrary/pcl/blob/master/CHANGES.md
[urdf-tut-h]: https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/Adding-Physical-and-Collision-Properties-to-a-URDF-Model.html
[gz-create-j]: https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_sim/src/create.cpp
[gzsim6-sec]: https://github.com/gazebosim/gz-sim/blob/ign-gazebo6/src/SdfEntityCreator.cc
[gzsim8-sec]: https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/SdfEntityCreator.cc
[distro-h]: https://github.com/ros/rosdistro/blob/master/humble/distribution.yaml
