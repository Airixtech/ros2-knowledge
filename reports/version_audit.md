# Version audit — ros2-core (Phase 1)

> Date: 2026-10-08 · Scope: every version-dependent statement in the original core wiki (not published)
> (CLI/flags, rclpy/rclcpp APIs, CMake/ament, setup.py/setup.cfg, launch, rosbag2, tf2, Nav2, MoveIt2,
> ros2_control, Gazebo, DDS/env vars, Ubuntu/Python, EOL).
> Baseline: **Humble is canonical**. Jazzy and Lyrical differences are annotated, not substituted.
> Extended 2026-10-13 with the **intermediate ROS 2 course** (Python build system, launch formats, parameters,
> executors, QoS, DDS, managed nodes): IDs V81–V105, sections `Pnn` = page of that course export (not published).
> Extended 2026-10-19 with the **ROS 2 security course** (SROS2: keystore, enclaves, governance, permissions,
> `ROS_SECURITY_*`): IDs V106–V139, sections `sec Pnn` = page of that course export (not published).
> Extended 2026-10-21: V140, the modern-Gazebo version of the security course's TurtleBot3 simulation.
> The "Lyrical" column includes changes that first appeared in **Kilted** (May 2025, non-LTS), marked "(Kilted)".

## Method
- Primary sources: ROS 2 release notes and complete changelogs (Iron, Jazzy, Kilted, Lyrical), REP 2000,
  the distro docs (humble / jazzy / rolling), package source code on the matching branch (ros2cli, rclpy,
  rclcpp, rcl, rmw, launch_ros, geometry2, rosbag2, ros2_tracing, ament_cmake, rosidl, message_filters,
  ros2_control, navigation2, docs.nav2.org, moveit2, ros_gz, example_interfaces, demos), the rosdistro
  `humble/distribution.yaml` and the packages.ros.org apt index for Jammy.
- Security course (V106–V139): `ros2/sros2`, `ros2/rcl` (`security.c`, `init.c`), `ros2/rmw_dds_common`
  (`security.cpp`) and `ros2/rmw_fastrtps` on the humble, jazzy, kilted and lyrical branches; the official
  security tutorials and concept page (humble, lyrical); the design articles "ROS 2 DDS-Security integration",
  "ROS 2 Security Enclaves" and "Topic and Service name mapping"; the `ros-swg/turtlebot3_demo` policies;
  `ROBOTIS-GIT/turtlebot3` and `turtlebot3_simulations` (humble, jazzy); rosdistro `humble`/`jazzy`/`lyrical`.
  The course follows the official keystore tutorial closely; its contradictions with its own output and XML are
  fix rows ("course mistake").
- docs.ros.org and ros.org block automated fetching (Anubis). Their content was read from the official
  source repos (`ros2/ros2_documentation`, `ros-infrastructure/rep`) on the matching branch. The tables
  cite the canonical docs.ros.org URL. The text is identical.
- Code facts were checked with grep against the branch source, not taken from memory. Anything that could
  not be confirmed is marked `[verify]` and listed at the end for Phase 5 (Docker).
- Actions: **keep** = correct for Humble · **annotate** = correct for Humble, add a version mark
  (`[≥Jazzy]`, `[changed in Jazzy: …]`, `[changed in Lyrical: …]`) · **fix** = wrong or outdated for Humble itself.
- The original wiki is not edited (and not part of this repo). Fixes and annotations live in the notes. Each row
  ID (V01…) becomes a `version_notes` entry in the affected note.

## Distro baseline
| | Humble | Jazzy | Kilted | Lyrical |
|---|---|---|---|---|
| Release – EOL | May 2022 – **May 2027** | May 2024 – May 2029 | May 2025 – Nov 2026 | May 2026 – May 2031 |
| Tier 1 Ubuntu | 22.04 Jammy | 24.04 Noble | 24.04 Noble | 26.04 Resolute |
| Python (Ubuntu) | 3.10 | 3.12 | 3.12 | 3.14 (min. 3.12) |
| Default RMW | rmw_fastrtps_cpp (Fast DDS 2.6) | rmw_fastrtps_cpp (Fast DDS 2.14) | rmw_fastrtps_cpp (2.14); Zenoh Tier 1 | rmw_fastrtps_cpp (Fast DDS 3.6) |
| Cyclone DDS | 0.9.x | 0.10.x | 0.10.x | 11.0.x |
| Gazebo pairing | Fortress (+ Classic 11) | Harmonic | Ionic | Jetty |
| SROS2 (`ros2 security`) | 6 verbs + deprecated `create_key`, `list_keys`; enclave files only as PEM files | same verbs; PKCS#11 URIs (`*.p11`) for keys/certs | `create_key`, `list_keys` removed | certificates valid from creation time (no 1-day backdate); Windows: hard links instead of symlinks |
| Sources | [REP 2000][rep2000] | [REP 2000][rep2000], [Jazzy notes][jazzy] | [REP 2000][rep2000], [Kilted notes][kilted] | [Lyrical notes][lyrical], [Lyrical platforms][lyr-plat] |

## Real Humble errors (fix)
| ID | Sheet(s) | Error | Correct Humble statement |
|---|---|---|---|
| V40 | B7, A4, C5, E3 | "`sudo apt install ros-humble-ros2trace` then `ros2 trace`" | Humble binaries are built **without** tracepoints. You also need LTTng (`lttng-tools liblttng-ust-dev python3-lttng python3-babeltrace`), then clone ros2_tracing into the workspace and build `tracetools`. Check with `ros2 run tracetools status` → `Tracing enabled`. Instrumentation is on by default only from Iron. |
| V61 | D5 | `fastdds discovery --server-id 0 --ip-address … --port 11811` | Fast DDS 2.6 has no `--ip-address`/`--port`. Use `--udp-address` (`-l`) and `--udp-port` (`-p`). |
| V35 | B8 | `qos_profile_system_default` = RELIABLE / VOLATILE / depth 10 | "System default" sets **every** policy to the RMW's own default. RELIABLE/VOLATILE/KEEP_LAST 10 is the *default* profile (`rmw_qos_profile_default`, or an int depth). |
| V36 | B8 | Liveliness default "AUTOMATIC" | Default liveliness is SYSTEM_DEFAULT with lease DEFAULT. Deadline and lifespan are "default" (the middleware usually treats them as infinite). |
| V48 | D3 | Nav2 chain "controller → cmd_vel_nav → velocity_smoother → collision_monitor → cmd_vel" | Humble default bringup: controller → `cmd_vel_nav` → velocity_smoother → `cmd_vel`. Collision Monitor exists in Humble but is **not** in the default bringup. The 4-stage chain is Jazzy+. |
| V53 | D3 | MoveIt2 "parallel planning in Humble"; STOMP listed among Humble planners | Humble MoveItCpp has no multi-pipeline (parallel) planning, and the Humble `moveit_planners` has no STOMP plugin (only the standalone `stomp` library). Both are ≥Iron. |
| V20 | A4 | `ExecuteProcess(cmd=['gz', 'sim', 'empty.sdf'])` | With Humble's official pairing (Fortress) the command is `ign gazebo empty.sdf`. `gz sim` needs Garden or Harmonic. Portable alternative: `ros_gz_sim`'s `gz_sim.launch.py gz_args:=empty.sdf`, which picks the right executable. |
| V58 | D4 | Fast DDS UDP-only XML (bare `<participant>`) | Incomplete. It needs the `<profiles>` root and a `<transport_descriptors>` block declaring `UdpTransport` with type `UDPv4`. Load it with `FASTRTPS_DEFAULT_PROFILES_FILE`. |
| V30 | B7, E1 | "executor runs callbacks FIFO" | It is roughly FIFO only while callbacks finish faster than events arrive. Under backlog the executor serves ready entities **round-robin, not FIFO**, with no ordering guarantee. |
| V22 | all py code | `get_logger().warn(...)` | `warn()` is already a deprecated alias in Humble. Use `warning()`, which works in every distro. `warn()` is **removed in Lyrical**. |
| V07 | A2 | "Canonical" setup.py uses `tests_require=['pytest']` | The current Humble `ros2 pkg create` template (ros2cli #1103, Sept 2025) uses `extras_require={'test': ['pytest']}`. Both still build on Humble, but the canonical template should match. |

### Intermediate course
| ID | Section | Origin | Error | Correct Humble statement |
|---|---|---|---|---|
| V81 | P09 | true for colcon-core < 0.16 (the course was written in 2022) | "`--symlink-install` only helps Python scripts; launch and param files in `install/` are hard copies" | colcon-core ≥ 0.16.0 (2024; the ROS apt repo for Jammy ships 0.21.3) also **symlinks every `data_files` entry** of an ament_python package into `install/`: edits to existing launch/config files apply without a rebuild; a new file still needs `colcon build` (the glob runs at build time). ament_cmake packages symlink installed files too. Docs: [colcon-core #592][colcon592], [symlink_data.py][colcon-symlink], [apt index][apt-jammy] |
| V83 | P15 | course mistake: remap syntax used for parameters | `ros2 run <pkg> <exe> --ros-args argument1:=VALUE` passes a value to the node | After `--ros-args` a bare `name:=value` is an unknown ROS argument: creating the node raises `UnknownROSArgsError`. Parameter: `--ros-args -p name:=value`; remap: `-r from:=to`; file: `--params-file f.yaml`. `--show-args` exists only for `ros2 launch`. Docs: [rcl arguments.c (humble)][rcl-args-h], [node arguments][node-args-h] |
| V87 | P29 | course claim, not true for Humble's rmw_fastrtps | "Fast DDS does not support incompatible QoS events; Cyclone does" | Humble's `rmw_fastrtps` raises `OFFERED_QOS_INCOMPATIBLE` / `REQUESTED_QOS_INCOMPATIBLE`; both RMWs call the `incompatible_qos` event callbacks. Docs: [custom_publisher_info.cpp (humble)][fastrtps-ev-h], [QoS concept][qos-doc] |
| V88 | P28, P29 | Galactic's default (Cyclone) | "In Humble, by default, cyclonedds is used"; "Cyclone is installed when you install ROS 2" | Humble's default is **Fast DDS** (`rmw_fastrtps_cpp`, V03). `ros-humble-rmw-implementation` depends on `rmw-fastrtps-cpp \| rmw-cyclonedds-cpp \| rmw-connextdds`, so apt installs Fast DDS only; Cyclone needs `sudo apt install ros-humble-rmw-cyclonedds-cpp`. Docs: [middleware vendors (humble)][mw-vendors-h], [apt index][apt-jammy] |
| V89 | P29 | course mistake | "after `export RMW_IMPLEMENTATION=…`, `ros2 doctor` still reports the default Fast DDS" | `ros2 doctor --report` prints `rclpy.get_rmw_implementation_identifier()` of its own process: it shows the RMW exported in that shell. Docs: [ros2doctor rmw.py (humble)][doctor-rmw-h] |
| V90 | P29 | course mistake | Connext: "a 30-day trial, you cannot use it for commercial purposes" | The RTI Connext libraries of the ROS apt repo (`rti-connext-dds-6.0.1` or `rti-connext-dds-7.3.0-ros`; `sudo apt install ros-humble-rmw-connextdds` pulls them in) are free for prototyping, research, non-commercial and academic use; commercial use needs an RTI license. Docs: [Connext (humble)][connext-h] |
| V91 | P29 | course mistake | "the ros2 daemon lets a new node avoid discovering the whole graph" | The daemon only serves the **command-line tools** (`ros2 node list`, `ros2 topic list`, …): the first CLI command starts it, nodes never use it. It keeps the RMW it was started with: after changing `RMW_IMPLEMENTATION` run `ros2 daemon stop`, or the CLI shows nothing or fails. Docs: [CLI tools (humble)][cli-concepts-h], [multiple RMWs (humble)][multi-rmw-h] |
| V94 | P25 | generalization from one AUTOMATIC test | "LeaseDuration is only used with MANUAL_BY_TOPIC" | The lease duration applies to both kinds and to compatibility (publisher lease ≤ subscriber lease). With AUTOMATIC the DDS RMWs assert the writer's liveliness while its process runs, so it is lost only when the process hangs or dies; a cleanly stopped publisher is reported at once (`alive_count_change=-1`). Docs: [QoS concept][qos-doc], [DDS 1.4 LIVELINESS][dds-spec] |
| V97 | P33 | course mistake (lines appended after `ament_package()`) | `CMakeLists.txt` with `ament_package()` before `add_executable` / `install` | `ament_package()` gathers information from the whole file and should be the **last** call. Docs: [ament_cmake docs (humble)][ament-doc-h] |
| V98 | P33 | true until Galactic | "managed nodes are available for C++, not Python" | Humble has `rclpy.lifecycle` (V51): Python lifecycle nodes and publishers. Docs: [rclpy lifecycle (humble)][lc-h] |
| V99 | P33 | incomplete (the example returns FAILURE) | "an uncaught exception jumps to `on_error`, taking the node to finalized" | An exception or `ERROR` return goes to *ErrorProcessing* → `on_error`: `SUCCESS` → **unconfigured** (recovered), `FAILURE`/`ERROR` → finalized. A transition returning `FAILURE` goes back to its start state. Docs: [default_state_machine.c (humble)][lc-sm-h] |
| V102 | P15 | course bug | `move_robot_with_arguments.py` switches mode with `if … if …` | Both branches run on every tick, so the robot always ends turning; use `elif` (the parameter version of the course does). |
| V103 | P04 | course typo | `ros pkg create <package_name> --build-type ament_python my_package --dependencies …` | `ros2 pkg create --build-type ament_python <package_name> --dependencies <deps>` |
| V105 | P05 | course mistake | "`colcon build --packages-select <pkg>` compiles the packages specified and their dependencies" | `--packages-select` builds **only** the listed packages (their dependencies must already be built or installed); `--packages-up-to <pkg>` builds the package and its recursive dependencies. Docs: [colcon package selection][colcon-sel] |

### Security course (SROS2)
| ID | Section | Origin | Error | Correct Humble statement |
|---|---|---|---|---|
| V106 | sec P12 | course mistake | `governance.p7s` is "a Synchronized Multimedia Integration Language (SMIL) signed file" | It is an **S/MIME** document: the XML in clear text plus a detached PKCS#7 signature made with the **Permissions CA** key. SMIL is unrelated. Code: [`_sign_bytes`][sros2-util-h]; docs: [keystore tutorial][sec-ks-h] |
| V107 | sec P12 | course mistake | An enclave "must contain six files", listed as governance.p7s, `identity_ca.cert.pm`, `permissions_ca.cert.pm`, **permissions.xml ("signed")**, cert.pem, key.pem | The six files the RMW loads are `identity_ca.cert.pem`, `cert.pem`, `key.pem`, `permissions_ca.cert.pem`, `governance.p7s` and **`permissions.p7s`** (the signed file); `crl.pem` is optional. `permissions.xml` is the unsigned source, kept to re-sign; DDS does not read it. Code: [rmw_dds_common][rdc-sec-h]; docs: [keystore tutorial][sec-ks-h], [About security][sec-about-h] |
| V108 | sec P12 | course mistake | After showing `permissions.xml`: "if you change this policy, insert a space…, the signature becomes invalid and the robot will not launch" | That happens when **`permissions.p7s`** is edited (with `Enforce`, the node fails to start). Editing `permissions.xml` alone changes nothing at runtime: change the policy and rerun `generate_artifacts` (or `create_permission`), or re-sign the XML with `openssl smime -sign` and the Permissions CA private key. Docs: [keystore quiz][sec-ks-h], [access controls][sec-ac-h] |
| V109 | sec P07, P12 | course contradiction (its own XML and `ll` output) | "Two enclaves have been generated, gazebo and teleop" | The policy defines **three**: `/gazebo`, `/teleop` and the root enclave `/` (allow-all `*`). The root enclave's `cert.pem`, `key.pem`, `permissions.xml/.p7s` sit directly in `enclaves/`, as the course's own listing shows. It is also the enclave of every node started without `--enclave` or override (V127). Code: [`create_enclave`][sros2-encl-h], [`exact_match_lookup`][rcl-sec-h] |
| V110 | sec P06, P10 | course contradiction (2.1.1 says the certificate binds the key to a name) | "A certificate is a public key" | A certificate **contains** a public key plus the subject name, signed by a CA (the CA certificate is self-signed). Docs: [keystore tutorial][sec-ks-h], [About security][sec-about-h] |
| V111 | sec P10 | course mistake | "The default user is sros2CA" | `sros2CA` is the default **common name** of the CA certificate (subject = issuer), not a user. Code: [`_DEFAULT_COMMON_NAME`][sros2-ks-h] |
| V112 | sec P11 | course mistake | "Every robot should have a different key; your key materials will not work on another robot" | Keys are files and work wherever they are copied; that is why `private/` should stay off the robot. A CA may be unique per robot or shared by a fleet that must trust each other; participants only accept certificates signed by their own identity CA. Docs: [keystore tutorial][sec-ks-h], [deployment guidelines][sec-deploy-h] |
| V113 | sec P12 | course claim, partly wrong | "The certificates are keyed to a domain; if you change your domain ID, they will not work" | Certificates have no domain. `governance.xml` and every `permissions.xml` contain `<id>` = `ROS_DOMAIN_ID` at generation time (default `0`): set `ROS_DOMAIN_ID` before creating the keystore and artifacts, or regenerate after a change. Runtime effect of a mismatch `[verify]`. Code: [`_create_governance_file`][sros2-ks-h], [`create_permission_file`][sros2-perm-h] |
| V114 | sec P13 | course contradiction (its own `ros2 pkg create` output) | "Go to `~/ros2_ws/src/unit2_pkg/unit2_pkg/setup.py`" (same for `package.xml`) | Both files are in the package root `~/ros2_ws/src/unit2_pkg/`; the inner `unit2_pkg/` folder holds the Python module. Template: [ament_python][tpl-dir-h] |
| V115 | sec P13 | course mistake | `package.xml` with only `<exec_depend>geometry_msgs</exec_depend>` for a node that imports `rclpy` | Add `<exec_depend>rclpy</exec_depend>`: the course package runs only because rclpy is already installed, and rosdep would not install it. Docs: [Python pub/sub tutorial][pubsub-py-h] |
| V116 | sec P02 | course claim, imprecise | "SROS2 … is contained within the ROS Client Library (RCL)" | The `ros2 security` tools are the **`sros2`** package (a ros2cli extension in the `ros_core` variant, [REP 2001][rep2001]); rcl only reads the `ROS_SECURITY_*` variables and finds the enclave directory, and the RMW loads the DDS-Security plugins. Code: [sros2 verbs][sros2-verbs-h], [rcl security.c][rcl-sec-h] |
| V138 | sec P13 | course mistake | `package.xml` with `<exec_depend>geometry_msgs</exec_depend>` placed after `</export>` | Package format 3 requires every dependency **before** `<export>`, which is the last element ([package_format3.xsd][pkg-xsd3]). colcon still builds it, but the file is not schema-valid: move the `exec_depend` lines above `<export>`. |
| V139 | sec P07 | course mistake (terminology) | "Use a _governance_file.xml_ called _turtlebot3_gazebo_policy.xml_ to create the overall enclaves" | That file is an **SROS2 policy** (`<policy version="0.2.0">`, enclaves and profiles). The DDS **governance** document is a different file, `enclaves/governance.xml`, written by `create_keystore`. Code: [policy.xsd][sros2-xsd-h], [`_create_governance_file`][sros2-ks-h] |

## Full table
| # | Sheet | Statement | Humble | Jazzy | Lyrical | Action | Source | Confidence |
|---|---|---|---|---|---|---|---|---|
| V01 | A1 | `ROS_LOCALHOST_ONLY=1` isolates a host | ✓ documented | Deprecated since Iron but still honored (rcl warns). Docs use `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST` | **Removed (Kilted)**, no effect. Use `ROS_AUTOMATIC_DISCOVERY_RANGE` / `ROS_STATIC_PEERS` | annotate | [env-h][env-h], [Iron notes][iron], [env-j][env-j], [rcl init.c (jazzy)][rcl-init-j], [rcl#1169][rcl1169], [Kilted changelog][kilted-cl] | High |
| V02 | A1, D5 | `ROS_DOMAIN_ID` safe 0–101, max 232 | ✓ | ✓ | ✓ | keep | [Domain ID][domain] | High |
| V03 | A1, D5 | Default RMW `rmw_fastrtps_cpp`; Cyclone optional | ✓ (Fast DDS 2.6) | ✓ (2.14) | ✓ (Fast DDS 3.6). Kilted renamed the packages fastrtps→fastdds (RMW names unchanged); Zenoh is Tier 1 | annotate | [REP 2000][rep2000], [Kilted notes][kilted], [Lyrical platforms][lyr-plat] | High |
| V04 | A1 | Ubuntu 22.04 / Python 3.10 | ✓ | 24.04 / 3.12 | 26.04 / 3.14 | annotate | [REP 2000][rep2000], [Lyrical platforms][lyr-plat] | High |
| V05 | A1 | colcon_cd + argcomplete lines in `.bashrc` | ✓ | ✓ | ✓ | keep | [Colcon tutorial][colcon-tut] | High |
| V06 | A1 | `rosdep install --from-paths src --ignore-src -r -y` | ✓ | ✓ | ✓ | keep | [Colcon tutorial][colcon-tut] | High |
| V07 | A2 | setup.py `tests_require=['pytest']` | Current template: `extras_require={'test': ['pytest']}` (both work) | template `extras_require` | template `extras_require` | **fix** | [template (humble)][tpl-py], [ros2cli#1103][cli1103] | High |
| V08 | A2 | setup.cfg "leave as generated" | Template uses underscore keys `script_dir` / `install_scripts`. The dash form `script-dir` from old templates triggers a setuptools deprecation warning | same | same | annotate | [setup.cfg template][tpl-cfg] | High |
| V09 | A2, B2, D1 | `ament_target_dependencies(tgt rclcpp std_msgs)` | ✓ canonical | ✓ | **Deprecated (Kilted)** with a CMake warning. **Removed in Lyrical**. Replacement: `target_link_libraries(tgt PUBLIC rclcpp::rclcpp ${std_msgs_TARGETS})` | annotate | [Kilted notes][kilted], [ament_cmake#583][ament583], [#614][ament614], [Lyrical changelog][lyrical-cl] | High |
| V10 | A2 | Portable form `${<pkg>_TARGETS}` also works in Humble | rosidl exports `<pkg>_TARGETS` in Humble `[verify]` (Phase 5 build) | ✓ | ✓ | annotate | [rosidl export targets (humble)][rosidl-tgt] | Medium |
| V11 | A2 | `cmake_minimum_required(VERSION 3.8)` | ✓ (CMake 3.22) | ✓ (3.28) | CMake 4.x on Resolute. Lyrical core bumped minimum versions to silence CMake deprecation warnings. 3.8 still configures but warns `[verify]` | annotate | [Lyrical platforms][lyr-plat], [Lyrical changelog][lyrical-cl] | Medium |
| V12 | A2 | `ros2 pkg create … --node-name`, `ros2 pkg executables/prefix/xml` | ✓ | ✓ | ✓ | keep | [ros2cli (humble)][cli-h] | High |
| V13 | A3 | `SetuptoolsDeprecationWarning` harmless; silence with `pip install setuptools==58.2.0` | Harmless ✓. The downgrade is a community workaround, not official | `pip install` into system Python is blocked by PEP 668 (Ubuntu 24.04). Do not downgrade | same | annotate | [answers.ros.org][setuptools-ans], [PEP 668][pep668] | Medium |
| V14 | A3 | colcon flags (`--symlink-install`, `--packages-select/up-to`, `--parallel-workers`, `--executor sequential`, `--event-handlers console_direct+`, `--continue-on-error`, `--cmake-args`, `--mixin`) | ✓ | ✓ | ✓ | keep | [colcon build][colcon-docs] | High |
| V15 | A4, D5 | `from launch_ros.actions import PushRosNamespace` | ✓ only name in Humble | Renamed `PushROSNamespace` (Iron); old name kept as alias | alias still present | annotate | [Iron notes][iron], [launch_ros (lyrical)][lr-init-l] | High |
| V16 | A4 | `ros2 launch … --show-args / --print / --debug` | ✓ | ✓ | ✓ | keep | [ros2launch (humble)][lr-launch-h] | High |
| V17 | A4 | `LaunchConfiguration` + `OpaqueFunction` + `.perform(context)` | ✓ | ✓ | ✓ | keep | — (API unchanged in release notes) | High |
| V18 | A4 | `PathJoinSubstitution([...])` | ✓ | ✓ | Kilted+ also concatenates within one component (`[cfg, '.xacro']`) | annotate (optional) | [Kilted notes][kilted] | High |
| V19 | A4, C2 | `ParameterValue(Command(['xacro ', f]), value_type=str)` | ✓ | ✓ | ✓. RSP can also read `robot_description` from a topic (Lyrical) | annotate (optional) | [Lyrical notes][lyrical] | High |
| V20 | A4 | `ExecuteProcess(cmd=['gz','sim','empty.sdf'])` | ✗ with Fortress → `ign gazebo`. `gz sim` = Garden/Harmonic | ✓ (Harmonic) | ✓ (Jetty) | **fix** | [ros_gz README (humble)][rosgz-h], [gz_sim.launch (humble)][rosgz-sim-h] | High |
| V21 | A4 | `Trace(session_name=…)` (tracetools_launch); output `~/.ros/tracing/<name>` | Action ✓; dir = `$ROS_TRACE_DIR` or `$ROS_HOME/tracing` ✓. Needs instrumentation (V40) | ✓ | ✓ | annotate | [path.py (humble)][trace-path-h] | High |
| V22 | B1…E3 | `get_logger().warn(...)` | Deprecated alias of `warning()` | still deprecated | **Removed** → `AttributeError` | **fix** (use `warning()`) | [rcutils_logger (humble)][logger-h], [(lyrical)][logger-l] | High |
| V23 | B1 | Logging kwargs `throttle_duration_sec`, `once`, `skip_first` | ✓ | ✓ | ✓ | keep | [rcutils_logger (humble)][logger-h] | High |
| V24 | B1 | `from rclpy.executors import ExternalShutdownException` | ✓ | ✓ | ✓ | keep | [executors.py (humble)][exec-py-h] | High |
| V25 | B1 | `--ros-args` (`-r`, `-p`, `--params-file`, `--log-level name:=lvl`) | ✓ | ✓; adds `--log-file-name` | ✓; logging backend selectable at runtime | annotate (optional) | [Jazzy notes][jazzy], [Lyrical notes][lyrical] | High |
| V26 | B2 | Topic CLI flags: echo `--field --no-arr --no-str --flow-style --once --qos-*`; pub `--once --rate --times`; hz `--window`; list `-t --include-hidden-topics`; info `-v` | ✓ all verified | Iron+: echo `--timeout`, pub `--max-wait-time`, `now`/`auto` keywords; hz/bw/pub honor `use_sim_time`; `--lost-messages` removed | + `ros2 topic bw` on several topics | annotate | [ros2cli (humble)][cli-h], [Iron notes][iron], [Lyrical notes][lyrical] | High |
| V27 | B2 | C++ sub callback `ConstSharedPtr` | ✓ (non-const signatures deprecated) | Non-const `shared_ptr<MessageT>` signatures **removed** | removed | keep (+ pitfall) | [Jazzy notes][jazzy] | High |
| V28 | B3 | rosidl package template (CMake + package.xml) | ✓ | ✓ | ✓ (`actionlib_msgs` removed, not used here) | keep | [Lyrical changelog][lyrical-cl] | High |
| V29 | B5 | `action_tutorials_interfaces/action/Fibonacci` (feedback `partial_sequence`) | ✓ | ✓ | **Removed (Kilted)**. Demos use `example_interfaces/action/Fibonacci`, whose feedback field is `sequence`. That type already exists in Humble | annotate | [demos (humble…lyrical)][demos-act], [example_interfaces Fibonacci][ex-fib] | High |
| V30 | B7, E1 | Executor runs callbacks FIFO | ✗: round-robin under backlog, no FIFO guarantee | Ordering explicitly not consistent (WaitSet executors) | same | **fix** | [Executors concept][executors], [Jazzy notes][jazzy] | High |
| V31 | B7 | MT executor default threads = CPU count | ✓ (rclpy `cpu_count()`, fallback 1; rclcpp `hardware_concurrency()`) | fallback changed to 2 (Iron) | same | keep | [executors.py][exec-py-h], [rclcpp MT][exec-cpp-h], [Iron notes][iron] | High |
| V32 | B7, D2 | C++ `StaticSingleThreadedExecutor` (lower overhead) | ✓ | ✓; default executors adopted its collection strategy | **Deprecated (Kilted)**, **removed in Lyrical** → `SingleThreadedExecutor` | annotate | [rclcpp (kilted)][sste-k], [rclcpp executors (lyrical)][sste-l] | High |
| V33 | B7 | Executor types (Single, MultiThreaded) | ✓ | + rclcpp EventsExecutor (experimental, since Iron) | + rclpy EventsExecutor (Kilted, exp.); Callback Group Events executor (rclcpp); rclpy `AsyncNode` (asyncio) | annotate (optional) | [Iron notes][iron], [Kilted notes][kilted], [Lyrical notes][lyrical] | High |
| V34 | B8 | Presets: sensor_data BEST_EFFORT/VOLATILE/5, services RELIABLE/VOLATILE/10, parameters …/1000, int depth = KEEP_LAST/RELIABLE/VOLATILE | ✓ | ✓; warning on KEEP_LAST depth 0 (Iron) | ✓ | keep | [rmw qos_profiles.h][rmw-qos], [QoS concept][qos-doc] | High |
| V35 | B8 | `qos_profile_system_default` = RELIABLE/VOLATILE/10 | ✗ all policies SYSTEM_DEFAULT | same | same | **fix** | [rmw qos_profiles.h][rmw-qos], [QoS concept][qos-doc] | High |
| V36 | B8 | Deadline/Lifespan/Liveliness default "∞ / AUTOMATIC" | ✗ liveliness SYSTEM_DEFAULT, durations "default" | same | same | **fix** | [rmw qos_profiles.h][rmw-qos] | High |
| V37 | B6 | `declare_parameter(name, default, descriptor)` | ✓ | Declaring a statically typed parameter **without a default** is rejected | same | annotate (pitfall) | [Jazzy notes][jazzy] | High |
| V38 | B6 | `add_on_set_parameters_callback` | ✓ | + pre/post set callbacks (Iron) | ✓ | annotate (optional) | [Iron notes][iron] | High |
| V39 | B6 | `ros2 param dump /n > file.yaml` | ✓ (stdout default; `--print`/`--output-dir` deprecated) | those options removed (Iron); `--timeout` added | + get from all nodes; get/set several params | keep | [dump.py (humble)][dump-h], [Iron notes][iron], [Lyrical notes][lyrical] | High |
| V40 | B7, A4, C5 | `sudo apt install ros-humble-ros2trace` + `ros2 trace --session-name x` | ✗ binaries have no tracepoints → LTTng + build `tracetools` from source; CLI flags `-s -p -u -k -c -l` ✓ (interactive Enter) | Instrumentation built in (since Iron); + verbs `ros2 trace start/stop/pause/resume` | + snapshot mode, dual session, runtime opt-out | **fix** | [ros2_tracing README (humble)][trace-readme-h], [args.py][trace-args-h], [Iron notes][iron], [verbs (jazzy)][trace-verbs-j], [Lyrical notes][lyrical] | High |
| V41 | B9 | `rclpy.init(signal_handler_options=SignalHandlerOptions.NO)` | ✓ | ✓ | ✓ | keep | [signals.py (humble)][signals-h] | High |
| V42 | B9 | `apt install ros-humble-tf-transformations && pip3 install transforms3d` | ✓ | `pip3 install` blocked (PEP 668). Use `sudo apt install python3-transforms3d` | same | annotate | [apt index (jammy)][apt-jammy], [PEP 668][pep668], [python3-transforms3d (noble)][noble-t3d] | High |
| V43 | C1 | `static_transform_publisher --x … --frame-id … --child-frame-id …`; legacy positional args | Flags ✓; positional deprecated (warning) | same | **Positional removed** | annotate | [program (humble)][stp-h], [program (lyrical)][stp-l] | High |
| V44 | C1 | C++ includes `tf2_ros/*.h`, `tf2/LinearMath/Quaternion.h` | `.h` and `.hpp` both exist | `tf2_geometry_msgs.h`, `tf2_eigen.h`, etc. removed (not used here) | `Quaternion.h` deprecated (Kilted) then **removed**; `tf2_ros/*.h` deprecated (`#warning`) | annotate. Code uses `.hpp` (valid since Humble) | [Jazzy notes][jazzy], [Quaternion.h (kilted)][quat-k], [LinearMath (lyrical)][quat-l], [transform_broadcaster.h (lyrical)][tf2-h-l] | High |
| V45 | C1 | `view_frames` listens 5 s → `frames_<date>.pdf/.gv` | ✓ (`--wait-time`) | ✓ | ✓ | keep | [view_frames.py][vf-h] | High |
| V46 | C3 | sqlite3 is the default storage; mcap needs `ros-humble-rosbag2-storage-mcap` | ✓ | **mcap default (Iron)** | mcap default | annotate | [Iron notes][iron], [apt index (jammy)][apt-jammy] | High |
| V47 | C3 | record `-a -e -x -o -s -b -d --compression-*` | ✓ all exist | `-a` = all topics **and services** (`--all-topics` for topics only); `-x/--exclude` → `--exclude-regex` (no `-x` in record); + `--topics --services --topic-types --exclude-topics` | + circular recording, remote control via services, Python API | annotate | [record.py (humble)][bag-rec-h], [record.py (jazzy)][bag-rec-j], [Jazzy notes][jazzy], [Lyrical notes][lyrical] | High |
| V49 | C3 | play `-r -l --topics --clock --start-offset --start-paused` | ✓ | + `--exclude-regex/-x`, `--services`, `--publish-service-requests`, `--playback-duration` | + several bags with `-i` (Kilted), progress bar | annotate | [play.py (humble)][bag-play-h], [Jazzy notes][jazzy], [Kilted notes][kilted] | High |
| V50 | C3 | `ros2 bag convert -i bag -o out.yaml` | ✓ | ✓ | ✓ | keep | [convert.py (humble)][bag-conv-h] | High |
| V51 | C4 | `rclpy.lifecycle` (`Node`, `State`, `TransitionCallbackReturn`, `create_lifecycle_publisher`, `is_activated`) | ✓ (new in Humble) | ✓; launch `LifecycleTransition` action (Iron) | ✓ | keep | [rclpy lifecycle (humble)][lc-h], [Iron notes][iron] | High |
| V52 | C4, D3 | `ros2 run nav2_util lifecycle_bringup <node>` | ✓ | ✓ | `[verify]` | keep | [nav2_util (humble)][nav2-util-h] | Medium |
| V48 | D3 | Nav2 cmd chain with collision_monitor | ✗ (see fix table) | ✓ chain as written | ✓ + TwistStamped | **fix** | [bringup (humble)][nav-bring-h], [bringup (jazzy)][nav-bring-j], [Nav2 Humble→Iron][nav-mig-h2i] | High |
| V54 | D3 | `/cmd_vel` is `geometry_msgs/Twist` | ✓ | Opt-in `enable_stamped_cmd_vel` (default false) | **TwistStamped default (Kilted)** | annotate | [Nav2 Iron→Jazzy][nav-mig-i2j], [Nav2 Jazzy→Kilted][nav-mig-j2k] | High |
| V55 | D3 | MPPI, Collision Monitor, Route server available | Packages exist in Humble binaries (later backports; Nav2 docs list them under Humble→Iron) | ✓ + docking (`opennav_docking`) | ✓ + following server; Nav2 lifecycle-node refactor | annotate | [apt index (jammy)][apt-jammy], [Nav2 Humble→Iron][nav-mig-h2i], [Nav2 Kilted→Lyrical][nav-mig-k2l] | High |
| V56 | D3 | BT customization (PipelineSequence, RecoveryNode, RoundRobin, ReactiveFallback, GoalUpdated) | ✓ BehaviorTree.CPP v3 | **BT.CPP 4.5** → XML/SubTree syntax migration | ✓ | annotate | [Nav2 Iron→Jazzy][nav-mig-i2j] | High |
| V57 | D3 | Plugin names (`nav2_costmap_2d::InflationLayer`) | ✓; other plugins mix `/` and `::` | All standardized to `::` | ✓ | annotate | [Nav2 Iron→Jazzy][nav-mig-i2j] | High |
| V53 | D3 | MoveIt2 parallel planning in Humble; STOMP | ✗ (see fix table) | ✓ (Iron+) | ✓ | **fix** | [planning_component.h (humble)][mi-pc-h], [moveit_planners (humble)][mi-plan-h], [(iron)][mi-plan-i] | High |
| V59 | D3 | `moveit_py` "Humble+" | Binary `ros-humble-moveit-py` exists (MoveIt 2.5.x). The official Python API tutorial lives in the main docs only | ✓ | ✓ | annotate | [apt index (jammy)][apt-jammy], [rosdistro humble][rosdistro-h], [tutorial (main)][mi-tut-main] | High |
| V60 | D3 | ros2_control: `robot_description` source | `ros2_control_node` takes `robot_description` as a **parameter** | CM subscribes to `/robot_description` (from RSP); parameter support removed | same | annotate | [ros2_control migration (jazzy)][rc-mig-j] | High |
| V62 | D3, C6 | `ros2 control switch_controllers --activate X --deactivate Y`; `list_controllers`, `list_hardware_interfaces` | ✓ (`--start/--stop` deprecated aliases) | `--start/--stop` removed; + `--activate-asap`, `--best-effort` | ✓ | keep | [switch (humble)][rc-sw-h], [switch (jazzy)][rc-sw-j] | High |
| V63 | D3, D2 | `mock_components/GenericSystem` | ✓ | ✓ | ✓ | keep | [ros2_control migration][rc-mig-j] | High |
| V64 | D4 | Gazebo "Modern (Fortress/Harmonic)" with ros_gz | Official: Fortress (packages.ros.org). Harmonic with Humble = packages.osrfoundation.org, "use with caution" | Harmonic (+ `gz_*_vendor` packages) | Jetty (Kilted: Ionic) | annotate | [REP 2000][rep2000], [ros_gz README][rosgz-h], [Jazzy notes][jazzy], [Lyrical platforms][lyr-plat] | High |
| V65 | D4 | Gazebo Classic 11 "EOL" | EOL **2025-01-31** | Not supported | Not supported | annotate (add date) | [Gazebo Classic EOL][gz-classic-eol] | High |
| V66 | D4 | Bridge YAML `gz_type_name: "gz.msgs.Twist"` | Fortress tables use `ignition.msgs.*`. The Humble bridge accepts both `ignition.msgs.*` and `gz.msgs.*` names (confirmed 2026-10-20 in `resource/get_mappings.cpp.em`, see GZ-V26 in version_audit_gazebo.md) | `gz.msgs.*` | `gz.msgs.*` | annotate | [bridge README (humble)][rosgz-bridge-h], [mappings (humble)][rosgz-gen-h] | High |
| V58 | D4 | Fast DDS UDP-only profile XML | ✗ incomplete (see fix table); env `FASTRTPS_DEFAULT_PROFILES_FILE` | same | env `FASTDDS_DEFAULT_PROFILES_FILE` (Fast DDS 3, Kilted rename) | **fix** | [Isaac Sim ROS 2 install][isaac-ros2], [FastDDS config (humble)][fdds-h], [(rolling)][fdds-r], [Kilted notes][kilted] | High |
| V67 | D4, A1 | Isaac Sim + Humble: "source /opt/ros/humble before isaac-sim.sh"; Cyclone "recommended" | Current Isaac Sim (Python 3.11/3.12) cannot load system Humble rclpy (Python 3.10) and uses its **internal** ROS libraries. Docs default to Fast DDS. "Never put internal libs in .bashrc" ✓ `[verify per Isaac Sim version]` | System Jazzy libs compatible on 24.04 | — | annotate | [Isaac Sim ROS 2 install][isaac-ros2] | Medium |
| V68 | D4 | Isaac ROS NITROS GEMs | Isaac ROS 3.2 = Humble (Jetson Orin) | Isaac ROS 4.x = Jazzy | — | annotate | [NVIDIA forum][isaac-ros-forum] | Medium |
| V69 | D4 | `use_sim_time` rules; Nav2 yaml `use_sim_time` | ✓ | Nav2: set from launch, removable from yaml (Iron) | ✓ | keep | [Nav2 Humble→Iron][nav-mig-h2i] | High |
| V61 | D5 | `fastdds discovery --ip-address --port` | ✗ → `--udp-address/-l`, `--udp-port/-p` | same | Fast DDS 3 CLI `[verify]` | **fix** | [Discovery Server (humble)][ds-h], [Fast DDS 2.6 server.h][fds26] | High |
| V70 | D5 | Static peers only via DDS XML | ✓ | + `ROS_STATIC_PEERS` env var, RMW-agnostic (Iron) | ✓ | annotate | [Iron notes][iron] | High |
| V71 | D5 | Cyclone XML + `sysctl` (rmem_max, ipfrag_time, ipfrag_high_thresh) | ✓ | ✓ | Cyclone 11 XML compatibility `[verify]` | keep | [DDS tuning][dds-tuning], [Lyrical platforms][lyr-plat] | High |
| V72 | D1 | message_filters Python `Subscriber(node, Type, topic, qos_profile=…)`, `ApproximateTimeSynchronizer` | ✓ | + `ApproximateEpsilonTime`, `LatestTime` policies (Iron, C++) | `[verify]` API changes | keep | [message_filters (humble)][mf-h], [Iron notes][iron] | High |
| V73 | D1 | `nav2_simple_commander.BasicNavigator` (`setInitialPose`, `waitUntilNav2Active`, `goToPose`, `isTaskComplete`, `getResult`) | ✓ | ✓ (+ multi-robot namespacing) | `[verify]` | keep | [robot_navigator.py (humble)][nav-cmd-h], [Nav2 Iron→Jazzy][nav-mig-i2j] | High |
| V74 | D2 | CI `ros-tooling/action-ros-ci@v0.3`, image `setup-ros-docker:ubuntu-jammy-latest` | Works, but the current major is **v0.4** (0.4.8) | Use `ubuntu-noble-latest`, `target-ros2-distro: jazzy` | Resolute image `[verify]` | annotate | [action-ros-ci][arci] | High |
| V75 | D2 | Dockerfile `FROM ros:humble` (builder) → `FROM ros:humble-ros-base` (runtime) | `ros:humble` **is** `humble-ros-base`, so the runtime is not slimmer. Use `ros:humble-ros-core` + exec deps | analogous tags (`jazzy-ros-core`) | `ros:latest` = lyrical | annotate | [official images: ros][docker-ros] | High |
| V76 | D2 | Intra-process zero-copy "rclcpp only in Humble" | ✓ | ✓ | + `rosidl::Buffer` zero-copy publish (new) | annotate (optional) | [Lyrical notes][lyrical] | Medium |
| V77 | C5 | `ros2 doctor --report / --include-warnings`, `ros2 wtf` | ✓ | ✓ | report adds Actions, Services, env vars | keep | [ros2cli (humble)][cli-h], [Lyrical notes][lyrical] | High |
| V78 | C6, B5 | `ros2 action type /a` | ✗ absent (use `ros2 action list -t`) | ✓ added | ✓ | annotate | [Jazzy notes][jazzy] | High |
| V79 | C6 | `ros2 component load … -e use_intra_process_comms:=true` | ✓ | ✓ | ✓ | keep | [ros2cli (humble)][cli-h] | High |
| V80 | E3 | Unit 5 tracing on the course platform (Humble) | Depends on V40: the course image must ship instrumented `tracetools` `[verify on the platform]` | — | — | annotate | [ros2_tracing README][trace-readme-h] | Medium |
| V81 | P09 | `--symlink-install` links only Python modules; launch/param files are copies | ✗ outdated: colcon-core ≥ 0.16 (Jammy repo: 0.21.3) symlinks `data_files` too; new files need a build | same | same | **fix** | [colcon-core #592][colcon592], [symlink_data.py][colcon-symlink], [apt index][apt-jammy] | High |
| V82 | P10 | resource marker: "in future versions you will have to add it to setup.py" | The template already installs it (`share/ament_index/resource_index/packages`). If the line or `package.xml` is missing, colcon-ros still installs both implicitly with a warning that this fallback will be removed | same | same | keep | [colcon-ros ament_python build.py][colcon-ros-py] | High |
| V83 | P15 | `ros2 run <pkg> <exe> --ros-args argument1:=VALUE` | ✗ unknown ROS argument → `UnknownROSArgsError`; use `-p name:=value` | same | same | **fix** | [rcl arguments.c (humble)][rcl-args-h], [node arguments][node-args-h] | High |
| V84 | P15, P16 | "declare a default value, otherwise warnings now and errors in future versions" | ✓ name-only declaration: deprecation warning. Options: default value, a `Parameter.Type`, or `dynamic_typing=True` | ✓ warning (also Kilted) | **TypeError** (declaring only a name is not allowed) | annotate | [node.py (humble)][rclpy-node-h], [node.py (lyrical)][rclpy-node-l] | High |
| V85 | P19 | `MultiThreadedExecutor()` without `num_threads` uses `multiprocessing.cpu_count()` | ✓ | CPUs available to the process (`os.sched_getaffinity`), else `os.cpu_count()`, else 2; warns when `num_threads=1` | same as Jazzy | annotate | [executors.py (humble)][exec-py-h], [executors.py (jazzy)][exec-py-j] | High |
| V86 | P23, P25 | `from rclpy.qos_event import PublisherEventCallbacks, SubscriptionEventCallbacks` | ✓ | moved to `rclpy.event_handler` (Iron); `qos_event` still imports with a deprecation warning (also Kilted) | `rclpy.qos_event` **removed** | annotate | [event_handler.py (jazzy)][evh-j], [rclpy (lyrical)][rclpy-l] | High |
| V87 | P29 | "Fast DDS does not support incompatible QoS events" | ✗ supported (`OFFERED/REQUESTED_QOS_INCOMPATIBLE`) | ✓ | ✓ | **fix** | [custom_publisher_info.cpp (humble)][fastrtps-ev-h] | High |
| V88 | P28, P29 | "Humble default is cyclonedds"; "Cyclone installed with ROS 2" | ✗ default Fast DDS (V03); apt installs only Fast DDS; Cyclone = `ros-humble-rmw-cyclonedds-cpp` | same | same (packages renamed fastrtps→fastdds in Kilted, V03) | **fix** | [middleware vendors (humble)][mw-vendors-h], [apt index][apt-jammy] | High |
| V89 | P29 | `ros2 doctor` keeps reporting Fast DDS after the export | ✗ it reports its own process's RMW | ✓ | ✓ (report adds env vars, V77) | **fix** | [ros2doctor rmw.py (humble)][doctor-rmw-h] | High |
| V90 | P29 | Connext "30-day trial, no commercial use" | ✗ free for prototyping, research, non-commercial and academic use (`rti-connext-dds-6.0.1` / `7.3.0-ros`) | same docs and packages | `[verify]` package version | **fix** | [Connext (humble)][connext-h] | High |
| V91 | P29 | ros2 daemon speeds up node discovery | ✗ it serves the CLI only; keeps its RMW until `ros2 daemon stop` | ✓ (process shown as `_ros2_daemon` in newer ros2cli) | ✓ | **fix** | [CLI tools (humble)][cli-concepts-h], [multiple RMWs][multi-rmw-h] | High |
| V92 | P29 | Zenoh only as a DDS bridge over Wi-Fi/Internet | Bridge exists (zenoh-plugin-dds); also a native **`rmw_zenoh_cpp` binary in Humble (0.1.x)** — needs the router `ros2 run rmw_zenoh_cpp rmw_zenohd` | binary (0.2.x) | **Tier 1** (Kilted) | annotate | [Zenoh (humble)][zenoh-h], [apt index][apt-jammy], [Kilted notes][kilted] | High |
| V93 | P29 | "Navigation, MoveIt, RMF work better with Cyclone" | Community advice from the Humble era; the current Nav2 docs give no RMW recommendation (only a CPU comparison). Test both | — | — | annotate `[verify]` | [Nav2 tuning guide][nav2-tuning] | Medium |
| V94 | P25 | lease duration only used with MANUAL_BY_TOPIC | ✗ used by both kinds and by the compatibility check; AUTOMATIC is asserted by the RMW while the process runs | same | same | **fix** | [QoS concept][qos-doc], [DDS 1.4][dds-spec] | Medium |
| V95 | P25 | "lifespan is only useful with reliable + transient_local" | Lifespan drops any sample older than the duration, whatever the durability; it matters most when old samples are stored (transient_local) | same | same | annotate | [QoS concept][qos-doc] | High |
| V96 | P25 | `ros2 topic echo --qos-durability transient_local` alone fails (Galactic) | Without QoS flags `echo` adapts reliability and durability to the publishers; with any flag the rest comes from the `sensor_data` preset (best effort), so add `--qos-reliability reliable` | ✓ | ✓ | annotate | [echo.py (humble)][echo-h] | High |
| V97 | P33 | `ament_package()` placed before `add_executable` / `install` | ✗ must be the last call | same | same | **fix** | [ament_cmake docs (humble)][ament-doc-h] | High |
| V98 | P33 | managed nodes only in C++ | ✗ `rclpy.lifecycle` exists (V51) | ✓ | ✓ | **fix** | [rclpy lifecycle][lc-h] | High |
| V99 | P33 | uncaught exception → `on_error` → finalized | `on_error` SUCCESS → unconfigured; FAILURE/ERROR → finalized | same | same | **fix** | [default_state_machine.c (humble)][lc-sm-h] | High |
| V100 | P33 | "no lifecycle class for subscribers" | ✓ only `LifecyclePublisher` | ✓ | ✓ still only the publisher | keep | [rclcpp_lifecycle (lyrical)][rclcpp-lc-l] | High |
| V101 | P04, P10 | ament_python template: tests `test_copyright`, `test_flake8`, `test_pep257`; `my_node.py` in the create output | ✓ (`my_node.py` only with `--node-name`) | ✓ same files | + `test_mypy.py`, `test_xmllint.py`, `py.typed` (Kilted) | annotate | [templates (humble)][tpl-dir-h], [templates (kilted)][tpl-dir-k] | High |
| V102 | P15 | `if … if …` mode switch in `move_robot_with_arguments.py` | ✗ course bug: use `elif` | — | — | **fix** | — (logic) | High |
| V103 | P04 | `ros pkg create <package_name> … my_package` | ✗ typo: `ros2 pkg create --build-type ament_python <name>` | — | — | **fix** | [ros2pkg create (humble)][create-h] | High |
| V104 | P12, P15 | `IncludeLaunchDescription(PythonLaunchDescriptionSource(path))` | ✓; a plain path also works (`AnyLaunchDescriptionSource` picks Python/XML/YAML by extension) | ✓ | ✓ | keep | [include_launch_description.py (humble)][include-h] | High |
| V105 | P05 | `--packages-select` also builds the dependencies | ✗ only the listed packages; `--packages-up-to` adds the dependencies | same | same | **fix** | [colcon package selection][colcon-sel] | High |
| V106 | sec P12 | `governance.p7s` = "SMIL signed file" | ✗ S/MIME (clear text + detached PKCS#7), signed by the Permissions CA | ✓ (signed with `cryptography`'s PKCS7 builder) | ✓ | **fix** | [sros2 utilities][sros2-util-h], [keystore][sec-ks-h], [Jazzy changelog][jazzy-cl] | High |
| V107 | sec P12 | 6 enclave files incl. "signed permissions.xml" | ✗ runtime files: identity_ca.cert.pem, cert.pem, key.pem, permissions_ca.cert.pem, governance.p7s, permissions.p7s (+ optional crl.pem) | + PKCS#11 alternatives `*.p11` (V133) | same (moved to `rmw_security_common`, Kilted) | **fix** | [rmw_dds_common][rdc-sec-h], [rmw_security_common (lyrical)][rsc-sec-l], [keystore][sec-ks-h] | High |
| V108 | sec P12 | editing `permissions.xml` breaks the signature | ✗ editing `permissions.p7s` does; the XML is not read at runtime; re-sign or regenerate | same | same | **fix** | [keystore][sec-ks-h], [access controls][sec-ac-h] | High |
| V109 | sec P07, P12 | "two enclaves generated" | ✗ three: `/gazebo`, `/teleop`, `/` (files in `enclaves/` itself) | same | same | **fix** | [create_enclave][sros2-encl-h], [rcl security.c][rcl-sec-h] | High |
| V110 | sec P06, P10 | "a certificate is a public key" | ✗ it contains the public key + subject, signed by a CA | same | same | **fix** | [keystore][sec-ks-h] | High |
| V111 | sec P10 | "default user is sros2CA" | ✗ default CA common name | same | same | **fix** | [_keystore.py][sros2-ks-h] | High |
| V112 | sec P11 | keys "will not work on another robot" | ✗ copied keys work; protect `private/`; CA per robot or per fleet | same | same | **fix** | [keystore][sec-ks-h], [deployment][sec-deploy-h] | High |
| V113 | sec P12 | certificates keyed to the domain ID | ✗ governance/permissions carry `ROS_DOMAIN_ID` at generation; certificates do not | same | same | **fix** | [_keystore.py][sros2-ks-h], [_permission.py][sros2-perm-h] | High (code); runtime effect `[verify]` |
| V114 | sec P13 | `setup.py`/`package.xml` in `unit2_pkg/unit2_pkg/` | ✗ package root | same | same | **fix** | [template][tpl-dir-h] | High |
| V115 | sec P13 | `package.xml` without `rclpy` | ✗ add `<exec_depend>rclpy</exec_depend>` | same | same | **fix** | [pub/sub tutorial][pubsub-py-h] | High |
| V116 | sec P02 | SROS2 "contained within RCL" | ✗ separate `sros2` package (ros_core variant); rcl handles env vars + enclave lookup | same | same | **fix** | [REP 2001][rep2001], [rcl security.c][rcl-sec-h] | High |
| V117 | sec P12 | `openssl smime -verify -in governance.p7s -CAfile ../public/permissions_ca.cert.pem` → `Verification successful` | ✓ checks the Permissions CA signature (works on `permissions.p7s` too) | ✓ | ✓ | keep | [keystore][sec-ks-h] | High |
| V118 | sec P07, P09–P11 | `ros2 security create_keystore <dir>` → `public/` (ca.cert.pem + identity/permissions symlinks), `private/` (ca.key.pem + symlinks), `enclaves/` (governance.xml, governance.p7s); fails if the keystore exists | ✓ | ✓ | ✓; Windows: hard links or copies instead of symlinks | annotate | [_keystore.py][sros2-ks-h], [sros2 utilities (lyrical)][sros2-util-l] | High |
| V119 | sec P10 | CA: ECDSA P-256, SHA-256, `CA:TRUE, pathlen:1`, 10 years | ✓ not before = creation − 1 day, not after = creation + 3650 days | ✓ | not before = creation time (backdate removed) | annotate | [sros2 utilities][sros2-util-h], [Lyrical changelog][lyrical-cl] | High |
| V120 | sec P11 | `ca.key.pem` = root of trust, needed only to add enclaves or change permissions, can live on another machine | ✓ (written as unencrypted PKCS#8 PEM: protect it, keep it offline) | ✓ | ✓ | keep | [sros2 utilities][sros2-util-h], [keystore][sec-ks-h], [deployment][sec-deploy-h] | High |
| V121 | sec P07, P13 | `ros2 security generate_artifacts -k <keystore> -p <policy.xml>` | ✓ `-k`, `-e`, `-p`; creates a missing keystore; keeps existing cert/key, rewrites `permissions.*`; uses current `ROS_DOMAIN_ID` and RMW (`ros_discovery_info` rule only for Fast DDS, Cyclone, Connext) | ✓ | ✓ | keep | [generate_artifacts][sros2-gen-h], [_permission.py][sros2-perm-h] | High |
| V122 | sec P07 | `ros2 security` verbs | ✓ create_keystore, create_enclave, create_permission, generate_artifacts, generate_policy, list_enclaves (+ deprecated create_key, list_keys) | same | **removed (Kilted)**: create_key, list_keys | annotate | [setup.py (humble)][sros2-verbs-h], [setup.py (kilted)][sros2-verbs-k], [Kilted changelog][kilted-cl] | High |
| V123 | sec P12, P13 | policy XML: `<policy version="0.2.0">`, enclave `path`, profile `ns` + `node`, topics publish/subscribe, services reply/request, actions call/execute, ALLOW/DENY, XInclude profiles | ✓ version fixed to 0.2.0 | ✓ | ✓ | keep | [policy.xsd][sros2-xsd-h] | High |
| V124 | sec P12 | "each enclave must contain all the nodes that share the same security policies" | ✓ all profiles of an enclave merge into ONE grant (`CN=<enclave path>`); `node`/`ns` only expand relative and `~` names; nodes of one process share one enclave | ✓ | ✓ | annotate | [permissions.xsl][sros2-xsl-h], [enclaves design][design-encl] | High; wrong `node` name → `~` services denied `[verify]` |
| V125 | sec P12 | teleop `permissions.xml`: `rt/…`, `rq/…Request`, `rr/…Reply`, `ros_discovery_info`, `<default>DENY</default>`, validity = certificate | ✓ DDS topic names | + `~/get_type_description` service in node profiles (sros2 `common/node/types.xml`) | ✓ | annotate | [permissions.xsl][sros2-xsl-h], [name mapping][design-names], [types.xml (jazzy)][sros2-types-j] | High; missing on Jazzy `[verify]` |
| V126 | sec P12 | governance defaults (no unauthenticated participants, join access control, discovery/liveliness ENCRYPT, RTPS SIGN, rule `*` with read/write access control, metadata/data ENCRYPT) | ✓ sros2 default file | ✓ | ✓ | keep | [governance.xml][sros2-gov-h] | High |
| V127 | sec P08 | `ROS_SECURITY_KEYSTORE`, `ROS_SECURITY_ENABLE=true`, `ROS_SECURITY_STRATEGY=Enforce`, `ROS_SECURITY_ENCLAVE_OVERRIDE` | ✓ `true` and `Enforce` case-sensitive (anything else = off / permissive); permissive: missing enclave → node runs unsecured; Enforce → fails; override beats `--enclave`/`-e`; default enclave `/` | ✓ (rcl unchanged) | ✓ | annotate | [rcl security.c][rcl-sec-h], [rcl init.c][rcl-init-h], [DDS-Security design][design-sec], [About security][sec-about-h] | High |
| V128 | sec P08, P13 | `[rcl]: Found security directory: …` INFO line | ✓ | ✓ | ✓ | keep | [rcl security.c][rcl-sec-h] | High |
| V129 | sec P08 | an unsecured shell lists only `/parameter_events`, `/rosout` and no nodes: "the data is encrypted" | ✓; reason: unauthenticated participants cannot join. To inspect the secured graph: same variables + an allowed enclave, `ros2 node list --no-daemon --spin-time 3` | ✓ | ✓ | annotate | [setting up security][sec-intro-h] | High |
| V130 | sec P02, P06 | DDS-Security built-in plugins: authentication, access control, cryptography | ✓ Fast DDS: `builtin.PKI-DH`, `builtin.Access-Permissions`, `builtin.AES-GCM-GMAC`; no secure communication between vendors | ✓ | ✓; `rmw_zenoh_cpp` (Tier 1 in Kilted) is not DDS: `zenoh_security_tools` builds Zenoh configs from the sros2 keystore (router enclave `/zenohd`) | annotate | [Fast DDS participant][fastrtps-part-h], [setting up security][sec-intro-h], [setting up security (lyrical)][sec-intro-l] | High (DDS), Medium (Zenoh) |
| V131 | sec P06 | access control: governance + permissions, both signed by a CA the plugin trusts (may be the identity CA) | ✓ | ✓ | ✓ | keep | [About security][sec-about-h] | High |
| V132 | sec P06 | "encryption and decryption can affect the real-time control loop unless there is dedicated hardware" | course claim, no measurement in the course | — | — | keep (as the course's claim) | — | Medium |
| V133 | sec P11 | "there could be some hardware where security is saved" | files only (`*.pem`) | + PKCS#11 URIs: `key.p11`, `cert.p11`, `*_ca.cert.p11` holding a `pkcs11:` URI (HSM), when the RMW supports it | ✓ | annotate | [rmw_dds_common (jazzy)][rdc-sec-j], [Jazzy changelog][jazzy-cl], [deployment][sec-deploy-h] | High |
| V134 | sec P08 | TurtleBot3: `turtlebot3_gazebo turtlebot3_world.launch.py`, `turtlebot3_teleop teleop_keyboard`, `TURTLEBOT3_MODEL=burger`; teleop limits 0.22/2.84 (Burger), 0.26/1.82 (Waffle) | ✓ binaries; Gazebo Classic 11 (node `/gazebo`) | same launch names, new Gazebo (`ros_gz_sim`, `ros_gz_bridge`): the Classic node profiles no longer match, regenerate (`ros2 security generate_policy`) `[verify]` | same as Jazzy `[verify]` | annotate | [rosdistro humble][rosdistro-h], [rosdistro jazzy][rosdistro-j], [tb3 world launch (jazzy)][tb3-sim-j], [teleop (humble)][tb3-teleop-h] | High; policy on Jazzy `[verify]` |
| V135 | sec P13 | `cmd_vel_subscriber` subscribes `geometry_msgs/Twist` | ✓ Humble teleop publishes `Twist` | ✗ teleop publishes `TwistStamped` (types differ, no data) | same | annotate | [teleop (jazzy)][tb3-teleop-j] | High |
| V136 | sec P07 | policy files from a course repository | the profiles match the public `ros-swg/turtlebot3_demo` `policies/` (Apache-2.0; its `tb3_gazebo_policy.xml` adds Nav2 enclaves) | ✓ | ✓ | keep (public source) | [turtlebot3_demo policies][tb3-demo] | High |
| V137 | sec P12 | "node directories are no longer relevant" | ✓ since Foxy one participant per context; the enclave path is independent of node names | ✓ | ✓ | keep | [enclaves design][design-encl] | High |
| V138 | sec P13 | `<exec_depend>` after `</export>` in `package.xml` | ✗ format 3 order: dependencies before `<export>` | same | same | **fix** | [package_format3.xsd][pkg-xsd3] | High |
| V139 | sec P07 | the policy file called a "governance file" | ✗ it is an SROS2 policy; the governance is `enclaves/governance.xml` | same | same | **fix** | [policy.xsd][sros2-xsd-h], [_keystore.py][sros2-ks-h] | High |
| V140 | sec P08 (2026-10-21) | modern-Gazebo version of the course's TurtleBot3 simulation | none official: branch `humble` of `turtlebot3_simulations` depends on `gazebo_ros_pkgs` (`gzserver`, `gzclient`) | ✓ branch `jazzy`: same `turtlebot3_world.launch.py` with `ros_gz_sim` and `ros_gz_bridge` | no `lyrical` branch (branches `humble`, `jazzy`, `main`) [verify] | annotate (pointer in core-learn-sec-start-here) | [package.xml][tb3-sim-pkg-h], [launch][tb3-sim-world-h], [tb3-sim-j] | High |

## Open `[verify]` items (for Phase 5 / Docker)
1. V10: `target_link_libraries(tgt PUBLIC rclcpp::rclcpp ${std_msgs_TARGETS})` builds on `ros:humble`.
2. V11: CMake warning level for `cmake_minimum_required(VERSION 3.8)` on Lyrical.
3. V66: resolved 2026-10-20 (the Humble bridge accepts both names, GZ-V26).
4. V67/V68: Isaac Sim / Isaac ROS version matrix (outside core; Isaac Sim is not part of ros2-gazebo, still open).
5. V61: Fast DDS 3 discovery CLI on Lyrical. V71: Cyclone 11 XML. V72/V73/V52: Lyrical API checks.
6. V80: is tracing enabled in the course platform Humble image?
7. V90: RTI Connext package version on Jazzy/Lyrical. V93: is Cyclone still advised for Nav2 on Humble? Compare both RMWs
   on the robot. V94: AUTOMATIC liveliness lost after `kill -9` of the publisher (expected: after the lease).
8. V113: what a node does (Enforce) when `ROS_DOMAIN_ID` differs from the domain in its governance/permissions files.
9. V124/V125: with Enforce, does a node fail to start when its profile's `node` name differs from the real node name
   (its `~` parameter services are not granted), and on Jazzy when the profile lacks `~/get_type_description`?
10. V134: TurtleBot3 + security on Jazzy (new Gazebo): which nodes need profiles; build the policy with
    `ros2 security generate_policy` from the running graph and compare with the Classic profiles.
11. Security course examples (keystore, three enclaves, teleop, `cmd_listener`) on Ubuntu 22.04 + Humble.

## Sources
[rep2000]: https://www.ros.org/reps/rep-2000.html
[iron]: https://docs.ros.org/en/rolling/Releases/Release-Iron-Irwini.html
[jazzy]: https://docs.ros.org/en/rolling/Releases/Release-Jazzy-Jalisco.html
[kilted]: https://docs.ros.org/en/rolling/Releases/Release-Kilted-Kaiju.html
[lyrical]: https://docs.ros.org/en/rolling/Releases/Release-Lyrical-Luth.html
[lyr-plat]: https://docs.ros.org/en/rolling/Releases/lyrical/supported-platforms.html
[kilted-cl]: https://docs.ros.org/en/rolling/Releases/Kilted-Kaiju-Complete-Changelog.html
[lyrical-cl]: https://docs.ros.org/en/rolling/Releases/Lyrical-Luth-Complete-Changelog.html
[env-h]: https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Configuring-ROS2-Environment.html
[env-j]: https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Configuring-ROS2-Environment.html
[domain]: https://docs.ros.org/en/humble/Concepts/Intermediate/About-Domain-ID.html
[qos-doc]: https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html
[executors]: https://docs.ros.org/en/humble/Concepts/Intermediate/About-Executors.html
[ds-h]: https://docs.ros.org/en/humble/Tutorials/Advanced/Discovery-Server/Discovery-Server.html
[dds-tuning]: https://docs.ros.org/en/humble/How-To-Guides/DDS-tuning.html
[fdds-h]: https://docs.ros.org/en/humble/Tutorials/Advanced/FastDDS-Configuration.html
[fdds-r]: https://docs.ros.org/en/rolling/Developer-Tools/Introspection-and-analysis/FastDDS-Configuration.html
[colcon-tut]: https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Colcon-Tutorial.html
[colcon-docs]: https://colcon.readthedocs.io/en/released/reference/verb/build.html
[rmw-qos]: https://github.com/ros2/rmw/blob/humble/rmw/include/rmw/qos_profiles.h
[fds26]: https://github.com/eProsima/Fast-DDS/blob/2.6.x/tools/fds/server.h
[rcl-init-j]: https://github.com/ros2/rcl/blob/jazzy/rcl/src/rcl/init.c
[rcl1169]: https://github.com/ros2/rcl/pull/1169
[tpl-py]: https://github.com/ros2/ros2cli/blob/humble/ros2pkg/ros2pkg/resource/ament_python/setup.py.em
[tpl-cfg]: https://github.com/ros2/ros2cli/blob/humble/ros2pkg/ros2pkg/resource/ament_python/setup.cfg.em
[cli1103]: https://github.com/ros2/ros2cli/pull/1103
[cli-h]: https://github.com/ros2/ros2cli/tree/humble
[dump-h]: https://github.com/ros2/ros2cli/blob/humble/ros2param/ros2param/verb/dump.py
[ament583]: https://github.com/ament/ament_cmake/pull/583
[ament614]: https://github.com/ament/ament_cmake/pull/614
[rosidl-tgt]: https://github.com/ros2/rosidl/blob/humble/rosidl_cmake/cmake/rosidl_cmake_export_typesupport_targets-extras.cmake.in
[lr-init-l]: https://github.com/ros2/launch_ros/blob/lyrical/launch_ros/launch_ros/actions/__init__.py
[lr-launch-h]: https://github.com/ros2/launch_ros/blob/humble/ros2launch/ros2launch/command/launch.py
[logger-h]: https://github.com/ros2/rclpy/blob/humble/rclpy/rclpy/impl/rcutils_logger.py
[logger-l]: https://github.com/ros2/rclpy/blob/lyrical/rclpy/rclpy/impl/rcutils_logger.py
[exec-py-h]: https://github.com/ros2/rclpy/blob/humble/rclpy/rclpy/executors.py
[exec-cpp-h]: https://github.com/ros2/rclcpp/blob/humble/rclcpp/src/rclcpp/executors/multi_threaded_executor.cpp
[sste-k]: https://github.com/ros2/rclcpp/blob/kilted/rclcpp/include/rclcpp/executors/static_single_threaded_executor.hpp
[sste-l]: https://github.com/ros2/rclcpp/tree/lyrical/rclcpp/include/rclcpp/executors
[signals-h]: https://github.com/ros2/rclpy/blob/humble/rclpy/rclpy/signals.py
[lc-h]: https://github.com/ros2/rclpy/tree/humble/rclpy/rclpy/lifecycle
[demos-act]: https://github.com/ros2/demos/tree/kilted/action_tutorials
[ex-fib]: https://github.com/ros2/example_interfaces/blob/humble/action/Fibonacci.action
[stp-h]: https://github.com/ros2/geometry2/blob/humble/tf2_ros/src/static_transform_broadcaster_program.cpp
[stp-l]: https://github.com/ros2/geometry2/blob/lyrical/tf2_ros/src/static_transform_broadcaster_program.cpp
[tf2-h-l]: https://github.com/ros2/geometry2/blob/lyrical/tf2_ros/include/tf2_ros/transform_broadcaster.h
[quat-k]: https://github.com/ros2/geometry2/blob/kilted/tf2/include/tf2/LinearMath/Quaternion.h
[quat-l]: https://github.com/ros2/geometry2/tree/lyrical/tf2/include/tf2/LinearMath
[vf-h]: https://github.com/ros2/geometry2/blob/humble/tf2_tools/tf2_tools/view_frames.py
[bag-rec-h]: https://github.com/ros2/rosbag2/blob/humble/ros2bag/ros2bag/verb/record.py
[bag-rec-j]: https://github.com/ros2/rosbag2/blob/jazzy/ros2bag/ros2bag/verb/record.py
[bag-play-h]: https://github.com/ros2/rosbag2/blob/humble/ros2bag/ros2bag/verb/play.py
[bag-conv-h]: https://github.com/ros2/rosbag2/blob/humble/ros2bag/ros2bag/verb/convert.py
[trace-readme-h]: https://github.com/ros2/ros2_tracing/blob/humble/README.md
[trace-args-h]: https://github.com/ros2/ros2_tracing/blob/humble/tracetools_trace/tracetools_trace/tools/args.py
[trace-path-h]: https://github.com/ros2/ros2_tracing/blob/humble/tracetools_trace/tracetools_trace/tools/path.py
[trace-verbs-j]: https://github.com/ros2/ros2_tracing/tree/jazzy/ros2trace/ros2trace/verb
[rc-sw-h]: https://github.com/ros-controls/ros2_control/blob/humble/ros2controlcli/ros2controlcli/verb/switch_controllers.py
[rc-sw-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/ros2controlcli/ros2controlcli/verb/switch_controllers.py
[rc-mig-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/doc/migration.rst
[nav-bring-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_bringup/launch/navigation_launch.py
[nav-bring-j]: https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_bringup/launch/navigation_launch.py
[nav-cmd-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_simple_commander/nav2_simple_commander/robot_navigator.py
[nav2-util-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_util/src/CMakeLists.txt
[nav-mig-h2i]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/Humble.md
[nav-mig-i2j]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/iron/Iron.md
[nav-mig-j2k]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/jazzy/Jazzy.md
[nav-mig-k2l]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/kilted/Kilted.md
[apt-jammy]: http://packages.ros.org/ros2/ubuntu/dists/jammy/main/binary-amd64/Packages.gz
[rosdistro-h]: https://github.com/ros/rosdistro/blob/master/humble/distribution.yaml
[mi-plan-h]: https://github.com/moveit/moveit2/tree/humble/moveit_planners
[mi-plan-i]: https://github.com/moveit/moveit2/tree/iron/moveit_planners
[mi-pc-h]: https://github.com/moveit/moveit2/blob/humble/moveit_ros/planning/moveit_cpp/include/moveit/moveit_cpp/planning_component.h
[mi-tut-main]: https://github.com/moveit/moveit2_tutorials/tree/main/doc/examples/motion_planning_python_api
[rosgz-h]: https://github.com/gazebosim/ros_gz/blob/humble/README.md
[rosgz-bridge-h]: https://github.com/gazebosim/ros_gz/blob/humble/ros_gz_bridge/README.md
[rosgz-gen-h]: https://github.com/gazebosim/ros_gz/blob/humble/ros_gz_bridge/ros_gz_bridge/__init__.py
[rosgz-sim-h]: https://github.com/gazebosim/ros_gz/blob/humble/ros_gz_sim/launch/gz_sim.launch.py.in
[gz-classic-eol]: https://discourse.openrobotics.org/t/gazebo-classic-end-of-life/48748
[isaac-ros2]: https://docs.isaacsim.omniverse.nvidia.com/latest/installation/install_ros.html
[isaac-ros-forum]: https://forums.developer.nvidia.com/t/roadmap-for-isaac-ros-jazzy-on-orin-devices/375982
[docker-ros]: https://github.com/docker-library/official-images/blob/master/library/ros
[arci]: https://github.com/ros-tooling/action-ros-ci
[setuptools-ans]: https://answers.ros.org/question/396439/
[pep668]: https://peps.python.org/pep-0668/
[noble-t3d]: https://packages.ubuntu.com/noble/python3-transforms3d
[mf-h]: https://github.com/ros2/message_filters/blob/humble/src/message_filters/__init__.py
[colcon592]: https://github.com/colcon/colcon-core/pull/592
[colcon-symlink]: https://github.com/colcon/colcon-core/blob/master/colcon_core/distutils/commands/symlink_data.py
[colcon-ros-py]: https://github.com/colcon/colcon-ros/blob/master/colcon_ros/task/ament_python/build.py
[rcl-args-h]: https://github.com/ros2/rcl/blob/humble/rcl/src/rcl/arguments.c
[node-args-h]: https://docs.ros.org/en/humble/How-To-Guides/Node-arguments.html
[rclpy-node-h]: https://github.com/ros2/rclpy/blob/humble/rclpy/rclpy/node.py
[rclpy-node-l]: https://github.com/ros2/rclpy/blob/lyrical/rclpy/rclpy/node.py
[exec-py-j]: https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/executors.py
[evh-j]: https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/event_handler.py
[rclpy-l]: https://github.com/ros2/rclpy/tree/lyrical/rclpy/rclpy
[fastrtps-ev-h]: https://github.com/ros2/rmw_fastrtps/blob/humble/rmw_fastrtps_shared_cpp/src/custom_publisher_info.cpp
[mw-vendors-h]: https://docs.ros.org/en/humble/Concepts/Intermediate/About-Different-Middleware-Vendors.html
[doctor-rmw-h]: https://github.com/ros2/ros2cli/blob/humble/ros2doctor/ros2doctor/api/rmw.py
[connext-h]: https://docs.ros.org/en/humble/Installation/RMW-Implementations/DDS-Implementations/Working-with-RTI-Connext-DDS.html
[cli-concepts-h]: https://docs.ros.org/en/humble/Concepts/Basic/About-Command-Line-Tools.html
[multi-rmw-h]: https://docs.ros.org/en/humble/How-To-Guides/Working-with-multiple-RMW-implementations.html
[zenoh-h]: https://docs.ros.org/en/humble/Installation/RMW-Implementations/Non-DDS-Implementations/Working-with-Zenoh.html
[nav2-tuning]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/tuning_guide.md
[dds-spec]: https://www.omg.org/spec/DDS/1.4/PDF
[echo-h]: https://github.com/ros2/ros2cli/blob/humble/ros2topic/ros2topic/verb/echo.py
[ament-doc-h]: https://docs.ros.org/en/humble/How-To-Guides/Ament-CMake-Documentation.html
[lc-sm-h]: https://github.com/ros2/rcl/blob/humble/rcl_lifecycle/src/default_state_machine.c
[rclcpp-lc-l]: https://github.com/ros2/rclcpp/tree/lyrical/rclcpp_lifecycle/include/rclcpp_lifecycle
[tpl-dir-h]: https://github.com/ros2/ros2cli/tree/humble/ros2pkg/ros2pkg/resource/ament_python
[tpl-dir-k]: https://github.com/ros2/ros2cli/tree/kilted/ros2pkg/ros2pkg/resource/ament_python
[create-h]: https://github.com/ros2/ros2cli/blob/humble/ros2pkg/ros2pkg/verb/create.py
[include-h]: https://github.com/ros2/launch/blob/humble/launch/launch/actions/include_launch_description.py
[colcon-sel]: https://github.com/colcon/colcon-package-selection/blob/master/colcon_package_selection/package_selection/select_skip.py
[sros2-util-h]: https://github.com/ros2/sros2/blob/humble/sros2/sros2/_utilities.py
[sros2-util-l]: https://github.com/ros2/sros2/blob/lyrical/sros2/sros2/_utilities.py
[sros2-ks-h]: https://github.com/ros2/sros2/blob/humble/sros2/sros2/keystore/_keystore.py
[sros2-encl-h]: https://github.com/ros2/sros2/blob/humble/sros2/sros2/keystore/_enclave.py
[sros2-perm-h]: https://github.com/ros2/sros2/blob/humble/sros2/sros2/keystore/_permission.py
[sros2-gen-h]: https://github.com/ros2/sros2/blob/humble/sros2/sros2/api/_artifact_generation.py
[sros2-verbs-h]: https://github.com/ros2/sros2/blob/humble/sros2/setup.py
[sros2-verbs-k]: https://github.com/ros2/sros2/blob/kilted/sros2/setup.py
[sros2-xsl-h]: https://github.com/ros2/sros2/blob/humble/sros2/sros2/policy/templates/dds/permissions.xsl
[sros2-xsd-h]: https://github.com/ros2/sros2/blob/humble/sros2/sros2/policy/schemas/policy.xsd
[sros2-gov-h]: https://github.com/ros2/sros2/blob/humble/sros2/sros2/policy/defaults/dds/governance.xml
[sros2-types-j]: https://github.com/ros2/sros2/blob/jazzy/sros2/test/policies/common/node/types.xml
[rcl-sec-h]: https://github.com/ros2/rcl/blob/humble/rcl/src/rcl/security.c
[rcl-init-h]: https://github.com/ros2/rcl/blob/humble/rcl/src/rcl/init.c
[rdc-sec-h]: https://github.com/ros2/rmw_dds_common/blob/humble/rmw_dds_common/src/security.cpp
[rdc-sec-j]: https://github.com/ros2/rmw_dds_common/blob/jazzy/rmw_dds_common/src/security.cpp
[rsc-sec-l]: https://github.com/ros2/rmw/blob/lyrical/rmw_security_common/src/security.cpp
[fastrtps-part-h]: https://github.com/ros2/rmw_fastrtps/blob/humble/rmw_fastrtps_shared_cpp/src/participant.cpp
[sec-about-h]: https://docs.ros.org/en/humble/Concepts/Intermediate/About-Security.html
[sec-intro-h]: https://docs.ros.org/en/humble/Tutorials/Advanced/Security/Introducing-ros2-security.html
[sec-intro-l]: https://docs.ros.org/en/lyrical/Developer-Tools/Introspection-and-analysis/Security/Introducing-ros2-security.html
[sec-ks-h]: https://docs.ros.org/en/humble/Tutorials/Advanced/Security/The-Keystore.html
[sec-ac-h]: https://docs.ros.org/en/humble/Tutorials/Advanced/Security/Access-Controls.html
[sec-deploy-h]: https://docs.ros.org/en/humble/Tutorials/Advanced/Security/Deployment-Guidelines.html
[design-sec]: https://design.ros2.org/articles/ros2_dds_security.html
[design-encl]: https://design.ros2.org/articles/ros2_security_enclaves.html
[design-names]: https://design.ros2.org/articles/topic_and_service_names.html
[rep2001]: https://www.ros.org/reps/rep-2001.html
[pubsub-py-h]: https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html
[jazzy-cl]: https://docs.ros.org/en/rolling/Releases/Jazzy-Jalisco-Complete-Changelog.html
[rosdistro-j]: https://github.com/ros/rosdistro/blob/master/jazzy/distribution.yaml
[tb3-demo]: https://github.com/ros-swg/turtlebot3_demo/tree/master/policies
[tb3-teleop-h]: https://github.com/ROBOTIS-GIT/turtlebot3/blob/humble/turtlebot3_teleop/turtlebot3_teleop/script/teleop_keyboard.py
[tb3-teleop-j]: https://github.com/ROBOTIS-GIT/turtlebot3/blob/jazzy/turtlebot3_teleop/turtlebot3_teleop/script/teleop_keyboard.py
[tb3-sim-j]: https://github.com/ROBOTIS-GIT/turtlebot3_simulations/blob/jazzy/turtlebot3_gazebo/launch/turtlebot3_world.launch.py
[tb3-sim-pkg-h]: https://github.com/ROBOTIS-GIT/turtlebot3_simulations/blob/humble/turtlebot3_gazebo/package.xml
[tb3-sim-world-h]: https://github.com/ROBOTIS-GIT/turtlebot3_simulations/blob/humble/turtlebot3_gazebo/launch/turtlebot3_world.launch.py
[pkg-xsd3]: https://github.com/ros-infrastructure/rep/blob/master/xsd/package_format3.xsd
