---
id: nav2-costmap-layer-api
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "nav2_costmap_2d::Layer API: required and optional methods, update windows, cost values"
domain: nav2
area: plugins
distro: humble
tested: false
audience: dev
summary: "Costmap layer plugin API (nav2_costmap_2d::Layer): required updateBounds, updateCosts, reset, isClearable; optional onInitialize, matchSize, onFootprintChanged; cost values."
tags: [nav2_costmap_2d::Layer, costmap plugin, costmap layer, onInitialize, updateBounds, updateCosts, reset, isClearable, matchSize, onFootprintChanged, LETHAL_OBSTACLE, NO_INFORMATION, StaticLayer]
see: ["[[nav2-costmap-plugin-gradient-layer]]", "[[nav2-plugins-overview]]", "[[nav2-costmap-concepts]]", "[[nav2-costmap-layers]]"]
requires: [ros2-core]
version_notes:
  - "humble: pure virtual (required) reset(), isClearable(), updateBounds(), updateCosts(); cost 254 lethal, 255 unknown — https://github.com/ros-navigation/navigation2/blob/humble/nav2_costmap_2d/include/nav2_costmap_2d/layer.hpp (NAV2-V50)"
  - "lyrical: same methods; the layer's node_ is a nav2::LifecycleNode::WeakPtr — https://github.com/ros-navigation/navigation2/blob/lyrical/nav2_costmap_2d/include/nav2_costmap_2d/layer.hpp (NAV2-V63)"
---
# nav2_costmap_2d::Layer API: required and optional methods

**TL;DR** A costmap plugin is a class derived from `nav2_costmap_2d::Layer`. Here you develop a custom costmap layer plugin, which modifies the way the navigation stack processes costmaps; it is the foundation for building more advanced plugins later on.

## A layer from the inside: StaticLayer (simplified)
```cpp
...INCLUDES...
PLUGINLIB_EXPORT_CLASS(nav2_costmap_2d::StaticLayer, nav2_costmap_2d::Layer)

namespace nav2_costmap_2d
{
StaticLayer::StaticLayer()
: map_buffer_(nullptr) {}
StaticLayer::~StaticLayer() {}
void StaticLayer::onInitialize() {...CODE...}
void StaticLayer::activate() {...CODE...}
void StaticLayer::deactivate() {...CODE...}
void StaticLayer::reset() {...CODE...}
void StaticLayer::getParameters() {...CODE...}
void StaticLayer::processMap(const nav_msgs::msg::OccupancyGrid & new_map) {...CODE...}
void StaticLayer::matchSize() {...CODE...}
unsigned char StaticLayer::interpretValue(unsigned char value) {...CODE...}
void StaticLayer::incomingMap(const nav_msgs::msg::OccupancyGrid::SharedPtr new_map) {...CODE...}
void StaticLayer::incomingUpdate(map_msgs::msg::OccupancyGridUpdate::ConstSharedPtr update) {...CODE...}
void StaticLayer::updateBounds(
  double /*robot_x*/, double /*robot_y*/, double /*robot_yaw*/, double * min_x,
  double * min_y, double * max_x, double * max_y) {...CODE...}
void StaticLayer::updateCosts(
  nav2_costmap_2d::Costmap2D & master_grid,
  int min_i, int min_j, int max_i, int max_j) {...CODE...}
/**
 * @brief Callback executed when a parameter change is detected
 * @param event ParameterEvent message
 */
rcl_interfaces::msg::SetParametersResult
StaticLayer::dynamicParametersCallback(std::vector<rclcpp::Parameter> parameters) {...CODE...}
}  // namespace nav2_costmap_2d
```
There are **two types of methods**:
- **Standard methods**, used by your own code: calculate something, access a topic or a database, run a deep learning algorithm — whatever your task needs.
- **API plugin methods**, overridden from the parent class `nav2_costmap_2d::Layer`. The plugin loading system calls them to perform the essential functions of the plugin, which makes plugins plug and play. They are all virtual:
```cpp
virtual void onInitialize();
virtual void activate();
virtual void deactivate();
virtual void reset();
virtual bool isClearable() {return false;}
virtual void updateBounds(
  double robot_x, double robot_y, double robot_yaw, double * min_x,
  double * min_y, double * max_x, double * max_y);
virtual void updateCosts(
  nav2_costmap_2d::Costmap2D & master_grid,
  int min_i, int min_j, int max_i, int max_j);
virtual void matchSize();
```

## Required and optional (Humble `layer.hpp`)
| Method | Required? | Role |
|---|---|---|
| `updateBounds()` | **yes** | decides how much of the costmap the layer updates, from the robot's pose and its own data; the smaller the area, the faster the plugin |
| `updateCosts()` | **yes** | updates the costs inside those bounds: on top of the costs of previous layers, or overwriting them |
| `reset()` | **yes** | run when the costmap is reset (e.g. a clear request from the behavior tree) |
| `isClearable()` | **yes** (the course omits it) | whether clearing operations should process this layer |
| `onInitialize()` | no | code run when the plugin starts: fetch parameters, initialize variables and counters |
| `matchSize()` | no | called when the map size changes; the default does nothing |
| `onFootprintChanged()` | no | for robots whose footprint changes (convertibles, tools, carried objects bigger than the robot) |

Source: [layer.hpp (humble)](https://github.com/ros-navigation/navigation2/blob/humble/nav2_costmap_2d/include/nav2_costmap_2d/layer.hpp), [costmap plugin tutorial](https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/tutorials/plugin_tutorials/writing_new_costmap2d_plugin/writing_new_costmap2d_plugin.md).

## Cost values
`unsigned char` per cell: 0 `FREE_SPACE` (no danger of hitting an obstacle), 1–252 rising cost, 253 `INSCRIBED_INFLATED_OBSTACLE`, 254 `LETHAL_OBSTACLE` (collision), 255 `NO_INFORMATION` (unknown, not "very high risk" as the course says) ([[nav2-costmap-concepts]]). The window indices `i`, `j` are cell coordinates (the `x`, `y` of the grid), not distances.

## Pitfalls
- A required method missing → the class is abstract and `PLUGINLIB_EXPORT_CLASS` fails to compile.
- Writing 255 to mean "dangerous" marks the cell as unknown; use 254 for lethal.
