---
id: nav2-planner-plugin-straight-line-cpp
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "StraightLine planner plugin: full source (straight_line_planner.cpp)"
domain: nav2
area: plugins
distro: humble
tested: false
audience: dev
summary: "Complete straight_line_planner.cpp: configure with interpolation_resolution, cleanup/activate/deactivate logs, createPlan straight-line interpolation, PLUGINLIB_EXPORT_CLASS."
tags: [StraightLine, straight_line_planner.cpp, createPlan, interpolation_resolution, declare_parameter_if_not_declared, nav2_core::GlobalPlanner, PLUGINLIB_EXPORT_CLASS]
see: ["[[nav2-planner-plugin-straight-line]]", "[[nav2-planner-plugin-wavy]]", "[[nav2-planner-plugin-package]]"]
requires: [ros2-core]
version_notes:
  - "humble: the official tutorial (humble branch) with the course's include path and an older ending (pushes goal as is, logs DONE); license header condensed — https://github.com/ros-navigation/navigation2_tutorials/blob/humble/nav2_straightline_planner/src/straight_line_planner.cpp (NAV2-V63)"
  - "jazzy: add the std::function<bool()> cancel_checker argument to createPlan — https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_core/include/nav2_core/global_planner.hpp (NAV2-V63)"
---
# StraightLine planner plugin: full source

**TL;DR** The source of the planner explained in [[nav2-planner-plugin-straight-line]]; it goes in `src/straight_line_planner.cpp` of `custom_nav2_planner_plugin`.

## src/straight_line_planner.cpp
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

#include <cmath>
#include <string>
#include <memory>
#include "nav2_util/node_utils.hpp"

#include "custom_nav2_planner_plugin/straight_line_planner.hpp"

namespace nav2_straightline_planner_namespace_name
{

void StraightLine::configure(
  const rclcpp_lifecycle::LifecycleNode::WeakPtr & parent,
  std::string name, std::shared_ptr<tf2_ros::Buffer> tf,
  std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros)
{
  node_ = parent.lock();
  name_ = name;
  tf_ = tf;
  costmap_ = costmap_ros->getCostmap();
  global_frame_ = costmap_ros->getGlobalFrameID();

  // Parameter initialization
  nav2_util::declare_parameter_if_not_declared(
    node_, name_ + ".interpolation_resolution", rclcpp::ParameterValue(
      0.1));
  node_->get_parameter(name_ + ".interpolation_resolution", interpolation_resolution_);
}

void StraightLine::cleanup()
{
  RCLCPP_INFO(
    node_->get_logger(), "CleaningUp plugin %s of type NavfnPlanner",
    name_.c_str());
}

void StraightLine::activate()
{
  RCLCPP_INFO(
    node_->get_logger(), "Activating plugin %s of type NavfnPlanner",
    name_.c_str());
}

void StraightLine::deactivate()
{
  RCLCPP_INFO(
    node_->get_logger(), "Deactivating plugin %s of type NavfnPlanner",
    name_.c_str());
}

nav_msgs::msg::Path StraightLine::createPlan(
  const geometry_msgs::msg::PoseStamped & start,
  const geometry_msgs::msg::PoseStamped & goal)
{
  nav_msgs::msg::Path global_path;

  // Checking if the goal and start state is in the global frame
  if (start.header.frame_id != global_frame_) {
    RCLCPP_ERROR(
      node_->get_logger(), "Planner will only except start position from %s frame",
      global_frame_.c_str());
    return global_path;
  }

  if (goal.header.frame_id != global_frame_) {
    RCLCPP_INFO(
      node_->get_logger(), "Planner will only except goal position from %s frame",
      global_frame_.c_str());
    return global_path;
  }

  global_path.poses.clear();
  global_path.header.stamp = node_->now();
  global_path.header.frame_id = global_frame_;
  // calculating the number of loops for current value of interpolation_resolution_
  int total_number_of_loop = std::hypot(
    goal.pose.position.x - start.pose.position.x,
    goal.pose.position.y - start.pose.position.y) /
    interpolation_resolution_;
  double x_increment = (goal.pose.position.x - start.pose.position.x) / total_number_of_loop;
  double y_increment = (goal.pose.position.y - start.pose.position.y) / total_number_of_loop;

  for (int i = 0; i < total_number_of_loop; ++i) {
    geometry_msgs::msg::PoseStamped pose;
    pose.pose.position.x = start.pose.position.x + x_increment * i;
    pose.pose.position.y = start.pose.position.y + y_increment * i;
    pose.pose.position.z = 0.0;
    pose.pose.orientation.x = 0.0;
    pose.pose.orientation.y = 0.0;
    pose.pose.orientation.z = 0.0;
    pose.pose.orientation.w = 1.0;
    pose.header.stamp = node_->now();
    pose.header.frame_id = global_frame_;
    global_path.poses.push_back(pose);
  }

  global_path.poses.push_back(goal);
  RCLCPP_WARN(node_->get_logger(), "Plann Straight line DONE");

  return global_path;
}

}  // namespace nav2_straightline_planner_namespace_name

#include "pluginlib/class_list_macros.hpp"
PLUGINLIB_EXPORT_CLASS(nav2_straightline_planner_namespace_name::StraightLine, nav2_core::GlobalPlanner)
```

## Pitfalls
- The log messages say "NavfnPlanner": copied from NavFn in the tutorial; they do not change the behavior.
- The upstream tutorial now copies `goal` and sets its stamp and frame before appending it; the course appends `goal` as received.
