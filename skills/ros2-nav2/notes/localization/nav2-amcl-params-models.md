---
id: nav2-amcl-params-models
title: "AMCL laser and odometry model parameters"
domain: nav2
area: localization
distro: humble
tested: false
audience: dev
summary: "AMCL laser model (likelihood_field/beam, z_hit, z_rand, sigma_hit, max_beams, ranges) and odometry model (robot_model_type, alpha1-5, frames, tf_broadcast)."
tags: [AMCL, laser_model_type, likelihood_field, z_hit, z_rand, sigma_hit, max_beams, robot_model_type, alpha1, base_frame_id, tf_broadcast]
see: ["[[nav2-amcl-params-filter]]", "[[nav2-amcl-launch]]", "[[nav2-amcl-concepts]]"]
requires: [ros2-core]
version_notes:
  - "humble: robot_model_type default nav2_amcl::DifferentialMotionModel; 'differential'/'omnidirectional' strings are pre-Humble (motion models became plugins) — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/galactic/Galactic.md (NAV2-V08)"
---
# AMCL laser and odometry model parameters

**TL;DR** The laser model says how a scan is compared with the map (`likelihood_field` is the default and the usual choice); the odometry model says how noisy the robot's motion is (`alpha1`–`alpha4` for a differential robot).

## Laser model (Humble defaults)
Whichever mixture weights are in use should sum to 1. The `beam` model uses all four (`z_hit`, `z_short`, `z_max`, `z_rand`); the `likelihood_field` model uses only `z_hit` and `z_rand`.

| Parameter | Default | Meaning |
|---|---|---|
| `laser_model_type` | `"likelihood_field"` | `beam`, `likelihood_field`, or `likelihood_field_prob` (likelihood_field plus the beam-skip feature, if enabled) |
| `laser_min_range` | -1.0 | minimum scan range considered; -1.0 = use the laser's reported minimum |
| `laser_max_range` | 100.0 | maximum scan range considered; -1.0 = use the laser's reported maximum |
| `max_beams` | 60 | how many evenly-spaced beams of each scan are used when updating the filter |
| `z_hit` | 0.5 | mixture weight of the z_hit part of the model |
| `z_short` | 0.05 | mixture weight of the z_short part |
| `z_max` | 0.05 | mixture weight of the z_max part |
| `z_rand` | 0.5 | mixture weight of the z_rand part |
| `sigma_hit` | 0.2 m | standard deviation of the Gaussian model used in z_hit |
| `lambda_short` | 0.1 | exponential decay parameter of z_short |
| `laser_likelihood_max_dist` | 2.0 m | maximum distance to do obstacle inflation on the map, for the likelihood_field model |
| `do_beamskip`, `beam_skip_distance`, `beam_skip_threshold`, `beam_skip_error_threshold` | false, 0.5, 0.3, 0.9 | ignore beams that most particles disagree with (only `likelihood_field_prob`) |

## Odometry model (Humble defaults)
| Parameter | Default | Meaning |
|---|---|---|
| `robot_model_type` | `"nav2_amcl::DifferentialMotionModel"` | motion model plugin; `nav2_amcl::OmniMotionModel` for omnidirectional robots |
| `alpha1` | 0.2 | expected noise in odometry's rotation estimate from the rotational component of the motion |
| `alpha2` | 0.2 | expected noise in odometry's rotation estimate from the translational component |
| `alpha3` | 0.2 | expected noise in odometry's translation estimate from the translational component |
| `alpha4` | 0.2 | expected noise in odometry's translation estimate from the rotational component |
| `alpha5` | 0.2 | translation-related noise; only used by the omni model |
| `odom_frame_id` | `"odom"` | frame used for odometry |
| `base_frame_id` | `"base_footprint"` | frame of the robot base |
| `global_frame_id` | `"map"` | frame published by the localization system |
| `tf_broadcast` | true | false = do not publish the transform between the global frame and the odometry frame |

## Pitfalls
- Particles spread out while driving → odometry noise too high or alphas too low; particles do not follow the robot → alphas too high or a poor odometry source.
- An old YAML with `robot_model_type: "differential"` fails to load the plugin in Humble: use the class name.
