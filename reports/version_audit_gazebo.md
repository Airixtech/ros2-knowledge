# Version audit — ros2-gazebo (Phase 1)

> Date: 2026-10-20.
> Scope: every version-dependent or checkable statement of the URDF course (course wiki, not published) that lands
> in `ros2-gazebo`: starting Gazebo Sim, worlds, spawning a URDF, `<gazebo>` tags (friction, contact, materials),
> the JointStatePublisher and DiffDrive systems, `ros_gz_bridge`, `gz_ros2_control` and its controllers, sensors
> (lidar, point cloud, cameras, IMU) and several robots in one world. Section IDs = the course's section numbers.
> Baseline: **Jazzy + Gazebo Harmonic is canonical** for this skill (decision of 2026-10-20): the course targets it
> and it is the official pairing of the current LTS distro. **Humble + Fortress** (the team's distro) and
> **Lyrical + Jetty** are annotated, and every Humble row names the official Humble/Fortress source to read.
> URDF and xacro rows are in [version_audit_urdf.md](version_audit_urdf.md) (`URDF-Vnn`); generic ROS 2 rows in
> [version_audit.md](version_audit.md) (`Vnn`, e.g. V20 `gz sim` vs `ign gazebo`, V64–V66 Gazebo pairing).

## Method
- Primary sources, read on the matching branch with grep: `gazebosim/gz-sim` (gz-sim8 = Harmonic, ign-gazebo6 =
  Fortress, gz-sim10 = Jetty: systems, `server.config`, `SystemLoader.cc`, `Util.hh`, `Migration.md`, changelog),
  `gazebosim/gz-sensors` (gz-sensors8, ign-sensors6), `gazebosim/sdformat` (sdf14: `parser_urdf.cc`,
  `sdf/1.11/surface.sdf`), `gazebosim/ros_gz` (humble, jazzy, lyrical: `ros_gz_sim` create and launch files,
  `ros_gz_bridge`), `ros-controls/gz_ros2_control` (humble, jazzy, lyrical), `ros-controls/ros2_controllers` and
  `ros2_control` (humble, jazzy), `ros/rosdistro` (humble, jazzy), the Gazebo docs repository (release table) and the
  official template `gazebosim/ros_gz_project_template` (Apache-2.0) as the reference for "how to do it right".
- Course logic was reviewed too: plugin elements against the code that reads them, explanations against the XML,
  launch files against each other. Contradictions are **fix** rows ("course mistake").
- Actions: **keep** = correct for Jazzy/Harmonic · **annotate** = correct, add marks (Humble/Fortress, Lyrical/Jetty)
  or a precise wording · **fix** = wrong for Jazzy/Harmonic itself. Confidence: High (read in code) · Medium (docs,
  or inferred) · `[verify]` (needs a run).

## Baseline (Gazebo per ROS 2 distro)
| | Humble | Jazzy (canonical) | Kilted | Lyrical |
|---|---|---|---|---|
| Official Gazebo (REP 2000, ros_gz README) | Fortress (`ign gazebo`), binaries on packages.ros.org; Harmonic only from packages.osrfoundation.org ("use with caution", `ros-humble-ros-gzharmonic`) | Harmonic | Ionic | Jetty |
| Gazebo EOL | Fortress May 2027 | Harmonic May 2029 | Ionic Dec 2026 | Jetty May 2031 |
| ros_gz branch | `humble` | `jazzy` | `kilted` | `lyrical` |
| gz_ros2_control | 0.7.21 (repo `ign_ros2_control`, releases `gz_ros2_control` + `ign_ros2_control`) | 1.2.x | — | lyrical branch |
| Physics default | DART | DART | DART | DART |
| Official docs | [Fortress ROS 2 integration][gz-fortress-ros], [ROS 2 Humble: Using a URDF in Gazebo][docs-gz-urdf-h] | [Harmonic ROS 2 integration][gz-harmonic-ros], [ROS 2 Jazzy: Gazebo][docs-gz-j] | — | [Jetty docs][gz-jetty] |

## Real Jazzy errors (fix)
| ID | Section | Origin | Error | Correct statement |
|---|---|---|---|---|
| GZ-V01 | 4.7 | course mistake | "`mu1`: the static friction coefficient … `mu2`: the dynamic friction coefficient" | `mu` (`mu1` in the URDF shortcut) and `mu2` are Coulomb friction coefficients in the two directions of the friction pyramid (`fdir1` and its perpendicular), "the unitless maximum ratio of force … to normal force"; static vs dynamic friction is not modelled by them. Sources: [surface.sdf][surface-sdf], [ROS 2 physical properties tutorial][docs-phys-j]. |
| GZ-V02 | 4.7 | course mistake | "`kp`: static contact stiffness … `kd`: dynamic contact stiffness" | `kp` = contact stiffness, `kd` = contact **damping** (SDF defaults `kp = 1e12`, `kd = 1`). Sources: [surface.sdf][surface-sdf], [ROS 2 tutorial][docs-phys-j] ("kd - Dampening coefficient"). |
| GZ-V03 | 5.4 | Gazebo Classic options | DiffDrive `<publish_odom>`, `<publish_odom_tf>`, `<publish_wheel_tf>`, and "it publishes the TF transforms … of all the positions of the wheels" | The gz-sim DiffDrive system reads none of those elements (they are ignored). It always publishes odometry on `<odom_topic>` and the `frame_id → child_frame_id` transform on `<tf_topic>`; the wheel link transforms come from the JointStatePublisher system plus robot_state_publisher. Code: [DiffDrive.cc][diffdrive-8] (same in Jetty). |
| GZ-V04 | 5.3 | course mistake | "As an alternative to the Joint State Publisher plugin, you can launch a Joint State Publisher node that provides equivalent functionality" | `joint_state_publisher` does not read simulated joints: it publishes GUI/default values (or merges other `JointState` topics given in `source_list`). The equivalents are the JointStatePublisher system (bridged) or `joint_state_broadcaster` with gz_ros2_control. Code: [joint_state_publisher.py][jsp-h]. |
| GZ-V05 | 6.4 | course mistake | Camera comment: "Base Gazebo topic; subtopics /image and /camera_info will be created" | The image is published on `<topic>` itself; `camera_info` goes to the parent of that topic + `/camera_info` (`robot1/camera1` → `/robot1/camera_info`; `rgb_camera` → `/camera_info`), unless `<camera_info_topic>` is set. Code: [CameraSensor.cc][camera-8] (same in Fortress). |
| GZ-V06 | 5.6, 5.8 | course mistake | Controller YAML: `joint_trajectory_controller: … interface_name: position` | `interface_name` is not a JointTrajectoryController parameter (Humble or Jazzy): it is ignored. JTC uses `joints`, `command_interfaces`, `state_interfaces`. Code: [JTC parameters][jtc-params-j]. |
| GZ-V07 | 5.8 | course mistake | `velocity_controller` (JointGroupVelocityController) with `interface_name: velocity`, `command_interfaces`, `state_interfaces` | Its parameters are those of forward_command_controller: `joints` and `interface_name`, and the velocity variant sets `interface_name` to `velocity` itself. `command_interfaces`/`state_interfaces` belong to JTC and are ignored here. Code: [forward_command_controller parameters][fcc-params-j], [joint_group_velocity_controller.cpp][velctrl-j]. |
| GZ-V08 | 5.8 | course contradiction | "That is why, in the previous example, you added the dependency in the CMakeLists.txt of the velocity_controllers" | The CMakeLists.txt shown adds no such dependency. Controllers are loaded at run time: declare `<exec_depend>` on `velocity_controllers`, `joint_trajectory_controller`, `joint_state_broadcaster` and `gz_ros2_control` in `package.xml` (binaries `ros-<distro>-ros2-controllers`, `ros-<distro>-gz-ros2-control`). Sources: [rosdistro jazzy][rosdistro-j]. |
| GZ-V09 | 7.4, 7.9 | Gazebo Classic name | "`spawn_entity.py` can use this information to create a robot model instance in Gazebo"; "two calls to the `spawn_entity.py` script" | `spawn_entity.py` is the spawner of Gazebo Classic. With Gazebo Sim the course's own code uses `ros2 run ros_gz_sim create` (`-topic`, `-file`, `-string` or `-param`), same flags in Humble, Jazzy and Lyrical. Code: [create.cpp][create-j]. |
| GZ-V50 | 5.8 | course mistake | "the interface's name is velocity, but the name could be anything here. Be sure to name it the same way in the YAML file" | GazeboSimSystem exports only interfaces named `position`, `velocity` and `effort`; any other name gives the controller nothing to claim. Code: [gz_system.cpp][gzr2c-sys-j]. |
| GZ-V53 | 5.6 | course contradiction | "For collision, add a cylinder shape that fits best the 3D mesh" | The file (and its inertia values) uses a box `0.074986 0.074935 0.0408` for `laser_scan_link`; the cylinder (`radius 0.037493`) appears only in the explanation snippet and later on `laser_scan_model_link`. The notes follow the file. |
| GZ-V54 | 6.2 | course mistake | "If your physical mount can move the LiDAR up/down but not rotate (a prismatic joint along Z), that constraint should be defined in … (`laser_scan_frame_joint`) connecting `laser_scan_frame` to `laser_scan_link`" | `laser_scan_frame_joint` is fixed; the prismatic joint is `laser_scan_link_joint` (chassis → laser_scan_link), as in the course's own file. |
| GZ-V56 | 6.5 | course claim | "The IMU sensor … will publish data to the specified ROS topics" | It publishes on the Gazebo topic `imu`; ROS nodes see it only after bridging `sensor_msgs/msg/Imu` ↔ `gz.msgs.IMU`. Source: [bridge README][bridge-j]. |

## Full table
| # | Section | Statement | Humble (Fortress) | Jazzy (Harmonic) | Lyrical (Jetty) | Action | Source | Confidence |
|---|---|---|---|---|---|---|---|---|
| GZ-V01 | 4.7 | mu = static, mu2 = dynamic friction | ✗ two pyramid directions | ✗ same | ✗ same | **fix** | [surface-sdf] | High |
| GZ-V02 | 4.7 | kp/kd = static/dynamic stiffness | ✗ stiffness / damping | ✗ same | ✗ same | **fix** | [surface-sdf], [docs-phys-j] | High |
| GZ-V03 | 5.4 | DiffDrive `publish_*` elements, wheel TF | ✗ ignored ([DiffDrive Fortress][diffdrive-6]) | ✗ ignored | ✗ ignored | **fix** | [diffdrive-8] | High |
| GZ-V04 | 5.3 | joint_state_publisher node = JointStatePublisher system | ✗ | ✗ | ✗ | **fix** | [jsp-h] | High |
| GZ-V05 | 6.4 | Camera subtopics `/image` and `/camera_info` | ✗ image on `<topic>`, info on parent + `/camera_info` ([Fortress][camera-6]) | ✗ same | ✗ same | **fix** | [camera-8] | High |
| GZ-V06 | 5.6 | JTC `interface_name` | ✗ not a parameter ([humble][jtc-params-h]) | ✗ | ✗ | **fix** | [jtc-params-j] | High |
| GZ-V07 | 5.8 | Velocity controller `command_interfaces`/`state_interfaces` | ✗ ignored | ✗ ignored | ✗ ignored | **fix** | [fcc-params-j], [velctrl-j] | High |
| GZ-V08 | 5.8 | "you added the dependency in CMakeLists.txt" | ✗ use `<exec_depend>` | ✗ | ✗ | **fix** | [rosdistro-j] | High |
| GZ-V09 | 7.4, 7.9 | `spawn_entity.py` | ✗ `ros_gz_sim create` | ✗ | ✗ | **fix** | [create-j] | High |
| GZ-V10 | 4.2 | Start the world with `ros_gz_sim/gz_sim.launch.py`, `gz_args: ['-r ', world]` (`-r` = run unpaused) | ✓ the same launch file runs `ign gazebo` for Fortress (core V20) | ✓ | ✓ | keep | [gzsim-launch-j], [gzsim-launch-h] | High |
| GZ-V11 | 4.2, 4.6, 7.4 | Meshes and `model://` found only through `GZ_SIM_RESOURCE_PATH`, set by hand with `os.environ` in the launch file | ✓ current Fortress reads `IGN_GAZEBO_RESOURCE_PATH` **and** `GZ_SIM_RESOURCE_PATH` ([Util.hh][util-6]); `gz_sim.launch.py` sets both | ✓ | ✓ | annotate: official alternatives are a `package.xml` export `<gazebo_ros gazebo_model_path="${prefix}/../"/>` read by `gz_sim.launch.py` (Humble and Jazzy), or an ament environment hook (`prepend-non-duplicate;GZ_SIM_RESOURCE_PATH;share`) as in the official template | [gzsim-launch-j], [template] | High |
| GZ-V12 | 4.2–6.5 | Plugin files `gz-sim-*-system`, names `gz::sim::systems::*` | ✓ with current Fortress: `SystemLoader` replaces the `gz-sim` prefix with `ignition-gazebo` and the course's systems register `gz::sim::systems::` aliases; the NavSat alias arrived in 6.18.0 (2026-06) ([PR 3369][pr3369]); check the installed version [verify] | ✓ | ✓ | annotate | [sysloader-6], [gzsim6-changelog] | High |
| GZ-V13 | 4.3 | World SDF with light and ground plane but no `<plugin>` | ✓ a world without plugins loads the defaults of `server.config`: Physics, UserCommands, SceneBroadcaster | ✓ | ✓ | annotate: the official template lists the world systems explicitly (Physics, Sensors, SceneBroadcaster…) | [server-config-8], [template] | High |
| GZ-V14 | 4.3 | `<include><uri>model://box_room</uri>` from the course's model repository | platform repository removed; any model folder on the resource path works | same | same | annotate | — | — |
| GZ-V15 | 4.4 | Gazebo only simulates rigid bodies; every simulated link needs collision and inertia | ✓ | ✓ | ✓ | keep | [docs-phys-j] | Medium |
| GZ-V16 | 4.4–4.7 | `<gazebo reference="link"><collision><surface>…</surface></collision></gazebo>` | ✓ the URDF converter inserts collision and visual blobs into every collision/visual of that link; the short form `<mu1>`, `<mu2>`, `<kp>`, `<kd>`, `<fdir1>`, `<maxVel>`, `<minDepth>` also exists | ✓ | ✓ | keep | [parser-urdf-14] | High |
| GZ-V17 | 4.5–7.9 | Wheel contact `kd = 1e7` (the 4.7 example uses `kd = 1.0`) | very high damping against the default 1; effect on wheel grip [verify] | same | same | annotate | [surface-sdf] | Medium |
| GZ-V18 | 4.6 | "Gazebo reads from the /robot_description topic and spawns … with the random name generated" | annotate: the `ros_gz_sim create` node reads the topic (`-topic`) and asks Gazebo to spawn it; `-allow_renaming` renames on a clash | same | same | annotate | [create-j] | High |
| GZ-V19 | 4.6 | URDF → SDF: links joined by fixed joints | annotate (own addition, checked): the converter merges them into the parent link unless `<gazebo reference="joint"><preserveFixedJoint>true</preserveFixedJoint></gazebo>` | same | same | annotate | [parser-urdf-14] | High |
| GZ-V20 | 2.8 (URDF) | `floating`/`planar` joints in Gazebo | the URDF converter creates no joint for them, so the child link is not constrained [verify] | same | same | annotate | [parser-urdf-14] | Medium |
| GZ-V21 | 4.6 | No TF for non-fixed joints until something publishes `/joint_states` | ✓ | ✓ | ✓ | keep | — | High |
| GZ-V22 | 5.2 | Systems DiffDrive, MecanumDrive, JointPositionController, JointTrajectoryController, JointStatePublisher; or ros2_control via gz_ros2_control | ✓ | ✓ | ✓ | keep | [gz-systems-8] | High |
| GZ-V23 | 5.3 | JointStatePublisher elements `<topic>`, `<update_rate>`, `<joint_name>` (default topic per model) | ✓ | ✓ | ✓ | keep | [jsp-sys-8] | High |
| GZ-V24 | 5.4 | DiffDrive: `<child_frame_id>` = robot root frame; `<wheel_separation>` = distance between wheel centres (0.1 here, equal to the chassis width by coincidence) | ✓ | ✓ | ✓ | annotate | [diffdrive-8] | High |
| GZ-V25 | 5.4 | "Unlike Gazebo Classic, Gazebo Sim systems use Gazebo Transport topics: bridge them" | ✓ | ✓ | ✓ | keep | [bridge-j] | High |
| GZ-V26 | 5.4, 6.2, 6.3 | Bridge syntax `topic@ros_type@gz_type` (both ways), `[` Gazebo → ROS, `]` ROS → Gazebo; pairs Clock, Twist, TFMessage↔Pose_V, Odometry, JointState↔Model, LaserScan, PointCloud2↔PointCloudPacked, Image, CameraInfo | ✓ same pairs; the Humble bridge accepts `gz.msgs.*` and `ignition.msgs.*` (resolves core V66) | ✓ | ✓ | annotate | [bridge-j], [bridge-map-h] | High |
| GZ-V27 | 4.2–7.9 | `SetParameter(name="use_sim_time", value=True)` "(doesn't work for nodes started from ignition gazebo)" | ✓ it applies to the ROS nodes started after it in the same launch scope; Gazebo is not a ROS node: bridge `/clock` | ✓ | ✓ | keep | ros2-core note `core-time-timers` | High |
| GZ-V28 | 5.5–5.8 | gz_ros2_control names `gz_ros2_control/GazeboSimSystem`, `gz_ros2_control-system`, `gz_ros2_control::GazeboSimROS2ControlPlugin`, `<parameters>` | ✓ in Humble's gz_ros2_control 0.7.21 (also the old `ign_ros2_control` aliases) | ✓ | ✓; the `ign_ros2_control::IgnitionSystem` export is gone | annotate | [gzr2c-j], [gzr2c-h], [gzr2c-l], [rosdistro-h] | High |
| GZ-V29 | 5.6 | Where the controller manager gets the robot description | Humble: parameter `robot_description` of node `robot_state_publisher` (`<robot_param_node>`, `<robot_param>`); the course names the node `robot_state_publisher_node`, so add `<robot_param_node>robot_state_publisher_node</robot_param_node>` or keep the default node name | from the `/robot_description` topic | topic | annotate | [gzr2c-h], [gzr2c-h-doc], [gzr2c-j] | High |
| GZ-V30 | 5.6 | `<parameters>$(find pkg)/config/x.yaml</parameters>` inside a `.urdf` | ✓ only because the launch file runs the `.urdf` through xacro; a URDF loaded without xacro keeps the literal `$(find …)` | ✓ | ✓ | annotate | [xacro] | High |
| GZ-V31 | 5.6 | Command interface `<param name="min">`/`max` (−0.05…0) while the URDF limit is −0.1…0 | interface metadata parsed by ros2_control; whether anything clamps to it [verify] | same | same | annotate | — | Medium |
| GZ-V32 | 5.6, 5.8 | `controller_manager: update_rate`, controller `type`s; `spawner <name>` per controller | ✓ | ✓ (spawner also takes several names and `--param-file`) | ✓ | annotate | [spawner-j] | High |
| GZ-V33 | 5.7 | Python FollowJointTrajectory client: `rclpy.shutdown()` in the result callback, `rclpy.spin` in main | ✓ same pattern as the official action client tutorial; `send_goal` returns nothing (the `future` variable is `None`) | ✓ | ✓ | keep | [docs-action-j] | High |
| GZ-V34 | 5.8 | `ros2 topic pub /velocity_controller/commands std_msgs/msg/Float64MultiArray` with 20 rad/s while the joint limit is 2.0 | the controller does not clamp; whether Gazebo enforces the URDF velocity limit [verify] | same | same | annotate | — | Medium |
| GZ-V35 | 6.2 | Sensors system loaded from the robot (`<gazebo><plugin gz-sim-sensors-system>`) with `<render_engine>ogre2` | works (default engine `ogre2`); the official template loads Sensors in the world SDF; with several robots each model would add its own Sensors system [verify] | same | same | annotate | [sensors-8], [template] | Medium |
| GZ-V36 | 6.2 | `<gz_frame_id>` sets `header.frame_id`; default "scoped name" | default = the sensor's name as gz-sim passes it; Fortress reads `ignition_frame_id` and also `gz_frame_id` ([ign-sensors6][sensor-6]) | ✓ | ✓ | annotate | [sensor-8] | High |
| GZ-V37 | 6.2 | `gpu_lidar`: `<topic>` is a Gazebo topic; `<always_on>`, `<visualize>`, `<update_rate>`, `<ray>`/`<scan>`/`<range>` | ✓ | ✓ | ✓ | keep | [lidar-8] | High |
| GZ-V38 | 6.3 | A 2-D `gpu_lidar` (horizontal + vertical samples) publishes a point cloud on `<topic>/points` (PointCloudPacked) | ✓ | ✓ | ✓ | keep | [lidar-8] | High |
| GZ-V39 | 6.3 | `wideanglecamera` with `<lens>` (custom function, `scale_to_hfov`, `cutoff_angle`, `env_texture_size`) | ✓ | ✓ | ✓ | keep | [wideangle-8] | Medium |
| GZ-V40 | 6.3 | RViz: set each sensor topic's QoS from `ros2 topic info -v` | ✓ | ✓ | ✓ | keep | — | High |
| GZ-V41 | 6.5, 7.7 | IMU needs the Imu system; GPS needs the NavSat system; Gaussian noise elements | ✓ (NavSat `gz::` alias from Fortress 6.18.0) | ✓ | ✓ | keep | [gz-systems-8], [pr3369] | High |
| GZ-V42 | 7.9 | Two `create` nodes with the same name `my_robot_spawn` in the same namespace | annotate: duplicate node names (rosout warns, CLI tools become ambiguous): give each a unique name | same | same | annotate | — | Medium |
| GZ-V43 | 7.9 | Per-robot plugin topics and frames through a xacro `robot_name` parameter; RSP `frame_prefix`; one bridge with per-robot topics | ✓ | ✓ | ✓ | keep | [diffdrive-8], [rsp-j] | High |
| GZ-V44 | — | Harmonic → Jetty for this material | no change in the systems and elements the course uses (DiffDrive, JointStatePublisher, default systems, DART default); Ionic changed only the C++ system API (velocity commands deleted after each step) | — | ✓ | annotate | [migration-10] | High |
| GZ-V45 | — | Humble with Harmonic | ros_gz `humble` branch against Harmonic, binaries from packages.osrfoundation.org (`ros-humble-ros-gzharmonic`), "use with caution"; do not mix with `ros-humble-ros-gz` | — | — | annotate | [rosgz-readme] | High |
| GZ-V46 | 4.4 | (own addition, checked) A link without `<inertial>` | an urdf2sdf error ("link[…] has no <inertial> block defined") drops its joint unless its fixed parent joint is lumped; empty frame links on fixed joints are fine | same | same | annotate | [parser-urdf-14] | High |
| GZ-V47 | 4.7, 7.8 | (own addition, checked) Colors and per-link extension tags | URDF `<material><color>` becomes the SDF visual color unless a `<gazebo reference><visual><material>` block sets it; per-link tags are `selfCollide` and `turnGravityOff` (written as `self_collide`, `gravity`) | same | same | annotate | [parser-urdf-14] | High |
| GZ-V48 | 4.3 | (own addition, checked) When the default world systems load | only when the world has no system at all: "No systems loaded from SDF, loading defaults"; model plugins do not count | same | same | annotate | [simrunner-8] | High |
| GZ-V49 | 4.6 | (own addition, checked) `create` start-up | asks the server for the world list ("Requesting list of world names.") until Gazebo answers, then waits for the description on a Transient Local subscription ("Waiting messages on topic [...]") | same | same | annotate | [create-j] | High |
| GZ-V50 | 5.8 | Interface name "could be anything" | ✗ only position/velocity/effort | ✗ same | ✗ same | **fix** | [gzr2c-sys-j] | High |
| GZ-V51 | 5.7 | Action client: rejected goal | the script returns without `rclpy.shutdown()` and keeps spinning (same in the official tutorial client); JTC rejects joints it does not handle ("Incoming joint … doesn't match the controller's joints.") | same | same | annotate | [docs-action-j], [jtc-j] | High |
| GZ-V52 | 5.8 | Inertia of `laser_scan_link` (0.02 m box) and `laser_scan_model_link` (cylinder) | both reuse the values of the 0.075 m box of 5.6: recompute for each shape | same | same | annotate | — | High |
| GZ-V53 | 5.6 | Laser collision "cylinder" vs the box in the file | ✗ the file uses a box | ✗ same | ✗ same | **fix** | — | High |
| GZ-V54 | 6.2 | Prismatic constraint on `laser_scan_frame_joint` | ✗ that joint is fixed | ✗ | ✗ | **fix** | — | High |
| GZ-V55 | 6.2 | `<resolution>` "can densify beams"; `<ray>` element | resolution multiplies samples and interpolates the data (no extra real beams); gpu_lidar reads `<lidar>` or, if absent, `<ray>` | same | same | annotate | [lidar-sdf-14], [sensor-sdf-14] | High |
| GZ-V56 | 6.5 | IMU "publishes to ROS topics" | ✗ Gazebo topic, bridge needed | ✗ | ✗ | **fix** | [bridge-j] | High |

## Open `[verify]` (Phase 5 or a real machine)
- GZ-V12: installed Fortress version on the Humble machine (`ign gazebo --versions`) for the `gz-sim` names and the NavSat alias.
- GZ-V17: wheel behaviour with `kd = 1e7` vs a small damping.
- GZ-V20: what Gazebo does with a URDF `floating`/`planar` joint.
- GZ-V31, GZ-V34: whether interface `min`/`max` or the URDF velocity limit clamp commands in simulation.
- GZ-V35: two robots that each load the Sensors system.

## Sources
[gz-releases]: https://gazebosim.org/docs/latest/releases/
[gz-fortress-ros]: https://gazebosim.org/docs/fortress/ros2_integration/
[gz-harmonic-ros]: https://gazebosim.org/docs/harmonic/ros2_integration/
[gz-jetty]: https://gazebosim.org/docs/jetty/
[docs-gz-urdf-h]: https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/Using-a-URDF-in-Gazebo.html
[docs-gz-j]: https://docs.ros.org/en/jazzy/Tutorials/Advanced/Simulators/Gazebo/Gazebo.html
[docs-phys-j]: https://docs.ros.org/en/jazzy/Tutorials/Intermediate/URDF/Adding-Physical-and-Collision-Properties-to-a-URDF-Model.html
[docs-action-j]: https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Writing-an-Action-Server-Client/Py.html
[rosgz-readme]: https://github.com/gazebosim/ros_gz/blob/jazzy/README.md
[gzsim-launch-j]: https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_sim/launch/gz_sim.launch.py.in
[gzsim-launch-h]: https://github.com/gazebosim/ros_gz/blob/humble/ros_gz_sim/launch/gz_sim.launch.py.in
[create-j]: https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_sim/src/create.cpp
[bridge-j]: https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md
[bridge-map-h]: https://github.com/gazebosim/ros_gz/blob/humble/ros_gz_bridge/resource/get_mappings.cpp.em
[diffdrive-8]: https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/systems/diff_drive/DiffDrive.cc
[diffdrive-6]: https://github.com/gazebosim/gz-sim/blob/ign-gazebo6/src/systems/diff_drive/DiffDrive.cc
[jsp-sys-8]: https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/systems/joint_state_publisher/JointStatePublisher.cc
[sensors-8]: https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/systems/sensors/Sensors.cc
[gz-systems-8]: https://github.com/gazebosim/gz-sim/tree/gz-sim8/src/systems
[server-config-8]: https://github.com/gazebosim/gz-sim/blob/gz-sim8/include/gz/sim/server.config
[simrunner-8]: https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/SimulationRunner.cc
[sysloader-6]: https://github.com/gazebosim/gz-sim/blob/ign-gazebo6/src/SystemLoader.cc
[util-6]: https://github.com/gazebosim/gz-sim/blob/ign-gazebo6/include/gz/sim/Util.hh
[gzsim6-changelog]: https://github.com/gazebosim/gz-sim/blob/ign-gazebo6/Changelog.md
[pr3369]: https://github.com/gazebosim/gz-sim/pull/3369
[migration-10]: https://github.com/gazebosim/gz-sim/blob/gz-sim10/Migration.md
[surface-sdf]: https://github.com/gazebosim/sdformat/blob/sdf14/sdf/1.11/surface.sdf
[parser-urdf-14]: https://github.com/gazebosim/sdformat/blob/sdf14/src/parser_urdf.cc
[lidar-sdf-14]: https://github.com/gazebosim/sdformat/blob/sdf14/sdf/1.11/lidar.sdf
[sensor-sdf-14]: https://github.com/gazebosim/sdformat/blob/sdf14/src/Sensor.cc
[sensor-8]: https://github.com/gazebosim/gz-sensors/blob/gz-sensors8/src/Sensor.cc
[sensor-6]: https://github.com/gazebosim/gz-sensors/blob/ign-sensors6/src/Sensor.cc
[camera-8]: https://github.com/gazebosim/gz-sensors/blob/gz-sensors8/src/CameraSensor.cc
[camera-6]: https://github.com/gazebosim/gz-sensors/blob/ign-sensors6/src/CameraSensor.cc
[lidar-8]: https://github.com/gazebosim/gz-sensors/blob/gz-sensors8/src/GpuLidarSensor.cc
[wideangle-8]: https://github.com/gazebosim/gz-sensors/blob/gz-sensors8/src/WideAngleCameraSensor.cc
[template]: https://github.com/gazebosim/ros_gz_project_template
[gzr2c-j]: https://github.com/ros-controls/gz_ros2_control/blob/jazzy/gz_ros2_control/src/gz_ros2_control_plugin.cpp
[gzr2c-sys-j]: https://github.com/ros-controls/gz_ros2_control/blob/jazzy/gz_ros2_control/src/gz_system.cpp
[jtc-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/joint_trajectory_controller/src/joint_trajectory_controller.cpp
[gzr2c-h]: https://github.com/ros-controls/gz_ros2_control/blob/humble/gz_ros2_control/src/gz_ros2_control_plugin.cpp
[gzr2c-h-doc]: https://github.com/ros-controls/gz_ros2_control/blob/humble/doc/index.rst
[gzr2c-l]: https://github.com/ros-controls/gz_ros2_control/blob/lyrical/gz_ros2_control/src/gz_system.cpp
[rosdistro-h]: https://github.com/ros/rosdistro/blob/master/humble/distribution.yaml
[rosdistro-j]: https://github.com/ros/rosdistro/blob/master/jazzy/distribution.yaml
[jtc-params-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/joint_trajectory_controller/src/joint_trajectory_controller_parameters.yaml
[jtc-params-h]: https://github.com/ros-controls/ros2_controllers/blob/humble/joint_trajectory_controller/src/joint_trajectory_controller_parameters.yaml
[fcc-params-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/forward_command_controller/src/forward_command_controller_parameters.yaml
[velctrl-j]: https://github.com/ros-controls/ros2_controllers/blob/jazzy/velocity_controllers/src/joint_group_velocity_controller.cpp
[spawner-j]: https://github.com/ros-controls/ros2_control/blob/jazzy/controller_manager/controller_manager/spawner.py
[jsp-h]: https://github.com/ros/joint_state_publisher/blob/humble/joint_state_publisher/joint_state_publisher/joint_state_publisher.py
[rsp-j]: https://github.com/ros/robot_state_publisher/blob/jazzy/src/robot_state_publisher.cpp
[xacro]: https://github.com/ros/xacro/blob/ros2/xacro/__init__.py
