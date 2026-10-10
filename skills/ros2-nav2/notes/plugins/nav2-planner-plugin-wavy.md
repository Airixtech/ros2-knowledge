---
id: nav2-planner-plugin-wavy
title: "WavyLine planner plugin (exercise solution): sine/cosine path"
domain: nav2
area: plugins
distro: humble
tested: false
audience: dev
summary: "WavyLine global planner (exercise EX.2): StraightLine with a sine/cosine offset per pose; header, createPlan loop, XML, CMake and launch changes."
tags: [WavyLine, WavyLineCustomPlugin, wavy_line_planner_core, nav2_wavyline_planner_namespace_name, planner plugin, sin, cos, createPlan, wavyline_planner, pathplanner_wavyline_planner_plugin.launch.py]
see: ["[[nav2-planner-plugin-straight-line-cpp]]", "[[nav2-planner-plugin-package]]", "[[nav2-planner-plugin-config]]", "[[nav2-learn-adv-unit3-plugins]]"]
requires: [ros2-core]
version_notes:
  - "humble: the course's solution launch starts nav2_recoveries (absent in Humble) and passes default_bt_xml_filename (ignored); fixed below — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/galactic/Galactic.md (NAV2-V52, NAV2-V51)"
  - "jazzy: createPlan needs the cancel_checker argument — https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_core/include/nav2_core/global_planner.hpp (NAV2-V63)"
---
# WavyLine planner plugin (exercise solution)

**TL;DR** Solution of exercise EX.2 ([[nav2-learn-adv-unit3-plugins]]): a planner based on the StraightLine plugin whose `createPlan()` generates wavy paths with **sin** and **cos** offsets. The global path is now wavy and changes with the distance to the goal.

## Suggested idea (course hint)
```cpp
#include <math.h>
#define PI 3.14159265
...
int A = 4;
float frequency = 2.0;
x_sin_increment = A * x_increment * sin (i_angle*frequency);
y_cos_increment = A * y_increment * cos (i_angle*frequency);
...
pose.pose.position.x = start.pose.position.x + x_increment * i + x_sin_increment;
pose.pose.position.y = start.pose.position.y + y_increment * i + y_cos_increment;
```
You are free to do whatever path; the only restriction is that it **cannot be straight**.

## wavy_line_planner.hpp / wavy_line_planner.cpp: what changes
Both files are the StraightLine ones ([[nav2-planner-plugin-straight-line]], [[nav2-planner-plugin-straight-line-cpp]]) with class `WavyLine`, namespace `nav2_wavyline_planner_namespace_name`, `#include "custom_nav2_planner_plugin/wavy_line_planner.hpp"` and `PLUGINLIB_EXPORT_CLASS(nav2_wavyline_planner_namespace_name::WavyLine, nav2_core::GlobalPlanner)`. The header guard is still `NAV2_WAVYLINE_PLANNER__STRAIGHT_LINE_PLANNER_HPP_`, and after `#include "nav2_costmap_2d/costmap_2d_ros.hpp"` it adds:
```cpp
#include <math.h>
#define PI 3.14159265
```
The `for` loop of `createPlan()` and its ending become:
```cpp
  for (int i = 0; i < total_number_of_loop; ++i) {
    geometry_msgs::msg::PoseStamped pose;
    // You only create zig zag if total_number_of_loop > 3
    float x_sin_increment = 0.0;
    float y_cos_increment = 0.0;
    float angle_increment = 2.0 * PI / total_number_of_loop;
    float i_angle = 0.0;
    if (total_number_of_loop > 3)
    {
      i_angle = angle_increment * i;
      int A = 4;
      float frequency = 2.0;
      x_sin_increment = A * x_increment * sin (i_angle*frequency);
      y_cos_increment = A * y_increment * cos (i_angle*frequency);
      RCLCPP_WARN(node_->get_logger(), ">>>>>>>> SIN X=%f,COS Y=%f, ANGLE=%f, index=%i", x_sin_increment, y_cos_increment, i_angle, i);
    }else{
    }
    pose.pose.position.x = start.pose.position.x + x_increment * i + x_sin_increment;
    pose.pose.position.y = start.pose.position.y + y_increment * i + y_cos_increment;
    RCLCPP_WARN(node_->get_logger(), "Pose X=%f, Y=%f, index=%i", pose.pose.position.x, pose.pose.position.y, i);
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
  RCLCPP_WARN(node_->get_logger(), ">>>>>>>>>>> Plann WAVY -/-/-/- line DONE");
  return global_path;
}
```

## Description file, build and configuration
- `wavy_line_plugin_info.xml`:
  ```xml
  <library path="wavy_line_planner_core">
    <class name="WavyLineCustomPlugin" type="nav2_wavyline_planner_namespace_name::WavyLine" base_class_type="nav2_core::GlobalPlanner">
      <description>This is an example plugin which produces Wavy line path.</description>
    </class>
  </library>
  ```
- `CMakeLists.txt` ([[nav2-planner-plugin-package]]) builds both libraries; for the new one:
  ```cmake
  set(wavy_plugin_name wavy_line_planner_core)
  # WavyLine plugin related stuff
  add_library(${wavy_plugin_name} SHARED
    src/wavy_line_planner.cpp)
  ament_target_dependencies(${wavy_plugin_name}
    ${dependencies})
  target_compile_definitions(${wavy_plugin_name} PUBLIC "PLUGINLIB__DISABLE_BOOST_FUNCTIONS")
  pluginlib_export_plugin_description_file(nav2_core wavy_line_plugin_info.xml)
  install(TARGETS ${wavy_plugin_name}
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION lib/${PROJECT_NAME}
  )
  # install(FILES straight_line_plugin_info.xml wavy_line_plugin_info.xml
  #   DESTINATION share/${PROJECT_NAME}
  # )
  ament_export_libraries(${wavy_plugin_name})
  ```
  (plus the commented `ament_cmake_copyright_FOUND` / `ament_cmake_cpplint_FOUND` lines of `ros2 pkg create` in `BUILD_TESTING`). `package.xml` exports both files: `<nav2_core plugin="${prefix}/straight_line_plugin_info.xml" />` and `<nav2_core plugin="${prefix}/wavy_line_plugin_info.xml" />`.
- `config/wavyline_planner/planner_server.yaml`: `GridBased: plugin: WavyLineCustomPlugin`, `interpolation_resolution: 0.1`, and the global costmap (`robot_base_frame: base_footprint`, `inflation_radius: 0.55`); `setup.py` installs `config/wavyline_planner`.
- `launch/pathplanner_wavyline_planner_plugin.launch.py`: the minimal path planning launch (controller, planner, behavior server, bt_navigator, `lifecycle_manager_pathplanner`), with `planner_yaml` from `config/wavyline_planner/` and the default `controller.yaml` and `behavior.xml`. Humble-correct nodes as in [[nav2-costmap-plugin-moving-obstacle-config]]: `package='nav2_behaviors', executable='behavior_server', name='behavior_server'` (course: `nav2_recoveries`/`recoveries_server`) and `{'default_nav_to_pose_bt_xml': default_bt_xml_path}`.

## Pitfalls
- The course text says "create a new Costmap plugin based on Example 3.2": it is a **planner** plugin.
- One `RCLCPP_WARN` per pose floods the log at the planner rate; use `RCLCPP_DEBUG` once it works.
