# Version audit — ros2-cpp (Phase 1)

> Date: 2026-10-25. Scope: every version-dependent or checkable statement of the C++ basics course (course wiki,
> not published; units 2–9: packages and CMake, nodes and timers, launch, topics, custom interfaces, services,
> callbacks and executors, callback groups, actions with a Nav2 client inside, components, logging and debugging
> tools) that lands in the new skill `ros2-cpp`, the course lines that become unions in `ros2-core`, and the claims of
> the new ros2-core note on choosing and combining rclpy and rclcpp. Section IDs = the course's unit numbers.
> Baseline: **Humble is canonical** (the course runs on Humble: `source /opt/ros/humble/setup.bash`). Jazzy, Kilted and
> **Lyrical** are annotated. Generic ROS 2 rows are in [version_audit.md](version_audit.md) (`Vnn`, e.g. V09
> `ament_target_dependencies`, V44 tf2 `.h` headers).

## Method
- Primary sources, read on the matching branch with grep: `ros2/rclcpp` (humble, jazzy, kilted, lyrical: `node.hpp`,
  `timer.hpp`, `create_timer.hpp`, `executor.hpp`, `executors.hpp`, `executor.cpp`, `multi_threaded_executor.*`,
  `context.hpp`, `logger.hpp`, `resource/logging.hpp.em`, `client.hpp`, `publisher.hpp`,
  `rclcpp_action/client.hpp` and its CHANGELOG, `rclcpp_components/src/component_manager.cpp`), `ros2/rcl` (humble:
  `rcl_action/src/rcl_action/goal_state_machine.c`), `ros2/rcutils` (humble: `logging.h`, `logging.c`),
  `ament/ament_cmake` (humble, kilted, lyrical: `ament_target_dependencies.cmake`, the export-dependencies extras,
  `version.h.in`), `ros-perception/vision_opencv` (humble, rolling: cv_bridge headers, CHANGELOG, package.xml),
  `ros2/geometry2` (humble…lyrical: tf2 headers), `ros2/ros2cli` (humble: `ros2action`, `ros2doctor`),
  `ros2/launch_ros` (humble: `composable_node.py`), `ros2/rclpy` (humble, lyrical), `ros2/demos` (humble:
  `composition`), `ros2/examples` (humble, lyrical: minimal action client/server), `ros2/ros2_documentation`
  (humble, lyrical), `ros/rosdistro` (`*/distribution.yaml`, `rosdep/base.yaml`, `rosdep/python.yaml`),
  `ros-infrastructure/rep` (REP 2001), crates.io metadata of `ros2-client`.
- Origin of the course code: the action client and server of 7.5–7.6 follow the official C++ action tutorial
  ([tutorial][act-tut-h], Apache-2.0 code, including its `RCLCPP_INFO(logger, ss.str().c_str())` lines); the
  components of 8.3 copy `visibility_control.h`, the `COMPOSITION_BUILDING_DLL` define and the `COMPOSITION__` header
  guards from the `composition` demo of `ros2/demos` ([demo][demo-comp-h], Apache-2.0, OSRF); the composition CLI
  steps follow the official tutorial ([Composition (Humble)][comp-tut-h]). The rest (Mars rover programs, the plant
  detector series, the Nav2 bridge server, the timeout client) is the course's own.
- Course logic was reviewed too: variables followed from writer to reader across threads, which objects are spun,
  loop exits, blocking calls inside callbacks, explained snippets against the full files, explanations against the
  printed outputs. Contradictions are **fix** rows ("course mistake").
- Actions: **keep** = correct for Humble · **annotate** = correct, add marks (Jazzy, Lyrical) or a precise wording ·
  **fix** = wrong for Humble itself. Confidence: High (read in code) · Medium (docs, or inferred) · `[verify]` (needs a
  build or run).

## Baseline
| | Humble (canonical) | Jazzy | Kilted | Lyrical |
|---|---|---|---|---|
| Ubuntu / EOL | 22.04 / May 2027 | 24.04 / May 2029 | 24.04 / Dec 2026 | 26.04 / May 2031 |
| rclcpp branch head | 16.0.22 | 28.1.22 | 29.5.11 | 32.0.3 |
| cv_bridge (rosdistro) | 3.2.1 (`cv_bridge.h` only) | 4.1.0 (`cv_bridge.hpp` only) | 4.1.0 | 4.1.0 |
| `ament_target_dependencies` | ✓ | ✓ | deprecated (CMake warning) | **removed** |
| `Node::create_timer` (node clock) | ✗ (free function `rclcpp::create_timer`) | ✓ | ✓ | ✓ |
| `create_service(…, rmw_qos_profile_t, group)` | ✓ only form | deprecated (`rclcpp::QoS` overload added) | **removed** | removed |
| Official docs | [Humble docs][docs-h] | [Jazzy docs][docs-j] | — | [Lyrical docs][docs-l] (pages moved under `ROS-Framework/`) |

## Real Humble errors (fix)
| ID | Section | Origin | Error | Correct statement |
|---|---|---|---|---|
| CPP-V01 | 2.8, 2.9 | course mistake | `sleep_for()` "does NOT use the ROS 2 clock" (sim time), so the program is rewritten with a ROS 2 timer: `create_wall_timer(...)` | `create_wall_timer` builds a `WallTimer` on `RCL_STEADY_TIME`: it ignores `use_sim_time` too ([timer.hpp (humble)][timer-h]). A timer on the node clock (follows `/clock` when `use_sim_time` is true): Humble `rclcpp::create_timer(this, this->get_clock(), rclcpp::Duration::from_seconds(p), cb)` ([create_timer.hpp (humble)][ctimer-h]); Jazzy+ `this->create_timer(period, cb)` ([node.hpp (jazzy)][node-j]). The course's switch is still right for another reason: the executor runs the callback instead of a blocking loop. |
| CPP-V02 | 3.7 | course mistake | Yaw error normalized with `std::fmod(yaw_error + M_PI, 2 * M_PI) - M_PI` "to the range [-pi, pi]" | `std::fmod` keeps the sign of its first argument: for `yaw_error < -π` the result stays below −π (e.g. −1.5π is returned unchanged, so the rover turns the long way). Use `std::atan2(std::sin(e), std::cos(e))` or `std::remainder(e, 2 * M_PI)` ([fmod][cpp-fmod], [remainder][cpp-rem]). |
| CPP-V03 | 3.9, 5.5 | course mistake | package.xml `<depend>OpenCV</depend>` (3.9) and `<depend>opencv2</depend>` (5.5) | Neither is a rosdep key: `rosdep install` stops with "Cannot locate rosdep definition". The key is `libopencv-dev` (what cv_bridge itself declares). colcon does not read the tag, so the build works and hides the error. Sources: [rosdep base.yaml][rosdep-base], [cv_bridge package.xml (humble)][cvb-pkg-h]. |
| CPP-V04 | 6.6 | course mistake | Snippet `#include "rclcpp/callback_groups.hpp"` | No such header: it is `rclcpp/callback_group.hpp` (also included by `rclcpp/rclcpp.hpp`) ([callback_group.hpp (humble)][cbg-h]). The full file of 6.6 includes only `rclcpp/rclcpp.hpp`. |
| CPP-V05 | 6.5, 6.6, 6.7 | course mistake | With a Reentrant group or two MutuallyExclusive groups and two threads, `listener_callback` writes `last_image_` while `detect_plants_callback` reads it; 6.7 calls `get_latest_image()` (a `clone()` without a lock) "a thread-safe copy" and includes `<mutex>` without using it | Two threads reading and writing the same non-atomic object is a data race (undefined behaviour) ([data races][cpp-race]); the official guide puts callbacks that share non-thread-safe resources in the same exclusive group or asks you to protect them ([callback groups][cbg-guide-h]). Fix: a `std::mutex` member; the writer assigns under `std::lock_guard`, `get_latest_image()` returns `last_image_.clone()` under the same lock. `[verify]` (build + run). |
| CPP-V06 | 6.7 | course mistake | Output of the `/detect_plants` call: `message='Plant detection completed'` | The program of 6.7 answers `"Plant detected successfully"` or `"Plant not detected within 10 seconds"`; the printed line comes from the earlier program of 5.5–6.6. |
| CPP-V07 | 7.3, 7.4 | course mistake | `ros2 action list` prints `rotate` | Action names in the graph are fully qualified: `/rotate` ([ros2action list (humble)][r2a-list-h]); the list printed in 7.6 shows `/go_to_pose`, `/navigate_to_pose`… |
| CPP-V08 | 7.5 | older distro (Foxy/Galactic) | Explained snippet `void goal_response_callback(std::shared_future<GoalHandleRotate::SharedPtr> future)` with `future.get()` | Since rclcpp_action 5.0.0 (#1311, before Humble) the callback receives the goal handle: `void goal_response_callback(const GoalHandleRotate::SharedPtr & goal_handle)`; the compatibility shim (#1495) is gone in Humble, so the snippet does not compile. The complete `action_client.cpp` already uses the Humble form. Sources: [client.hpp (humble)][act-cli-h], [CHANGELOG][act-cl-h], [tutorial client.cpp (humble)][act-tut-h]. |
| CPP-V09 | 7.5 | course mistake | Launch output `[example62-1] … process started` | The launch file starts `action_client_node`: launch prefixes the lines with `[action_client_node-1]`. |
| CPP-V10 | 7.6 | course mistake | Explanation: `rclcpp::spin_until_future_complete(this->get_node_base_interface(), send_goal_future)` inside `execute()` | `execute()` runs in a detached thread while `main()` spins the same node; `spin_until_future_complete(node, …)` adds the node to a new executor and throws `std::runtime_error` ("Node '…' has already been added to an executor") ([executors.hpp][execs-h], [executor.cpp][exec-cpp-h]). The full file waits with `send_goal_future.wait_for(10s)` and `result_future.wait()`, which works because the main thread's executor delivers the responses. The file wins. |
| CPP-V11 | 7.8 | course mistake | After the 30 s timeout "the robot was able to … cancel that goal, and continue toward the correct location of the lost astronaut" at (−13, −3) | The client only calls `async_cancel_goal`; it never sends a second goal. The server's `handle_cancel` accepts, but `execute()` never checks `goal_handle->is_canceling()` and never cancels the Nav2 goal, so Nav2 keeps driving to (−8, 6) and `succeed()` ends the goal as SUCCEEDED (CANCELING → SUCCEEDED is a legal transition, [goal_state_machine.c (humble)][gsm-h]). The printed logs show exactly that ("Received request to cancel goal" … "Navigation succeeded", client "The robot reached the goal."). Fix: in `execute()`, wait in a loop, and on `is_canceling()` call `nav_to_pose_client_->async_cancel_goal(nav_goal_handle)` and `goal_handle->canceled(result)` (the official server checks `is_canceling()`, [tutorial server.cpp][act-tut-h]); in the client, on CANCELED after the timeout, send the goal (−13, −3). `[verify]` (run with Nav2). |
| CPP-V12 | 8.5 | course mistake | Solution of exercise 8.3 (`TextRecognitionService` with `custom_interfaces/srv/TextRecognition`) | It does not compile: `detect_text_with_bounding_box()` and `to_upper()` are defined as members but not declared in the header (which declares an unused `detect_text()`), the constructor assigns `srv_` while the header declares `service_`, and the header uses `cv::Mat` without an OpenCV include. 8.6 and 8.7 call the service with `std_srvs/srv/Trigger`: unit 8.7 gives the solution that compiles, which the notes keep. |
| CPP-V13 | 8.7 | course mistake | `simulate_text_recognition()`: "Simulate detection with 70% probability" with `std::uniform_int_distribution<> dis(0, 1)` | `dis(gen) == 0` is true with 50 % probability. The service handler also invents FOOD/WASTE at random when nothing was detected: it is a simulation, not text recognition (the note says so). |
| CPP-V14 | 2.6, 9.5 | course mistake | "`ros2 doctor` belongs to the `ros2cli` package" | It is the package `ros2doctor` (in the ros2cli repository; apt `ros-humble-ros2doctor`) ([ros2doctor setup.py (humble)][doctor-h]). |
| CPP-V15 | 3.3 | older distro (Foxy, EOL) | Link to the Foxy page "About ROS Interfaces" | Humble page: [About interfaces (Humble)][iface-h]; Lyrical moved it to `ROS-Framework/interfaces/About-Interfaces`. |
| CPP-V16 | 7.9 | course mistake (contradiction) | "DO NOT use custom interfaces defined in external packages, such as the `custom_interfaces` package, you can just use `leo_description` package" next to "Create a new package named `actions_quiz_msg` … with `Distance.action`" | The grader checks the package `actions_quiz_msg` and its action ("Did the custom Action message compile successfully?"): put `Distance.action` there and do not reuse `custom_interfaces`; `leo_description` is only needed for the simulation. The spec keeps the course's exact names. |
| CPP-V17 | 8.5, 8.8 | course mistake | "Inter-Process Communication: Components can communicate efficiently within the same process"; `extra_arguments=[{'use_intra_process_comms': True}]` "optimizes performance" | Inside one process it is **intra**-process communication, and it must be enabled per node (`NodeOptions::use_intra_process_comms`, which the container sets from that extra argument, [component_manager.cpp (humble)][compmgr-h]). rclcpp's intra-process path covers publishers and subscriptions only ([publisher.hpp (humble)][pub-h]; zero-copy needs `std::unique_ptr` messages, [intra-process demo][ipc-h]): both components of the course only offer services and subscribe to a topic of another process, so the flag changes nothing there. |
| CPP-V18 | 3.2, 5.6, 6.5, 9.5 | course mistake (transcribed outputs) | `ros2 topic list` output headed by the prompt `ros2 node list`; 5.6 shows `[INFO] [launch]: …` and `[callback_spinonce_function-1]` prefixes for a `ros2 run` command; 6.5 "Plant Detecte!"; 9.5 doctor report `inet : 128.0.0.1` for `lo` | Outputs pasted from other runs or edited: `ros2 run` prints no launch lines or process prefixes; the 6.5 program prints "Plant Detected!"; the loopback address is 127.0.0.1. The notes show the outputs the commands print. |

## Full table
| # | Section | Statement | Humble | Jazzy | Lyrical | Action | Source | Confidence |
|---|---|---|---|---|---|---|---|---|
| CPP-V01 | 2.8, 2.9 | `create_wall_timer` replaces `sleep_for` "to use the ROS 2 clock" | ✗ steady wall clock | `Node::create_timer` added | same | **fix** | [timer-h], [ctimer-h], [node-j] | High |
| CPP-V02 | 3.7 | `fmod(e + π, 2π) − π` normalizes to [−π, π] | ✗ | same | same | **fix** | [cpp-fmod], [cpp-rem] | High |
| CPP-V03 | 3.9, 5.5 | `<depend>OpenCV</depend>`, `<depend>opencv2</depend>` | ✗ no rosdep key | same | same | **fix** | [rosdep-base], [cvb-pkg-h] | High |
| CPP-V04 | 6.6 | `rclcpp/callback_groups.hpp` | ✗ `callback_group.hpp` | same | same | **fix** | [cbg-h] | High |
| CPP-V05 | 6.5–6.7 | shared `last_image_` across two threads without a lock | ✗ data race | same | same | **fix** | [cpp-race], [cbg-guide-h] | High; fix `[verify]` |
| CPP-V06 | 6.7 | response message "Plant detection completed" | ✗ other program | — | — | **fix** | course code | High |
| CPP-V07 | 7.3 | `ros2 action list` → `rotate` | ✗ `/rotate` | same | same | **fix** | [r2a-list-h] | High |
| CPP-V08 | 7.5 | `goal_response_callback(std::shared_future<…>)` | ✗ `GoalHandle::SharedPtr` | same | same | **fix** | [act-cli-h], [act-cl-h] | High |
| CPP-V09 | 7.5 | output prefix `[example62-1]` | ✗ `[action_client_node-1]` | — | — | **fix** | course launch file | High |
| CPP-V10 | 7.6 | `spin_until_future_complete` inside the execute thread | ✗ throws | same | same | **fix** | [execs-h], [exec-cpp-h] | High |
| CPP-V11 | 7.8 | timeout cancels and the rover goes to (−13, −3) | ✗ cancel ignored, no 2nd goal | same | same | **fix** | [gsm-h], [act-tut-h] | High; fix `[verify]` |
| CPP-V12 | 8.5 | exercise 8.3 solution | ✗ does not compile | same | same | **fix** | course code | High |
| CPP-V13 | 8.7 | "70% probability" | ✗ 50 % | — | — | **fix** | course code | High |
| CPP-V14 | 9.5 | doctor "belongs to the ros2cli package" | ✗ `ros2doctor` | same | same | **fix** | [doctor-h] | High |
| CPP-V15 | 3.3 | Foxy docs link | ✗ EOL page | — | moved | **fix** | [iface-h], [iface-l] | High |
| CPP-V16 | 7.9 | quiz: "do not use custom interfaces… use leo_description" | contradiction | — | — | **fix** | course grading guide | Medium |
| CPP-V17 | 8.5, 8.8 | "Inter-Process Communication" in one process; intra-process flag for service components | ✗ intra-process, pub/sub only | same | same | **fix** | [compmgr-h], [pub-h], [ipc-h] | High |
| CPP-V18 | 3.2, 5.6, 6.5, 9.5 | transcribed outputs | ✗ | — | — | **fix** | course commands and code | High |
| CPP-V19 | all CMakeLists | `ament_target_dependencies(tgt rclcpp …)` | ✓ | ✓ | deprecated in Kilted, **removed** in Lyrical | annotate (V09): `target_link_libraries(tgt PUBLIC rclcpp::rclcpp ${std_msgs_TARGETS} cv_bridge::cv_bridge ${OpenCV_LIBS})`, valid since Humble | [atd-l], [cvb-cmake-h], [ocv-cmake] | High |
| CPP-V20 | 6.3, 6.5, 6.7 | packages in `ament_target_dependencies` with no `find_package` (`std_msgs`; `geometry_msgs` and `sensor_msgs` missing from some lists) | ✓ by chance | same | same | annotate: they are found because `sensor_msgs`/`cv_bridge` export them (`find_package` of exported dependencies); declare every dependency you use | [atd-h], [expdeps-h] | High |
| CPP-V21 | 3.7, 4.3, 5.5–8.7 | `#include <cv_bridge/cv_bridge.h>` | ✓ only header | ✗ removed (4.0.0): `cv_bridge/cv_bridge.hpp` | same as Jazzy | annotate: `[changed in Jazzy: cv_bridge.hpp]`; one source for both: `#if __has_include(<cv_bridge/cv_bridge.hpp>)` | [cvb-cl], [cvb-h-h] | High |
| CPP-V22 | 7.6, 7.8 | `#include "tf2/LinearMath/Quaternion.h"`, `tf2_geometry_msgs/tf2_geometry_msgs.hpp` | ✓ (`.hpp` exists too) | ✓ | `Quaternion.h` **removed** | annotate (V44): use `Quaternion.hpp`, valid since Humble | [quat-l] | High |
| CPP-V23 | 6.5–6.7 | `create_service(name, cb, rmw_qos_profile_services_default, group)` | ✓ only form | deprecated | **removed** (Kilted) | annotate: Jazzy+ `create_service<T>(name, cb, rclcpp::ServicesQoS(), group)`; one source for all: `#if RCLCPP_VERSION_GTE(28, 0, 0)` (`rclcpp/version.h`) | [node-h], [node-j], [node-k], [verh] | High |
| CPP-V24 | 7.5, 7.8 | `RCLCPP_INFO(logger, ss.str().c_str())` (copied from the official tutorial) | works | same | same | annotate: the format is not a literal (GCC `-Wformat-security` warns; Ubuntu enables it by default) and a `%` in the text would be read as a conversion; use `RCLCPP_INFO_STREAM(logger, "… " << value)` or `RCLCPP_INFO(logger, "%s", s.c_str())` | [logging-em-h], [rcutils-log-h], [ubuntu-flags] | Medium (warning `[verify]`) |
| CPP-V25 | 9.2 | level in code with `rcutils_logging_set_logger_level(name, RCUTILS_LOG_SEVERITY_DEBUG)`; CLI `--log-level DEBUG` | ✓ | ✓ | ✓ | keep; also `get_logger().set_level(rclcpp::Logger::Level::Debug)` (Humble ✓); the level string is case-insensitive | [logger-h], [rcutils-c-h] | High |
| CPP-V26 | 6.3 | `MultiThreadedExecutor(rclcpp::ExecutorOptions(), 2)`; `nproc` | ✓ | ✓ | ✓ | keep; `0` (default) = `std::thread::hardware_concurrency()`, at least 1 | [mte-h] | High |
| CPP-V27 | 6.4–6.6 | default group = MutuallyExclusive; Reentrant vs separate exclusive groups | ✓ | ✓ | ✓ | keep | [cbg-guide-h] | High |
| CPP-V28 | 3.6 | `context->add_pre_shutdown_callback(...)` publishes a zero Twist before shutdown | ✓ | ✓ | ✓ | keep; that the last message reaches the robot before the process exits is `[verify]` | [ctx-h], [ctx-l] | High / delivery `[verify]` |
| CPP-V29 | 4.6 | async client loop `while (ok()) { spin_some(client); if (future_ready()) … }` | works | same | same | annotate: `spin_some()` collects work once and returns, so the loop spins the CPU; add a short sleep (as the course's own 5.6 loop does) or `spin_until_future_complete(node, future, timeout)` | [exec-h] | High |
| CPP-V30 | 4.6 | "sync" client: spin thread + blocking wait | ✓ | ✓ | ✓ | annotate: rclcpp has only `async_send_request`; "sync" = wait on its future while another thread spins (official guide: the C++ API is async only) | [syncasync-h], [client-h] | High |
| CPP-V31 | 3.10 | hint: one `rclcpp::spin_some(node)` right after creating the node reads the initial odometry | weak | same | same | annotate: right after creation the subscription usually has no message yet (discovery, first publication); spin until the odom callback sets a flag, with a timeout | [exec-h] | Medium `[verify]` |
| CPP-V32 | 6.7 | `/green_detector` callback opens OpenCV windows and loops on `waitKey` until `q` | works | same | same | annotate: the callback (and one executor thread) is blocked until a key is pressed; the response is sent only then (the course output shows the call still waiting) | course code | High |
| CPP-V33 | 6.7 | "exchange data directly without relying on inter-process communication" (one node holds a `shared_ptr` to the other) | ✓ | ✓ | ✓ | annotate: direct calls between nodes in one process are not ROS communication; they couple the nodes and need the lock of CPP-V05 | [cpp-race] | High |
| CPP-V34 | 8.3 | `visibility_control.h`, `COMPOSITION_BUILDING_DLL`, header guards `COMPOSITION__…`; `--dependencies … composition` | ✓ | ✓ | ✓ | annotate: copied from the `composition` demo; rename the guards and macros after your package; the `composition` dependency (a demo package of the desktop variant) is not needed | [demo-comp-h], [rep2001] | High |
| CPP-V35 | 8.3, 8.5 | `ros2 component types` prints the component names | partial | — | — | annotate: it prints the package name, then its components indented | [comp-tut-h] | High |
| CPP-V36 | 8.3–8.6 | `ros2 component load/list/unload` outputs; manual composition invisible to `ros2 component list` | ✓ | ✓ | ✓ | keep | [comp-tut-h] | High |
| CPP-V37 | 8.2 (+ core note) | components = shared libraries loaded into a container; no `main()` | ✓ rclcpp only | same | no Python container in rclpy | keep; composition is an rclcpp feature (`rclcpp_components`) | [about-comp-h], [rclpy-l] | High |
| CPP-V38 | 7.7, 8.x | interface package.xml: `<build_depend>rosidl_default_generators</build_depend>`, schema `package_format2.xsd` with `format="3"`; 9.2 `schematypepath=` | builds | same | same | annotate: official form `<buildtool_depend>rosidl_default_generators</buildtool_depend>`, `<depend>action_msgs</depend>` for actions (goal IDs), `package_format3.xsd`, attribute `schematypens` | [custom-if-h], [create-act-h] | High |
| CPP-V39 | 8.3 | `std::setprecision` without `#include <iomanip>` | builds only through another header | same | same | annotate: no rclcpp header includes `<iomanip>`; add it | [rclcpp-h] | Medium `[verify]` |
| CPP-V40 | 2.9, 5.5, 6.3 | unused code: `rover_name_` never set, `model_loaded_` never read, `from tracetools_launch.action import Trace` never used | harmless | same | same | annotate: drop them; the unused import fails when `tracetools_launch` is not installed | course code | High |
| CPP-V41 | 2.6 (core note) | Rust: the crate `ros2-client` "is gaining traction" | — | — | — | annotate: the official page lists the community Rust client `rclrs` (ros2-rust, on rcl); `ros2-client` is another community crate built on RustDDS | [about-cl-h], [crate-r2c], [ros2rust] | Medium |
| CPP-V42 | core note | Python for prototyping/visualization, C++ where efficiency matters; messages shared between languages through generated code; common core `rcl` | ✓ | ✓ | ✓ | keep (claims of the new note) | [about-cl-h], [about-cl-l] | High |
| CPP-V43 | core note | C++-only building blocks: pluginlib plugins, composition, zero-copy intra-process with `std::unique_ptr` | ✓ | ✓ | ✓ | keep (claims of the new note) | [pluginlib-h], [about-comp-h], [ipc-h] | High |
| CPP-V44 | 9.5 | `ros2 doctor`: "All 5 checks passed", report sections | ✓ 5 checks (platform, network, topic, QoS compatibility, package) | — | — | keep; a failure prints `N/5 checks failed` | [doctor-h] | High |
| CPP-V45 | 7.6 | `topic_names_and_types.find(topic_name)` (explanation) vs a loop in the code | ✓ both (`std::map`) | ✓ | ✓ | keep | [node-h] | High |

## Canonical alternatives (features of later distros)
| Later feature | Humble way | Checked in |
|---|---|---|
| `this->create_timer(period, cb)` (Jazzy) | `rclcpp::create_timer(this, this->get_clock(), rclcpp::Duration::from_seconds(p), cb)` (accepts `this`: the interface getters take raw and smart pointers) | [ctimer-h], `resource/get_interface.hpp.em` (humble) |
| `create_service(…, rclcpp::QoS, group)` (Jazzy) | `create_service(…, rmw_qos_profile_services_default, group)` | [node-h] |
| `cv_bridge/cv_bridge.hpp` (Iron+) | `cv_bridge/cv_bridge.h` (the only header of cv_bridge 3.2.1) | [cvb-h-h] |

## Open `[verify]`
- CPP-V05: the mutex fix of the plant detector (build and run the reentrant and exclusive-group variants).
- CPP-V11: the corrected cancel path (server cancels the Nav2 goal, client sends (−13, −3)) with Nav2 running.
- CPP-V24: the `-Wformat-security` warning on Ubuntu 22.04 for `RCLCPP_INFO(logger, ss.str().c_str())`.
- CPP-V28: the zero Twist of the pre-shutdown callback reaches the simulated robot on Ctrl+C.
- CPP-V31: a single `spin_some()` right after construction leaves the initial pose unknown.
- CPP-V39: `robot_status_component.cpp` without `<iomanip>` (build).
- CPP-V01: the Humble `rclcpp::create_timer(this, …)` form follows `/clock` with `use_sim_time:=true`.

## Sources
[docs-h]: https://docs.ros.org/en/humble/
[docs-j]: https://docs.ros.org/en/jazzy/
[docs-l]: https://docs.ros.org/en/lyrical/
[timer-h]: https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/timer.hpp
[ctimer-h]: https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/create_timer.hpp
[node-h]: https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/node.hpp
[node-j]: https://github.com/ros2/rclcpp/blob/jazzy/rclcpp/include/rclcpp/node.hpp
[node-k]: https://github.com/ros2/rclcpp/blob/kilted/rclcpp/include/rclcpp/node.hpp
[client-h]: https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/client.hpp
[pub-h]: https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/publisher.hpp
[exec-h]: https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/executor.hpp
[execs-h]: https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/executors.hpp
[exec-cpp-h]: https://github.com/ros2/rclcpp/blob/humble/rclcpp/src/rclcpp/executor.cpp
[mte-h]: https://github.com/ros2/rclcpp/blob/humble/rclcpp/src/rclcpp/executors/multi_threaded_executor.cpp
[cbg-h]: https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/callback_group.hpp
[ctx-h]: https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/context.hpp
[ctx-l]: https://github.com/ros2/rclcpp/blob/lyrical/rclcpp/include/rclcpp/context.hpp
[logger-h]: https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/logger.hpp
[logging-em-h]: https://github.com/ros2/rclcpp/blob/humble/rclcpp/resource/logging.hpp.em
[rclcpp-h]: https://github.com/ros2/rclcpp/tree/humble/rclcpp/include/rclcpp
[act-cli-h]: https://github.com/ros2/rclcpp/blob/humble/rclcpp_action/include/rclcpp_action/client.hpp
[act-cl-h]: https://github.com/ros2/rclcpp/blob/humble/rclcpp_action/CHANGELOG.rst
[compmgr-h]: https://github.com/ros2/rclcpp/blob/humble/rclcpp_components/src/component_manager.cpp
[gsm-h]: https://github.com/ros2/rcl/blob/humble/rcl_action/src/rcl_action/goal_state_machine.c
[rcutils-log-h]: https://github.com/ros2/rcutils/blob/humble/include/rcutils/logging.h
[rcutils-c-h]: https://github.com/ros2/rcutils/blob/humble/src/logging.c
[atd-h]: https://github.com/ament/ament_cmake/blob/humble/ament_cmake_target_dependencies/cmake/ament_target_dependencies.cmake
[atd-l]: https://github.com/ament/ament_cmake/blob/lyrical/ament_cmake_target_dependencies/CHANGELOG.rst
[expdeps-h]: https://github.com/ament/ament_cmake/blob/humble/ament_cmake_export_dependencies/cmake/ament_cmake_export_dependencies-extras.cmake.in
[verh]: https://github.com/ament/ament_cmake/blob/humble/ament_cmake_gen_version_h/cmake/version.h.in
[cvb-h-h]: https://github.com/ros-perception/vision_opencv/tree/humble/cv_bridge/include/cv_bridge
[cvb-pkg-h]: https://github.com/ros-perception/vision_opencv/blob/humble/cv_bridge/package.xml
[cvb-cmake-h]: https://github.com/ros-perception/vision_opencv/blob/humble/cv_bridge/CMakeLists.txt
[cvb-cl]: https://github.com/ros-perception/vision_opencv/blob/rolling/cv_bridge/CHANGELOG.rst
[quat-l]: https://github.com/ros2/geometry2/tree/lyrical/tf2/include/tf2/LinearMath
[r2a-list-h]: https://github.com/ros2/ros2cli/blob/humble/ros2action/ros2action/verb/list.py
[doctor-h]: https://github.com/ros2/ros2cli/blob/humble/ros2doctor/setup.py
[rclpy-l]: https://github.com/ros2/rclpy/tree/lyrical/rclpy
[demo-comp-h]: https://github.com/ros2/demos/tree/humble/composition
[rosdep-base]: https://github.com/ros/rosdistro/blob/master/rosdep/base.yaml
[rep2001]: https://ros.org/reps/rep-2001.html
[act-tut-h]: https://docs.ros.org/en/humble/Tutorials/Intermediate/Writing-an-Action-Server-Client/Cpp.html
[comp-tut-h]: https://docs.ros.org/en/humble/Tutorials/Intermediate/Composition.html
[about-comp-h]: https://docs.ros.org/en/humble/Concepts/Intermediate/About-Composition.html
[ipc-h]: https://docs.ros.org/en/humble/Tutorials/Demos/Intra-Process-Communication.html
[cbg-guide-h]: https://docs.ros.org/en/humble/How-To-Guides/Using-callback-groups.html
[syncasync-h]: https://docs.ros.org/en/humble/How-To-Guides/Sync-Vs-Async.html
[custom-if-h]: https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html
[create-act-h]: https://docs.ros.org/en/humble/Tutorials/Intermediate/Creating-an-Action.html
[iface-h]: https://docs.ros.org/en/humble/Concepts/Basic/About-Interfaces.html
[iface-l]: https://docs.ros.org/en/lyrical/ROS-Framework/interfaces/About-Interfaces.html
[about-cl-h]: https://docs.ros.org/en/humble/Concepts/Basic/About-Client-Libraries.html
[about-cl-l]: https://docs.ros.org/en/lyrical/ROS-Framework/About-Client-Libraries.html
[pluginlib-h]: https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Pluginlib.html
[cpp-fmod]: https://en.cppreference.com/w/cpp/numeric/math/fmod
[cpp-rem]: https://en.cppreference.com/w/cpp/numeric/math/remainder
[cpp-race]: https://en.cppreference.com/w/cpp/language/multithread
[ocv-cmake]: https://docs.opencv.org/4.x/db/df5/tutorial_linux_gcc_cmake.html
[ubuntu-flags]: https://wiki.ubuntu.com/ToolChain/CompilerFlags
[crate-r2c]: https://crates.io/crates/ros2-client
[ros2rust]: https://github.com/ros2-rust/ros2_rust
