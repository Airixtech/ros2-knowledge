---
id: core-learn-inter-start-here
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "Intermediate course: start here"
domain: core
area: learn-intermediate
distro: humble
tested: false
audience: students
order: 1
summary: "Map of the intermediate ROS 2 course (MP-400 simulation): units 2–10, their exercises and the technical notes behind them."
tags: [course, intermediate, learning path, MP-400, Neobotix, students, simulation workspace]
see: ["[[core-learn-start-here]]", "[[core-learn-inter-unit2-build]]", "[[core-learn-inter-project]]", "[[core-pkg-ament-python]]"]
requires: []
version_notes: []
---
# Intermediate course: start here

**TL;DR** The intermediate course extends the basics course ([[core-learn-start-here]]): build system, launch files in three formats, parameters, executors and callback groups, QoS, DDS and managed nodes, then a final project. Its exercises run on a simulated Neobotix **MP-400**. Read the technical note first, then do the unit.

## Environment
- Your workspace is `~/ros2_ws` (packages in `src/`, build from the root).
- The simulation lives in a separate workspace. Source it in the shells that need the robot model (RViz RobotModel display): `source /home/simulations/ros2_sims_ws/install/setup.bash`.
- When a unit says so, restart the simulation so the robot is back at its start pose; `ros2 service call /reset_world std_srvs/srv/Empty "{}"` resets the world.

## Units
| Unit | Topic | Technical notes | Exercises |
|---|---|---|---|
| 2 | Python build system | [[core-pkg-ament-python]], [[core-pkg-setup-py-fields]], [[core-symlink-install]], [[core-pkg-ament-index]], [[core-launch-testing]] | [[core-learn-inter-unit2-build]] |
| 3 | Advanced launch files | [[core-launch-args-include]], [[core-launch-substitutions]], [[core-launch-node-arguments]] | [[core-learn-inter-unit3-launch]] |
| 4 | XML and YAML launch | [[core-launch-xml-yaml]] | [[core-learn-inter-unit4-launch-formats]] |
| 5 | Node parameters | [[core-param-api]], [[core-param-yaml-cli]] | [[core-learn-inter-unit5-params]] |
| 6 | Executors and callback groups | [[core-exec-model]], [[core-exec-callback-groups]] | [[core-learn-inter-unit6-blocking]], [[core-learn-inter-unit6-executor]], [[core-learn-inter-unit6-exercises]], [[core-learn-inter-unit6-groups-demo]] |
| 7 | QoS | [[core-qos-policies]], [[core-qos-events]], [[core-qos-durability]], [[core-qos-deadline]], [[core-qos-lifespan]], [[core-qos-liveliness]] | [[core-learn-inter-unit7-8-qos-dds]]; programs: [[core-qos-events-demo]], [[core-qos-durability-demo]], [[core-qos-deadline-demo]], [[core-qos-lifespan-demo]], [[core-qos-liveliness-demo]] |
| 8 | DDS | [[core-dds-overview]], [[core-rmw-implementations]], [[core-dds-loss-test]], [[core-ros2-daemon]] | [[core-learn-inter-unit7-8-qos-dds]] |
| 9 | Managed nodes | [[core-lifecycle-concepts]], `cpp-lifecycle-node` (ros2-cpp skill), [[core-lifecycle-services-cli]], `cpp-lifecycle-manager-client` (ros2-cpp skill) | [[core-learn-inter-unit9-lifecycle]] |
| 10 | Final project | [[core-recipe-laser-circles]] | [[core-learn-inter-project]] |

## Unit 2 in one paragraph
Unit 2 recaps the basics first (packages, `ros2 pkg create`, `colcon build`, sourcing: [[core-pkg-workspace]], [[core-colcon-build]]); skip that part if you know it. The new material is how the Python build system really installs files.

## Pitfalls
- Sourcing only the simulation workspace, or only yours: source `/opt/ros/humble`, then the simulation workspace, then `~/ros2_ws/install/setup.bash`.
- Exercises that move the robot fast can make the simulation unstable: restart it.
