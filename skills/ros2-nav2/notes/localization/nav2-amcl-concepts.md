---
id: nav2-amcl-concepts
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "AMCL: particle filter and the map -> odom transform"
domain: nav2
area: localization
distro: humble
tested: false
audience: dev
summary: "AMCL (adaptive Monte Carlo localization): particles, weights, resampling; a robot is localized when map -> odom is published."
tags: [AMCL, nav2_amcl, particle filter, KLD sampling, map, odom, base_link, localization, pose]
see: ["[[nav2-amcl-launch]]", "[[nav2-amcl-params-filter]]", "[[nav2-amcl-params-models]]", "[[core-tf-basics]]"]
requires: [ros2-core]
version_notes: []
---
# AMCL: particle filter and the map -> odom transform

**TL;DR** AMCL estimates the robot's (x, y, θ) on a known map with a particle filter and publishes the **`map → odom`** transform. That transform is what "the robot is localized" means in ROS.

## What AMCL is
AMCL (Adaptive Monte Carlo Localization, `nav2_amcl`) is a robust probabilistic localization system for a robot moving in 2D. It implements the adaptive (KLD-sampling) Monte Carlo localization approach described by Dieter Fox: a particle filter tracks the robot's pose against a known map (served by `map_server`, see [[nav2-map-server]]).

## A ROS robot is localized when somebody publishes `map → odom`
- The odometry driver publishes `odom → base_link` (or `base_footprint`): smooth, but drifting.
- AMCL publishes `map → odom`, so the `odom` frame knows its position relative to `map`. Because `base_link` hangs from `odom`, the robot's position on the map is known.
- When everything is correct, AMCL is the node that publishes that transform ([[core-tf-basics]]).

## The pose and the particles
For 2D localization the robot is localized when you know, in the `map` frame:
- `x`: the x position of the robot,
- `y`: the y position of the robot,
- `θ`: the orientation (yaw) of the robot.

AMCL uses the static map and computes (x, y, θ) with particles:
1. Each particle is a pose hypothesis with its own coordinates, orientation and a **weight**.
2. The weight measures how well the current laser scan matches the map when seen from that particle's pose (the likelihood of the measurement). The larger the weight, the better that particle explains the robot's pose.
3. Particles are re-sampled as the robot moves and new sensor data arrives: low-weight particles perish and high-weight ones survive (and are copied).
4. After many iterations the particles converge, and their distribution approximates the robot's position and orientation.

To localize accurately you need a well-configured AMCL node: [[nav2-amcl-params-filter]] (particles, update thresholds) and [[nav2-amcl-params-models]] (laser and odometry models).

## Topics and services (Humble)
| Name | Type | Use |
|---|---|---|
| `initialpose` (sub) | `geometry_msgs/PoseWithCovarianceStamped` | initial pose from RViz or a node |
| `amcl_pose` (pub) | `geometry_msgs/PoseWithCovarianceStamped` | estimated pose |
| `particle_cloud` (pub) | `nav2_msgs/ParticleCloud` | particles, for RViz |
| `reinitialize_global_localization` (srv) | `std_srvs/Empty` | spread particles over the whole map ([[nav2-global-localization]]) |
| `request_nomotion_update` (srv) | `std_srvs/Empty` | force a filter update without motion |

## Pitfalls
- AMCL does not publish `map → odom` until it gets an initial pose ([[nav2-initial-pose-config]]).
- Two nodes publishing `map → odom` (AMCL and a SLAM node still running) → the robot jumps in RViz.
- Bad odometry cannot be fixed by AMCL tuning: check `odom → base_link` first.
