---
id: nav2-costmap-plugin-gradient-layer
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "GradientLayer costmap plugin: header and how each method works"
domain: nav2
area: plugins
distro: humble
tested: false
audience: dev
summary: "GradientLayer (nav2_costmap_2d::Layer) header and walkthrough: namespace, enabled parameter, updateBounds window, onFootprintChanged, updateCosts overwrite, PLUGINLIB_EXPORT_CLASS."
tags: [GradientLayer, custom_nav2_costmap_plugin, gradient_layer.hpp, costmap plugin, onInitialize, declareParameter, updateBounds, updateCosts, master_grid, updateWithMax, PLUGINLIB_EXPORT_CLASS]
see: ["[[nav2-costmap-plugin-gradient-layer-cpp]]", "[[nav2-costmap-layer-api]]", "[[nav2-costmap-plugin-package]]", "[[nav2-costmap-plugin-config]]"]
requires: [ros2-core]
version_notes:
  - "humble: same code as the humble branch of the official nav2_gradient_costmap_plugin tutorial, namespace renamed; isClearable() is required too — https://github.com/ros-navigation/navigation2_tutorials/tree/humble/nav2_gradient_costmap_plugin (NAV2-V50, NAV2-V63)"
  - "lyrical: Layer API unchanged; node_ is a nav2::LifecycleNode::WeakPtr — https://github.com/ros-navigation/navigation2/blob/lyrical/nav2_costmap_2d/include/nav2_costmap_2d/layer.hpp (NAV2-V63)"
---
# GradientLayer costmap plugin: header and how each method works

**TL;DR** Example 3.1 of the course: a layer that writes a repeating cost gradient over the costmap. Create the files, then read the header and the method walkthrough below; the full source is [[nav2-costmap-plugin-gradient-layer-cpp]].
```bash
cd ~/ros2_ws/src/custom_nav2_costmap_plugin
touch src/gradient_layer.cpp
touch include/custom_nav2_costmap_plugin/gradient_layer.hpp
```

## include/custom_nav2_costmap_plugin/gradient_layer.hpp
```cpp
/*********************************************************************
 * Software License Agreement (BSD License), SPDX-License-Identifier: BSD-3-Clause
 * Full text: https://opensource.org/license/bsd-3-clause
 *
 *  Copyright (c) 2008, 2013, Willow Garage, Inc.
 *  Copyright (c) 2020, Samsung R&D Institute Russia
 *  All rights reserved.
 *
 * Author: Eitan Marder-Eppstein
 *         David V. Lu!!
 *         Alexey Merzlyakov
 *
 * Reference tutorial:
 * https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/tutorials/plugin_tutorials/writing_new_costmap2d_plugin/writing_new_costmap2d_plugin.md
 *********************************************************************/
#ifndef GRADIENT_LAYER_HPP_
#define GRADIENT_LAYER_HPP_

#include "rclcpp/rclcpp.hpp"
#include "nav2_costmap_2d/layer.hpp"
#include "nav2_costmap_2d/layered_costmap.hpp"

namespace custom_nav2_costmap_plugin
{

class GradientLayer : public nav2_costmap_2d::Layer
{
public:
  GradientLayer();

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

private:
  double last_min_x_, last_min_y_, last_max_x_, last_max_y_;

  // Indicates that the entire gradient should be recalculated next time.
  bool need_recalculation_;

  // Size of gradient in cells
  int GRADIENT_SIZE = 20;
  // Step of increasing cost per one cell in gradient
  int GRADIENT_FACTOR = 10;
};

}  // namespace custom_nav2_costmap_plugin

#endif  // GRADIENT_LAYER_HPP_
```
- A namespace for the plugin's class (`custom_nav2_costmap_plugin`) avoids confusion with methods of other plugins that have the same name.
- The class `GradientLayer` inherits from the base class `nav2_costmap_2d::Layer`: from it you inherit methods and override them ([[nav2-costmap-layer-api]]).
- The methods you override go in the `public` section. `matchSize()` is not defined here: it is optional, so the base class version (which does nothing) is used ([layer.hpp](https://github.com/ros-navigation/navigation2/blob/humble/nav2_costmap_2d/include/nav2_costmap_2d/layer.hpp), [layer.cpp](https://github.com/ros-navigation/navigation2/blob/humble/nav2_costmap_2d/src/layer.cpp) on the humble branch).

## The methods ([[nav2-costmap-plugin-gradient-layer-cpp]])
- **onInitialize()** declares and reads the parameter `enabled` with `declareParameter("enabled", rclcpp::ParameterValue(true))` and `node->get_parameter(name_ + "." + "enabled", enabled_)`. It comes from the `.yaml` file where you load the plugin:
  ```yaml
  custom_gradient_layer:
    plugin: "custom_nav2_costmap_plugin/GradientLayer"
    enabled: True
  ```
- **updateBounds()** keeps the biggest limits seen, updated with the bounds given as parameters; after a footprint change it asks for the whole map. Unused input parameters are commented out:
  ```cpp
  double /*robot_x*/, double /*robot_y*/, double /*robot_yaw*/
  ```
  so that extra-pedantic compilers do not complain about unused parameters (warnings, or errors with `-Werror`): you must keep them because the virtual methods of the base class have them.
- **onFootprintChanged()** prints a debug message and sets `need_recalculation_` to true, to force the full window again in `updateBounds()`.
- **updateCosts()** overwrites whatever costs were previously in `master_grid` (through `master_array`). To build on the work of previous layers, write to the layer's own `costmap_` instead and merge it with one of:
  ```cpp
  updateWithAddition()
  updateWithMax()
  updateWithOverwrite()
  updateWithTrueOverwrite()
  ```
  It updates costs from the position in the costmap, in a fixed repetitive pattern: not useful, but it shows how to manage costmaps. The `cost` value goes from 0 (no cost) to 254 (lethal); 255 means unknown ([[nav2-costmap-layer-api]]). `i` and `j` are the equivalent of `x` and `y` on the map, in grid cells instead of distance.
- **Export macro**, vital to use the class as a plugin in Nav2:
  ```cpp
  #include "pluginlib/class_list_macros.hpp"
  PLUGINLIB_EXPORT_CLASS(custom_nav2_costmap_plugin::GradientLayer, nav2_costmap_2d::Layer)
  ```
  i.e. `PLUGINLIB_EXPORT_CLASS(NAMESPACE_OF_OUR_CUSTOM_PLUGIN::NAME_OF_CUSTOM_CLASS, BASE_CLASS_NAMESPACE::BASE_CLASS)`.

## Pitfalls
- With this layer last in `plugins`, every cell in the window is overwritten: obstacles of earlier layers disappear ([[nav2-costmap-plugin-config]]).
- The YAML `plugin:` must be the `name` of the description XML ([[nav2-plugin-description-xml]]).
