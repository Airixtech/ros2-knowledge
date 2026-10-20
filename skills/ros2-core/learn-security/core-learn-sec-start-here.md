---
id: core-learn-sec-start-here
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Security course: learning path and prerequisites"
domain: core
area: learn-security
distro: humble
tested: false
audience: students
order: 1
summary: "Map of the ROS 2 security course (SROS2, TurtleBot3 simulation): units 2–3, workspaces, prerequisites, technical notes behind each step."
tags: [course, security, SROS2, TurtleBot3, learning path, students, keystore, enclave]
see: ["[[core-sros2-overview]]", "[[core-learn-sec-unit2-tb3]]", "[[core-learn-sec-unit3-key-materials]]", "[[core-learn-sec-unit3-cmd-listener]]", "[[core-learn-start-here]]"]
requires: []
version_notes: []
---
# Security course: learning path and prerequisites

**TL;DR** The course teaches the ROS 2 security layer (SROS2 on top of DDS-Security) on a simulated **TurtleBot3**. The main problem it solves: confirm the identity of every ROS node and give each one access only to the topics it needs. Read the technical note first, then do the unit.

## What you learn
- Basic security concepts: authentication, cryptography, access control ([[core-sros2-overview]]).
- Create the security files for a TurtleBot3 simulation; launch it and drive it with teleop with security enabled.
- What a keystore contains, how enclaves are generated, how to read and validate a certificate.
- How to add a new custom node to the `turtlebot_keystore`.

Prerequisite: ROS 2 basics (nodes, topics, packages, launch): [[core-learn-start-here]].

## Units
| Unit | Time | Topic | Technical notes | Exercises |
|---|---|---|---|---|
| 2 | 1.5 h | Activate security: keystore, enclaves, secured Gazebo + teleop | [[core-sros2-overview]], [[core-sros2-keystore]], [[core-sros2-policy]], [[core-sros2-generate-artifacts]], [[core-sros2-env-vars]] | [[core-learn-sec-unit2-tb3]] |
| 3 | 2 h | Key materials (public, private, enclaves, governance, permissions) and a secured `cmd_vel` listener | [[core-sros2-openssl-inspect]], [[core-sros2-enclaves]], [[core-sros2-governance]], [[core-sros2-permissions]] | [[core-learn-sec-unit3-key-materials]], [[core-learn-sec-unit3-cmd-listener]] |

## Environment
| Workspace | Content |
|---|---|
| `~/security_ws` | the keystore `turtlebot_keystore` |
| `~/ros2_ws/src` | the policy repository `turtlebot3_security_policy` (course project, link given in the course) and your packages |
| simulation workspace | the TurtleBot3 Gazebo simulation, as the course provides it (`source /home/simulations/ros2_sims_ws/install/setup.bash`); on your own Humble machine the binary packages `turtlebot3_gazebo` and `turtlebot3_teleop` do the same |

Every shell that runs a secured node needs the security variables ([[core-sros2-env-vars]]). The course uses three shells: simulation, teleop, and a third one to inspect or run your node.

## Pitfalls
- The course runs on Humble with Gazebo Classic 11. On Jazzy the TurtleBot3 simulation uses the new Gazebo and the teleop publishes `TwistStamped`: the policy and the listener need changes ([[core-learn-sec-unit2-tb3]]).
- Never commit or share the keystore's `private/` folder, even for a course ([[core-sros2-keystore]]).
