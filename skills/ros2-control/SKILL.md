---
name: ros2-control
description: "ros2_control on ROS 2 (Jazzy; Humble noted): controller manager, controller YAML, <ros2_control> tag, ros2 control CLI, spawner, hardware interfaces, Dynamixel."
---
# ros2-control — controllers and hardware interfaces with ros2_control

Atomic notes for writing correct ros2_control configurations and hardware interfaces. **Jazzy is canonical** (the course's API); Humble, Kilted and Lyrical differences are marked, never substituted, and every Humble difference names the official `humble` source. Paths are relative to this skill's folder. `[[note-id]]` means the file `<note-id>.md`; find it via the area index or a glob `**/<note-id>.md`.

## Golden rules (always apply)
1. Check the user's distro first: on **Humble** a hardware interface uses `on_init(const HardwareInfo &)` and the controller manager needs `robot_description` as a parameter ([[control-humble-to-jazzy]]); on **Lyrical** `export_state_interfaces()`/`export_command_interfaces()` and the `HardwareInfo` `on_init` no longer exist, and the `JointGroup{Position,Velocity,Effort}Controller` packages are not released (use `forward_command_controller/ForwardCommandController` with `interface_name`) ([[control-jazzy-to-lyrical]]).
2. Controller YAML: the `controller_manager` block holds `update_rate` and each controller's name and `type`; each controller's parameters go in its own root block; `joints` must be URDF joints listed in `<ros2_control>` ([[control-controller-config]]).
3. Check every controller key in that controller's `*_parameters.yaml` on the user's branch: unknown keys are ignored silently (`state_publish_rate` is gone in Jazzy, `goal_time: 0.0` means no limit until Lyrical makes 10.0 the default) ([[control-jtc-parameters]]).
4. `<ros2_control>`: one block per hardware component, `<plugin>` = the plugin `name` of its XML, `<param>` values for `on_init()`, and only the interfaces the plugin really accepts; `min`/`max` clamp only with `enforce_command_limits: true` (Jazzy default false, Kilted/Lyrical true) ([[control-urdf-tag]]).
5. Simulation: the controller YAML goes into the gz_ros2_control `<parameters>` and spawners start after the robot is spawned; real hardware: launch `ros2_control_node` with the YAML plus `robot_state_publisher` ([[control-bringup-sim-launch]], [[control-bringup-hardware-launch]]).
6. A controller moves joints only when **active**. Two controllers that claim the same command interfaces cannot both be active: spawn the second with `--inactive` and use `switch_controllers`; deactivate before unloading ([[control-controller-lifecycle]], [[control-cli-state-changes]], [[control-services-spawner]]).
7. Debug from the states: `ros2 control list_controllers` (unconfigured = no topics, inactive = topics without effect), `list_hardware_components`, then the spawner and controller manager logs ([[control-cli-list]]).
8. A hardware interface is a pluginlib plugin derived from `SystemInterface`/`ActuatorInterface`/`SensorInterface`: parameters in `on_init()`, communication in `on_configure()`, `read()`/`write()` every cycle; `ERROR` from them calls `on_error()`, and unless that returns `SUCCESS` the component ends finalized until the plugin is reloaded; on Jazzy+ prefer the framework's interfaces with `set_state()`/`get_command()` ([[control-hw-interface-concept]], [[control-hw-template-export]], [[control-hw-template-activate-rw]]).
9. Register it: `PLUGINLIB_EXPORT_CLASS` after the namespace, a plugin XML whose `library path` is the CMake library target, and `pluginlib_export_plugin_description_file(hardware_interface <xml>)`; on Lyrical link with `target_link_libraries` and namespaced targets (`ament_target_dependencies` is removed) ([[control-hw-plugin-export]], [[control-hw-package-build]]).
10. Dynamixel: the course's code is the deprecated `dynamixel_hardware`; for real servos recommend ROBOTIS's `dynamixel_hardware_interface` (the course package has the same name and hides it) and the SDK from apt ([[control-dynamixel-sdk]]).

## Retrieval protocol
1. Pick the area from the **Areas** table below (column "Covers").
2. Open that area's `_index.md` and choose notes by their summary.
3. Open 1–3 notes. Use their YAML, XML, launch and C++ code as the template: keep the structure, adapt the names.
4. No clear match → `grep -ril "<keyword>" notes/` (API, verb and parameter names work best: `set_controller_state`, `enforce_command_limits`, `HardwareComponentInterfaceParams`, `PLUGINLIB_EXPORT_CLASS`) and open the top hits.
5. Follow a note's `see:` links **one hop** at most; URDF and xacro questions go to ros2-urdf.
6. Do not open `learn/` unless the question is about the ros2_control course (rrbot, units 1–5).
7. Humble, Kilted, Lyrical or porting a hardware interface → open `migration/` and apply the version marks.
8. Simulation → answer with modern Gazebo (Gazebo Sim with gz_ros2_control); simulator details are in the ros2-gazebo skill.
If the notes do not cover the question, read the official source for the user's distro (below) or say that you answer from standard knowledge. Never invent parameters, verbs or methods.

## Version marks and official sources
`[Humble: …]` what Humble needs instead · `[≥Jazzy]` / `[≥Jazzy 4.x]` added in Jazzy (from that ros2_control release) · `[changed in Kilted: …]` / `[changed in Lyrical: …]` what to use there · `[verify]` not confirmed by a source or a build: tell the user. Simulation lines use the distro + Gazebo pairs of ros2-gazebo (`[Humble + Fortress]`, `[Lyrical + Jetty]`). Each note's `version_notes` holds the source URL and audit ID of every difference (`reports/version_audit_control.md`).

| Distro | ros2_control / ros2_controllers | Read first |
|---|---|---|
| Humble | 2.54 / 2.54 | branches `humble` of ros2_control, ros2_controllers and ros2_control_demos (example_1) |
| Jazzy | 4.49 / 4.43 | branches `jazzy`; `doc/migration.rst` of ros2_control and ros2_controllers (Humble → Jazzy) |
| Kilted | 5.19 / 5.18 | branches `kilted`; their `doc/migration.rst` (Jazzy → Kilted) |
| Lyrical | 6.12 / 6.10 | branches `master`; their `doc/migration.rst` (Kilted → Lyrical) |

## Areas
<!-- INDEX:START -->
<!-- generated by tools/build_index.py — do not edit by hand -->
| Area | Notes | Open | Covers |
|---|---|---|---|
| framework | 2 | `notes/framework/_index.md` | What ros2_control is: controller manager, resource manager, hardware components, controllers and their interfaces; controller lifecycle states and transitions |
| setup | 5 | `notes/setup/_index.md` | Controller YAML (controller_manager, update_rate, types, forward_command_controller, JTC parameters), the <ros2_control> URDF tag, simulation and real-hardware launch files, spawner order |
| manager | 3 | `notes/manager/_index.md` | ros2 control CLI (list_controllers, list_controller_types, set_controller_state, load/unload, switch_controllers), controller_manager services, spawner |
| hardware | 14 | `notes/hardware/_index.md` | Writing a hardware interface: SystemInterface methods, on_init params, exporting interfaces, read/write, pluginlib export, CMake and package.xml; Dynamixel example with dynamixel_workbench |
| controllers | 11 | `notes/controllers/_index.md` | Built-in controllers of ros2_controllers (forward family, joint_trajectory_controller topic and action, diff_drive_controller) and writing a custom controller: ControllerInterface methods, interface configuration, realtime tools, plugin, build, launch |
| learn | 12 | `learn/_index.md` | ros2_control course units 1–5 for students (rrbot demo, bringup package, controller manager, hardware template, Dynamixel) and the course map; open only for course questions |
| migration | 2 | `migration/_index.md` | Humble hardware interface API and other Humble differences; Jazzy → Kilted/Lyrical removals and default changes; open for other distros or porting |
<!-- INDEX:END -->

## Related skills
ros2-core (required): packages, colcon, launch, parameters, lifecycle nodes, the short ros2_control overview. ros2-urdf (required): URDF and xacro of the robot that carries the `<ros2_control>` tag. ros2-gazebo builds on this skill: gz_ros2_control in Gazebo Sim (GazeboSimSystem, the system plugin, Humble + Fortress). Install ros2-core and ros2-urdf with this skill.
