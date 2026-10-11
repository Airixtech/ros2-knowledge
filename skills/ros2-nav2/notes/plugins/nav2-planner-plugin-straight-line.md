---
id: nav2-planner-plugin-straight-line
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "StraightLine planner plugin (nav2_core::GlobalPlanner): header, configure, createPlan"
domain: nav2
area: plugins
distro: humble
tested: false
audience: dev
summary: "Global planner plugin that returns straight-line paths (ignores obstacles): nav2_core::GlobalPlanner methods, header, interpolation_resolution, how createPlan interpolates."
tags: [StraightLine, nav2_core::GlobalPlanner, planner plugin, global planner, createPlan, configure, interpolation_resolution, straight_line_planner.hpp, nav2_straightline_planner_namespace_name]
see: ["[[nav2-planner-plugin-straight-line-cpp]]", "[[nav2-planner-plugin-package]]", "[[nav2-planner-plugin-config]]", "[[nav2-planner-plugin-wavy]]", "[[nav2-plugins-overview]]"]
requires: [ros2-core]
version_notes:
  - "humble: GlobalPlanner pure virtuals configure, cleanup, activate, deactivate, createPlan(start, goal) — https://github.com/ros-navigation/navigation2/blob/humble/nav2_core/include/nav2_core/global_planner.hpp (NAV2-V63)"
  - "jazzy: createPlan(start, goal, std::function<bool()> cancel_checker); lyrical: nav2::LifecycleNode, nav2::TransformBuffer, createPlan(start, goal, viapoints, cancel_checker) — https://github.com/ros-navigation/navigation2/blob/lyrical/nav2_core/include/nav2_core/global_planner.hpp (NAV2-V63)"
---
# StraightLine planner plugin (nav2_core::GlobalPlanner)

**TL;DR** Example 3.2: a **planner plugin** that generates **straight-line paths without considering obstacles**, a foundation for understanding how custom path planners work in Nav2. Code from the official Nav2 tutorial ([humble version](https://github.com/ros-navigation/navigation2_tutorials/tree/humble/nav2_straightline_planner)).
```bash
cd ~/ros2_ws/src/custom_nav2_planner_plugin
touch src/straight_line_planner.cpp
touch include/custom_nav2_planner_plugin/straight_line_planner.hpp
```

## include/custom_nav2_planner_plugin/straight_line_planner.hpp
```cpp
/*********************************************************************
 * Software License Agreement (BSD License), SPDX-License-Identifier: BSD-3-Clause
 * Full text: https://opensource.org/license/bsd-3-clause
 *
 *  Copyright (c) 2020 Shivang Patel
 *  All rights reserved.
 *
 * Author: Shivang Patel
 *
 * Reference tutorial:
 * https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/tutorials/plugin_tutorials/writing_new_planner_plugin/writing_new_planner_plugin.md
 *********************************************************************/

#ifndef NAV2_STRAIGHTLINE_PLANNER__STRAIGHT_LINE_PLANNER_HPP_
#define NAV2_STRAIGHTLINE_PLANNER__STRAIGHT_LINE_PLANNER_HPP_

#include <string>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/point.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"

#include "nav2_core/global_planner.hpp"
#include "nav_msgs/msg/path.hpp"
#include "nav2_util/robot_utils.hpp"
#include "nav2_util/lifecycle_node.hpp"
#include "nav2_costmap_2d/costmap_2d_ros.hpp"

namespace nav2_straightline_planner_namespace_name
{

class StraightLine : public nav2_core::GlobalPlanner
{
public:
  StraightLine() = default;
  ~StraightLine() = default;

  // plugin configure
  void configure(
    const rclcpp_lifecycle::LifecycleNode::WeakPtr & parent,
    std::string name, std::shared_ptr<tf2_ros::Buffer> tf,
    std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros) override;

  // plugin cleanup
  void cleanup() override;

  // plugin activate
  void activate() override;

  // plugin deactivate
  void deactivate() override;

  // This method creates path for given start and goal pose.
  nav_msgs::msg::Path createPlan(
    const geometry_msgs::msg::PoseStamped & start,
    const geometry_msgs::msg::PoseStamped & goal) override;

private:
  // TF buffer
  std::shared_ptr<tf2_ros::Buffer> tf_;

  // node ptr
  nav2_util::LifecycleNode::SharedPtr node_;

  // Global Costmap
  nav2_costmap_2d::Costmap2D * costmap_;

  // The global frame of the costmap
  std::string global_frame_, name_;

  double interpolation_resolution_;
};

}  // namespace nav2_straightline_planner_namespace_name

#endif  // NAV2_STRAIGHTLINE_PLANNER__STRAIGHT_LINE_PLANNER_HPP_
```
All the methods you override from the base class `nav2_core::GlobalPlanner` are in the `public` section, and all of them are **required** (pure virtual):
- `configure()`: called when the node is in the **configure** state: load all the parameters and initialize all the variables here.
- `activate()`: executed when the plugin is activated; put here what you need before it is active.
- `deactivate()`: executed when it is deactivated.
- `cleanup()`: executed in the cleanup state: free memory and similar tasks.
- `createPlan()`: called when the server wants a global path generation based on a `start` and a `goal_pose`; it returns the `nav_msgs::msg::Path` used as the global planned path.

## configure() and createPlan() ([[nav2-planner-plugin-straight-line-cpp]])
- `configure()` stores the node, name, TF buffer, costmap and global frame, and gets the parameter `interpolation_resolution` (default 0.1) used for the straight-line path generation. It is set in the YAML:
  ```yaml
  planner_plugins: ["GridBased"]
  GridBased:
    plugin: StraightLineCustomPlugin
    interpolation_resolution: 0.1
  ```
- `createPlan()` receives `start` and `goal`, checks both are in the global frame, computes the distance between the two 2D points and divides it by `interpolation_resolution`:
  ```cpp
  int total_number_of_loop = std::hypot(
    goal.pose.position.x - start.pose.position.x,
    goal.pose.position.y - start.pose.position.y) /
    interpolation_resolution_;
  ```
  That is the number of parts the straight-line path is divided into: the larger the distance, the more parts. Then it generates the points of the path linearly, with increments `x_increment`, `y_increment`, which gives a perfectly straight path line (all orientations `w = 1.0`), and appends the goal.

## Pitfalls
- Start or goal in another frame → empty path ("Planner will only except start position from map frame"; "except" is the tutorial's typo).
- Start equal to the goal → `total_number_of_loop` is 0 and the increments divide by zero; the loop does not run, so only the goal is returned.
