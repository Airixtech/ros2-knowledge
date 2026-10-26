---
name: ros2-cpp
description: "ROS 2 C++ (rclcpp) on Humble: ament_cmake packages, nodes, timers, topics, services, actions, executors, callback groups, components, logging, cv_bridge. Jazzy/Lyrical notes."
---
# ros2-cpp — ROS 2 programming in C++ with rclcpp

Atomic notes for writing correct code and debugging it. **Humble is canonical**; differences for later versions are marked, never substituted. Paths are relative to this skill's folder. `[[note-id]]` means the file `<note-id>.md`; find it via the area index or a glob `**/<note-id>.md`.

## Golden rules (always apply)
1. Check the user's distro first. Most Humble code builds unchanged on Jazzy. What breaks: `cv_bridge/cv_bridge.h` (Jazzy: `.hpp`), `create_service(…, rmw_qos_profile_services_default, group)` (removed in Kilted: `rclcpp::ServicesQoS()`, Jazzy+), `ament_target_dependencies` and the tf2 `.h` headers (removed in Lyrical: `target_link_libraries(tgt PUBLIC rclcpp::rclcpp)` and `.hpp`, both valid since Humble) ([[cpp-humble-to-jazzy]]).
2. Every executable needs `add_executable`, its dependencies and `install(TARGETS … DESTINATION lib/${PROJECT_NAME})`; launch files need `install(DIRECTORY launch DESTINATION share/${PROJECT_NAME}/)`. Every package used needs `find_package` **and** a `<depend>` with a valid rosdep key (`libopencv-dev`, not `OpenCV`, CPP-V03). `--packages-select` builds only the listed packages (CPP-V47) ([[cpp-pkg-cmake]], [[cpp-cmake-library]]).
3. A node is an `rclcpp::Node` subclass named in the initializer list. Store every timer, publisher, subscription, service and client in a `SharedPtr` member: a local one dies with the constructor. Nothing runs without `rclcpp::spin` or an executor ([[cpp-node-class]]).
4. `create_wall_timer` runs on the steady clock and ignores `use_sim_time`; on sim time use `rclcpp::create_timer(this, this->get_clock(), …)` (Humble) or `this->create_timer(…)` (≥Jazzy) (CPP-V01, [[cpp-node-class]]).
5. Subscription callbacks: `std::bind(&Class::cb, this, std::placeholders::_1)` and `MsgT::ConstSharedPtr msg`; the course's `const MsgT::SharedPtr msg` warns on Humble and Lyrical (CPP-V46). QoS must be compatible with the publisher (`ros2 topic info <topic> -v`) ([[cpp-topic-subscriber]]).
6. `async_send_request` returns a future. Wait with `spin_until_future_complete` only from `main()`; inside a callback or an action's execute thread of a node that already spins, never spin again (CPP-V10): use a response callback, or block on the future while **another thread** spins ([[cpp-srv-client]], [[cpp-srv-sync-async]]).
7. A long callback blocks the single-threaded executor. Overlap needs both a `MultiThreadedExecutor` with ≥2 threads **and** groups that allow it (one Reentrant group or separate MutuallyExclusive groups; the default group never overlaps). Protect shared data with `std::mutex` (CPP-V05); the header is `rclcpp/callback_group.hpp` (CPP-V04) ([[cpp-exec-blocking]], [[cpp-exec-callback-groups]]).
8. Action server: `handle_accepted` returns fast and starts `execute()` in a new thread; `execute()` publishes feedback, checks `is_canceling()` and ends with `succeed()`, `abort()` or `canceled()`, since a client cancel is only a request (CPP-V11). Client: `SendGoalOptions` callbacks, the goal-response one takes `GoalHandle::SharedPtr` (CPP-V08); both sides use the same interface package ([[cpp-action-server]], [[cpp-action-client]], [[cpp-action-custom-timeout]]).
9. A component is a Node subclass with `explicit Class(const rclcpp::NodeOptions & options)`, no `main()`, `RCLCPP_COMPONENTS_REGISTER_NODE`, a SHARED library and `rclcpp_components_register_nodes`. One process is not automatically intra-process: `use_intra_process_comms` is per node and covers publishers and subscriptions only (CPP-V17) ([[cpp-component-write]], [[cpp-component-run]]).
10. Log with `RCLCPP_INFO` and friends, not `std::cout`: printf formats (`"%s", text.c_str()`), never built text as the format (`RCLCPP_INFO_STREAM` instead, CPP-V24); level with `--ros-args --log-level DEBUG`. Wrap `cv_bridge::toCvCopy` in `try`/`catch (cv_bridge::Exception&)` ([[cpp-logging]], [[cpp-recipe-cv-bridge]]).

## Retrieval protocol
1. Pick the area from the **Areas** table below (column "Covers").
2. Open that area's `_index.md` and choose notes by their summary.
3. Open 1–3 notes. Use their code as the template: keep the structure, adapt the names.
4. No clear match → `grep -ril "<keyword>" notes/` (API names work best: `create_subscription`, `MultiThreadedExecutor`, `rclcpp_action`, `RCLCPP_COMPONENTS_REGISTER_NODE`, `toCvCopy`) and open the top hits.
5. Follow a note's `see:` links **one hop** at most. The language-neutral parts (CLI, interface packages, launch files, QoS, TF, `ros2 doctor`) and the Python twins of these programs live in ros2-core.
6. Do not open `learn/` unless the question is about the C++ basics course (Leo Mars rover; units 2–9).
7. Jazzy, Kilted, Lyrical or porting → open `migration/` and apply the version marks.
8. Simulation → answer with modern Gazebo (Gazebo Sim); see the ros2-gazebo skill.
If the notes do not cover the question, read the official source for the user's distro (below) or say that you answer from standard knowledge. Never invent APIs or flags.

## Version marks and official sources
`[Humble]` Humble-only · `[≥Jazzy]` added in Jazzy (or later) · `[changed in Jazzy: …]` / `[changed in Lyrical: …]` what to use there instead · `[verify]` not confirmed by a source or a build: tell the user. Each note's `version_notes` holds the source URL and audit ID of every difference (`reports/version_audit_cpp.md`).

| Distro | rclcpp | Read first |
|---|---|---|
| Humble | 16.0 | docs.ros.org/en/humble; branch `humble` of rclcpp |
| Jazzy | 28.1 | docs.ros.org/en/jazzy; branch `jazzy` |
| Kilted | 29.5 | branch `kilted` |
| Lyrical | 32.0 | docs.ros.org/en/lyrical (pages under `ROS-Framework/`); branch `lyrical` |

## Areas
<!-- INDEX:START -->
<!-- generated by tools/build_index.py — do not edit by hand -->
| Area | Notes | Open | Covers |
|---|---|---|---|
| basics | 6 | `notes/basics/_index.md` | C++ packages (ament_cmake, CMakeLists, package.xml, own headers and libraries), first rclcpp program, Node subclass, timers and clocks, launching C++ executables, RCLCPP_* logging |
| communication | 12 | `notes/communication/_index.md` | rclcpp publishers and subscribers, custom interfaces from C++, service servers and clients (async, spin_some, spin thread), rclcpp_action servers and clients, timeouts and cancel |
| executors | 9 | `notes/executors/_index.md` | Callbacks and the executor: single-threaded blocking, spin vs spin_some, MultiThreadedExecutor, Reentrant and MutuallyExclusive callback groups, thread safety, several nodes in one executor |
| components | 3 | `notes/components/_index.md` | rclcpp components: NodeOptions constructor, RCLCPP_COMPONENTS_REGISTER_NODE, SHARED library, component_container, ros2 component CLI, ComposableNodeContainer, compile-time composition |
| recipes | 3 | `notes/recipes/_index.md` | C++ recipes: LaserScan sectors and obstacle detection, cv_bridge and OpenCV (HSV masks, excess green, trackbar tuner) |
| learn | 10 | `learn/_index.md` | C++ basics course for students (Leo Mars rover simulation): course map, units 2-9, exercises and quizzes; open only for course questions |
| migration | 1 | `migration/_index.md` | The course's rclcpp code on Jazzy, Kilted and Lyrical: CMake linking, headers, service QoS, callback signatures, timers; open for other distros |
<!-- INDEX:END -->

## Related skills
ros2-core (required): nodes, topics, services, actions, executors, launch, colcon, QoS, TF, debugging tools, the Python versions of these programs, and the note on choosing and combining rclpy and rclcpp; install it with this skill. Other skills with C++ code name this one in plain text and never require it: ros2-bt (BT nodes with rclcpp), ros2-nav2 (Nav2 itself, the `NavigateToPose` server of unit 7), ros2-control (controllers and hardware interfaces).
