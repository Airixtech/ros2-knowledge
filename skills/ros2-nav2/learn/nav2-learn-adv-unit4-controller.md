---
id: nav2-learn-adv-unit4-controller
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Advanced Unit 4 exercise: critics with an unmapped obstacle"
domain: nav2
area: learn
distro: humble
tested: false
audience: students
summary: "Advanced Unit 4: controller server and exercise E1.1, global costmap without obstacle_layer and the PathAlign critic."
tags: [course, students, advanced unit 4, controller_server, exercise E1.1, PathAlign, BaseObstacle, construction_cone, critics]
see: ["[[nav2-dwb-critic-tuning]]", "[[nav2-goal-progress-checkers]]", "[[nav2-dwb-generators-critics]]", "[[nav2-rpp-controller-params]]", "[[nav2-learn-adv-start-here]]"]
requires: [ros2-core]
version_notes: []
---
# Advanced Unit 4 exercise: critics with an unmapped obstacle

**TL;DR** The **Controller Server** manages path execution by generating velocity commands for the robot, selecting and running controller plugins. Unit 4 looks at its configuration ([[nav2-goal-progress-checkers]]), its controllers ([[nav2-dwb-generators-critics]], [[nav2-rpp-controller-params]]) and how critics change the behavior.

## Exercise E1.1
See the difference between using one critic or another (the course numbers it E1.1 and E5.1).
1. Configure the global costmap without the `obstacle_layer` plugin.
2. Recompile, source and relaunch; give an initial pose in RViz.
3. Spawn the cone if you do not have it yet (source the simulation workspace of the course first):
   ```bash
   ros2 run gazebo_ros spawn_entity.py -entity construction_cone -database construction_cone -x -1
   ```
4. Put the robot about 1 m in front of the cone and send a goal on the other side.
5. Observe; then remove the `PathAlign` critic, recompile, relaunch and repeat. What happens?

Steps, explanation and expected results: [[nav2-dwb-critic-tuning]]. [changed in Jazzy: spawn with `ros2 run ros_gz_sim create`, NAV2-V28]

## Conclusions
You explored the controller server, how it manages robot motion, and how critics influence the way the controller evaluates and selects trajectories.
