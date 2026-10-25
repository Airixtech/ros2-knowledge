# Version audit — ros2-control (Phase 1)

> Date: 2026-10-24 (part 1: CONTROL-V01–V49; part 2: CONTROL-V50–V82, same day).
> Scope: every version-dependent or checkable statement of the ros2_control course (course wiki, not published).
> Part 1 (units 1–5): controller YAML, the `<ros2_control>` tag, simulation and real-hardware launch files, the
> controller manager (states, `ros2 control` CLI, services, spawner), the hardware interface template and the
> Dynamixel hardware interface. Part 2 (units 6–8): the controllers of ros2_controllers (forward family,
> joint_trajectory_controller, diff_drive_controller), a custom controller (header, methods, realtime tools, plugin,
> CMake, launch) and the quadruped project with its solution. Section IDs = the course's section numbers.
> Baseline: **Jazzy is canonical** for this skill (decision of 2026-10-24): the course's hardware API
> (`on_init(const HardwareComponentInterfaceParams &)`) exists only from Jazzy (ros2_control 4.34.0). **Humble**
> (the team's distro) is annotated and every Humble row names the official `humble` branch; Kilted and Lyrical are
> annotated. Simulation rows (Gazebo Sim, gz_ros2_control) are in [version_audit_gazebo.md](version_audit_gazebo.md)
> (`GZ-Vnn`); generic rows in [version_audit.md](version_audit.md) (`Vnn`, e.g. V09 `ament_target_dependencies`,
> V60 `robot_description` topic, V62 `switch_controllers` flags).

## Method
- Primary sources, read on the matching branch with grep: `ros-controls/ros2_control` (humble 2.54.3, jazzy 4.49.0,
  kilted 5.19.0, master = Lyrical 6.12.0: `hardware_interface`, `controller_manager`, `ros2controlcli`,
  `controller_manager_msgs`, changelogs, `doc/migration.rst`), `ros-controls/ros2_controllers` (humble, jazzy, kilted,
  master: parameter YAML of generate_parameter_library, read by hand because `param_audit.py` does not read it),
  `ros-controls/ros2_control_demos` (humble, jazzy, master: example_1), `ros-controls/control.ros.org` (jazzy: getting
  started), `ros/pluginlib` (jazzy), `dynamixel-community/dynamixel_hardware` (tag 0.6.1, branch jazzy),
  `ROBOTIS-GIT/dynamixel-workbench` (branch `ros2`), `gazebosim/ros_gz` (jazzy), `ros2/rclcpp` (jazzy),
  `ros2/design` (node lifecycle), `ros/rosdistro` (released versions) and the apt indexes of packages.ros.org.
- Course origin (version-audit.md, "Find the course's origin first"): the controller YAML is the official **Humble**
  file `example_1/bringup/config/rrbot_controllers.yaml` of ros2_control_demos (same keys and comments); the hardware
  template is example_1's `RRBotSystemPositionOnlyHardware` in its Humble shape, with the Jazzy `on_init(params)`;
  the Dynamixel code is an older `dynamixel_hardware` (dynamixel-community) adapted the same way; its SDK calls are
  `dynamixel_workbench_toolbox`.
- Part 2 sources, same method: `ros-controls/realtime_tools` (humble 2.15.1, jazzy 3.13.0, kilted 4.10.0, master =
  Lyrical 5.4.0), `ros-controls/control_msgs` (humble 4.9.0, jazzy 5.10.0, master = Kilted and Lyrical 6.10.0),
  `ros-controls/control_toolbox` (jazzy, kilted, master: `RateLimiter`), `ros2_controllers` (`forward_command_controller`,
  `effort_controllers`, `joint_trajectory_controller`, `diff_drive_controller`, `ros2_controllers_test_nodes`,
  `doc/migration.rst`, `doc/release_notes.rst`), `ros2_control` (`controller_interface`, `controller_manager`,
  `hardware_interface/handle.hpp`), `ros2_control_demos` (example_1 test launch files, example_2 diffbot, example_7
  custom controller), `ros-controls/gz_ros2_control` (jazzy `gz_system.cpp`), `ros2/ros2cli` (jazzy `topic pub`),
  `ros2/launch` (jazzy), `open-dynamic-robot-initiative/robot_properties_solo` (master).
- Course logic was reviewed too: launch files against their YAML, explanations against code, printed outputs
  against the tools' print statements. Contradictions are **fix** rows ("course mistake").
- Part 2 origin: the unit 6 diffbot YAML is the official **Humble** `example_2/bringup/config/diffbot_controllers.yaml`
  of ros2_control_demos plus `use_stamped_vel: false`; the unit 6 trajectory YAML is the same Humble demo block as
  part 1; the custom controller of unit 7 (`RRBotController`, JointJog commands, "Copyright (c) 2021, Bence Magyar
  and Denis Stogl") is the controller of the ros2_control maintainers' 2021 "Getting started with ros2_control"
  workshop ([rosconfr-2021]) with Jazzy API calls in `update()`; its appendix keeps the older `update()`. The Solo 8
  model is `robot_properties_solo` (BSD-3-Clause) of the Open Dynamic Robot Initiative.
- Actions: **keep** = correct for Jazzy · **annotate** = correct, add marks (Humble, Kilted, Lyrical) or a precise
  wording · **fix** = wrong for Jazzy itself. Confidence: High (read in code) · Medium (docs, or inferred) ·
  `[verify]` (needs a build or a run).

## Baseline
| | Humble | Jazzy (canonical) | Kilted | Lyrical |
|---|---|---|---|---|
| Release – EOL | May 2022 – May 2027 | May 2024 – May 2029 | May 2025 – Nov 2026 | May 2026 – May 2031 |
| Tier 1 Ubuntu | 22.04 | 24.04 | 24.04 | 26.04 |
| ros2_control (rosdistro) | 2.54.3 (branch `humble`) | 4.49.0 (`jazzy`) | 5.19.0 (`kilted`) | 6.12.0 (`master`) |
| ros2_controllers | 2.54.1 | 4.43.0 | 5.18.0 | 6.10.0 |
| Hardware `on_init` | `on_init(const HardwareInfo &)` | `on_init(const HardwareComponentInterfaceParams &)` (≥ 4.34.0; `HardwareInfo` form deprecated) | same as Jazzy | params form only (6.12.0 removed the deprecated methods) |
| Exporting interfaces | `export_state_interfaces()` / `export_command_interfaces()` returning vectors | framework export from the URDF + `set_state`/`get_command`; the vector methods are deprecated | same as Jazzy | framework export only |
| `robot_description` for the controller manager | parameter of `ros2_control_node` | `/robot_description` topic (robot_state_publisher) | topic | topic |
| `enforce_command_limits` (controller manager) | — | default `false` | default `true` | default `true` |
| `dynamixel_hardware` / ROBOTIS `dynamixel_hardware_interface` | — / 1.5.0 | 0.5.0 / 1.5.2 | 0.6.0 / 1.5.1 | — / 1.5.1 |
| realtime_tools | 2.15.1 (`humble`) | 3.13.0 (`jazzy`) | 4.10.0 (`kilted`) | 5.4.0 (`master`) |
| `realtime_buffer.h` / `realtime_publisher.h` | deprecated (`#pragma message`); `.hpp` exist | deprecated (`#warning`) | removed | removed |
| `RealtimePublisher` `msg_`, `lock()`, `trylock()`, `unlockAndPublish()` | ✓ | ✓; `try_publish(msg)` added | deprecated | removed (`try_publish()` only) |
| `RealtimeBuffer` | ✓ | ✓; `RealtimeThreadSafeBox` added | ✓ | deprecated (5.4.0) |
| control_msgs (`JointJog`, `JointControllerState` unchanged) | 4.9.0 | 5.10.0 | 6.10.0 (`master`) | 6.10.0 (`master`) |
| `CommandInterface::set_value()` / reading a value | `void set_value(double)` / `double get_value()` | `[[nodiscard]] bool set_value()` / `get_optional()`; `get_value()` deprecated | `double get_value()` removed | same as Kilted |
| diff_drive_controller command | `~/cmd_vel` TwistStamped, or `~/cmd_vel_unstamped` Twist with `use_stamped_vel: false` | `~/cmd_vel` TwistStamped only | same | same |

## Real Jazzy errors (fix)
| ID | Section | Origin | Error | Correct statement |
|---|---|---|---|---|
| CONTROL-V01 | 4.19 | course mistake | The real-hardware launch spawns `joint_trajectory_controller`, but the YAML of 4.20 names it `position_trajectory_controller` | The controller manager logs "The 'type' param was not defined for 'joint_trajectory_controller'." and that spawner fails (the other two controllers start). Spawn `position_trajectory_controller`, with `--inactive`, because it claims the same `position` interfaces as `forward_position_controller`. Code: [cm-j], [spawner-j]. |
| CONTROL-V02 | 2.5 | course mistake | The text says the controllers are named `forward_position_controller` and `position_trajectory_controller`; the YAML of 2.5 and 2.9 defines `joint_trajectory_controller` | The name is free; it must match between `controller_manager` and the controller's own block. The notes follow the YAML and say that units 1, 4 and 5 call it `position_trajectory_controller`. |
| CONTROL-V03 | 2.7 | course mistake | `joint_state_broadcaster` publishes on `/rrbot_controller/state` and `/joint_states` | It publishes `joint_states` (`sensor_msgs/JointState`) and `dynamic_joint_states` (`control_msgs/DynamicJointState`), relative names, so `/joint_states` and `/dynamic_joint_states` by default (`~/…` with `use_local_topics`); the publishers are created in `on_configure`. Code: [jsb-j], [jsb-params-j]. |
| CONTROL-V04 | 2.6 | course mistake | "inside the `<gazebo><plugin>` tag we include a `<parameter>` element" | The element is `<parameters>` (as in the XML of the same section). |
| CONTROL-V05 | 2.5 | course mistake | Example controller `joint1_position_controller: type: effort_controllers/JointPositionController` | No such type in ros2_controllers (Humble, Jazzy): `effort_controllers` exports only `effort_controllers/JointGroupEffortController`. Lyrical releases no `effort_controllers` package (CONTROL-V35). Code: [effort-h], [effort-j]. |
| CONTROL-V06 | 2.5, 2.9, 4.20, 5.22, 6.7, 8.9 | Humble demo YAML | `state_publish_rate: 200.0 # Hz, Defaults to 50` under the trajectory controller | Not a JointTrajectoryController parameter in Jazzy (it is ignored): JTC publishes `~/controller_state` in every `update()`, at its update rate. Humble: a parameter, default 50.0. Code: [jtc-params-j], [jtc-j], [jtc-params-h]. |
| CONTROL-V07 | 2.5, 2.9, 4.20, 5.22, 6.7, 8.9 | Humble demo YAML | `goal_time: 0.0 # Defaults to 0.0 (start immediately)` | Humble and Jazzy: default 0.0, and 0.0 means **no time limit** ("the controller will wait a potentially infinite amount of time"), not "start immediately". Lyrical: default 10.0; 0.0 = the goal must be reached on time; a negative value waits indefinitely. The official Humble demo YAML carries the same wrong comment. Code: [jtc-params-j], [jtc-params-m], [rctrl-mig-m]. |
| CONTROL-V08 | 3.5, 5.23 | output of an older release | Spawner output "Configured and started joint_state_broadcaster" (logger `spawner_my_controller_name`) | Humble and Jazzy print "Configured and activated <name>"; the logger is `spawner_<controller>`. Code: [spawner-h], [spawner-j]. |
| CONTROL-V09 | 3.3 | output of an older release | `set_controller_state` prints "successfully configured …" and "successfully started …" | Humble and Jazzy print "Successfully configured <name>", "Successfully deactivated <name>" and "Successfully activated <name>". Code: [cli-scs-h], [cli-scs-j]. |
| CONTROL-V10 | 4.21, 5.23, 6.8, 7.20, 8.9 | output of an older release | `list_controllers` prints `joint_state_broadcaster[joint_state_broadcaster/JointStateBroadcaster] active` | Humble and Jazzy print three columns: name, type, state (as in unit 3). Code: [cli-lc-h], [cli-lc-j]. |
| CONTROL-V11 | 2.4 | course mistake | The output of `ros2 pkg create … --dependencies urdf xacro robot_state_publisher` lists `joint_state_publisher` | The output lists the dependencies given in the command; the notes show the command's three. |
| CONTROL-V12 | 4.16, 7.15 | course mistake | `<library path="my_robot_hardware_interface">` is "the relative path, including the namespace"; "my_robot_hardware_interface is the namespace"; 7.15: `<library>` "specifies the relative path to the library" | `path` is the **library name**: the CMake target `${PROJECT_NAME}` (file `libmy_robot_hardware_interface.so`, `librrbot_controller.so`), which pluginlib looks for in the package's library folders. It matches the namespace only by choice. Code: [pluginlib-j]. |
| CONTROL-V13 | 5.21 | course mistake | The explained snippet reads the YAML from `<package_name>/controllers/controllers.yaml` | The launch file of the same section (and the files of 5.22) use `dynamixel_hardware_interface/config/controller_configuration.yaml`: the code wins. |
| CONTROL-V14 | 5.12, 5.13 | course mistake | `read()` converts to "velocity in m/s and current in m/A"; `write()` converts velocity "from meters per second" | `convertValue2Velocity`/`convertVelocity2Value` use **rad/s** (rpm × 0.104719755); `convertValue2Current(int16_t)` returns **mA** (unit 2.69 mA of the X series). So the `effort` state interface holds a current in mA, not a torque. Code: [dxlwb]. |
| CONTROL-V15 | 3.2 | course mistake | "A transition process can only have two outcomes, either SUCCESS or FAILURE" | Lifecycle callbacks return `SUCCESS`, `FAILURE` or `ERROR`; `ERROR` (or an exception) leads to `ErrorProcessing` and the `on_error` callback. Code: [lifecycle-iface-j], [lifecycle-design]. |
| CONTROL-V16 | 5.8 | course mistake | The four type values are "defined in `hardware_interface::StateInterface`" | They are string constants in `hardware_interface/types/hardware_interface_type_values.hpp`. Humble defines four (`HW_IF_POSITION`, `_VELOCITY`, `_ACCELERATION`, `_EFFORT`); Jazzy adds `_CURRENT`, `_TORQUE`, `_FORCE`, `_TEMPERATURE`, `_PROPORTIONAL`, `_INTEGRAL`, `_DERIVATIVE`, `_FEEDFORWARD`. Code: [rc-types-h], [rc-types-j]. |
| CONTROL-V17 | 3.6 | course mistake | The controller manager makes sure "two controllers cannot claim the same joint" | The conflict is per **command interface**: "Resource conflict for controller '…'. Command interface '…' is already claimed."; state interfaces can be read by any number of controllers. Code: [cm-j]. |
| CONTROL-V50 | 7.4 | course mistake | "This course is for the ROS2 Galactic version" | The unit's code needs Jazzy or later: `[[nodiscard]] bool set_value()` and `get_optional()` exist from the `jazzy` branch; Humble 2.54.3 has `void set_value(double)` and `double get_value()` (CONTROL-V74). Code: [handle-h], [handle-j]. |
| CONTROL-V51 | 6.4 | course mistake | The effort YAML gives `command_interfaces` and `state_interfaces` to `effort_controllers/JointGroupEffortController` | That controller declares only `joints` and `interface_name` (set to `effort` internally); the other keys are ignored without a message. Code: [fcc-params-j], [effort-cpp-j]. |
| CONTROL-V52 | 6.5, 6.6, 6.7 | course mistake | `<state_interface name="acceleration"/>` and `<command_interface name="acceleration">` on joints of `gz_ros2_control/GazeboSimSystem` | GazeboSimSystem registers only `position`, `velocity` and `effort`; any other name is skipped without a message, so these interfaces do not exist. Code: [gzsys-j]. |
| CONTROL-V53 | 6.7 | course mistake | The "configuration file explained" list gives `state_interfaces` "Default: 50.0", `state_publish_rate` "Default: 20.0" and no default for `action_monitor_rate` | The defaults are shifted by one line: `state_interfaces` has none, `state_publish_rate` was 50.0 on Humble (not a Jazzy parameter, CONTROL-V06), `action_monitor_rate` is 20.0. Code: [jtc-params-h], [jtc-params-j]. |
| CONTROL-V54 | 6.8 | course mistake | `ros2 topic pub --rate 30 /diffbot_base_controller/cmd_vel geometry_msgs/msg/TwistStamped "…" -1`, then "You should now see the robot circling" | `-1` (`--once`) publishes one message and exits; `--rate` does not repeat it. With `cmd_vel_timeout: 0.5` the controller brakes half a second later ("Velocity command timed out. Braking."). Leave out `-1` and stop with Ctrl+C. Code: [pub-j], [ddc-j]. |
| CONTROL-V55 | 7.10 | course mistake (logic) | The `get_ordered_interfaces()` template compares `command_interface.get_name()` with a joint name | `get_name()` returns `<joint>/<interface>` (Humble and Jazzy), so the template never matches and returns `false`; the course never calls it. With `INDIVIDUAL` the loaned interfaces already come in the requested order; for `ALL`, `INDIVIDUAL_BEST_EFFORT` or `REGEX` use `controller_interface::get_ordered_interfaces()` from `controller_interface/helpers.hpp`, which compares `get_prefix_name()`. Code: [handle-h], [handle-j], [ci-helpers-j], [ci-base-j]. |
| CONTROL-V56 | 7.11 | course mistake | `writeFromNonRT()` "can be used in real time if no non-rt thread is calling the same function (we are not subscribing to ros callbacks) and there is only one single rt thread" | This controller does subscribe: its `~/commands` callback calls `writeFromNonRT()` too, so the condition does not hold here. `writeFromNonRT()` waits for the buffer's mutex (retrying every 0.5 ms), and the controller manager normally runs the switch, and with it `on_activate()`, inside its real-time `update()`. Jazzy's official custom controller uses `RealtimeThreadSafeBox` instead (`set()` in the callback, `try_get()` in `update()`). Code: [rtbuf-j], [cm-j], [demo7-j]. |
| CONTROL-V57 | 7.7, 7.13 | course mistake (logic) | The command callback checks only `msg->joint_names.size()`; `update()` reads `displacements[i]` for every command interface | A `JointJog` with the right number of names but fewer `displacements` (for example only `velocities`) makes `update()` read past the end of the vector (undefined behaviour). The names are not compared either, so a message with the joints in another order commands the wrong joints. Check `displacements.size()` (and the names) in the callback. Code: course code, [jointjog-j]. |
| CONTROL-V58 | 7.16 | course mistake | `target_compile_definitions(rrbot_controller PUBLIC "PLUGINLIB__DISABLE_BOOST_FUNCTIONS")` "prevents pluginlib from using boost" | pluginlib (humble, jazzy) never reads this definition: the line has no effect, and the official controllers do not have it. Code: [pluginlib-j], [fcc-cmake-j]. |
| CONTROL-V59 | 7.16 | course mistake | The explanation of the `install()` lines: "We also tell CMake to install all launch files under the launch folder" | The `CMakeLists.txt` shown installs only the library and `include/`; `config/` is added in 7.17, and the package has no launch folder. Course file. |
| CONTROL-V60 | 8.9 (solution) | course mistake | "Provide a proper Gazebo integration" shows `<hardware><plugin>` and a `<gazebo><plugin>` with names and a `<robot_sim_type>` element that gz_ros2_control does not provide, and the YAML at `$(find odri_solo_quadruped_bringup)/config/…` | The complete file of the same page uses `gz_ros2_control/GazeboSimSystem`, `gz_ros2_control-system` with `gz_ros2_control::GazeboSimROS2ControlPlugin`, and `$(find my_quadruped_bringup)/config/solo8_controller_config.yaml`: follow the complete file. Code: [gzsys-j], course file. |

## Full table
| # | Section | Statement | Humble | Jazzy | Lyrical | Action | Source | Confidence |
|---|---|---|---|---|---|---|---|---|
| CONTROL-V01 | 4.19 | real-hardware launch spawns `joint_trajectory_controller` | same error | ✗ spawner fails | same | **fix** | [cm-j], [spawner-j] | High |
| CONTROL-V02 | 2.5 | trajectory controller name in text vs YAML | — | ✗ text | — | **fix** | course YAML | High |
| CONTROL-V03 | 2.7 | JSB topics | `/joint_states`, `/dynamic_joint_states` | same | `/dynamic_joint_states` off by default (CONTROL-V34) | **fix** | [jsb-j] | High |
| CONTROL-V04 | 2.6 | `<parameter>` in the text | — | ✗ `<parameters>` | — | **fix** | course XML | High |
| CONTROL-V05 | 2.5 | `effort_controllers/JointPositionController` | ✗ not a type | ✗ | no `effort_controllers` | **fix** | [effort-h], [effort-j] | High |
| CONTROL-V06 | 2.5… | `state_publish_rate` | ✓ default 50 | ✗ not a parameter | ✗ | **fix** | [jtc-params-h], [jtc-params-j] | High |
| CONTROL-V07 | 2.5… | `goal_time: 0.0` "start immediately" | ✗ 0.0 = no limit | ✗ same | default 10.0, 0.0 = on time, < 0 = no limit | **fix** | [jtc-params-j], [rctrl-mig-m] | High |
| CONTROL-V08 | 3.5, 5.23 | spawner "Configured and started" | "Configured and activated" | same | same | **fix** | [spawner-h], [spawner-j] | High |
| CONTROL-V09 | 3.3 | `set_controller_state` messages | "Successfully configured/deactivated/activated" | same | same | **fix** | [cli-scs-h], [cli-scs-j] | High |
| CONTROL-V10 | 4.21, 5.23, 6.8, 7.20, 8.9 | `list_controllers` `name[type] state` | columns | columns | columns | **fix** | [cli-lc-j] | High |
| CONTROL-V11 | 2.4 | `ros2 pkg create` output deps | — | ✗ output | — | **fix** | course command | High |
| CONTROL-V12 | 4.16, 7.15 | `<library path>` = namespace / relative path | ✗ library name | ✗ | ✗ | **fix** | [pluginlib-j] | High |
| CONTROL-V13 | 5.21 | explained YAML path | — | ✗ code wins | — | **fix** | course launch | High |
| CONTROL-V14 | 5.12, 5.13 | Dynamixel units m/s, m/A | rad/s, mA | same | same | **fix** | [dxlwb] | High |
| CONTROL-V15 | 3.2 | two transition outcomes | SUCCESS/FAILURE/ERROR | same | same | **fix** | [lifecycle-iface-j] | High |
| CONTROL-V16 | 5.8 | four type values in `StateInterface` | 4 constants, other header | 12 constants | 12 | **fix** | [rc-types-h], [rc-types-j] | High |
| CONTROL-V17 | 3.6 | "same joint" conflict | per command interface | same | same | **fix** | [cm-j] | High |
| CONTROL-V18 | 4.5–4.7, 5.5–5.7 | `on_init(const HardwareComponentInterfaceParams &)`, header `types/hardware_component_interface_params.hpp` | ✗ absent: `on_init(const HardwareInfo &)` and `SystemInterface::on_init(info)` ([demo1-hw-h]) | ✓ since 4.34.0; the `HardwareInfo` form is deprecated | ✓ only form (6.12.0) | annotate | [rc-hci-j], [rc-hi-cl-j], [rc-si-h] | High |
| CONTROL-V19 | 4.9, 4.10, 5.8, 5.9 | `export_state_interfaces()`/`export_command_interfaces()` returning vectors of interfaces that point to `hw_states_`/`hw_commands_` | ✓ the only way | deprecated ("Exporting is handled by the Framework"): it compiles; the official example_1 exports nothing and uses `set_state()`/`get_command()` by interface name ([demo1-hw-j]) | ✗ removed in 6.12.0: the course code does not compile | annotate | [rc-hci-j], [rc-hi-cl-m], [demo1-hw-j] | High |
| CONTROL-V20 | 4.2 | "because a hardware interface is a plugin, it does not create a ROS2 node" | ✓ | the component is still a plugin, but since 4.35.0 the framework creates a node for it, named after the lower-case `<ros2_control name>` (`get_node()`) | same | annotate | [rc-hci-cpp-j], [rc-hi-cl-j] | High |
| CONTROL-V21 | 4.5 | "a system includes the functionality of a sensor and actuator, so there is not much of a difference" | docs: System = multi-DOF hardware on one communication channel (complex transmissions); Actuator = 1 DOF, one joint; Sensor = read only | same | same | annotate | [getting-started-j] | High |
| CONTROL-V22 | 2.6, 4.18 | `<param name="min">`/`max` in `<command_interface>` | parsed, not enforced by the controller manager | combined with the URDF `<limit>` (the most restrictive wins) and enforced only with controller_manager `enforce_command_limits: true` (default `false`); unit 4 sends 1.57 rad with min/max ±1 | default `true` (also Kilted): 1.57 would be clamped to 1.0 [verify] | annotate | [rc-parser-j], [cm-params-j], [cm-params-k], [cm-params-m] | High |
| CONTROL-V23 | 4.19, 5.21 | `ros2_control_node` with parameters `{"robot_description": …}` + YAML | ✓ required | the controller manager ignores the parameter and reads the `/robot_description` topic (works because robot_state_publisher is launched); the official example_1 passes only `update_rate` | same | annotate | V60, [cm-j], [demo1-launch-j] | High |
| CONTROL-V24 | 3.4 | list of `/controller_manager/*` services | no `cleanup_controller`, no logger or type-description services | + `~/cleanup_controller` (since 4.42.0), `get/set_logger_levels`, `get_type_description` | same | annotate | [cm-j], [cm-cl-j] | High |
| CONTROL-V25 | 3.4 | `ListControllers` response fields | no `is_async`, `update_rate`, `exported_state_interfaces` | ✓ as printed | ✓ | annotate | [cmmsg-cs-h], [cmmsg-cs-j] | High |
| CONTROL-V26 | 3.3 | `set_controller_state <name> inactive/active`; unload after deactivating | states `inactive`, `active` only | + `unconfigured` (cleanup from inactive); unloading an active controller fails: "Could not unload controller with name '…' because it is still active" | same | annotate | [cli-scs-h], [cli-scs-j], [cm-j] | High |
| CONTROL-V27 | 3.3 | commands to an inactive controller do nothing | ✓ | ✓; the forward controller also logs "Can't accept new commands. Controller is not active." (throttled, 1 s) | ✓ | annotate | [fcc-base-j] | High |
| CONTROL-V28 | 2.5… | `open_loop_control: true` | ✓ default false | deprecated (read only): use `interpolate_from_desired_state` and zero feedback gains | ✗ removed | annotate | [jtc-params-j], [rctrl-mig-j], [jtc-params-m] | High |
| CONTROL-V29 | 4.17, 5.19, 7.16 | `set(CMAKE_CXX_STANDARD 14)`; `ament_target_dependencies(...)` | `hardware_interface` (and `controller_interface`, 7.16) export `cxx_std_17`, so linking their targets raises the standard to C++17 [verify build] | same | `ament_target_dependencies` removed (V09): `target_link_libraries(<tgt> PUBLIC hardware_interface::hardware_interface pluginlib::pluginlib rclcpp::rclcpp rclcpp_lifecycle::rclcpp_lifecycle)` as in [demo1-cmake-m] | annotate | [rc-cmake-j], V09 | Medium |
| CONTROL-V30 | 5.4–5.22 | the course's package `dynamixel_hardware_interface` with the `dynamixel_hardware` code | ROBOTIS releases a package with the **same name** (1.5.0) | same (1.5.2); `dynamixel_hardware` itself (0.5.0) is deprecated upstream in favour of the ROBOTIS package | ROBOTIS 1.5.1; `dynamixel_hardware` not released | annotate | [dxlhw-readme], [dxlhw-mig], [robotis-dxlhi], [rosdistro-j] | High |
| CONTROL-V31 | 5.3 | clone DynamixelSDK and dynamixel-workbench (`-b ros2`) and build them | binaries `ros-humble-dynamixel-sdk`, `ros-humble-dynamixel-workbench-toolbox` | `ros-jazzy-dynamixel-sdk`, `ros-jazzy-dynamixel-workbench-toolbox` | released (rosdistro) | annotate | [apt-jammy], [apt-noble], [rosdistro-l] | High |
| CONTROL-V32 | 2.7 | `ros_gz_sim create … "-allow_renaming", "true"` | — | `allow_renaming` is a gflags bool: the flag alone enables renaming, so `"true"` is not read as its value (and `"false"` would still enable it) [verify] | same | annotate | [create-j] | Medium |
| CONTROL-V33 | 3.2 | controller state diagram (P19) | consistent with the lifecycle design: `on_shutdown` from every primary state; omits `ErrorProcessing` | same | same | annotate | [lifecycle-design] | High |
| CONTROL-V34 | 2.7, 3.3 | `/dynamic_joint_states` appears with the broadcaster | ✓ | ✓ (`publish_dynamic_joint_states` default `true`) | parameter deprecated, default `false`: not published unless enabled | annotate | [jsb-params-j], [rctrl-mig-m] | High |
| CONTROL-V35 | 3.3, 6.2–6.5, 8.6 | `list_controller_types` shows `JointGroupEffort/Position/VelocityController`; unit 6 uses them | ✓ | ✓ | deprecated in favour of `forward_command_controller` with `interface_name`, and no `effort_controllers`, `position_controllers`, `velocity_controllers` packages in the Lyrical release | annotate | [rctrl-mig-m], [rosdistro-l] | High |
| CONTROL-V36 | 5.7 | control-table items read with `getItemInfo(joint_ids_[0], …)` | — | logic: the addresses of the **first** servo are used for all servos, so every servo on the bus must have the same control table (same series) | — | annotate | [dxlhw-061] | High |
| CONTROL-V37 | 5.7, 5.12 | `Present_Current` falls back to `Present_Load` | — | logic: the fallback value is still converted with the current unit (2.69 mA), so for servos that only have `Present_Load` the effort value is not a current | — | annotate | [dxlwb] | Medium |
| CONTROL-V38 | 5.7 | `const auto &info_ = params.hardware_info;` | — | shadows the member `info_`, which the base `on_init` filled with the same data: harmless; upstream uses the member | — | keep | [dxlhw-061], [rc-hci-cpp-j] | High |
| CONTROL-V39 | 4.7 | `hardware_interface::HardwareComponentInterface::on_init(params)` | — | `SystemInterface` does not override `on_init`, so this is the same call as `SystemInterface::on_init(params)` of the official demo; the base sets `info_` and parses the interface descriptions | same | keep | [rc-hci-cpp-j], [demo1-hw-j] | High |
| CONTROL-V40 | 2.5 | controller YAML layout (`type` under `controller_manager`) | ✓ (official Humble demo) | ✓; the Jazzy demo also writes `type` in each controller's `ros__parameters` and loads the file with `spawner --param-file` | ✓ | annotate | [demo1-h], [demo1-launch-j] | High |
| CONTROL-V41 | 1.3 | "Successfully loaded controller X into state active" | `ros2 control load_controller --set-state` | same | same | keep | [cli-ld-j] | High |
| CONTROL-V42 | 3.5 | spawner on an already active controller: "Controller already loaded, skipping load_controller" then "Failed to configure controller" | ✓ | ✓ | ✓ | keep | [spawner-h], [spawner-j] | High |
| CONTROL-V44 | 2.7 | the explained snippet names the node `robot_state_pub_node` with `output="both"`; the launch file names it `node_robot_state_publisher` with `output='screen'` (found while writing) | — | course mistake: the launch code wins | — | **fix** | course launch | High |
| CONTROL-V45 | 4.7, 4.9, 4.10 | the text pastes the methods into `my_robot_hardware.cpp`; 4.6 and the CMake source list use `my_robot_hardware_interface.cpp` (found while writing) | — | course mistake: the file is `my_robot_hardware_interface.cpp` | — | **fix** | course CMakeLists | High |
| CONTROL-V46 | 5.5 | the explanation shows `namespace my_robot_hardware_interface` and "protected variables"; the header uses `namespace dynamixel_hardware` and private members (found while writing) | — | course mistake: the header wins | — | **fix** | course header | High |
| CONTROL-V47 | 5.8 | the explained snippet exports `&hw_joint_state_`, a member the class does not have (found while writing) | — | course mistake: the method of the same section uses `&joints_[i].state.position` | — | **fix** | course code | High |
| CONTROL-V48 | 5.10–5.12 | Dynamixel `on_activate()`, `on_deactivate()`, `read()` | — | logic: `on_activate()` ignores the results of `read()`/`write()`; `on_deactivate()` leaves the torque on (servos hold their goal); `read()` returns `OK` after a failed Sync Read and converts the zero-initialised raw values (upstream 1.0 now holds the last state on read errors) | — | annotate | [dxlhw-061], [dxlhw-cl] | High |
| CONTROL-V49 | 5.14, 5.15 | Dynamixel `enable_torque()`, `set_control_mode()` | — | logic: `torque_enabled_` starts `false`, so the first `enable_torque(false)` sends nothing; every mode switch calls `enable_torque(true)` → `reset_command()`, which zeroes the velocity commands of the `write()` cycle that switches to velocity mode; whether a servo with torque still on refuses the mode write [verify] | — | annotate | course code, [dxlhw-061] | High |
| CONTROL-V43 | 1.3 | `switch_controllers` prints "Successfully switched controllers!" and the deactivated/activated lists | prints only "Successfully switched controllers" | ✓ | ✓ | annotate | [cli-sw-h], [cm-j] | High |
| CONTROL-V50 | 7.4 | "This course is for the ROS2 Galactic version" | ✗ the code needs the Jazzy API | ✗ text; the code is Jazzy | code ✓ (header and appendix: V73, V74) | **fix** | [handle-h], [handle-j] | High |
| CONTROL-V51 | 6.4 | `command_interfaces`/`state_interfaces` under `JointGroupEffortController` | ignored | ignored | no `effort_controllers` (V35) | **fix** | [fcc-params-j], [effort-cpp-j] | High |
| CONTROL-V52 | 6.5, 6.6, 6.7 | `acceleration` state and command interfaces with GazeboSimSystem | skipped | skipped without a message | skipped | **fix** | [gzsys-j], [gzsys-l] | High |
| CONTROL-V53 | 6.7 | defaults of the explained JTC list shifted by one line | — | ✗ | — | **fix** | [jtc-params-h], [jtc-params-j] | High |
| CONTROL-V54 | 6.8 | `ros2 topic pub --rate 30 … -1`, "robot circling" | same | ✗ one message, braking after `cmd_vel_timeout` (0.5 s) | same | **fix** | [pub-j], [ddc-j] | High |
| CONTROL-V55 | 7.10 | course `get_ordered_interfaces()` compares `get_name()` with joint names | never matches | never matches; order already given with `INDIVIDUAL` | same | **fix** | [handle-h], [handle-j], [ci-helpers-j], [ci-base-j] | High |
| CONTROL-V56 | 7.11 | `writeFromNonRT()` "can be used in RT if no non-rt thread calls it" | condition not met (the callback writes too) | same; `RealtimeThreadSafeBox` available | `RealtimeBuffer` deprecated (V73) | **fix** | [rtbuf-j], [cm-j], [demo7-j] | High |
| CONTROL-V57 | 7.7, 7.13 | callback checks only the number of joint names | out-of-range read possible | same | same | **fix** | course code, [jointjog-j] | High |
| CONTROL-V58 | 7.16 | `PLUGINLIB__DISABLE_BOOST_FUNCTIONS` "prevents pluginlib from using boost" | no effect | no effect | — | **fix** | [pluginlib-j], [fcc-cmake-j] | High |
| CONTROL-V59 | 7.16 | "we also install all launch files" | — | ✗ not in the file | — | **fix** | course file | High |
| CONTROL-V60 | 8.9 | solution snippet: plugin names and `<robot_sim_type>` not provided by gz_ros2_control, other YAML package | — | ✗ contradicts the complete file | — | **fix** | [gzsys-j], course file | High |
| CONTROL-V61 | 8.4, 8.9 | text: "the ROS package named `solo_description`"; xacro includes: `$(find odri_solo_quadruped_bringup)/description/solo/…` | — | the package named in `$(find)` must be installed for xacro to expand; the course repository is not public [verify] | — | annotate | course files | Medium |
| CONTROL-V62 | 6.2, 8.6 | "available controllers": six types | ros2_controllers also has admittance, steering (Ackermann, bicycle, tricycle), `gpio_controllers`, `gripper_controllers`, mecanum, PID, `tricycle_controller` and the broadcasters | adds `chained_filter_controller`, `motion_primitives_controllers`, `omni_wheel_drive_controller`, `parallel_gripper_controller` and more broadcasters (battery, GPS, magnetometer, state interfaces) | no `position_controllers`, `velocity_controllers`, `effort_controllers`, `gripper_controllers` | annotate | [rctrl-tree-h], [rctrl-tree-j], [rctrl-tree-m] | High |
| CONTROL-V63 | 6.3–6.6 | JointGroup{Position,Effort,Velocity}Controller and ForwardCommandController forward `~/commands` (`std_msgs/Float64MultiArray`) unchanged; ForwardCommandController needs `interface_name`; one joint with several interfaces: `MultiInterfaceForwardCommandController` (`joint`, `interface_names`) | ✓ | ✓ | `forward_command_controller` only (V35) | keep | [fcc-params-j], [fcc-base-j], [fcc-plugin-j] | High |
| CONTROL-V64 | 6.6, 6.7, 6.8 | `min`/`max` ±1 with larger commands (1.14 rad; diffbot 0.2 m/s on 0.015 m wheels ≈ 13.3 rad/s) | not enforced | not enforced (`enforce_command_limits: false`) | clamped to ±1, the diffbot then reaches at most 0.015 m/s [verify] | annotate | V22, [cm-params-k], [cm-params-m] | High |
| CONTROL-V65 | 6.7 | "the joints must reach the waypoints within a goal tolerance, otherwise the controller will inform a failure" | same as Jazzy | tolerances default to 0.0 = not enforced; a violated tolerance aborts an action goal and tells the client; with the `~/joint_trajectory` topic nobody is told, and a violated state tolerance aborts the trajectory and holds the position | same | annotate | [jtc-doc-j], [jtc-tol-j] | High |
| CONTROL-V66 | 6.7, 8.7 | JTC takes trajectories on `~/joint_trajectory` (`trajectory_msgs/JointTrajectory`) and the action `<name>/follow_joint_trajectory`; the course's test scripts publish to `/position_trajectory_controller/joint_trajectory` | ✓; state on `~/controller_state` and the older `~/state`; `JointTrajectoryControllerState` also has `desired`, `actual` | ✓; state on `~/controller_state` (`reference`, `feedback`, `error`, `output`) | ✓ | keep | [jtc-h], [jtc-j], [cmsg-jtcs-h], [cmsg-jtcs-j], [testnodes-j], [demo1-test-j] | High |
| CONTROL-V67 | 6.8 | `use_stamped_vel: false` | parameter, default `true`; `false` → `geometry_msgs/Twist` on `~/cmd_vel_unstamped`, so the course's TwistStamped on `~/cmd_vel` has no subscriber | removed: TwistStamped on `~/cmd_vel` only, the key is ignored | same | annotate | [ddc-h], [ddc-params-h], [rctrl-mig-j] | High |
| CONTROL-V68 | 6.8 | `has_velocity/acceleration/jerk_limits`, `min_acceleration`, `max_jerk: 0.0`, `min_jerk: 0.0` | `has_*` default `false` (the course sets velocity and acceleration `true`, jerk `false`) | deprecated, with a warning; `false` sets those limits to NaN; `min_acceleration` deprecated (use `max_deceleration`) and not read by the code: the limiter uses −`max_acceleration`, the same −1.0; the Jazzy demo leaves the `has_*` and jerk lines out | Kilted and Lyrical: removed; the jerk lines become limits of 0, and the rate limiter then never raises the speed from 0, so the diffbot does not move [verify] | annotate | [ddc-params-h], [ddc-params-j], [ddc-params-m], [ddc-j], [ctb-rl-m], [demo2-j], [rctrl-mig-k] | High |
| CONTROL-V69 | 6.8 | `publish_rate: 50.0` (odometry and TF) | ✓ | ✓ | Kilted ✓; Lyrical: removed (6.7.0) | annotate | [rctrl-rn-m] | High |
| CONTROL-V70 | 6.8 | the controller "reads in position and velocity states from the wheels, estimates the position … and publishes nav_msgs/Odometry", with `open_loop: true` | with `open_loop: true` (course and official demo) odometry comes from the commanded velocities, not the wheel states | same | same | annotate | [ddc-params-j] | High |
| CONTROL-V71 | 6.8 | topics `/controller_manager/introspection_data/*`, `/controller_manager/activity`, `/controller_manager/statistics/*` | none | introspection ≥ 4.27.0, activity ≥ 4.28.0, statistics ≥ 4.37.0 | ✓ | annotate | [cm-cl-j] | High |
| CONTROL-V72 | 6.8 | launch output `[ros2-1] Sucessfully loaded controller … into state active` | — | typo of "Successfully loaded controller <name> into state active" (`load_controller --set-state active`, V41) | — | keep | [cli-ld-j] | High |
| CONTROL-V73 | 7.4, 7.7, 7.13 | `realtime_buffer.h`, `realtime_publisher.h`, `RealtimeBuffer`, `RealtimePublisher(publisher)`, `msg_`, `lock()`, `unlock()`, `trylock()`, `unlockAndPublish()` | `.h` deprecated (`#pragma message`), `.hpp` exist; API ✓ | `.h` deprecated (`#warning`); API ✓; `try_publish(msg)`, constructor `(node, topic, qos)` and `RealtimeThreadSafeBox` available | Kilted: `.h` removed, `msg_`/`lock`/`unlock`/`trylock`/`unlockAndPublish` deprecated; Lyrical: those removed (`msg_` private), constructor from a publisher deprecated, `RealtimeBuffer` deprecated | annotate | [rt-pub-h], [rt-pub-j], [rt-pub-k], [rt-pub-m], [rt-buf-m], [rt-cl-m], [rt-doc-m] | High |
| CONTROL-V74 | 7.13, 7.20 | `bool ok = set_value(…)` and `get_optional()` in 7.13; the appendix's `set_value(…)` unchecked and `get_value()` | only the appendix form compiles | 7.13 form; the appendix compiles with warnings (`[[nodiscard]]`, deprecated `get_value()`) | the appendix does not compile (`double get_value()` removed) | annotate | [handle-h], [handle-j], [handle-k], [handle-m] | High |
| CONTROL-V75 | 7.6 | an `on_init()` ERROR "will transition into finalized" | same | the controller node is shut down (finalized), `init()` returns ERROR, the controller manager logs "Could not initialize the controller named '<name>'" and does not load it | same | annotate | [ci-base-cpp-h], [ci-base-cpp-j], [cm-j] | High |
| CONTROL-V76 | 7.8 | three configuration types `ALL`, `INDIVIDUAL`, `NONE` | ✓ | also `INDIVIDUAL_BEST_EFFORT` and `REGEX` | same | annotate | [ci-base-h], [ci-base-j] | High |
| CONTROL-V77 | 7.4–7.13 | `ControllerInterface` API: `on_init()`, `auto_declare()`, `get_node()`, `*_interface_configuration() const`, `on_configure/activate/deactivate(state)`, `update(time, period)`, the `CallbackReturn` alias | ✓; controller nodes allow undeclared parameters and declare YAML keys automatically; an `update()` ERROR is only logged | ✓; controller nodes have only `enable_logger_service`: reading an undeclared parameter throws `ParameterNotDeclaredException`; an `update()` ERROR deactivates the controller and activates its fallback controllers | as Jazzy | keep | [ci-base-h], [ci-base-j], [ci-base-m], [cm-j], [cm-h] | High |
| CONTROL-V78 | 7.19 | `OnExecutionComplete(target_action=gz_spawn_entity)` plus a 10 s `TimerAction` | — | for a process the event fires when it has exited: the broadcaster spawner starts 10 s after `create` exits (unit 2: right away); `ExecuteProcess`, `IncludeLaunchDescription`, `PythonLaunchDescriptionSource` are imported and not used | — | keep | [launch-action-j], [launch-exec-j] | High |
| CONTROL-V79 | 8.3 | Solo: 24 cm standing height, just over 2 kg, 3D-printed structure; Solo 8 has two joints per leg, Solo 12 three | — | consistent with the 2020 announcement of NYU and the Max Planck Institute | — | keep | [solo-nyu] | Medium |
| CONTROL-V80 | 8.4 | starter xacro "copied and modified from robot_properties_solo"; a comment links an internal upstream address | — | same base link (mass 1.43315091) and leg macro; the comment's address is internal to the upstream lab (left out) | — | keep | [solo-xacro] | High |
| CONTROL-V81 | 7.3, 7.16 | `ros2 pkg create … example_interfaces`; `test_depend`s in package.xml | — | not used by the code: harmless | — | keep | course files | High |
| CONTROL-V82 | 8.4 | `solo_quadruped` macro: `<child link="${prefix}base_link" />` but `<link name="base_link">` (found while writing) | — | logic: consistent only with `prefix=""`, which the course passes; any other prefix names a link that does not exist | — | annotate | course file | High |

## Humble alternatives (features that exist only in Jazzy or later)
| Jazzy feature | Humble way (checked in the `humble` branch) |
|---|---|
| `on_init(const HardwareComponentInterfaceParams & params)` | `on_init(const hardware_interface::HardwareInfo & info)` calling `hardware_interface::SystemInterface::on_init(info)` ([demo1-hw-h]) |
| framework export + `set_state()`/`get_command()` | `export_state_interfaces()`/`export_command_interfaces()` with pointers to member vectors ([demo1-hw-h]) |
| `set_controller_state <name> unconfigured`, `~/cleanup_controller` | none: `unload_controller` and `load_controller` again |
| `enforce_command_limits` | none in the controller manager |
| node per hardware component (`get_node()`) | none |
| `is_async`, `update_rate` in `ListControllers` | none |
| `HW_IF_CURRENT`, `HW_IF_TORQUE`… constants | the interface name as a string (`"current"`): names are strings, the constants are conveniences |
| controller manager reads `/robot_description` | pass `robot_description` as a parameter of `ros2_control_node` (CONTROL-V23) |
| `bool ok = command_interfaces_[i].set_value(v)`, `get_optional()` | `command_interfaces_[i].set_value(v)` (returns nothing) and `get_value()`: the form of the course appendix ([handle-h]) (CONTROL-V74) |
| `realtime_tools::RealtimeThreadSafeBox` (`set()`, `try_get()`) | `realtime_tools::RealtimeBuffer` (`writeFromNonRT()`, `readFromRT()`) as in the course, header `realtime_tools/realtime_buffer.hpp` ([rt-pub-h] folder) |
| `RealtimePublisher::try_publish(msg)` | `trylock()`, fill `msg_`, `unlockAndPublish()` as in the course ([rt-pub-h]) |
| `INDIVIDUAL_BEST_EFFORT`, `REGEX` interface configurations | `INDIVIDUAL` with the full names, or `ALL` plus `controller_interface::get_ordered_interfaces()` ([ci-base-h]) |
| diff_drive_controller: only TwistStamped on `~/cmd_vel` | TwistStamped on `~/cmd_vel` with `use_stamped_vel: true` (the default), or Twist on `~/cmd_vel_unstamped` with `false` ([ddc-h]) (CONTROL-V67) |
| controller manager introspection, statistics and activity topics | none |

## Updates to other reports (found during this audit)
- **GZ-V31 resolved** (version_audit_gazebo.md): gz_ros2_control's `gz_system.cpp` does not clamp commands; the
  controller manager clamps to the most restrictive of the URDF `<limit>` and the interface `min`/`max` only with
  `enforce_command_limits: true` (Jazzy default `false`, Kilted and Lyrical `true`) (CONTROL-V22).
- **GZ-V34 narrowed**: the controller manager limits velocity commands only with `enforce_command_limits: true`
  (Jazzy default `false`); whether Gazebo's physics applies the URDF velocity limit stays `[verify]`.
- **GZ-V59 (new)**: Lyrical releases no `velocity_controllers` package; use `forward_command_controller/ForwardCommandController`
  with `interface_name: velocity` (CONTROL-V35), for the velocity controller of the Gazebo course notes.
- Part 2: no new rows in other reports. CONTROL-V52 confirms ros2-gazebo's rule that GazeboSimSystem accepts only
  `position`, `velocity` and `effort` (jazzy and lyrical `gz_system.cpp`).

## Open `[verify]` (Phase 5 or a real machine)
- CONTROL-V22: on Kilted/Lyrical, the unit 4 command of 1.57 rad with `min`/`max` ±1 is clamped to 1.0.
- CONTROL-V29: the template package builds on Jazzy with `CMAKE_CXX_STANDARD 14` (C++17 raised by the target).
- CONTROL-V32: `ros2 run ros_gz_sim create … -allow_renaming false` still renames.
- CONTROL-V61: the package that holds the Solo 8 description in the course workspace (`solo_description` in the
  text, `odri_solo_quadruped_bringup` in the xacro `$(find)`).
- CONTROL-V64: on Kilted/Lyrical the forward command of 1.14 rad and the diffbot wheel commands are clamped to ±1.
- CONTROL-V68: on Kilted/Lyrical the diffbot with the course YAML (`max_jerk: 0.0`, `min_jerk: 0.0`) does not move;
  with the jerk lines removed (or `.NAN`) it does.
- Phase 5 (part 2): build `rrbot_controller` on `ros:jazzy` (the course includes `<limits>` but uses `std::isnan`,
  declared in `<cmath>`), its Humble form (Humble alternatives table) on `ros:humble`, and the Lyrical form
  (`.hpp` headers, `try_publish()`, `target_link_libraries`) on `ros:lyrical`.
- Phase 5 (optional): build `my_robot_hardware_interface` and the Dynamixel package in dummy mode on `ros:jazzy`
  and the Humble form of the template (Humble alternatives table) on `ros:humble`.

## Sources
[cm-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/controller_manager/src/controller_manager.cpp
[cm-h]: https://github.com/ros-controls/ros2_control/blob/humble/controller_manager/src/controller_manager.cpp
[cm-cl-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/controller_manager/CHANGELOG.rst
[cm-params-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/controller_manager/src/controller_manager_parameters.yaml
[cm-params-k]: https://github.com/ros-controls/ros2_control/blob/kilted/controller_manager/src/controller_manager_parameters.yaml
[cm-params-m]: https://github.com/ros-controls/ros2_control/blob/master/controller_manager/src/controller_manager_parameters.yaml
[spawner-h]: https://github.com/ros-controls/ros2_control/blob/humble/controller_manager/controller_manager/spawner.py
[spawner-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/controller_manager/controller_manager/spawner.py
[cli-scs-h]: https://github.com/ros-controls/ros2_control/blob/humble/ros2controlcli/ros2controlcli/verb/set_controller_state.py
[cli-scs-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/ros2controlcli/ros2controlcli/verb/set_controller_state.py
[cli-lc-h]: https://github.com/ros-controls/ros2_control/blob/humble/ros2controlcli/ros2controlcli/verb/list_controllers.py
[cli-lc-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/ros2controlcli/ros2controlcli/verb/list_controllers.py
[cli-ld-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/ros2controlcli/ros2controlcli/verb/load_controller.py
[cli-sw-h]: https://github.com/ros-controls/ros2_control/blob/humble/ros2controlcli/ros2controlcli/verb/switch_controllers.py
[cmmsg-cs-h]: https://github.com/ros-controls/ros2_control/blob/humble/controller_manager_msgs/msg/ControllerState.msg
[cmmsg-cs-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/controller_manager_msgs/msg/ControllerState.msg
[rc-hci-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/include/hardware_interface/hardware_component_interface.hpp
[rc-hci-cpp-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/src/hardware_component_interface.cpp
[rc-si-h]: https://github.com/ros-controls/ros2_control/blob/humble/hardware_interface/include/hardware_interface/system_interface.hpp
[rc-hi-cl-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/CHANGELOG.rst
[rc-hi-cl-m]: https://github.com/ros-controls/ros2_control/blob/master/hardware_interface/CHANGELOG.rst
[rc-types-h]: https://github.com/ros-controls/ros2_control/blob/humble/hardware_interface/include/hardware_interface/types/hardware_interface_type_values.hpp
[rc-types-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/include/hardware_interface/types/hardware_interface_type_values.hpp
[rc-parser-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/src/component_parser.cpp
[rc-cmake-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/CMakeLists.txt
[jsb-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/joint_state_broadcaster/src/joint_state_broadcaster.cpp
[jsb-params-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/joint_state_broadcaster/src/joint_state_broadcaster_parameters.yaml
[jtc-params-h]: https://github.com/ros-controls/ros2_controllers/blob/humble/joint_trajectory_controller/src/joint_trajectory_controller_parameters.yaml
[jtc-params-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/joint_trajectory_controller/src/joint_trajectory_controller_parameters.yaml
[jtc-params-m]: https://github.com/ros-controls/ros2_controllers/blob/master/joint_trajectory_controller/src/joint_trajectory_controller_parameters.yaml
[jtc-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/joint_trajectory_controller/src/joint_trajectory_controller.cpp
[rctrl-mig-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/doc/migration.rst
[rctrl-mig-m]: https://github.com/ros-controls/ros2_controllers/blob/master/doc/migration.rst
[fcc-base-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/forward_command_controller/src/forward_controllers_base.cpp
[effort-h]: https://github.com/ros-controls/ros2_controllers/blob/humble/effort_controllers/effort_controllers_plugins.xml
[effort-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/effort_controllers/effort_controllers_plugins.xml
[demo1-h]: https://github.com/ros-controls/ros2_control_demos/blob/humble/example_1/bringup/config/rrbot_controllers.yaml
[demo1-hw-h]: https://github.com/ros-controls/ros2_control_demos/blob/humble/example_1/hardware/rrbot.cpp
[demo1-hw-j]: https://github.com/ros-controls/ros2_control_demos/blob/jazzy/example_1/hardware/rrbot.cpp
[demo1-launch-j]: https://github.com/ros-controls/ros2_control_demos/blob/jazzy/example_1/bringup/launch/rrbot.launch.py
[demo1-cmake-m]: https://github.com/ros-controls/ros2_control_demos/blob/master/example_1/CMakeLists.txt
[getting-started-j]: https://github.com/ros-controls/control.ros.org/blob/jazzy/doc/getting_started/getting_started.rst
[pluginlib-j]: https://github.com/ros/pluginlib/blob/jazzy/pluginlib/include/pluginlib/class_loader_imp.hpp
[lifecycle-iface-j]: https://github.com/ros2/rclcpp/blob/jazzy/rclcpp_lifecycle/include/rclcpp_lifecycle/node_interfaces/lifecycle_node_interface.hpp
[lifecycle-design]: https://github.com/ros2/design/blob/gh-pages/articles/node_lifecycle.md
[create-j]: https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_sim/src/create.cpp
[dxlhw-061]: https://github.com/dynamixel-community/dynamixel_hardware/tree/0.6.1
[dxlhw-readme]: https://github.com/dynamixel-community/dynamixel_hardware/blob/jazzy/README.md
[dxlhw-mig]: https://github.com/dynamixel-community/dynamixel_hardware/blob/jazzy/docs/migration_to_dynamixel_hardware_interface.md
[robotis-dxlhi]: https://github.com/ROBOTIS-GIT/dynamixel_hardware_interface
[dxlwb]: https://github.com/ROBOTIS-GIT/dynamixel-workbench/blob/ros2/dynamixel_workbench_toolbox/src/dynamixel_workbench_toolbox/dynamixel_workbench.cpp
[rosdistro-j]: https://github.com/ros/rosdistro/blob/master/jazzy/distribution.yaml
[rosdistro-l]: https://github.com/ros/rosdistro/blob/master/lyrical/distribution.yaml
[apt-jammy]: http://packages.ros.org/ros2/ubuntu/dists/jammy/main/binary-amd64/Packages.gz
[apt-noble]: http://packages.ros.org/ros2/ubuntu/dists/noble/main/binary-amd64/Packages.gz
[dxlhw-cl]: https://github.com/dynamixel-community/dynamixel_hardware/blob/jazzy/dynamixel_hardware/CHANGELOG.rst
[rosconfr-2021]: https://control.ros.org/jazzy/_downloads/9889caef43ffab44b1fb8d6d1e5f0372/2021-06_RosConFR_Getting_started_with_ros2_control.pdf
[handle-h]: https://github.com/ros-controls/ros2_control/blob/humble/hardware_interface/include/hardware_interface/handle.hpp
[handle-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/include/hardware_interface/handle.hpp
[handle-k]: https://github.com/ros-controls/ros2_control/blob/kilted/hardware_interface/include/hardware_interface/handle.hpp
[handle-m]: https://github.com/ros-controls/ros2_control/blob/master/hardware_interface/include/hardware_interface/handle.hpp
[ci-base-h]: https://github.com/ros-controls/ros2_control/blob/humble/controller_interface/include/controller_interface/controller_interface_base.hpp
[ci-base-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/controller_interface/include/controller_interface/controller_interface_base.hpp
[ci-base-m]: https://github.com/ros-controls/ros2_control/blob/master/controller_interface/include/controller_interface/controller_interface_base.hpp
[ci-base-cpp-h]: https://github.com/ros-controls/ros2_control/blob/humble/controller_interface/src/controller_interface_base.cpp
[ci-base-cpp-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/controller_interface/src/controller_interface_base.cpp
[ci-helpers-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/controller_interface/include/controller_interface/helpers.hpp
[fcc-params-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/forward_command_controller/src/forward_command_controller_parameters.yaml
[fcc-plugin-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/forward_command_controller/forward_command_plugin.xml
[fcc-cmake-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/forward_command_controller/CMakeLists.txt
[effort-cpp-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/effort_controllers/src/joint_group_effort_controller.cpp
[jtc-h]: https://github.com/ros-controls/ros2_controllers/blob/humble/joint_trajectory_controller/src/joint_trajectory_controller.cpp
[jtc-doc-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/joint_trajectory_controller/doc/userdoc.rst
[jtc-tol-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/joint_trajectory_controller/include/joint_trajectory_controller/tolerances.hpp
[testnodes-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/ros2_controllers_test_nodes/ros2_controllers_test_nodes/publisher_joint_trajectory_controller.py
[ddc-h]: https://github.com/ros-controls/ros2_controllers/blob/humble/diff_drive_controller/src/diff_drive_controller.cpp
[ddc-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/diff_drive_controller/src/diff_drive_controller.cpp
[ddc-params-h]: https://github.com/ros-controls/ros2_controllers/blob/humble/diff_drive_controller/src/diff_drive_controller_parameter.yaml
[ddc-params-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/diff_drive_controller/src/diff_drive_controller_parameter.yaml
[ddc-params-m]: https://github.com/ros-controls/ros2_controllers/blob/master/diff_drive_controller/src/diff_drive_controller_parameter.yaml
[rctrl-mig-k]: https://github.com/ros-controls/ros2_controllers/blob/kilted/doc/migration.rst
[rctrl-rn-m]: https://github.com/ros-controls/ros2_controllers/blob/master/doc/release_notes.rst
[rctrl-tree-h]: https://github.com/ros-controls/ros2_controllers/tree/humble
[rctrl-tree-j]: https://github.com/ros-controls/ros2_controllers/tree/jazzy
[rctrl-tree-m]: https://github.com/ros-controls/ros2_controllers/tree/master
[ctb-rl-m]: https://github.com/ros-controls/control_toolbox/blob/master/control_toolbox/include/control_toolbox/rate_limiter.hpp
[demo1-test-j]: https://github.com/ros-controls/ros2_control_demos/blob/jazzy/example_1/bringup/launch/test_joint_trajectory_controller.launch.py
[demo2-j]: https://github.com/ros-controls/ros2_control_demos/blob/jazzy/example_2/bringup/config/diffbot_controllers.yaml
[demo7-j]: https://github.com/ros-controls/ros2_control_demos/blob/jazzy/example_7/controller/r6bot_controller.cpp
[jointjog-j]: https://github.com/ros-controls/control_msgs/blob/jazzy/control_msgs/msg/JointJog.msg
[cmsg-jtcs-h]: https://github.com/ros-controls/control_msgs/blob/humble/control_msgs/msg/JointTrajectoryControllerState.msg
[cmsg-jtcs-j]: https://github.com/ros-controls/control_msgs/blob/jazzy/control_msgs/msg/JointTrajectoryControllerState.msg
[rtbuf-j]: https://github.com/ros-controls/realtime_tools/blob/jazzy/realtime_tools/include/realtime_tools/realtime_buffer.hpp
[rt-pub-h]: https://github.com/ros-controls/realtime_tools/blob/humble/include/realtime_tools/realtime_publisher.hpp
[rt-pub-j]: https://github.com/ros-controls/realtime_tools/blob/jazzy/realtime_tools/include/realtime_tools/realtime_publisher.hpp
[rt-pub-k]: https://github.com/ros-controls/realtime_tools/blob/kilted/realtime_tools/include/realtime_tools/realtime_publisher.hpp
[rt-pub-m]: https://github.com/ros-controls/realtime_tools/blob/master/realtime_tools/include/realtime_tools/realtime_publisher.hpp
[rt-buf-m]: https://github.com/ros-controls/realtime_tools/blob/master/realtime_tools/include/realtime_tools/realtime_buffer.hpp
[rt-cl-m]: https://github.com/ros-controls/realtime_tools/blob/master/realtime_tools/CHANGELOG.rst
[rt-doc-m]: https://github.com/ros-controls/realtime_tools/blob/master/doc/index.rst
[gzsys-j]: https://github.com/ros-controls/gz_ros2_control/blob/jazzy/gz_ros2_control/src/gz_system.cpp
[gzsys-l]: https://github.com/ros-controls/gz_ros2_control/blob/lyrical/gz_ros2_control/src/gz_system.cpp
[pub-j]: https://github.com/ros2/ros2cli/blob/jazzy/ros2topic/ros2topic/verb/pub.py
[launch-action-j]: https://github.com/ros2/launch/blob/jazzy/launch/launch/action.py
[launch-exec-j]: https://github.com/ros2/launch/blob/jazzy/launch/launch/actions/execute_local.py
[solo-nyu]: https://engineering.nyu.edu/news/open-source-low-cost-quadruped-robot-makes-sophisticated-robotics-available-all
[solo-xacro]: https://github.com/open-dynamic-robot-initiative/robot_properties_solo/blob/master/src/robot_properties_solo/resources/xacro/solo8.urdf.xacro
