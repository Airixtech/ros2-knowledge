# Version audit — ros2-nav2 (Phase 1)

> Date: 2026-10-09 (intro course, NAV2-V01–V41) · 2026-10-10 (advanced course, NAV2-V42–V68) · 2026-10-21 (NAV2-V69: modern-Gazebo equivalent of the course's spawn command).
> Scope: every version-dependent statement in two course wikis (not published): "Introduction to ROS 2 Navigation"
> (Nav2 servers and parameters, behavior trees, lifecycle manager, map server, AMCL, costmaps, Cartographer,
> multi-robot setup, simulator commands, course code) and "Advanced ROS 2 Navigation" (Simple Commander API,
> waypoint follower, costmap filters, Nav2 behavior tree nodes, custom costmap/planner/controller plugins,
> controller server plugins). Section IDs: `Pnn` = intro course page, `A-Pnn` = advanced course page.
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
- Advanced course, in addition: `nav2_simple_commander`, `nav2_waypoint_follower`, the costmap filters and
  `costmap_filter_info_server`, the `nav2_core` plugin interfaces and `nav2_costmap_2d::Layer` on each branch,
  `ros/pluginlib` and `ros/class_loader` (`humble`), the Nav2 tutorials in `ros-navigation/docs.nav2.org`, and the
  `navigation2` release tags 1.0.x (Galactic) and 1.1.x (Humble) to find which upstream version the course's
  controller plugin code was copied from (token similarity of the whole file).
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
### Intro course
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

### Advanced course
Origin: where the wrong statement comes from. "Foxy"/"Galactic" = a name of that older distro that Humble no longer accepts; "course …" = a mistake of the course itself, wrong in every distro.

| ID | Section | Origin | Error in the course | Correct Humble statement |
|---|---|---|---|---|
| NAV2-V42 | A-P06 | Galactic name | "`isNavComplete()` returns True only after the robot has reached the goal" (the code calls `isTaskComplete()`) | The Humble method is `isTaskComplete()` (`isNavComplete()` is the Galactic name). It returns True when the task ends with **any** result (succeeded, canceled or failed); `getResult()` tells which. |
| NAV2-V43 | A-P10, A-P32 | course advice (any distro) | To stop `ObstacleFootprint/Trajectory Hits Obstacle` near a keepout zone, "remove the critic `ObstacleFootprint`"; the custom costmap config runs DWB without `BaseObstacle` too | In DWB only `BaseObstacle` and `ObstacleFootprint` reject trajectories through lethal cells (the grid critics never mark obstacle cells). Without both, DWB has **no collision check** for any obstacle. Keep one of them: the error means the footprint already touches a lethal cell (robot inside or at the edge of the zone). Jazzy+ `KeepoutFilter` adds `override_lethal_cost` to drive out of a zone. |
| NAV2-V44 | A-P11 | course typo | `filters.yaml` loads `…/maps/map_speeds.yaml`; the mask created is `map_speed.yaml` | The mask server cannot load the file. Use the same name in both places. |
| NAV2-V45 | A-P15 | course claim (any distro) | "You MUST create a behavior for the `bt_navigator`" | Optional: if `default_nav_to_pose_bt_xml` is not set, Humble loads `navigate_to_pose_w_replanning_and_recovery.xml` from `nav2_bt_navigator`. |
| NAV2-V46 | A-P17 | Galactic name + course claim | `Spin` "rotates the number of degrees in `spin_dist`"; `Spin` and `Wait` are served by "the `nav2_recoveries` node" | `spin_dist` is in **radians** (default 1.57 = 90°), `wait_duration` in seconds. Both actions are served by `behavior_server` (`nav2_behaviors`, NAV2-V31). |
| NAV2-V47 | A-P19 | course solution (any distro) | Exercise solution: `<Inverter><IsBatteryLow …/></Inverter>` as first child of the `PipelineSequence` "aborts the current goal" | Inside `RecoveryNode number_of_retries="6"` a low battery fails the pipeline, so the recovery branch runs (clear costmaps, spin, wait 5 s) and the pipeline is retried: the goal aborts only after 6 recovery rounds. An immediate abort needs the battery check outside the RecoveryNode `[verify]`. |
| NAV2-V48 | A-P20 | Galactic names | `recovery.yaml`: `recovery_plugins: ["spin", "backup", "wait"]`, `transform_timeout`; `ros2 action list` shows `/backup`, `/spin`, `/wait` and `/move_robot_as` | Humble reads `behavior_plugins` (default `spin`, `backup`, `drive_on_heading`, `wait`) and `transform_tolerance` (NAV2-V02, V03). `recovery_plugins` is ignored, the defaults load, and the list also shows `/drive_on_heading`. `/move_robot_as` is not a Nav2 action. |
| NAV2-V49 | A-P25, A-P39 | course claim (any distro) | "You CAN NOT change the name of the plugin tag: it has to be `GridBased`" (`planner GridBased is not a valid planner…`) | Any name works. The BT asks for `planner_id="GridBased"` in `ComputePathToPose` and the planner server looks that id up in `planner_plugins`: rename both, or leave `planner_id` empty when only one planner is loaded. |
| NAV2-V50 | A-P29 | course claim (any distro) | Cost "0–255: 0 no danger, 255 very high risk"; required layer methods `updateBounds`, `updateCosts`, `reset` | 0 `FREE_SPACE`, 1–252 rising cost, 253 `INSCRIBED_INFLATED_OBSTACLE`, 254 `LETHAL_OBSTACLE`, 255 `NO_INFORMATION` (unknown). Pure virtual (required): `reset()`, `isClearable()`, `updateBounds()`, `updateCosts()`. |
| NAV2-V51 | A-P32, A-P33, A-P39, A-P40, A-P40.S01, A-P46 | Foxy name | Launch files pass the tree with `parameters=[bt_navigator_yaml, {'default_bt_xml_filename': default_bt_xml_path}]` | `default_bt_xml_filename` is the Foxy name. Humble does not declare it, so the override is ignored and the tree comes from `default_nav_to_pose_bt_xml` in `bt_navigator.yaml`. Use `{'default_nav_to_pose_bt_xml': default_bt_xml_path}`. |
| NAV2-V52 | A-P33, A-P40, A-P40.S01 | Galactic package | Exercise launch files start `Node(package='nav2_recoveries', executable='recoveries_server', …)` | `nav2_recoveries` does not exist in Humble: the launch fails. Use `package='nav2_behaviors', executable='behavior_server'` (NAV2-V31). |
| NAV2-V53 | A-P46 | Galactic code + course claim | Custom controller config sets `max_allowed_time_to_collision_up_to_carrot`, `max_linear_accel`, `max_linear_decel`; "`lookahead_dist` regulates up to what distance you check for collisions, limited by `min_`/`max_lookahead_dist`" | The course plugin (Galactic code, NAV2-V64) reads `max_allowed_time_to_collision`, so the `_up_to_carrot` key is ignored. No Galactic, Humble or Jazzy RPP declares `max_linear_accel`/`max_linear_decel`, so they are ignored too. `lookahead_dist` is the distance to the lookahead point on the path. `min_`/`max_lookahead_dist` bound it only with `use_velocity_scaled_lookahead_dist: true`. Collisions are checked over the time `max_allowed_time_to_collision(_up_to_carrot)`. |
| NAV2-V54 | A-P51 | Galactic-era list + typos | "Only one progress checker"; "currently (ROS2 Galactic) two goal checkers"; `plugin: "nav2_controller::StopedGoalChecker"`; `trajectory_generator_name: “dwb_plugins::StandardTrajectoryGenerator”` | Humble 1.1.20: progress checkers `SimpleProgressChecker`, `PoseProgressChecker`; goal checkers `SimpleGoalChecker`, `StoppedGoalChecker`, `PositionGoalChecker`. The misspelled `StopedGoalChecker` fails to load. Typographic quotes stay inside the YAML string, so the generator name does not match any plugin: use ASCII quotes. |
| NAV2-V55 | A-P38, A-P40, A-P45 | ROS 1 leftover | `target_compile_definitions(… "PLUGINLIB__DISABLE_BOOST_FUNCTIONS")` "is needed to disable BOOST functions" | Humble's `pluginlib` and `class_loader` never read this define: the line is a harmless leftover. |

## Full table
| # | Section | Statement | Humble | Jazzy | Lyrical | Action | Source | Confidence |
|---|---|---|---|---|---|---|---|---|
| NAV2-V01 | P37.S04, P63, A-P20 | YAML key `behavior_server` for node `recoveries_server` | ✗ (see fix table) | ✗ same | ✗ same | **fix** | [rcl YAML parser][rcl-parse], [behavior_server (humble)][bs-h] | High |
| NAV2-V02 | P40.S01 | `local_frame`, `global_frame: map`, `transform_timeout` | ✗ `global_frame` (odom) + `transform_tolerance` | `local_frame: odom` + `global_frame: map`; `local_/global_costmap_topic`, `local_/global_footprint_topic` (Iron) | ✓ as Jazzy | **fix** | [behavior_server (humble)][bs-h], [timed_behavior (jazzy)][tb-j], [Humble→Iron][mig-h2i] | High |
| NAV2-V03 | P37.S04, A-P20 | 3 recoveries | ✗ spin, backup, drive_on_heading, wait (+ assisted_teleop) | ✓ same set | ✓ | **fix** | [behavior_server (humble)][bs-h], [nav2_params (humble)][np-h] | High |
| NAV2-V04 | P37.S01 | only NavFn | ✗ NavFn, Smac, Theta* | ✓ | ✓ | **fix** | [apt index (jammy)][apt-jammy] | High |
| NAV2-V05 | P37.S02, A-P51 | only DWB + TEB (advanced: "two controllers, DWB and RPP; TEB still unavailable") | ✗ DWB, RPP, MPPI, Rotation Shim, Graceful; no TEB | default MPPI | ✓ | **fix** | [apt index (jammy)][apt-jammy], [rosdistro][rd], [nav2_params (jazzy)][np-j] | High |
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
| NAV2-V17 | P37–P40, P50–P53, A-P20, A-P25, A-P39 | plugin names `nav2_navfn_planner/NavfnPlanner`, `nav2_behaviors/Spin` | ✓ (Humble mixes `/` and `::`) | all `::` (`nav2_navfn_planner::NavfnPlanner`, `nav2_behaviors::Spin`); DWB stays `dwb_core::DWBLocalPlanner` | ✓ as Jazzy | annotate | [Iron→Jazzy][mig-i2j], V57 | High |
| NAV2-V18 | P39, A-P50 | `progress_checker_plugin: "progress_checker"` | ✓ string | `progress_checker_plugins: ["progress_checker"]` (Iron) | ✓ as Jazzy | annotate | [Humble→Iron][mig-h2i] | High |
| NAV2-V19 | P37.S03, P40.S02, A-P18 | `plugin_lib_names` lists the Nav2 BT libraries | ✓ (all 44 exist in Humble; Humble's default list has 49; the advanced course's 28 exist too) | Nav2 BT nodes load automatically; list only custom plugins; new `navigators` param | ✓ as Jazzy | annotate | [bt_navigator (humble)][btn-h], [Iron→Jazzy][mig-i2j] | High |
| NAV2-V20 | P37.S03, A-P16, A-P17, A-P19 | behavior tree XML (`root main_tree_to_execute`, `SequenceStar`) | ✓ BT.CPP 3.8 (Humble's default XML uses `RoundRobin` + `BackUp` for recoveries) | BT.CPP 4.5: `<root BTCPP_format="4" …>`, SubTree syntax; `SequenceStar` still accepted (alias of `SequenceWithMemory`) | ✓ + SubTree support improvements (Kilted) | annotate | [default XML (humble)][bt-xml-h], [default XML (jazzy)][bt-xml-j], [BT.CPP factory][btcpp], V56 | High |
| NAV2-V21 | P37.S03, P63, A-P18 | `default_nav_to_pose_bt_xml` absolute path | ✓ absolute path (no substitutions in param files) | `$(find-pkg-share pkg)/…` allowed in param files | ✓ | annotate | [Iron→Jazzy][mig-i2j] | High |
| NAV2-V22 | P22 | `ManageLifecycleNodes` commands 0–4 | ✓ | + `CONFIGURE = 5`, `CLEANUP = 6` | ✓ | annotate | [srv (humble)][srv-h], [srv (jazzy)][srv-j] | High |
| NAV2-V23 | P62, P63 | `bond_timeout: 0.0` "required to prevent launching errors" | ✓ `bond_timeout` (default 4.0 s; ≤ 0 disables bonds = no crash detection). Likely cause: namespaced nodes vs a manager in the global namespace | + `bond_heartbeat_period` per node (default 0.1 s; ≤ 0 disables) | heartbeat default 0.25 s | annotate | [lifecycle_manager (humble)][lm-h], [Iron→Jazzy][mig-i2j], [Kilted→Lyrical][mig-k2l] | Medium |
| NAV2-V24 | P63 | costmap-level `map_topic: /map` | ✓ exists (StaticLayer reads it) | ✓ | removed (Kilted): set `map_topic` inside `static_layer` | annotate | [static_layer (humble)][static-h], [Jazzy→Kilted][mig-j2k] | High |
| NAV2-V25 | P62, P63 | multi-robot: absolute `/tb3_0/scan`, `/map`; per-robot YAML copies | ✓ needed (relative layer topics resolve inside the costmap namespace) | ✓ | relative topics + one `nav2_params.yaml` for single and multi-robot (Kilted) | annotate | [Jazzy→Kilted][mig-j2k] | Medium |
| NAV2-V26 | P55 | `cmd_vel` from controller_server | ✓ Twist | opt-in `enable_stamped_cmd_vel` | **TwistStamped default** (Kilted) | annotate | V54 | High |
| NAV2-V27 | P05, P55 | navigation nodes and cmd chain | ✓ course launch has no smoother; default bringup: controller → velocity_smoother | collision_monitor in the default chain | ✓ + route/following servers | annotate | V48, V55 | High |
| NAV2-V28 | P50, A-P52 | `ros2 run gazebo_ros spawn_entity.py -entity … -database …` | ✓ Gazebo Classic (gazebo_ros released) | ✗ gazebo_ros not released (only `gazebo_msgs`): use `ros2 run ros_gz_sim create` | ✗ same | annotate | [rosdistro][rd], [bringup (jazzy)][bringup-j], [Gazebo Classic EOL][gz-classic-eol] | High |
| NAV2-V29 | P15, P16 | Cartographer and SLAM Toolbox | ✓ both released | ✓ both released | ✓ both released (Lyrical) | keep | [rosdistro][rd] | High |
| NAV2-V30 | P20, P27, P37 | `use_sim_time` set per node in YAML/launch | ✓ | ✓; Nav2 launch files can set it for all nodes (Iron) | ✓ | annotate | [Humble→Iron][mig-h2i] | High |
| NAV2-V31 | P05, P37.S04, A-P15, A-P17, A-P20 | "Nav2 Recoveries" | ✓ renamed in Humble: `nav2_behaviors` / `behavior_server`, `behavior_plugins` | ✓ | ✓ | annotate | [Galactic→Humble][mig-g2h] | High |
| NAV2-V32 | P38, P39, P52, A-P06, A-P08, A-P10, A-P17, A-P24–A-P29, A-P41, A-P51 | doc links `navigation.ros.org`, `github.com/ros-planning/navigation2`, old `docs.nav2.org/configuration/packages/…` pages | moved to `docs.nav2.org` and `github.com/ros-navigation/navigation2` | ✓ | ✓ | annotate | [nav2 repo][n2-h] | High |
| NAV2-V33 | P29 | AMCL defaults (particles 500/2000, `update_min_d` 0.25, `update_min_a` 0.2, laser/odom model values, frames) | ✓ match the code | ✓ | ✓ | keep | [amcl_node (humble)][amcl-h] | High |
| NAV2-V34 | P30, P31 | initial pose via `set_initial_pose` + `initial_pose.{x,y,z,yaw}`; `/initialpose` with `frame_id='/map'` | ✓ (AMCL strips a leading `/`; prefer `map`) | ✓ | ✓ | keep | [amcl_node (humble)][amcl-h] | High |
| NAV2-V35 | P22 | `node_names`, `autostart` (default false), service `<manager>/manage_nodes` | ✓ (+ `<manager>/is_active`) | ✓ | ✓ | keep | [lifecycle_manager (humble)][lm-h] | High |
| NAV2-V36 | P19, P20 | `map_saver_cli -f`, thresholds 0.25/0.65; map_server `yaml_filename`, `topic_name`, `frame_id` | ✓ (+ `-t`, `--occ`, `--free`, `--mode`, `--fmt`) | ✓; `map` launch argument overrides `yaml_filename` in Nav2 launch files (Iron) | ✓ | keep | [map_saver_cli (humble)][msc-h], [map_server (humble)][ms-h] | High |
| NAV2-V37 | P17 | `cartographer_node`, `cartographer_occupancy_grid_node` (`-resolution`, `-publish_period_sec`); `/map` is transient local | ✓ | ✓ | ✓ | keep | [cartographer_ros CMake][carto-cmake], [occupancy grid node][carto-og] | High |
| NAV2-V38 | P38, P39 | NavFn params (0.5 / false / true), progress and goal checker values, DWB class `dwb_core::DWBLocalPlanner` | ✓ | ✓ | ✓ | keep | [navfn (humble)][navfn-h], [nav2_params (humble)][np-h] | High |
| NAV2-V39 | P62, P63 | flat YAML keys `tb3_0/amcl:`; `/reinitialize_global_localization`; `goal_pose` topic | ✓ (rcl prepends `/` to the key) | ✓ | ✓ | keep | [rcl YAML parser][rcl-parse], [amcl_node (humble)][amcl-h] | High |
| NAV2-V40 | P22 | lifecycle diagram: unconfigured, inactive, active, finalized; `on_configure` … `on_error` | ✓ (generic, see `core-lifecycle-concepts`) | ✓ | Nav2 lifecycle node moves to `nav2_ros_common` (`nav2::LifecycleNode`) in Lyrical (not on the kilted branch; corrected 2026-10-10) | annotate | [Kilted→Lyrical][mig-k2l] | High |
| NAV2-V41 | P63 | `cmd_vel_topic` parameter | ✗ not a parameter; relative `cmd_vel` | ✗ same | ✗ same | **fix** | [controller_server (humble)][cs-h] | High |
| NAV2-V42 | A-P06 | `isNavComplete()` | ✗ `isTaskComplete()`, True on any end state | ✓ same | `isTaskComplete(task=RunningTask.NONE)` (Kilted) | **fix** | [robot_navigator (humble)][sc-h], [Simple Commander README (humble)][sc-readme-h], [robot_navigator (lyrical)][sc-l] | High |
| NAV2-V43 | A-P10, A-P32 | remove `ObstacleFootprint` (and `BaseObstacle`) from DWB `critics` | ✗ no collision check left | ✗ same; `KeepoutFilter` `override_lethal_cost`, `lethal_override_cost` | ✗ same | **fix** | [dwb_critics (humble)][dwbc-h], [BaseObstacle docs][doc-baseobs], [ObstacleFootprint docs][doc-obsfp], [keepout tutorial][tut-keepout] | High |
| NAV2-V44 | A-P11 | mask file `map_speeds.yaml` vs `map_speed.yaml` | ✗ file not found | ✗ | ✗ | **fix** | course text | High |
| NAV2-V45 | A-P15 | a custom BT XML is mandatory | ✗ default tree loaded | ✓ same | ✓ same | **fix** | [navigate_to_pose (humble)][nav2pose-h], [bt_navigator docs][doc-btn] | High |
| NAV2-V46 | A-P17 | `spin_dist` in degrees; served by `nav2_recoveries` | ✗ radians; `behavior_server` | ✓ same | ✓ same | **fix** | [spin_action (humble)][spin-bt-h], [Spin docs][doc-spin], [Simple Commander README (humble)][sc-readme-h], [Galactic→Humble][mig-g2h] | High |
| NAV2-V47 | A-P19 | low-battery check inside the `RecoveryNode` aborts the goal | ✗ 6 recovery rounds first | ✗ same | ✗ same | **fix** | [recovery_node (humble)][recnode-h], [RecoveryNode docs][doc-recnode] | High (alternative tree `[verify]`) |
| NAV2-V48 | A-P20 | `recovery_plugins`, `transform_timeout`; action list without `/drive_on_heading` | ✗ `behavior_plugins` (4 defaults), `transform_tolerance` | `local_frame` + `global_frame` (NAV2-V02) | ✓ as Jazzy | **fix** | [behavior_server (humble)][bs-h], [behavior server docs][doc-bs], [Galactic→Humble][mig-g2h] | High |
| NAV2-V49 | A-P25, A-P39 | the planner plugin name must be `GridBased` | ✗ any name; the BT `planner_id` must match | ✓ same | ✓ same | **fix** | [planner_server (humble)][ps-h], [planner server docs][doc-ps] | High |
| NAV2-V50 | A-P29 | cost 255 = highest risk; required layer methods | ✗ 254 lethal, 255 unknown; `isClearable()` also required | ✓ same | ✓ same API; `node_` is a `nav2::LifecycleNode` | **fix** | [cost_values (humble)][costval-h], [layer.hpp (humble)][layer-h], [costmap setup docs][doc-cm-setup], [costmap_2d docs][doc-c2d], [costmap plugin tutorial][tut-costmap] | High |
| NAV2-V51 | A-P32, A-P33, A-P39, A-P40, A-P40.S01, A-P46 | launch override `default_bt_xml_filename` | ✗ Foxy name, ignored | ✗ same | ✗ same | **fix** | [bt_navigator (foxy)][btn-foxy], [navigate_to_pose (humble)][nav2pose-h], [bt_navigator docs][doc-btn] | High |
| NAV2-V52 | A-P33, A-P40, A-P40.S01 | `package='nav2_recoveries', executable='recoveries_server'` | ✗ package absent, launch fails | ✗ | ✗ | **fix** | [rosdistro][rd], [apt index (jammy)][apt-jammy], [Galactic→Humble][mig-g2h] | High |
| NAV2-V53 | A-P46 | custom controller config keys; `lookahead_dist` "checks collisions" | ✗ see fix table | ✗ same | `max_linear_accel`/`max_linear_decel` exist again (dynamic window) | **fix** | [RPP (galactic 1.0.12)][rpp-g], [RPP (humble)][rpp-h], [RPP README (humble)][rpp-readme-h], [RPP docs][rpp-doc] | High |
| NAV2-V54 | A-P51 | checker lists, `StopedGoalChecker`, typographic quotes | ✗ see fix table | ✓ same plugins | + `AdaptiveToleranceGoalChecker`, `AxisGoalChecker` | **fix** | [nav2_controller plugins (humble)][ctrl-plugins-h], [controller server plugin docs][doc-ctrl-plugins], [nav2_controller plugins (lyrical)][ctrl-plugins-l] | High |
| NAV2-V55 | A-P38, A-P40, A-P45 | `PLUGINLIB__DISABLE_BOOST_FUNCTIONS` is needed | ✗ never read (harmless) | ✗ | ✗ | **fix** | [pluginlib (humble)][pluginlib-h] (code search, no doc) | High |
| NAV2-V56 | A-P31, A-P33, A-P38, A-P45 | `package.xml` `<costmap_2d plugin=…/>` / `<nav2_core plugin=…/>` tells where the plugin is | ✓ harmless: pluginlib finds the XML through the ament index entry that `pluginlib_export_plugin_description_file()` creates (the Nav2 tutorials still show the export line) | ✓ | ✓ | annotate | [pluginlib (humble)][pluginlib-h], [costmap plugin tutorial][tut-costmap] | High |
| NAV2-V57 | A-P05, A-P06, A-P08 | Simple Commander: `BasicNavigator`, `TaskResult`, `setInitialPose`, `waitUntilNav2Active`, `goToPose`, `goThroughPoses`, `followWaypoints`, `getFeedback`, `getResult` | ✓ | + `driveOnHeading`, `followGpsWaypoints`, docking, `clearCostmapAroundRobot` | typed signatures, `getTaskError()` (Kilted); `followWaypoints(poses, number_of_loops, goal_index)`, `followObjectByTopic`/`ByFrame`, `toggleCollisionMonitor` | annotate | [robot_navigator (humble)][sc-h], [robot_navigator (jazzy)][sc-j], [robot_navigator (lyrical)][sc-l] | High |
| NAV2-V58 | A-P06 | `NavigateToPose.action` (result `std_msgs/Empty`) | ✓ | result `error_code`, `error_msg` | error codes 9000–9003 (Kilted); `GOAL_REJECTED`, `SEND_GOAL_FAILURE`; feedback `position_tracking_error`, `heading_tracking_error` | annotate | [NavigateToPose (humble)][ntp-h], [NavigateToPose (jazzy)][ntp-j], [NavigateToPose (lyrical)][ntp-l] | High |
| NAV2-V59 | A-P08 | `FollowWaypoints.action` (result `int32[] missed_waypoints`) | ✓ | goal `number_of_loops`, `goal_index`; result `MissedWaypoint[]`, `error_code` 600/601, `error_msg` | result `WaypointStatus[]`, codes 602/603 | annotate | [FollowWaypoints (humble)][fw-h], [FollowWaypoints (jazzy)][fw-j], [FollowWaypoints (lyrical)][fw-l] | High |
| NAV2-V60 | A-P08 | waypoint_follower `loop_rate`, `stop_on_failure`, `waypoint_task_executor_plugin`, `waypoint_pause_duration` (ms); Wait/Photo/InputAtWaypoint; "not started by default" | ✓ (defaults: `stop_on_failure` true, pause 0 ms). "Not started" refers to the course launch file: `nav2_bringup`'s `navigation_launch.py` starts it | + `action_server_result_timeout`, `global_frame_id` | ✓ | keep | [waypoint_follower (humble)][wf-h], [navigation_launch (humble)][bringup-nav-h] | High |
| NAV2-V61 | A-P09–A-P11 | costmap filters: `KeepoutFilter`, `SpeedFilter`, `filters` list, info server `type` 0/1/2, `base`, `multiplier`, `mask_topic`; speed formula; `mode: scale`; controller `speed_limit_topic` | ✓; 1.1.20 also has `BinaryFilter` (type 3) and the `toggle_filter` service (backported from Iron) | + `override_lethal_cost`, `lethal_override_cost` (KeepoutFilter) | keepout and speed zones in the default bringup, vector object server (Kilted); zone parameter filter (type 4) | annotate | [filter_values (humble)][fv-h], [info server (humble)][cfis-h], [Humble→Iron][mig-h2i], [Jazzy→Kilted][mig-j2k], [Kilted→Lyrical][mig-k2l] | High |
| NAV2-V62 | A-P16, A-P17, A-P19 | BT nodes `RecoveryNode`, `PipelineSequence`, `RateController`, `ComputePathToPose`, `FollowPath`, `ClearEntireCostmap`, `Spin`, `Wait`, `SequenceStar`; `IsBatteryLow` ports `battery_topic`, `min_battery`, `is_voltage` | ✓ (`battery_topic` default `/battery_status`; `percentage` is 0–1) | ✓ same ports | ✓ | keep | [recovery_node (humble)][recnode-h], [IsBatteryLow (humble)][ibl-h] | High |
| NAV2-V63 | A-P25, A-P29, A-P34, A-P36, A-P41, A-P43 | plugin base classes `nav2_costmap_2d::Layer`, `nav2_core::GlobalPlanner`, `nav2_core::Controller` | ✓ (Controller: `setSpeedLimit()` is pure virtual too) | `createPlan(…, cancel_checker)`; Controller + `cancel()`, `reset()` | `nav2::LifecycleNode`, `nav2::TransformBuffer`; `createPlan(start, goal, viapoints, cancel_checker)`; Controller `newPathReceived()` replaces `setPlan()`, `computeVelocityCommands(…, transformed_global_plan, global_goal)` | annotate | [global_planner.hpp (humble)][gp-h], [(jazzy)][gp-j], [(lyrical)][gp-l], [controller.hpp (humble)][ctl-h], [(jazzy)][ctl-j], [(lyrical)][ctl-l] | High |
| NAV2-V64 | A-P40.S01, A-P41, A-P43 | controller plugin "based on the original code" at commit `b92561bd` | The code is Galactic's RPP 1.0.9–1.0.12 (98 % token match; the linked Jan 2021 commit matches 70 %) with the namespace renamed. A-P43 passes `configure()` arguments by value as Humble requires; A-P40.S01 keeps Galactic's `const &` arguments, which do not override Humble's pure virtual | – | – | annotate | [RPP (galactic 1.0.12)][rpp-g], [controller.hpp (galactic 1.0.12)][ctl-g], [controller.hpp (humble)][ctl-h] | High (builds on Humble: `[verify]`) |
| NAV2-V65 | A-P51 | Nav2 RPP parameters (`desired_linear_vel` … `max_robot_pose_search_dist`, `use_interpolation`) | ✓ Humble names | + `use_fixed_curvature_lookahead`, `curvature_lookahead_dist`, `stateful`, `cancel_deceleration`, `use_cancel_deceleration`, `interpolate_curvature_after_goal`; − `use_interpolation` | + dynamic window (`use_dynamic_window`, velocity and acceleration limits), `min_distance_to_obstacle`, `allow_obstacle_checking_beyond_goal`; − `transform_tolerance`, `max_robot_pose_search_dist`, `stateful` (path handling moves to the controller server) | annotate | [RPP (humble)][rpp-h], [RPP (jazzy)][rpp-j], [RPP (lyrical)][rpp-l] | High |
| NAV2-V66 | A-P51 | DWB generators `StandardTrajectoryGenerator`, `LimitedAccelGenerator`; 10 critics | ✓ | ✓ | ✓ | keep | [dwb_plugins (humble)][dwbp-h], [dwb_critics (humble)][dwbc-h] | High |
| NAV2-V67 | A-P50, A-P51 | `controller_server`: `progress_checker_plugin`, `goal_checker_plugins`, `controller_plugins` | ✓ | `progress_checker_plugins` list (NAV2-V18) | + path handler plugin (`nav2_controller::FeasiblePathHandler`) and the goal checkers of NAV2-V54 | annotate | [Kilted→Lyrical][mig-k2l] | High |
| NAV2-V68 | A-P31, A-P33, A-P38, A-P40, A-P45 | plugin `CMakeLists.txt` uses `ament_target_dependencies()` | ✓ | ✓ | deprecated (Kilted), removed (Lyrical): `target_link_libraries(<lib> PUBLIC <pkg>::<pkg>)` | annotate | V09 | High |
| NAV2-V69 | P50, A-P52 (2026-10-21) | modern-Gazebo equivalent of `spawn_entity.py -entity … -database …` | `ros2 run ros_gz_sim create -name … -file <model.sdf or Fuel URL> -x … -y …` (ros_gz `humble`, Fortress), only in a world started with `ros_gz_sim`; the cone is `https://fuel.gazebosim.org/1.0/OpenRobotics/models/Construction Cone` (CC0); Fuel has no model named gas_bottle (search of 2026-10-21) | same flags (Harmonic) | same flags (Jetty) | annotate (pointer in nav2-global-costmap, nav2-dwb-critic-tuning) | [create.cpp][create-h], [README][rosgz-sim-readme], [Fuel model][fuel-cone], [example world][gz-cone-world] | High |

## Humble alternatives to features of later distros (advanced course)
Each alternative was checked in the Humble code or a Humble README before it was listed. "None" means no Humble equivalent was found.

| Later-distro feature | Rows | Humble alternative | Checked in |
|---|---|---|---|
| `KeepoutFilter` `override_lethal_cost` (Jazzy): drive out of a zone | NAV2-V43 | Mask values 1–99 make a "weighted area": non-lethal cost (mask 0–100 maps linearly to cost 0–254), so the robot may cross it but planners avoid it. Or apply the filter only to the global costmap (plans avoid the zone; the controller may still enter it). | [keepout tutorial][tut-keepout], [Costmap2D from OccupancyGrid (humble)][c2d-cpp-h] |
| Collision monitor in the default bringup (Jazzy, NAV2-V27) | NAV2-V43 | `nav2_collision_monitor` is released for Humble; add it to your launch as an extra safety layer after the controller. | [collision monitor README (humble)][cm-readme-h], [collision monitor docs][doc-cm] |
| RPP dynamic window with `max_linear_accel`/`max_linear_decel` (Lyrical) | NAV2-V53 | `nav2_velocity_smoother` (`max_accel`, `max_decel`, `max_velocity`) between the controller and the robot. | [velocity smoother README (humble)][vs-readme-h], [velocity smoother docs][doc-vs] |
| Jazzy RPP parameters (`use_fixed_curvature_lookahead`, `cancel_deceleration`, `stateful`) | NAV2-V65 | None; Humble's parameter list is in the RPP README. | [RPP README (humble)][rpp-readme-h] |
| Simple Commander `driveOnHeading()`, `clearCostmapAroundRobot()`, `getTaskError()`, docking methods (Jazzy+) | NAV2-V57 | `clearLocalCostmap()`, `clearGlobalCostmap()`, `clearAllCostmaps()`; outcome from `getResult()` (`TaskResult`). The `DriveOnHeading` behavior and action exist in Humble (call them with an action client). Docking: `opennav_docking`, a separate repository released for Humble. | [Simple Commander README (humble)][sc-readme-h], [DriveOnHeading.action (humble)][doh-h], [opennav_docking (humble)][dock-h] |
| `NavigateToPose`/`FollowWaypoints` error codes (Jazzy) | NAV2-V58, V59 | No error codes: use the goal status (`TaskResult`) and the server log; `FollowWaypoints` returns the indices of `missed_waypoints`. | [NavigateToPose (humble)][ntp-h], [FollowWaypoints (humble)][fw-h] |
| `FollowWaypoints` `number_of_loops`, `goal_index` (Jazzy) | NAV2-V59 | None: call `followWaypoints()` again with the poses you still need. | [Simple Commander README (humble)][sc-readme-h] |
| `progress_checker_plugins` list (Iron) | NAV2-V67 | One `progress_checker_plugin`: `SimpleProgressChecker` or `PoseProgressChecker` (both in Humble). | [nav2_controller plugins (humble)][ctrl-plugins-h] |
| Controller server path handler `FeasiblePathHandler` (Lyrical) | NAV2-V65, V67 | The controller plugin prunes and transforms the path itself (RPP: `max_robot_pose_search_dist`, `transform_tolerance`). | [RPP README (humble)][rpp-readme-h] |
| Zone parameter filter (Lyrical) | NAV2-V61 | `BinaryFilter` publishes a `std_msgs/Bool` on `binary_state_topic` when the robot enters or leaves marked areas; a node of yours can change parameters on that signal. | [binary_filter (humble)][bf-h], [binary filter docs][doc-bf] |
| Keepout and speed zones in the default bringup (Kilted) | NAV2-V61 | Configure them yourself; the official demo package `nav2_costmap_filters_demo` has a `humble` branch. | [navigation2_tutorials (humble)][tut-h] |
| Plugin interfaces of Jazzy/Lyrical (`cancel_checker`, `newPathReceived`, `nav2::LifecycleNode`) | NAV2-V63 | The Humble versions of the official tutorial plugins: `nav2_gradient_costmap_plugin`, `nav2_straightline_planner` (`createPlan(start, goal)`), `nav2_pure_pursuit_controller` (with `setSpeedLimit()`). | [navigation2_tutorials (humble)][tut-h] |

## Open `[verify]` (Phase 5 or a real robot)
- NAV2-V10: whether the Jazzy **release** (not only the jazzy branch) has `enable_groot_monitoring`.
- NAV2-V13: axis order of the Burger footprint (x = forward length 0.138 or 0.178 m).
- NAV2-V23: the exact launch error that `bond_timeout: 0.0` avoids in the course's multi-robot setup.
- NAV2-V47: a tree that aborts at once on low battery (battery check outside the `RecoveryNode`).
- NAV2-V64: the course's costmap, planner and controller plugins build and load on Humble (`colcon build` + launch).
- A-P52: the course's result that DWB stops in front of an unmapped cone with `PathAlign` and goes around it without it.

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
[sc-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_simple_commander/nav2_simple_commander/robot_navigator.py
[sc-j]: https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_simple_commander/nav2_simple_commander/robot_navigator.py
[sc-l]: https://github.com/ros-navigation/navigation2/blob/lyrical/nav2_simple_commander/nav2_simple_commander/robot_navigator.py
[ntp-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_msgs/action/NavigateToPose.action
[ntp-j]: https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_msgs/action/NavigateToPose.action
[ntp-l]: https://github.com/ros-navigation/navigation2/blob/lyrical/nav2_msgs/action/NavigateToPose.action
[fw-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_msgs/action/FollowWaypoints.action
[fw-j]: https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_msgs/action/FollowWaypoints.action
[fw-l]: https://github.com/ros-navigation/navigation2/blob/lyrical/nav2_msgs/action/FollowWaypoints.action
[wf-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_waypoint_follower/src/waypoint_follower.cpp
[bringup-nav-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_bringup/launch/navigation_launch.py
[fv-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_costmap_2d/include/nav2_costmap_2d/costmap_filters/filter_values.hpp
[cfis-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_map_server/src/costmap_filter_info/costmap_filter_info_server.cpp
[tut-keepout]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/tutorials/general_tutorials/navigation2_with_keepout_filter/navigation2_with_keepout_filter.md
[dwbc-h]: https://github.com/ros-navigation/navigation2/tree/humble/nav2_dwb_controller/dwb_critics/src
[dwbp-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_dwb_controller/dwb_plugins/plugins.xml
[nav2pose-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_bt_navigator/src/navigators/navigate_to_pose.cpp
[btn-foxy]: https://github.com/ros-navigation/navigation2/blob/foxy-devel/nav2_bt_navigator/src/bt_navigator.cpp
[spin-bt-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_behavior_tree/include/nav2_behavior_tree/plugins/action/spin_action.hpp
[recnode-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_behavior_tree/plugins/control/recovery_node.cpp
[ibl-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_behavior_tree/plugins/condition/is_battery_low_condition.cpp
[costval-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_costmap_2d/include/nav2_costmap_2d/cost_values.hpp
[layer-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_costmap_2d/include/nav2_costmap_2d/layer.hpp
[gp-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_core/include/nav2_core/global_planner.hpp
[gp-j]: https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_core/include/nav2_core/global_planner.hpp
[gp-l]: https://github.com/ros-navigation/navigation2/blob/lyrical/nav2_core/include/nav2_core/global_planner.hpp
[ctl-g]: https://github.com/ros-navigation/navigation2/blob/1.0.12/nav2_core/include/nav2_core/controller.hpp
[ctl-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_core/include/nav2_core/controller.hpp
[ctl-j]: https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_core/include/nav2_core/controller.hpp
[ctl-l]: https://github.com/ros-navigation/navigation2/blob/lyrical/nav2_core/include/nav2_core/controller.hpp
[rpp-g]: https://github.com/ros-navigation/navigation2/blob/1.0.12/nav2_regulated_pure_pursuit_controller/src/regulated_pure_pursuit_controller.cpp
[rpp-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_regulated_pure_pursuit_controller/src/regulated_pure_pursuit_controller.cpp
[rpp-j]: https://github.com/ros-navigation/navigation2/tree/jazzy/nav2_regulated_pure_pursuit_controller/src
[rpp-l]: https://github.com/ros-navigation/navigation2/tree/lyrical/nav2_regulated_pure_pursuit_controller/src
[rpp-doc]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/controller_plugins/configuring_regulated_pp.md
[ctrl-plugins-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_controller/plugins.xml
[ctrl-plugins-l]: https://github.com/ros-navigation/navigation2/blob/lyrical/nav2_controller/plugins.xml
[pluginlib-h]: https://github.com/ros/pluginlib/blob/humble/pluginlib/include/pluginlib/class_loader_imp.hpp
[tut-costmap]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/tutorials/plugin_tutorials/writing_new_costmap2d_plugin/writing_new_costmap2d_plugin.md
[tut-h]: https://github.com/ros-navigation/navigation2_tutorials/tree/humble
[sc-readme-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_simple_commander/README.md
[rpp-readme-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_regulated_pure_pursuit_controller/README.md
[vs-readme-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_velocity_smoother/README.md
[cm-readme-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_collision_monitor/README.md
[c2d-cpp-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_costmap_2d/src/costmap_2d.cpp
[bf-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_costmap_2d/plugins/costmap_filters/binary_filter.cpp
[doh-h]: https://github.com/ros-navigation/navigation2/blob/humble/nav2_msgs/action/DriveOnHeading.action
[dock-h]: https://github.com/open-navigation/opennav_docking/tree/humble
[doc-baseobs]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/controller_plugins/dwb_controller/trajectory_critics/base_obstacle.md
[doc-obsfp]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/controller_plugins/dwb_controller/trajectory_critics/obstacle_footprint.md
[doc-btn]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/configuring_bt_navigator.md
[doc-spin]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/bt_plugins/actions/Spin.md
[doc-recnode]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/bt_plugins/controls/RecoveryNode.md
[doc-bs]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/configuring_behavior_server.md
[doc-ps]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/configuring_planner_server.md
[doc-cm-setup]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/first_time_robot_setup_guide/sensors/mapping_localization.md
[doc-c2d]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/costmap_2d/index.md
[doc-ctrl-plugins]: https://github.com/ros-navigation/docs.nav2.org/tree/rolling/docs/configuration_and_development/configuration_guide/core_servers/controller_server/controller_server_plugins
[doc-bf]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/costmap_2d/costmap_filters/binary_filter/binary_filter.md
[doc-vs]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/configuring_velocity_smoother.md
[doc-cm]: https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/configuration_guide/core_servers/collision_monitor/index.md
[create-h]: https://github.com/gazebosim/ros_gz/blob/humble/ros_gz_sim/src/create.cpp
[rosgz-sim-readme]: https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_sim/README.md
[fuel-cone]: https://app.gazebosim.org/OpenRobotics/fuel/models/Construction%20Cone
[gz-cone-world]: https://github.com/gazebosim/gz-sim/blob/gz-sim8/examples/worlds/camera_sensor.sdf
