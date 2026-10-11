---
id: nav2-costmap-plugin-moving-obstacle
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Moving-obstacle costmap layer (exercise solution): parameters and updateCosts"
domain: nav2
area: plugins
distro: humble
tested: false
audience: dev
summary: "MyCustomCostmap layer (exercise EX.1): a box that oscillates in the global costmap; parameters x_oscilation_height, y_oscilation_range, obstacle_radius; build and launch changes."
tags: [MyCustomCostmap, my_custom_costmap_namespace_name, MyCrazyCustomCostmapLayer_Plugin_Name, moving obstacle, costmap layer, pointInsideCircle, x_oscilation_height, y_oscilation_range, obstacle_radius, my_custom_crazy_costmap]
see: ["[[nav2-costmap-plugin-gradient-layer-cpp]]", "[[nav2-costmap-layer-api]]", "[[nav2-costmap-plugin-config]]", "[[nav2-learn-adv-unit3-plugins]]"]
requires: [ros2-core]
version_notes:
  - "humble: the course's solution launch starts package nav2_recoveries (absent in Humble) and passes default_bt_xml_filename (ignored); fixed in nav2-costmap-plugin-moving-obstacle-config — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/galactic/Galactic.md (NAV2-V52, NAV2-V51)"
---
# Moving-obstacle costmap layer (exercise solution)

**TL;DR** Solution of exercise EX.1 ([[nav2-learn-adv-unit3-plugins]]): a costmap layer based on the GradientLayer that draws a small box moving up and down, simulating a person walking, only in the **global** costmap. The planner replans when the box crosses the path.

## include/custom_nav2_costmap_plugin/my_custom_costmap.hpp
```cpp
#ifndef MY_CUSTOM_COSTMAP_HPP_
#define MY_CUSTOM_COSTMAP_HPP_

#include "rclcpp/rclcpp.hpp"
#include "nav2_costmap_2d/layer.hpp"
#include "nav2_costmap_2d/layered_costmap.hpp"
#include <math.h>

namespace my_custom_costmap_namespace_name
{

class MyCustomCostmap : public nav2_costmap_2d::Layer
{
public:
  MyCustomCostmap();

  virtual void onInitialize();
  virtual void updateBounds(
    double robot_x, double robot_y, double robot_yaw, double * min_x,
    double * min_y,
    double * max_x,
    double * max_y);
  virtual void updateCosts(
    nav2_costmap_2d::Costmap2D & master_grid,
    int min_i, int min_j, int max_i, int max_j);

  virtual void reset()
  {
    return;
  }

  virtual void onFootprintChanged();

  virtual bool isClearable() {return false;}

  bool pointInsideCircle(int x_point, int y_point);

private:
  double last_min_x_, last_min_y_, last_max_x_, last_max_y_;

  // Indicates that the entire gradient should be recalculated next time.
  bool need_recalculation_;

  // Size of gradient in cells
  int GRADIENT_SIZE = 20;
  // Step of increasing cost per one cell in gradient
  int GRADIENT_FACTOR = 10;

  // Init Crazy Circle pose
  float circle_p_x;
  float circle_p_y;
  float circle_p_y_delta = 0;
  bool delta_flag = true;
  int obstacle_radius = 30;
  float x_oscilation_height;
  float y_oscilation_range;
};

}  // namespace my_custom_costmap_namespace_name

#endif  // MY_CUSTOM_COSTMAP_HPP_
```

## src/my_custom_costmap.cpp: what changes
The file is `gradient_layer.cpp` ([[nav2-costmap-plugin-gradient-layer-cpp]]) with `#include "custom_nav2_costmap_plugin/my_custom_costmap.hpp"`, namespace `my_custom_costmap_namespace_name`, class `MyCustomCostmap`, and `PLUGINLIB_EXPORT_CLASS(my_custom_costmap_namespace_name::MyCustomCostmap, nav2_costmap_2d::Layer)`. Constructor and `onFootprintChanged()` are the same. These methods change:
```cpp
void
MyCustomCostmap::onInitialize()
{
  auto node = node_.lock();
  declareParameter("enabled", rclcpp::ParameterValue(true));
  node->get_parameter(name_ + "." + "enabled", enabled_);
  declareParameter("x_oscilation_height", rclcpp::ParameterValue(10.0));
  node->get_parameter(name_ + "." + "x_oscilation_height", x_oscilation_height);
  declareParameter("y_oscilation_range", rclcpp::ParameterValue(10.0));
  node->get_parameter(name_ + "." + "y_oscilation_range", y_oscilation_range);
  declareParameter("obstacle_radius", rclcpp::ParameterValue(30));
  node->get_parameter(name_ + "." + "obstacle_radius", obstacle_radius);

  need_recalculation_ = false;
  current_ = true;
}

void
MyCustomCostmap::updateBounds(
  double /*robot_x*/, double /*robot_y*/, double /*robot_yaw*/, double * min_x,
  double * min_y, double * max_x, double * max_y)
{
  last_min_x_ = *min_x;
  last_min_y_ = *min_y;
  last_max_x_ = *max_x;
  last_max_y_ = *max_y;
  *min_x = -std::numeric_limits<float>::max();
  *min_y = -std::numeric_limits<float>::max();
  *max_x = std::numeric_limits<float>::max();
  *max_y = std::numeric_limits<float>::max();
  need_recalculation_ = true;
}
```
In `updateCosts()`, after fixing the window coordinates (as in the GradientLayer), the gradient loop is replaced by:
```cpp
  // You calculate the new position of circle
  circle_p_x = x_oscilation_height;
  // Calculate center
  circle_p_y = (max_j - min_j)/2;
  if (delta_flag)
  {
    circle_p_y_delta += 10;
  }else{
    circle_p_y_delta -= 10;
  }
  circle_p_y += circle_p_y_delta;

  if (circle_p_y >= (((max_j - min_j)/2) + y_oscilation_range))
  {
    delta_flag = false;
  }else if (circle_p_y <= (((max_j - min_j)/2) - y_oscilation_range))
  {
    delta_flag = true;
  }

  RCLCPP_WARN(rclcpp::get_logger("nav2_costmap_2d"), "circle_p_x = %f", circle_p_x);
  RCLCPP_WARN(rclcpp::get_logger("nav2_costmap_2d"), "circle_p_y = %f", circle_p_y);

  for (int j = min_j; j < max_j; j++) {
    for (int i = min_i; i < max_i; i++) {
      int index = master_grid.getIndex(i, j);
      bool result = pointInsideCircle(i, j);
      if (result)
      {
        master_array[index] = 200;
      }else{
        master_array[index] = 1;
      }
    }
  }
}

bool
MyCustomCostmap::pointInsideCircle(int x_point, int y_point)
{
  int delta_x = abs(circle_p_x - x_point);
  int delta_y = abs(circle_p_y - y_point);
  bool delta_x_in = (delta_x <= obstacle_radius);
  bool delta_y_in = (delta_y <= obstacle_radius);
  bool inside_circle = (delta_x_in && delta_y_in);
  // RCLCPP_WARN(rclcpp::get_logger(
  //     "nav2_costmap_2d"), "Point Inside Cicle = %d", inside_circle);
  return inside_circle;
}
```
`pointInsideCircle()` actually tests a square of side `2 * obstacle_radius` cells, the "small box" of the exercise.

## Build and configuration
Description file, CMake, `package.xml`, the `my_crazy_layer` parameters (`x_oscilation_height`, `y_oscilation_range`, `obstacle_radius`) in the global costmap and the launch: [[nav2-costmap-plugin-moving-obstacle-config]].

## Pitfalls
- Every cell of the window is written (1 or 200) and `updateBounds()` always asks for the whole map: the walls of the static and obstacle layers vanish from the global costmap, and plans only avoid the box.
- The parameter names keep the course spelling (`oscilation`): YAML and code must match.
