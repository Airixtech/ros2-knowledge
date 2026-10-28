---
id: moveit-setup-assistant-model
type: reference
owner: equipo-ros2
updated: 2026-10-28
review_by: 2027-04-26
source: manual
confidentiality: internal
title: "MoveIt Setup Assistant (1/2): launch, load the xacro, self-collisions, virtual joint, planning groups, poses, end effector"
domain: moveit
area: config
distro: humble
tested: false
audience: dev
summary: "moveit_setup_assistant setup_assistant.launch.py: load ur_moveit.urdf.xacro, self-collision matrix, virtual joint fixed_base, planning groups ur_manipulator and gripper, home pose, end effector hand_ee."
tags: [MoveIt Setup Assistant, moveit_setup_assistant, setup_assistant.launch.py, self-collisions, collision matrix, Sampling Density, virtual joint, fixed_base, planning group, ur_manipulator, gripper, KDLKinematicsPlugin, kinematic chain, robot poses, home, end effector, hand_ee, wrist_3_link, UR3e, Robotiq 85]
see: ["[[moveit-setup-assistant-controllers]]", "[[moveit-architecture]]", "[[moveit-kinematics-plugins]]", "[[urdf-overview]]", "[[core-xacro]]"]
requires: [ros2-core, ros2-urdf]
version_notes:
  - "humble: button and field labels ('Create New MoveIt Configuration Package', 'Sampling Density', 'Min. collisions for \"always\"-colliding pairs', 'Generate Collision Matrix', 'Add Kin. Chain') as in the Humble sources — https://github.com/moveit/moveit2/blob/humble/moveit_setup_assistant/moveit_setup_srdf_plugins/src/default_collisions_widget.cpp (MOVEIT-V22)"
  - "humble: disabled-collision reasons Adjacent, Always, Never, Default, User; the course says adjacent links 'always collide' — https://github.com/moveit/moveit2/blob/humble/moveit_setup_assistant/moveit_setup_srdf_plugins/src/compute_default_collisions.cpp (MOVEIT-V12)"
  - "course: the SRDF home values (0, -2.5, 1.5, -1.5, -1.55, 0) differ from the joint target the C++ programs call home (0, -2.3562, 1.5708, -1.5708, -1.5708, 0) (MOVEIT-V47)"
---
# MoveIt Setup Assistant (1/2): from the robot description to groups and poses

**TL;DR** The Setup Assistant takes a URDF or xacro of the robot and writes a MoveIt configuration package. Part 1: load the description, generate the self-collision matrix, attach the robot to the world with a virtual joint, define the planning groups (arm with a kinematics plugin, gripper), named poses and the end effector. Part 2 (controllers, package generation): [[moveit-setup-assistant-controllers]].

## Prepare and launch
The Setup Assistant needs the robot description packages in your workspace. The course copies three packages of its simulation workspace (UR3e arm, Robotiq 85 gripper, sensors) into `~/ros2_ws/src`:
```bash
# from the workspace that holds the robot's description packages
cp -r <sim_ws>/src/universal_robot_ros2/Universal_Robots_ROS2_Description/ ~/ros2_ws/src/
cp -r <sim_ws>/src/universal_robot_ros2/robotiq_85_gripper/ ~/ros2_ws/src/
cp -r <sim_ws>/src/universal_robot_ros2/robotnik_sensors/ ~/ros2_ws/src/
cd ~/ros2_ws
colcon build
source install/setup.bash
ros2 launch moveit_setup_assistant setup_assistant.launch.py
```

## Steps (tabs of the Setup Assistant)
1. **Start**: click **Create New MoveIt Configuration Package**, **Browse** to `~/ros2_ws/src/Universal_Robots_ROS2_Description/urdf/ur_moveit.urdf.xacro` (the course's file), click **Load Files**: the robot appears.
2. **Self-Collisions**: drag **Sampling Density** to the maximum, set **Min. collisions for "always"-colliding pairs** between 95 % and 99 %, click **Generate Collision Matrix**. The assistant lists the link pairs that collision checking can skip, each with a reason: **Adjacent** (connected by a joint), **Always** (in collision in at least the chosen share of the sampled states), **Never** (never in collision while sampling), **Default** (in collision in the default pose) or **User** (MOVEIT-V12; the course says adjacent links "always collide").
3. **Virtual Joints**: a virtual joint attaches the robot to the world, so the arm does not float in space. Name `fixed_base`, child link `base_link`, parent frame `world`, type `fixed`.
4. **Planning Groups**: **Add Group** `ur_manipulator` with kinematic solver `KDLKinematicsPlugin` ([[moveit-kinematics-plugins]]); **Add Kin. Chain**: select the **Base Link** and the **Tip Link** of the arm (without the gripper) in the Robot Links list, **Save**. A planning group is the set of joints MoveIt plans for, plus the plugin that solves it. Add a second group `gripper` with the gripper joints (the course lists them only in a figure).
5. **Robot Poses**: named joint values of a group that you can set as goals with two clicks, useful for poses the robot visits often. Arm: `home`; gripper: `open` and `close` (their values are only in figures of the course). A missed pose can be added later in the SRDF ([[moveit-setup-assistant-controllers]]), where the course's `home` is `shoulder_pan_joint` 0, `shoulder_lift_joint` −2.5, `elbow_joint` 1.5, `wrist_1_joint` −1.5, `wrist_2_joint` −1.55, `wrist_3_joint` 0. The C++ programs use a slightly different joint target they also call home: (0, −2.3562, 1.5708, −1.5708, −1.5708, 0) (MOVEIT-V47).
6. **End Effectors**: name `hand_ee`, End Effector Group `gripper`, Parent Link `wrist_3_link` (the last arm link, where the gripper is attached), Parent Group `ur_manipulator`.

## Pitfalls
- Load the **xacro** the robot really uses (here a MoveIt variant `ur_moveit.urdf.xacro` that includes the gripper); a description without the gripper gives no `gripper` group.
- The tip link of the arm chain decides the end-effector link that pose goals move ([[moveit-cpp-pose-goal]]).
- If the Setup Assistant window appears black, double-click its title bar so it redraws (the course's tip for its graphical tools window).
