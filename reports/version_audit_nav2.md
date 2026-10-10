# Version audit — ros2-nav2 (Phase 1)

> Date: 2026-10-09 · Scope: every version-dependent statement in the original "Introduction to ROS 2 Navigation"
> course wiki (not published): Nav2 servers and parameters, behavior trees, lifecycle manager, map server,
> AMCL, costmaps, Cartographer, multi-robot setup, simulator commands and the course code.
> Baseline: **Humble is canonical**. Jazzy and Lyrical differences are annotated, not substituted.
> The "Lyrical" column includes changes that first appeared in **Kilted**, marked "(Kilted)".
> Generic ROS 2 rows are in [version_audit.md](version_audit.md) (IDs `Vnn`); this report cites them instead of repeating them.

## Method
- Primary sources: `ros-navigation/navigation2` source on the `humble`, `jazzy`, `kilted` and `lyrical` branches
  (parameter declarations and defaults in the `.cpp` files, `nav2_bringup/params/nav2_params.yaml`, behavior tree
  XML files, `.srv` definitions), the Nav2 migration guides in `ros-navigation/docs.nav2.org` (named by the OLD
  distro: `Humble.md` = Humble→Iron, `iron/Iron.md` = Iron→Jazzy, `jazzy/Jazzy.md` = Jazzy→Kilted,
  `kilted/Kilted.md` = Kilted→Lyrical), `ros2/rcl` (YAML parameter parser), `ros2/geometry2` (`view_frames`),
  `ros2/cartographer_ros` (`ros2` branch), `ROBOTIS-GIT/turtlebot3` (`humble`), `BehaviorTree/BehaviorTree.CPP`,
  the rosdistro `distribution.yaml` of each distro, and the packages.ros.org apt index for Jammy.
- Defaults are taken from the code, not from the configuration docs: the course copied several defaults from
  older documentation pages, and the code disagrees.
- Actions: **keep** = correct for Humble · **annotate** = correct for Humble, add a version mark · **fix** = wrong
  or outdated for Humble itself. Confidence: High (read in code) · Medium (docs, or inferred) · `[verify]` (Phase 5).
- The original wiki is not edited (and not part of this repo). Fixes and marks live in the notes; each row ID
  becomes a `version_notes` entry in the affected note.

## Distro baseline (Nav2)
| | Humble | Jazzy | Kilted | Lyrical |
|---|---|---|---|---|
| Release – EOL | May 2022 – **May 2027** | May 2024 – May 2029 | May 2025 – Nov 2026 | May 2026 – May 2031 |
| Ubuntu / Python | 22.04 / 3.10 | 24.04 / 3.12 | 24.04 / 3.12 | 26.04 / 3.14 |
| navigation2 release (rosdistro) | 1.1.x | 1.3.x | 1.4.x | 1.5.x |
| BehaviorTree.CPP | 3.8 | 4.5+ | 4.x | 4.x |
| Default controller in `nav2_params.yaml` | DWB | MPPI | MPPI | MPPI |
| Simulator in `nav2_bringup` | Gazebo Classic (`spawn_entity.py`) | Gazebo Harmonic (`ros_gz_sim`) | Gazebo (`ros_gz_sim`) | Gazebo (`ros_gz_sim`) |
| `cmd_vel` type | Twist | Twist (opt-in TwistStamped) | **TwistStamped** | TwistStamped |
| Sources | [nav2 humble][n2-h], [rosdistro][rd] | [nav2 jazzy][n2-j], [Iron→Jazzy][mig-i2j] | [Jazzy→Kilted][mig-j2k] | [nav2 lyrical][n2-l], [Kilted→Lyrical][mig-k2l] |

## Real Humble errors (fix)
| ID | Section | Error in the course | Correct Humble statement |
|---|---|---|---|
| NAV2-V01 | P37.S04, P40.S01, P55, P63 | The node is launched with `name='recoveries_server'`, but its YAML starts with `behavior_server:` (multi-robot: `tb3_0/behavior_server:`) | Parameter files are matched by node name, so this YAML is **never applied** and the node runs with defaults. Single robot it works by accident. Multi-robot it breaks: the defaults `global_frame: odom` / `robot_base_frame: base_link` have no namespace, so behaviors fail their TF lookups. The YAML key must equal the launched name (`recoveries_server:` / `tb3_0/recoveries_server:`), or launch the node as `behavior_server`. |
| NAV2-V02 | P37.S04, P40.S01 | behavior_server params `local_frame: odom`, `global_frame: map`, `transform_timeout: 0.1` | Humble has no `local_frame` and no `transform_timeout`. `global_frame` is the frame the behaviors work in (default `odom`) and the TF tolerance is `transform_tolerance` (default 0.1). Humble YAML: `global_frame: odom`, `transform_tolerance: 0.1`. |
| NAV2-V03 | P37.S04, P40.S01 | "three recovery behaviors: spin, backup, wait"; default list `{"spin","back_up","wait"}` | Humble default `behavior_plugins`: `spin`, `backup`, `drive_on_heading`, `wait`; `assisted_teleop` is also available (enabled in `nav2_params.yaml`). |
| NAV2-V04 | P37.S01 | "Currently (Galactic), only one planner algorithm: NavFn" | Humble planners: NavFn, Smac (2D, Hybrid-A*, Lattice), Theta* (all released as Humble binaries). |
| NAV2-V05 | P37.S02 | "only two local planners: DWB and TEB" | Humble controllers: DWB, Regulated Pure Pursuit, MPPI, Rotation Shim, Graceful (Humble binaries; MPPI and Graceful are backports). TEB is not released for any ROS 2 distro in rosdistro. |
| NAV2-V06 | P38 | `expected_planner_frequency` default 20; "the frequency at which to compute the path" | Code default is **1.0** Hz (`nav2_params.yaml` sets 20.0). It does not set how often paths are computed (the BT decides that, e.g. `RateController hz="1.0"`): it only sets the duration (1/frequency) above which a planning-overrun warning is printed. |
| NAV2-V07 | P39 | defaults `min_x_velocity_threshold` 0.01, `min_y_…` 0.0, `min_theta_…` 0.1; `failure_tolerance` "0.5 m" | All three thresholds default to **0.0001**. `failure_tolerance` is in **seconds**, default **0.0** (−1 = infinite). |
| NAV2-V08 | P29 | `robot_model_type` default `"differential"`; `always_reset_initial_pose` is a double; `save_pose_rate` stores the pose "to the parameter server" for later runs | Default is `nav2_amcl::DifferentialMotionModel` (motion models became plugins in Galactic→Humble; `nav2_amcl::OmniMotionModel` for omni). `always_reset_initial_pose` is a bool (default false). `save_pose_rate` is declared but has **no effect** in Humble: the pose is not saved or reused. |
| NAV2-V09 | P52 | defaults `always_send_full_costmap` true, static `subscribe_to_updates` true, static `transform_tolerance` 0.1 m, inflation `cost_scaling_factor` 1.0, source `clearing` true; params `obstacle_range`, `raytrace_range` | Code defaults: `always_send_full_costmap` **false**, `subscribe_to_updates` **false**, static `transform_tolerance` **0.0** s, `cost_scaling_factor` **10.0**, `clearing` **false** (`marking` true). Range params are `obstacle_max_range`/`obstacle_min_range` and `raytrace_max_range`/`raytrace_min_range`. `obstacle_range`/`raytrace_range` are ROS 1 names. |
| NAV2-V10 | P63 | "disable Groot monitoring with `enable_groot_monitoring: false`, or the ZMQ ports of two bt_navigators collide" | Live Groot monitoring was **removed in Humble** (Galactic→Humble guide), so there is no port to collide; the parameter has no effect. The collision (issue 2386) was a Galactic problem. |
| NAV2-V11 | P63 | multi-robot `odom_topic: tb3_0/odom` in a node already in namespace `tb3_0` | A relative name gets the node namespace prepended, giving `/tb3_0/tb3_0/odom`. Use `odom` (relative) or `/tb3_0/odom`. |
| NAV2-V12 | P18 | Cartographer option `fixed_frame_sampling_ratio` | The Lua key the code reads is `fixed_frame_pose_sampling_ratio`, as in the course's `cartographer.lua`. The name in the table comes from the cartographer_ros docs and is wrong. |
| NAV2-V13 | P54 | "The footprint for Turtlebot3 Waffle is ±0.089 × ±0.069" | Those are Burger-sized values (0.178 × 0.138 m). A Waffle Pi is about 0.28 × 0.31 m. ROBOTIS's own Burger Nav2 params use `robot_radius: 0.1`. Axis order `[verify]`. |
| NAV2-V14 | P43 | action client puts `theta` in `pose.position.z`; `'Result: {0}' + str(result)` | The orientation is never set (it stays `w = 1`, yaw 0) and `z` is ignored by 2D planning. Set the orientation quaternion from yaw. The log line prints a literal `{0}`. |
| NAV2-V15 | P60, P62 | `view_frames` "will generate a `frames.pdf` file" | Humble writes `frames_<YYYY-MM-DD_HH.MM.SS>.pdf` (the log says `frames.pdf`). Use `-o frames` for a fixed name. |
| NAV2-V16 | P22 | lifecycle manager moves nodes "to `initialized`" in list order | It **configures and activates** the nodes in `node_names` order, and deactivates/cleans them up in reverse order. |
| NAV2-V41 | P63 | "Add the `cmd_vel_topic: \"cmd_vel\"` parameter to the controller_server" | Humble's `controller_server` has no `cmd_vel_topic` parameter (the value is ignored). It publishes on the relative topic `cmd_vel`, so the node namespace already makes it `/tb3_0/cmd_vel`. |

## Full table
| # | Section | Statement | Humble | Jazzy | Lyrical | Action | Source | Confidence |
|---|---|---|---|---|---|---|---|---|
| NAV2-V01 | P37.S04, P63 | YAML key `behavior_server` for node `recoveries_server` | ✗ (see fix table) | ✗ same | ✗ same | **fix** | [rcl YAML parser][rcl-parse], [behavior_server (humble)][bs-h] | High |
| NAV2-V02 | P40.S01 | `local_frame`, `global_frame: map`, `transform_timeout` | ✗ `global_frame` (odom) + `transform_tolerance` | `local_frame: odom` + `global_frame: map`; `local_/global_costmap_topic`, `local_/global_footprint_topic` (Iron) | ✓ as Jazzy | **fix** | [behavior_server (humble)][bs-h], [timed_behavior (jazzy)][tb-j], [Humble→Iron][mig-h2i] | High |
| NAV2-V03 | P37.S04 | 3 recoveries | ✗ spin, backup, drive_on_heading, wait (+ assisted_teleop) | ✓ same set | ✓ | **fix** | [behavior_server (humble)][bs-h], [nav2_params (humble)][np-h] | High |
| NAV2-V04 | P37.S01 | only NavFn | ✗ NavFn, Smac, Theta* | ✓ | ✓ | **fix** | [apt index (jammy)][apt-jammy] | High |
| NAV2-V05 | P37.S02 | only DWB + TEB | ✗ DWB, RPP, MPPI, Rotation Shim, Graceful; no TEB | default MPPI | ✓ | **fix** | [apt index (jammy)][apt-jammy], [rosdistro][rd], [nav2_params (jazzy)][np-j] | High |
| NAV2-V06 | P38 | `expected_planner_frequency` default 20 and meaning | ✗ 1.0; only an overrun-warning threshold | ✓ same | ✓ | **fix** | [planner_server (humble)][ps-h] | High |
| NAV2-V07 | P39 | controller thresholds and `failure_tolerance` defaults | ✗ 0.0001; 0.0 s | ✓ same | ✓ | **fix** | [controller_server (humble)][cs-h] | High |
| NAV2-V08 | P29 | AMCL `robot_model_type`, `always_reset_initial_pose`, `save_pose_rate` | ✗ see fix table | ✓ same | ✓ | **fix** | [amcl_node (humble)][amcl-h], [Galactic→Humble][mig-g2h] | High |
| NAV2-V09 | P52 | costmap/layer defaults and range param names | ✗ see fix table | ✓ same | inflation layer refactor (Kilted) | **fix** | [costmap_2d_ros (humble)][c2d-h], [layers (humble)][layers-h] | High |
| NAV2-V10 | P63 | `enable_groot_monitoring: false` against port collisions | ✗ no live monitoring | not in the Jazzy release notes; Groot 2 code present on the jazzy branch `[verify]` | Groot 2 live monitoring, off by default (Kilted) | **fix** | [Galactic→Humble][mig-g2h], [Jazzy→Kilted][mig-j2k] | High |
| NAV2-V11 | P63 | `odom_topic: tb3_0/odom` | ✗ double namespace | ✗ same | ✗ same | **fix** | ROS 2 name resolution ([core-ros-args note](../skills/ros2-core/notes/core-api/core-ros-args.md)) | High |
| NAV2-V12 | P18 | `fixed_frame_sampling_ratio` | ✗ `fixed_frame_pose_sampling_ratio` | ✗ same | ✗ same | **fix** | [cartographer_ros trajectory_options][carto-opts] | High |
| NAV2-V13 | P54 | Waffle footprint | ✗ Burger-sized | – | – | **fix** | [turtlebot3 burger params][tb3-burger] | Medium |
| NAV2-V14 | P43 | goal yaw in `position.z` | ✗ set orientation | ✗ | ✗ | **fix** | code reading | High |
| NAV2-V15 | P60 | `frames.pdf` | ✗ `frames_<date>.pdf` | ✓ same | ✓ | **fix** | [view_frames (humble)][vf-h] | High |
| NAV2-V16 | P22 | "moved to initialized" | ✗ configure + activate | ✓ | ✓ | **fix** | [lifecycle_manager (humble)][lm-h] | High |
| NAV2-V17 | P37–P40, P50–P53 | plugin names `nav2_navfn_planner/NavfnPlanner`, `nav2_behaviors/Spin` | ✓ (Humble mixes `/` and `::`) | all `::` (`nav2_navfn_planner::NavfnPlanner`, `nav2_behaviors::Spin`); DWB stays `dwb_core::DWBLocalPlanner` | ✓ as Jazzy | annotate | [Iron→Jazzy][mig-i2j], V57 | High |
| NAV2-V18 | P39 | `progress_checker_plugin: "progress_checker"` | ✓ string | `progress_checker_plugins: ["progress_checker"]` (Iron) | ✓ as Jazzy | annotate | [Humble→Iron][mig-h2i] | High |
| NAV2-V19 | P37.S03, P40.S02 | `plugin_lib_names` lists the Nav2 BT libraries | ✓ (all 44 exist in Humble; Humble's default list has 49) | Nav2 BT nodes load automatically; list only custom plugins; new `navigators` param | ✓ as Jazzy | annotate | [bt_navigator (humble)][btn-h], [Iron→Jazzy][mig-i2j] | High |
| NAV2-V20 | P37.S03 | behavior tree XML (`root main_tree_to_execute`, `SequenceStar`) | ✓ BT.CPP 3.8 (Humble's default XML uses `RoundRobin` + `BackUp` for recoveries) | BT.CPP 4.5: `<root BTCPP_format="4" …>`, SubTree syntax; `SequenceStar` still accepted (alias of `SequenceWithMemory`) | ✓ + SubTree support improvements (Kilted) | annotate | [default XML (humble)][bt-xml-h], [default XML (jazzy)][bt-xml-j], [BT.CPP factory][btcpp], V56 | High |
| NAV2-V21 | P37.S03, P63 | `default_nav_to_pose_bt_xml` absolute path | ✓ absolute path (no substitutions in param files) | `$(find-pkg-share pkg)/…` allowed in param files | ✓ | annotate | [Iron→Jazzy][mig-i2j] | High |
| NAV2-V22 | P22 | `ManageLifecycleNodes` commands 0–4 | ✓ | + `CONFIGURE = 5`, `CLEANUP = 6` | ✓ | annotate | [srv (humble)][srv-h], [srv (jazzy)][srv-j] | High |
| NAV2-V23 | P62, P63 | `bond_timeout: 0.0` "required to prevent launching errors" | ✓ `bond_timeout` (default 4.0 s; ≤ 0 disables bonds = no crash detection). Likely cause: namespaced nodes vs a manager in the global namespace | + `bond_heartbeat_period` per node (default 0.1 s; ≤ 0 disables) | heartbeat default 0.25 s | annotate | [lifecycle_manager (humble)][lm-h], [Iron→Jazzy][mig-i2j], [Kilted→Lyrical][mig-k2l] | Medium |
| NAV2-V24 | P63 | costmap-level `map_topic: /map` | ✓ exists (StaticLayer reads it) | ✓ | removed (Kilted): set `map_topic` inside `static_layer` | annotate | [static_layer (humble)][static-h], [Jazzy→Kilted][mig-j2k] | High |
| NAV2-V25 | P62, P63 | multi-robot: absolute `/tb3_0/scan`, `/map`; per-robot YAML copies | ✓ needed (relative layer topics resolve inside the costmap namespace) | ✓ | relative topics + one `nav2_params.yaml` for single and multi-robot (Kilted) | annotate | [Jazzy→Kilted][mig-j2k] | Medium |
| NAV2-V26 | P55 | `cmd_vel` from controller_server | ✓ Twist | opt-in `enable_stamped_cmd_vel` | **TwistStamped default** (Kilted) | annotate | V54 | High |
| NAV2-V27 | P05, P55 | navigation nodes and cmd chain | ✓ course launch has no smoother; default bringup: controller → velocity_smoother | collision_monitor in the default chain | ✓ + route/following servers | annotate | V48, V55 | High |
| NAV2-V28 | P50 | `ros2 run gazebo_ros spawn_entity.py -entity … -database …` | ✓ Gazebo Classic (gazebo_ros released) | ✗ gazebo_ros not released (only `gazebo_msgs`): use `ros2 run ros_gz_sim create` | ✗ same | annotate | [rosdistro][rd], [bringup (jazzy)][bringup-j], [Gazebo Classic EOL][gz-classic-eol] | High |
| NAV2-V29 | P15, P16 | Cartographer and SLAM Toolbox | ✓ both released | ✓ both released | ✓ both released (Lyrical) | keep | [rosdistro][rd] | High |
| NAV2-V30 | P20, P27, P37 | `use_sim_time` set per node in YAML/launch | ✓ | ✓; Nav2 launch files can set it for all nodes (Iron) | ✓ | annotate | [Humble→Iron][mig-h2i] | High |
| NAV2-V31 | P05, P37.S04 | "Nav2 Recoveries" | ✓ renamed in Humble: `nav2_behaviors` / `behavior_server`, `behavior_plugins` | ✓ | ✓ | annotate | [Galactic→Humble][mig-g2h] | High |
| NAV2-V32 | P38, P39, P52 | doc links `navigation.ros.org`, `github.com/ros-planning/navigation2` | moved to `docs.nav2.org` and `github.com/ros-navigation/navigation2` | ✓ | ✓ | annotate | [nav2 repo][n2-h] | High |
| NAV2-V33 | P29 | AMCL defaults (particles 500/2000, `update_min_d` 0.25, `update_min_a` 0.2, laser/odom model values, frames) | ✓ match the code | ✓ | ✓ | keep | [amcl_node (humble)][amcl-h] | High |
| NAV2-V34 | P30, P31 | initial pose via `set_initial_pose` + `initial_pose.{x,y,z,yaw}`; `/initialpose` with `frame_id='/map'` | ✓ (AMCL strips a leading `/`; prefer `map`) | ✓ | ✓ | keep | [amcl_node (humble)][amcl-h] | High |
| NAV2-V35 | P22 | `node_names`, `autostart` (default false), service `<manager>/manage_nodes` | ✓ (+ `<manager>/is_active`) | ✓ | ✓ | keep | [lifecycle_manager (humble)][lm-h] | High |
| NAV2-V36 | P19, P20 | `map_saver_cli -f`, thresholds 0.25/0.65; map_server `yaml_filename`, `topic_name`, `frame_id` | ✓ (+ `-t`, `--occ`, `--free`, `--mode`, `--fmt`) | ✓; `map` launch argument overrides `yaml_filename` in Nav2 launch files (Iron) | ✓ | keep | [map_saver_cli (humble)][msc-h], [map_server (humble)][ms-h] | High |
| NAV2-V37 | P17 | `cartographer_node`, `cartographer_occupancy_grid_node` (`-resolution`, `-publish_period_sec`); `/map` is transient local | ✓ | ✓ | ✓ | keep | [cartographer_ros CMake][carto-cmake], [occupancy grid node][carto-og] | High |
| NAV2-V38 | P38, P39 | NavFn params (0.5 / false / true), progress and goal checker values, DWB class `dwb_core::DWBLocalPlanner` | ✓ | ✓ | ✓ | keep | [navfn (humble)][navfn-h], [nav2_params (humble)][np-h] | High |
| NAV2-V39 | P62, P63 | flat YAML keys `tb3_0/amcl:`; `/reinitialize_global_localization`; `goal_pose` topic | ✓ (rcl prepends `/` to the key) | ✓ | ✓ | keep | [rcl YAML parser][rcl-parse], [amcl_node (humble)][amcl-h] | High |
| NAV2-V40 | P22 | lifecycle diagram: unconfigured, inactive, active, finalized; `on_configure` … `on_error` | ✓ (generic, see `core-lifecycle-concepts`) | ✓ | Nav2 lifecycle node moves to `nav2_ros_common` (`nav2::LifecycleNode`) (Kilted) | annotate | [Kilted→Lyrical][mig-k2l] | High |
| NAV2-V41 | P63 | `cmd_vel_topic` parameter | ✗ not a parameter; relative `cmd_vel` | ✗ same | ✗ same | **fix** | [controller_server (humble)][cs-h] | High |

## Open `[verify]` (Phase 5 or a real robot)
- NAV2-V10: whether the Jazzy **release** (not only the jazzy branch) has `enable_groot_monitoring`.
- NAV2-V13: axis order of the Burger footprint (x = forward length 0.138 or 0.178 m).
- NAV2-V23: the exact launch error that `bond_timeout: 0.0` avoids in the course's multi-robot setup.

[n2-h]: https://github.com/ros-navigation/navigation2/tree/humble
[n2-j]: https://github.com/ros-navigation/navigation2/tree/jazzy
[n2-l]: https://github.com/ros-navigation/navigation2/tree/lyrical
[rd]: https://github.com/ros/rosdistro/blob/master/humble/distribution.yaml
[apt-jammy]: http://packages.ros.org/ros2/ubuntu/dists/jammy/main/binary-amd64/Packages.gz
[mig-g2h]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/galactic/Galactic.md
[mig-h2i]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/Humble.md
[mig-i2j]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/iron/Iron.md
[mig-j2k]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/jazzy/Jazzy.md
[mig-k2l]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/kilted/Kilted.md
[bs-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_behaviors/src/behavior_server.cpp
[tb-j]: https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_behaviors/include/nav2_behaviors/timed_behavior.hpp
[np-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_bringup/params/nav2_params.yaml
[np-j]: https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_bringup/params/nav2_params.yaml
[ps-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_planner/src/planner_server.cpp
[cs-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_controller/src/controller_server.cpp
[amcl-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_amcl/src/amcl_node.cpp
[c2d-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_costmap_2d/src/costmap_2d_ros.cpp
[layers-h]: https://github.com/ros-navigation/navigation2/tree/humble/nav2_costmap_2d/plugins
[static-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_costmap_2d/plugins/static_layer.cpp
[btn-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_bt_navigator/src/bt_navigator.cpp
[bt-xml-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_bt_navigator/behavior_trees/navigate_to_pose_w_replanning_and_recovery.xml
[bt-xml-j]: https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_bt_navigator/behavior_trees/navigate_to_pose_w_replanning_and_recovery.xml
[btcpp]: https://github.com/BehaviorTree/BehaviorTree.CPP/blob/master/src/bt_factory.cpp
[lm-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_lifecycle_manager/src/lifecycle_manager.cpp
[srv-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_msgs/srv/ManageLifecycleNodes.srv
[srv-j]: https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_msgs/srv/ManageLifecycleNodes.srv
[msc-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_map_server/src/map_saver/main_cli.cpp
[ms-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_map_server/src/map_server/map_server.cpp
[navfn-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_navfn_planner/src/navfn_planner.cpp
[bringup-j]: https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_bringup/launch/tb3_simulation_launch.py
[rcl-parse]: https://github.com/ros2/rcl/blob/humble/rcl_yaml_param_parser/src/parse.c
[vf-h]: https://github.com/ros2/geometry2/blob/humble/tf2_tools/tf2_tools/view_frames.py
[carto-opts]: https://github.com/ros2/cartographer_ros/blob/ros2/cartographer_ros/src/trajectory_options.cpp
[carto-cmake]: https://github.com/ros2/cartographer_ros/blob/ros2/cartographer_ros/CMakeLists.txt
[carto-og]: https://github.com/ros2/cartographer_ros/blob/ros2/cartographer_ros/src/occupancy_grid_node_main.cpp
[tb3-burger]: https://github.com/ROBOTIS-GIT/turtlebot3/blob/humble/turtlebot3_navigation2/param/humble/burger.yaml
[gz-classic-eol]: https://discourse.openrobotics.org/t/gazebo-classic-end-of-life/48748
