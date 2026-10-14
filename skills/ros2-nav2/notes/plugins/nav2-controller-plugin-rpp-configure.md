---
id: nav2-controller-plugin-rpp-configure
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Custom RPP controller plugin: configure() and its parameters with defaults"
domain: nav2
area: plugins
distro: humble
tested: false
audience: dev
summary: "configure() of the course RPP plugin: node lock, members, parameter declarations, reversing check, publishers; 22 parameters with defaults."
tags: [configure, declare_parameter_if_not_declared, RegulatedPurePursuitController, custom_nav2_controller_plugin, max_allowed_time_to_collision, use_approach_linear_velocity_scaling, lookahead_dist, desired_linear_vel, controller_frequency, lookahead_point]
see: ["[[nav2-controller-plugin-rpp]]", "[[nav2-controller-plugin-rpp-algorithm]]", "[[nav2-controller-plugin-config]]", "[[nav2-rpp-controller-params]]"]
requires: [ros2-core]
version_notes:
  - "humble: Galactic parameter names (max_allowed_time_to_collision, use_approach_linear_velocity_scaling); Humble's own RPP uses max_allowed_time_to_collision_up_to_carrot and approach_velocity_scaling_dist — https://github.com/ros-navigation/navigation2/blob/1.0.12/nav2_regulated_pure_pursuit_controller/src/regulated_pure_pursuit_controller.cpp (NAV2-V53, NAV2-V64)"
---
# Custom RPP controller plugin: configure() and its parameters

**TL;DR** `configure()` of the controller plugin of [[nav2-controller-plugin-rpp]]: it locks the node, stores the costmap, TF buffer and name, declares and reads one parameter per tuning knob (`<plugin name>.<parameter>`), reads the server's `controller_frequency` and creates the debug publishers `received_global_plan`, `lookahead_point` and `lookahead_collision_arc`.

## configure() (src/regulated_pure_pursuit_controller.cpp)
```cpp
void RegulatedPurePursuitController::configure(
  const rclcpp_lifecycle::LifecycleNode::WeakPtr & parent,
  std::string name, const std::shared_ptr<tf2_ros::Buffer> tf,
  const std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros)
{
  auto node = parent.lock();
  if (!node) {
    throw nav2_core::PlannerException("Unable to lock node!");
  }

  costmap_ros_ = costmap_ros;
  costmap_ = costmap_ros_->getCostmap();
  tf_ = tf;
  plugin_name_ = name;
  logger_ = node->get_logger();
  clock_ = node->get_clock();

  double transform_tolerance = 0.1;
  double control_frequency = 20.0;
  goal_dist_tol_ = 0.25;  // reasonable default before first update

  // declare_parameter_if_not_declared(node, plugin_name_ + ".<name>", rclcpp::ParameterValue(<default>))
  // for each parameter of the table below

  // node->get_parameter(plugin_name_ + ".<name>", <member>_) for each parameter above
  // (max_allowed_time_to_collision -> max_allowed_time_to_collision_, …)
  node->get_parameter("controller_frequency", control_frequency);

  transform_tolerance_ = tf2::durationFromSec(transform_tolerance);
  control_duration_ = 1.0 / control_frequency;

  if (inflation_cost_scaling_factor_ <= 0.0) {
    RCLCPP_WARN(
      logger_, "The value inflation_cost_scaling_factor is incorrectly set, "
      "it should be >0. Disabling cost regulated linear velocity scaling.");
    use_cost_regulated_linear_velocity_scaling_ = false;
  }

  /** Possible to drive in reverse direction if and only if
   "use_rotate_to_heading" parameter is set to false **/

  if (use_rotate_to_heading_ && allow_reversing_) {
    RCLCPP_WARN(
      logger_, "Disabling reversing. Both use_rotate_to_heading and allow_reversing "
      "parameter cannot be set to true. By default setting use_rotate_to_heading true");
    allow_reversing_ = false;
  }

  global_path_pub_ = node->create_publisher<nav_msgs::msg::Path>("received_global_plan", 1);
  carrot_pub_ = node->create_publisher<geometry_msgs::msg::PointStamped>("lookahead_point", 1);
  carrot_arc_pub_ = node->create_publisher<nav_msgs::msg::Path>("lookahead_collision_arc", 1);
}
```
| Parameter | Default | Parameter | Default |
|---|---|---|---|
| `desired_linear_vel` | 0.5 | `max_allowed_time_to_collision` | 1.0 |
| `lookahead_dist` | 0.6 | `use_regulated_linear_velocity_scaling` | true |
| `min_lookahead_dist` | 0.3 | `use_cost_regulated_linear_velocity_scaling` | true |
| `max_lookahead_dist` | 0.9 | `cost_scaling_dist` | 0.6 |
| `lookahead_time` | 1.5 | `cost_scaling_gain` | 1.0 |
| `rotate_to_heading_angular_vel` | 1.8 | `inflation_cost_scaling_factor` | 3.0 |
| `transform_tolerance` | 0.1 | `regulated_linear_scaling_min_radius` | 0.90 |
| `use_velocity_scaled_lookahead_dist` | false | `regulated_linear_scaling_min_speed` | 0.25 |
| `min_approach_linear_velocity` | 0.05 | `use_rotate_to_heading` | true |
| `use_approach_linear_velocity_scaling` | true | `rotate_to_heading_min_angle` | 0.785 |
| `allow_reversing` | false | `max_angular_accel` | 3.2 |

These are the parameters of **this** plugin (Galactic names); Humble's `nav2_regulated_pure_pursuit_controller` renamed `max_allowed_time_to_collision` to `max_allowed_time_to_collision_up_to_carrot` and replaced `use_approach_linear_velocity_scaling` (NAV2-V53).
