# Version audit — ros2-urdf (Phase 1)

> Date: 2026-10-20.
> Scope: every version-dependent or checkable statement of the URDF course (course wiki, not published) that lands
> in `ros2-urdf`: URDF links, joints and special elements, materials and meshes, robot_state_publisher and
> joint_state_publisher, RViz2 display, inertia, xacro (properties, macros, conditionals, includes, launch
> processing) and the Onshape export. Section IDs = the course's section numbers (2.4, 7.6…).
> Baseline: **Humble is canonical**. Jazzy and Lyrical differences are annotated, not substituted.
> The course itself targets Jazzy (its solution repository uses a `jazzy` branch); the URDF side barely depends on
> the distro. Gazebo rows (simulation tags, plugins, gz_ros2_control, sensors) are in
> [version_audit_gazebo.md](version_audit_gazebo.md) (IDs `GZ-Vnn`). Generic ROS 2 rows are in
> [version_audit.md](version_audit.md) (IDs `Vnn`); this report cites them instead of repeating them.

## Method
- Primary sources, read on the matching branch with grep: `ros/urdfdom` (humble 3.0.2, jazzy 4.0.2, lyrical 6.0.0:
  `urdf_parser/src/joint.cpp`, `link.cpp`, `model.cpp`), `ros/kdl_parser` (humble), `ros/robot_state_publisher`
  (humble, jazzy, lyrical), `ros/joint_state_publisher` (humble), `ros/xacro` (ros2 branch, 2.1.1), `ros2/rviz`
  (humble, jazzy: `robot_link.cpp`, `robot_model_display.cpp`), `Rhoban/onshape-to-robot` (master, 1.8.3, and its
  `docs/`), and the official URDF tutorials of `ros2/ros2_documentation` (humble, jazzy).
- Origin first: the course does not follow one official tutorial; its URDF and xacro parts match the topics of the
  official "URDF" tutorial series. Its own code and printed values were checked against the parser and the math
  (inertia values recomputed from the formulas).
- Course logic was reviewed too: macro parameters against their calls, properties and args against their use,
  explanations against the XML they describe. Contradictions are **fix** rows ("course mistake").
- The course links to a third-party URDF specification page; notes cite the parser code and the official ROS 2
  tutorials instead.
- Actions: **keep** = correct for Humble · **annotate** = correct for Humble, add marks or a precise wording ·
  **fix** = wrong for Humble itself. Confidence: High (read in code) · Medium (docs, or inferred) · `[verify]`
  (needs a run).

## Baseline (packages per ROS 2 distro)
| | Humble | Jazzy | Lyrical |
|---|---|---|---|
| urdfdom | 3.0.2 (TinyXML) | 4.0.2 (tinyxml2) | 6.0.0 (tinyxml2; adds `capsule` for `<robot version="1.1">`) |
| robot_state_publisher | `robot_description` parameter → `/robot_description` (transient local), fixed joints on `/tf_static`, movable joints on `/tf` | same parameters | adds `use_robot_description_topic` (subscribe to the description instead of the parameter) |
| xacro | 2.0.x (ros2 branch) | 2.x (ros2 branch) | 2.x (ros2 branch) |
| joint_state_publisher(_gui) | separate packages `joint_state_publisher`, `joint_state_publisher_gui` | same | same |
| Ubuntu / Python | 22.04 / 3.10 | 24.04 / 3.12 (system pip is externally managed, PEP 668) | 26.04 / 3.14 |
| Sources | [urdfdom][urdfdom-h], [RSP][rsp-h], [REP 2000][rep2000] | [urdfdom][urdfdom-j] | [urdfdom link.cpp][urdfdom-link-l], [RSP][rsp-l] |

## Real Humble errors (fix)
| ID | Section | Origin | Error | Correct statement |
|---|---|---|---|---|
| URDF-V01 | 4.4 | course mistake | Box inertia macro: `izz="${mass*(x*x+z*z)/12}"` | `izz = m(x²+y²)/12` (the two sides perpendicular to z), like `ixx = m(y²+z²)/12` and `iyy = m(x²+z²)/12`. The values in the course's URDF files are right (recomputed: laser box `izz = 9.365e-06` uses x and y); only the printed formula is wrong. The 4.4 example also says mass 0.2 for the chassis, while the URDF uses 0.5 kg with `I = 8.33e-4` (= 0.5·(0.1²+0.1²)/12). Sources: [physical properties tutorial][docs-phys-h] (links the standard formulas). |
| URDF-V02 | 3.2, 4.5–7.9 (every wheel joint) | course mistake | `<joint_properties damping="1.0" friction="1.0"/>` and `<axis rpy="0 0 0" xyz="0 1 0"/>` | URDF has no `<joint_properties>`: the parser reads only `origin`, `parent`, `child`, `axis`, `limit`, `dynamics`, `mimic`, `safety_controller` and `calibration` inside a joint, so the element is silently ignored. Joint damping and friction go in `<dynamics damping friction/>`. `<axis>` has only `xyz`. Code: [joint.cpp][urdfdom-joint-h]. |
| URDF-V03 | 2.7, 2.9 | course claim | "robot_state_publisher publishes the TF frames of all the links into the topic `/tf`" | Fixed joints are sent once on `/tf_static` (StaticTransformBroadcaster, transient local); only movable joints go on `/tf`, computed from `/joint_states`. Code: [robot_state_publisher.cpp][rsp-h]. |
| URDF-V04 | 2.11 | course claim | "Materials will not affect DAE or OBJ because they already have their own materials" | In RViz2 a `<material>` inside the `<visual>` **replaces** the materials of every submesh; a mesh keeps its own colors only when the visual has no `<material>` (or the submesh has none). Same in Humble and Jazzy. Code: [robot_link.cpp][rviz-link-h]. |
| URDF-V05 | 2.12 | course claim | "In URDFs without simulation, the `effort` and `velocity` elements are irrelevant" | `effort` and `velocity` are required attributes of `<limit>`: without them the parser logs "joint limit: no effort / no velocity" and the joint fails to parse. They are also read by any consumer of joint limits (controllers, planners), not only by simulators. Code: [joint.cpp][urdfdom-joint-h]. |
| URDF-V06 | 2.12 | course claim | "The joint that has the `mimic` element will use the same limits as the joint it is mimicking" | joint_state_publisher gives a mimic joint no slider and publishes `multiplier · parent + offset` without clamping it to any limit (`multiplier` defaults to 1, `offset` to 0). The mimic joint still needs its own `<limit>` only because revolute and prismatic joints require one. Code: [joint_state_publisher.py][jsp-h], [joint.cpp][urdfdom-joint-h]. |
| URDF-V07 | 3.2, 7.5 | course mistake | Materials used but never defined (`box_bot_blue`, `black`, `white`, `green`) | An undefined material name only logs "link '…' material '…' undefined" and the visual gets no color (RViz default). Define each named material at robot level (`<material name><color rgba/></material>`) or inline with a color. Code: [model.cpp][urdfdom-model-h]. |
| URDF-V08 | 4.5 | course mistake | "Both collision and visual have a unique name" | The XML shown has no `name` attribute on either element. Names are optional (`<visual name="…">`, `<collision name="…">`); add them when a plugin needs the collision name. Code: [link.cpp][urdfdom-link-h]. |
| URDF-V09 | 7.6 | course mistake | Macro `params="wheel_name"` called as `<xacro:wheel wheel_link_name="…"/>`, and the body uses `${wheel_length}`, which no property defines | xacro stops with `Invalid parameter "wheel_link_name"`, then `Undefined parameters [wheel_name]`, and `name 'wheel_length' is not defined`. The exercise solution (7.5.1) uses matching names (`wheel_name`, `wheel_width`). Code: [xacro][xacro]. |
| URDF-V10 | 7.7 | course mistake | `<xacro:arg name="indoor_robot" default="true"/>` followed by `<xacro:if value="${indoor_robot}">` | An arg is read with `$(arg indoor_robot)`; `${indoor_robot}` needs a property of that name (the course's second variant defines `<xacro:property name="indoor_robot" value="true"/>`, which works). Code: [xacro substitution args][xacro-subst]. |
| URDF-V11 | 7.9 | course mistake | `<xacro:property name="robot_name" value="$(arg robot_name)"/>` with no `<xacro:arg name="robot_name">` | It works only when every caller passes `robot_name:=…`. The single-robot launch of 7.4 (`xacro.process_doc(doc)` without mappings) then fails with "Undefined substitution argument". Declare `<xacro:arg name="robot_name" default="…"/>`. A default of `""` produces frame ids such as `/odom`, which tf2 rejects (frame ids cannot start with `/`) [verify]. Code: [xacro][xacro]. |
| URDF-V12 | 8.4 | outdated install | `sudo pip install onshape-to-robot` | Never `sudo pip`. Official: `pip install onshape-to-robot` in a virtual environment; on Ubuntu 24.04 (Jazzy) the system pip refuses with "externally-managed-environment" (PEP 668), so use a venv or `pipx install onshape-to-robot` (as the course does in 8.7). OpenSCAD and MeshLab are needed only for optional processors (`scad`, `simplify_stls`). Sources: [getting started][o2r-start], [processors][o2r-scad], [PEP 668][pep668]. |
| URDF-V13 | 8.8 | course mistake | Final `config.json` with no comma after `"assemblyName": "quadruped_v1"` | Invalid JSON: the export stops. Add the comma. (Comments are allowed in this file; missing commas are not.) Source: [config docs][o2r-config]. |

## Full table
| # | Section | Statement | Humble | Jazzy | Lyrical | Action | Source | Confidence |
|---|---|---|---|---|---|---|---|---|
| URDF-V01 | 4.4 | Box inertia formula for `izz` | ✗ `m(x²+y²)/12` | same | same | **fix** | [docs-phys-h] | High |
| URDF-V02 | 3.2–7.9 | `<joint_properties>`, `<axis rpy>` | ✗ ignored | same | same | **fix** | [urdfdom-joint-h] | High |
| URDF-V03 | 2.7 | RSP: all TF on `/tf` | ✗ fixed → `/tf_static` | same | same | **fix** | [rsp-h] | High |
| URDF-V04 | 2.11 | URDF material does not affect DAE/OBJ | ✗ it overrides them | same | same | **fix** | [rviz-link-h] | High |
| URDF-V05 | 2.12 | effort/velocity irrelevant without sim | ✗ required by the parser | same | same | **fix** | [urdfdom-joint-h] | High |
| URDF-V06 | 2.12 | mimic joint uses the mimicked limits | ✗ not clamped, no slider | same | same | **fix** | [jsp-h] | High |
| URDF-V07 | 3.2, 7.5 | Undefined material names | ✗ warning, no color | same | same | **fix** | [urdfdom-model-h] | High |
| URDF-V08 | 4.5 | "visual and collision have a unique name" | ✗ no names in the XML | same | same | **fix** | [urdfdom-link-h] | High |
| URDF-V09 | 7.6 | Macro call with wrong parameter, undefined property | ✗ xacro error | same | same | **fix** | [xacro] | High |
| URDF-V10 | 7.7 | `${arg}` instead of `$(arg …)` | ✗ NameError | same | same | **fix** | [xacro-subst] | High |
| URDF-V11 | 7.9 | `$(arg robot_name)` without `<xacro:arg>` | ✗ fails without the arg | same | same | **fix** | [xacro] | High (tf2 part `[verify]`) |
| URDF-V12 | 8.4 | `sudo pip install onshape-to-robot` | ✗ venv/pipx | ✗ PEP 668 blocks it | same | **fix** | [o2r-start], [pep668] | High |
| URDF-V13 | 8.8 | `config.json` missing comma | ✗ invalid JSON | same | same | **fix** | [o2r-config] | High |
| URDF-V14 | 2.4 | "Three basic geometries: box, cylinder, sphere" | + `mesh` (2.11) | same | + `capsule` (needs `<robot version="1.1">`) | annotate | [urdfdom-link-h], [urdfdom-link-l] | High |
| URDF-V15 | 2.4 | Units: meters, radians, kilograms | ✓ | ✓ | ✓ | keep | [docs-urdf-h] | High |
| URDF-V16 | 2.5, 2.7 | RSP publishes `/robot_description`; RViz RobotModel reads it with Transient Local | ✓ (`QoS(1).transient_local()`, RViz default the same) | ✓ | ✓ + `use_robot_description_topic` | annotate | [rsp-h], [rviz-model-h], [rsp-l] | High |
| URDF-V17 | 2.5–8.9 | `'robot_description': Command(['xacro ', path])` (no ParameterValue) | works; the official tutorials wrap it in `ParameterValue(…, value_type=str)` so launch never parses it as YAML | same | same | annotate | [docs-xacro-h] | Medium |
| URDF-V18 | 2.5 | `xacro` also processes a plain `.urdf` | ✓ (one Command for both) | ✓ | ✓ | keep | [xacro] | High |
| URDF-V19 | 2.6, 2.9 | Joint origin in the parent frame; rotation axis in the child (joint) frame | ✓ | ✓ | ✓ | keep | [docs-urdf-h] | High |
| URDF-V20 | 2.7 | One link only → no TF; a joint is needed to see transforms | ✓ (no joint, no transform; RViz still draws the root link as Fixed Frame) | ✓ | ✓ | keep | [rsp-h] | High |
| URDF-V21 | 2.8 | `floating` and `planar` "do not work properly in ROS 2" | annotate: urdfdom parses both; kdl_parser turns `planar` into a fixed joint (warning) and RSP skips `floating` joints (no TF); joint_state_publisher gives them no slider. A moving base is published as `odom → base_link` by another node (ros2-core note `core-tf-broadcaster`) | same | same | annotate | [kdl-h], [rsp-h], [jsp-h] | High |
| URDF-V22 | 2.8 | Link to a forum post on emulating planar/floating joints | dropped: not an official reference; use chains of prismatic + continuous joints | — | — | annotate | — | — |
| URDF-V23 | 2.9 | joint_state_publisher_gui publishes `/joint_states`; RSP turns them into TF | ✓ | ✓ | ✓ | keep | [jsp-h], [rsp-h] | High |
| URDF-V24 | 2.10 | Material names are free; defined at robot level, referenced in `<visual>` | ✓ (texture via `<texture filename>` too) | ✓ | ✓ | keep | [urdfdom-link-h] | High |
| URDF-V25 | 2.11 | Mesh formats `.dae`, `.stl`, `.obj`; `package://` URI; `scale` | ✓ | ✓ | ✓ | keep | [docs-urdf-h] | Medium |
| URDF-V26 | 2.11 | "scale all the models by 10; therefore 1/10 = 0.1" | wording: the mesh is drawn at one tenth of its size (`scale="0.1 0.1 0.1"`) | — | — | annotate | — | High |
| URDF-V27 | 2.12 | `<limit>` attributes and defaults (lower/upper 0; effort, velocity required) | ✓ | ✓ | ✓ | keep | [urdfdom-joint-h] | High |
| URDF-V28 | 2.12 | `check_urdf` error text from an older urdfdom path | message unchanged in Humble: "Joint [x] is of type REVOLUTE but it does not specify limits"; drop the build path | same | same | annotate | [urdfdom-joint-h] | High |
| URDF-V29 | 2.12 | `<dynamics>` (damping, friction, defaults 0) and `<safety_controller>` (soft limits and k_position default 0, k_velocity required) | ✓ | ✓ | ✓ | keep | [urdfdom-joint-h] | High |
| URDF-V30 | 2.12 | `<calibration rising falling reference_position>` | the parser reads only `rising` and `falling`; `reference_position` is ignored | same | same | annotate | [urdfdom-joint-h] | High |
| URDF-V31 | 2.12 | Reference link to a third-party URDF XML page | replaced by the parser code and the official URDF tutorials | — | — | annotate | [docs-urdf-h] | — |
| URDF-V32 | 3.2 | Empty link (`<link name="base_link"/>`) gives a frame only | ✓; also avoids kdl_parser's warning "the root link … has an inertia … KDL does not support a root link with an inertia" | ✓ | ✓ | keep | [kdl-h] | High |
| URDF-V33 | 4.4 | Every simulated link needs `<inertial>`; near-zero inertia can make the model unstable | ✓ (the official tutorial says the same for real-time controllers) | ✓ | ✓ | keep | [docs-phys-h] | High |
| URDF-V34 | 4.4 | Cylinder and sphere inertia formulas | ✓ (`ixx = iyy = m(3r²+l²)/12`, `izz = mr²/2`; sphere `2mr²/5`) | ✓ | ✓ | keep | [docs-phys-h] | High |
| URDF-V35 | 4.5 | Inertia calculator from a course package | removed (platform repository); the notes give the formulas and xacro macros that compute them | — | — | annotate | — | — |
| URDF-V36 | 4.5 | `<inertial>`, `<collision>` and `<visual>` each take their own `<origin>` | ✓ | ✓ | ✓ | keep | [urdfdom-link-h] | High |
| URDF-V37 | 7.2 | A xacro file declares `xmlns:xacro="http://www.ros.org/wiki/xacro"`; `.xacro` / `.urdf.xacro` extensions | ✓ | ✓ | ✓ | keep | [docs-xacro-h] | High |
| URDF-V38 | 7.3 | `xacro in.xacro > out.urdf` | ✓ (also `-o out.urdf`) | ✓ | ✓ | keep | [xacro-cli] | High |
| URDF-V39 | 7.4 | `doc = xacro.parse(open(f)); xacro.process_doc(doc); doc.toxml()` | valid API; simpler `xacro.process_file(path).toxml()`, or `Command(['xacro ', path, ' name:=value'])` to pass args | same | same | annotate | [xacro] | High |
| URDF-V40 | 7.5 | "Properties can be declared anywhere" | annotate: anywhere **before** the first `${…}` that uses them (document order); lazy evaluation lets a property's value refer to a later one only if it is used after both | same | same | annotate | [xacro] | High |
| URDF-V41 | 7.6 | Macro params separated by spaces; defaults `name:=value` | ✓ | ✓ | ✓ | keep | [xacro] | High |
| URDF-V42 | 7.7 | `<xacro:if>` / `<xacro:unless>` with `value` | ✓ | ✓ | ✓ | keep | [xacro] | High |
| URDF-V43 | 7.8 | `<xacro:include filename="$(find pkg)/urdf/x.xacro"/>`; included file wrapped in `<robot xmlns:xacro>` | ✓ (`$(find)` needs the package built, sourced and its `urdf/` installed) | ✓ | ✓ | keep | [xacro] | High |
| URDF-V44 | 7.8 | Stray text "Exercise" inside the solution XML | export artefact: removed | — | — | annotate | — | High |
| URDF-V45 | 8.5 | Onshape API keys as `ONSHAPE_API`, `ONSHAPE_ACCESS_KEY`, `ONSHAPE_SECRET_KEY` (keys page) | ✓ (also a `.env` file, or OAuth2) | ✓ | ✓ | keep | [o2r-start] | High |
| URDF-V46 | 8.6, 8.8 | `config.json` keys `documentId`, `outputFormat`, `assemblyName`, `packageName`, `robotName` | onshape-to-robot ≥ 1.0 (current 1.8.3) uses snake_case (`url` required, `output_format`, `assembly_name`, `package_name`, `robot_name`); camelCase is still accepted | same | same | annotate | [o2r-config] | High |
| URDF-V47 | 8.8 | "Add the format shebang `<?xml version="1.0"?>`" | wording: it is the XML declaration; check whether the current exporter already writes it [verify] | — | — | annotate | [o2r-repo] | Medium |
| URDF-V48 | 8.8 | Inertia exported from the CAD materials | ✓ | ✓ | ✓ | keep | [o2r-repo] | Medium |
| URDF-V49 | 2.5–8.9 | `use_sim_time: True` in RViz/RSP launch files without a simulator | only meaningful when a simulator publishes `/clock`; for RViz-only work keep the default `false` (time stays 0 without `/clock`) [verify] | same | same | annotate | ros2-core note `core-time-timers` | Medium |

## Open `[verify]` (Phase 5 or a real machine)
- URDF-V11: tf2 rejecting frame ids that start with `/` when `robot_name` is empty.
- URDF-V47: whether onshape-to-robot 1.8.3 writes the XML declaration itself.
- URDF-V49: RViz and RSP behaviour with `use_sim_time: True` and no `/clock`.

## Sources
[urdfdom-h]: https://github.com/ros/urdfdom/tree/humble
[urdfdom-j]: https://github.com/ros/urdfdom/tree/jazzy
[urdfdom-joint-h]: https://github.com/ros/urdfdom/blob/humble/urdf_parser/src/joint.cpp
[urdfdom-link-h]: https://github.com/ros/urdfdom/blob/humble/urdf_parser/src/link.cpp
[urdfdom-model-h]: https://github.com/ros/urdfdom/blob/humble/urdf_parser/src/model.cpp
[urdfdom-link-l]: https://github.com/ros/urdfdom/blob/lyrical/urdf_parser/src/link.cpp
[kdl-h]: https://github.com/ros/kdl_parser/blob/humble/kdl_parser/src/kdl_parser.cpp
[rsp-h]: https://github.com/ros/robot_state_publisher/blob/humble/src/robot_state_publisher.cpp
[rsp-l]: https://github.com/ros/robot_state_publisher/blob/lyrical/src/robot_state_publisher.cpp
[jsp-h]: https://github.com/ros/joint_state_publisher/blob/humble/joint_state_publisher/joint_state_publisher/joint_state_publisher.py
[xacro]: https://github.com/ros/xacro/blob/ros2/xacro/__init__.py
[xacro-subst]: https://github.com/ros/xacro/blob/ros2/xacro/substitution_args.py
[xacro-cli]: https://github.com/ros/xacro/blob/ros2/xacro/cli.py
[rviz-link-h]: https://github.com/ros2/rviz/blob/humble/rviz_default_plugins/src/rviz_default_plugins/robot/robot_link.cpp
[rviz-model-h]: https://github.com/ros2/rviz/blob/humble/rviz_default_plugins/src/rviz_default_plugins/displays/robot_model/robot_model_display.cpp
[docs-urdf-h]: https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/URDF-Main.html
[docs-phys-h]: https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/Adding-Physical-and-Collision-Properties-to-a-URDF-Model.html
[docs-xacro-h]: https://docs.ros.org/en/humble/Tutorials/Intermediate/URDF/Using-Xacro-to-Clean-Up-a-URDF-File.html
[o2r-repo]: https://github.com/Rhoban/onshape-to-robot
[o2r-start]: https://onshape-to-robot.readthedocs.io/en/latest/getting_started.html
[o2r-config]: https://onshape-to-robot.readthedocs.io/en/latest/config.html
[o2r-scad]: https://onshape-to-robot.readthedocs.io/en/latest/processor_scad.html
[pep668]: https://peps.python.org/pep-0668/
[rep2000]: https://www.ros.org/reps/rep-2000.html
