---
id: nav2-controller-plugin-rpp-algorithm
title: "Regulated Pure Pursuit algorithm: lookahead point, curvature, regulation, collision check"
domain: nav2
area: plugins
distro: humble
tested: false
audience: dev
summary: "Course RPP plugin computeVelocityCommands: lookahead carrot, curvature 2y/L², rotate to heading, regulation, collision projection, speed limit."
tags: [Regulated Pure Pursuit, computeVelocityCommands, getLookAheadPoint, carrot, curvature, applyConstraints, isCollisionImminent, setSpeedLimit, lookahead_dist, max_allowed_time_to_collision, PlannerException]
see: ["[[nav2-controller-plugin-rpp]]", "[[nav2-controller-plugin-config]]", "[[nav2-rpp-controller-params]]", "[[nav2-speed-filter]]"]
requires: [ros2-core]
version_notes:
  - "humble: excerpt of Galactic's RPP 1.0.12 as copied by the course (plus a debug RCLCPP_WARN); Humble's own RPP checks collisions only with use_collision_detection and adds approach_velocity_scaling_dist — https://github.com/ros-navigation/navigation2/blob/1.0.12/nav2_regulated_pure_pursuit_controller/src/regulated_pure_pursuit_controller.cpp (NAV2-V64, NAV2-V65)"
---
# Regulated Pure Pursuit algorithm

**TL;DR** Each control cycle the plugin transforms the global path to the robot frame, picks a **carrot** (lookahead point) on it, computes the curvature of the arc that reaches it, limits the speed (curvature, obstacles, approach to the goal), checks for collisions along the projected motion and returns the command. Interface and parameters: [[nav2-controller-plugin-rpp]].

## computeVelocityCommands()
```cpp
geometry_msgs::msg::TwistStamped RegulatedPurePursuitController::computeVelocityCommands(
  const geometry_msgs::msg::PoseStamped & pose,
  const geometry_msgs::msg::Twist & speed,
  nav2_core::GoalChecker * goal_checker)
{
  RCLCPP_WARN(logger_, "START computeVelocityCommands >>>>>>>>>>>>>>>>>>>");
  // Update for the current goal checker's state
  geometry_msgs::msg::Pose pose_tolerance;
  geometry_msgs::msg::Twist vel_tolerance;
  if (!goal_checker->getTolerances(pose_tolerance, vel_tolerance)) {
    RCLCPP_WARN(logger_, "Unable to retrieve goal checker's tolerances!");
  } else {
    goal_dist_tol_ = pose_tolerance.position.x;
  }

  // Transform path to robot base frame
  auto transformed_plan = transformGlobalPlan(pose);

  // Find look ahead distance and point on path and publish
  double lookahead_dist = getLookAheadDistance(speed);

  // Check for reverse driving
  if (allow_reversing_) {
    // Cusp check
    double dist_to_direction_change = findDirectionChange(pose);

    // if the lookahead distance is further than the cusp, use the cusp distance instead
    if (dist_to_direction_change < lookahead_dist) {
      lookahead_dist = dist_to_direction_change;
    }
  }

  auto carrot_pose = getLookAheadPoint(lookahead_dist, transformed_plan);
  carrot_pub_->publish(createCarrotMsg(carrot_pose));

  double linear_vel, angular_vel;

  // Find distance^2 to look ahead point (carrot) in robot base frame
  // This is the chord length of the circle
  const double carrot_dist2 =
    (carrot_pose.pose.position.x * carrot_pose.pose.position.x) +
    (carrot_pose.pose.position.y * carrot_pose.pose.position.y);

  // Find curvature of circle (k = 1 / R)
  double curvature = 0.0;
  if (carrot_dist2 > 0.001) {
    curvature = 2.0 * carrot_pose.pose.position.y / carrot_dist2;
  }

  // Setting the velocity direction
  double sign = 1.0;
  if (allow_reversing_) {
    sign = carrot_pose.pose.position.x >= 0.0 ? 1.0 : -1.0;
  }

  linear_vel = desired_linear_vel_;

  // Make sure we're in compliance with basic constraints
  double angle_to_heading;
  if (shouldRotateToGoalHeading(carrot_pose)) {
    double angle_to_goal = tf2::getYaw(transformed_plan.poses.back().pose.orientation);
    rotateToHeading(linear_vel, angular_vel, angle_to_goal, speed);
  } else if (shouldRotateToPath(carrot_pose, angle_to_heading)) {
    rotateToHeading(linear_vel, angular_vel, angle_to_heading, speed);
  } else {
    applyConstraints(
      fabs(lookahead_dist - sqrt(carrot_dist2)),
      lookahead_dist, curvature, speed,
      costAtPose(pose.pose.position.x, pose.pose.position.y), linear_vel, sign);

    // Apply curvature to angular velocity after constraining linear velocity
    angular_vel = linear_vel * curvature;
  }

  // Collision checking on this velocity heading
  if (isCollisionImminent(pose, linear_vel, angular_vel)) {
    throw nav2_core::PlannerException("RegulatedPurePursuitController detected collision ahead!");
  }

  // populate and return message
  geometry_msgs::msg::TwistStamped cmd_vel;
  cmd_vel.header = pose.header;
  cmd_vel.twist.linear.x = linear_vel;
  cmd_vel.twist.angular.z = angular_vel;
  return cmd_vel;
}
```
The first line is the course's debug message: one warning per control cycle (up to 20 Hz).

## The helpers, in short (full code: [1.0.12 source](https://github.com/ros-navigation/navigation2/blob/1.0.12/nav2_regulated_pure_pursuit_controller/src/regulated_pure_pursuit_controller.cpp))
- `getLookAheadDistance(speed)`: `lookahead_dist_`, or with `use_velocity_scaled_lookahead_dist` `|v| * lookahead_time_` clamped to `[min_lookahead_dist_, max_lookahead_dist_]`.
- `getLookAheadPoint(dist, plan)`: the first pose of the transformed plan at least `dist` away from the robot; the last pose if none is.
- Curvature: with the carrot at (x, y) in the robot frame and L² = x² + y², `curvature = 2.0 * y / L²` (k = 1 / R); then `angular_vel = linear_vel * curvature`.
- `shouldRotateToGoalHeading` / `shouldRotateToPath` + `rotateToHeading`: with `use_rotate_to_heading`, rotate in place (at `rotate_to_heading_angular_vel`, limited by `max_angular_accel`) when the path heading differs more than `rotate_to_heading_min_angle`, or at the goal.
- `applyConstraints(...)`: the linear speed is the minimum of
  - the curvature limit: `curvature_vel *= 1.0 - (fabs(radius - min_rad) / min_rad)` when the radius is below `regulated_linear_scaling_min_radius`;
  - the obstacle limit: `cost_vel *= cost_scaling_gain_ * min_distance_to_obstacle / cost_scaling_dist_` when the estimated distance to obstacles (from the inflation cost) is below `cost_scaling_dist`;
  then at least `regulated_linear_scaling_min_speed`, slowed near the end of the path by the approach scaling (not below `min_approach_linear_velocity`) and clamped to `desired_linear_vel_`.
- `isCollisionImminent(pose, v, w)`: projects the command forward in steps of one costmap cell for up to `max_allowed_time_to_collision` seconds and checks the cost at each point; a collision throws `PlannerException("RegulatedPurePursuitController detected collision ahead!")`, which fails `FollowPath` ([[nav2-recovery-flow]]).
- `setSpeedLimit(limit, percentage)`: `desired_linear_vel_ = base_desired_linear_vel_ * speed_limit / 100.0` (percentage) or `= speed_limit` (m/s); `NO_SPEED_LIMIT` restores the base value ([[nav2-speed-filter]]).

## Pitfalls
- The lookahead distance is not a collision distance (the course says it is): collisions use the time `max_allowed_time_to_collision` (NAV2-V53).
- A carrot closer than `lookahead_dist` means the end of the path: the approach scaling slows the robot down.
