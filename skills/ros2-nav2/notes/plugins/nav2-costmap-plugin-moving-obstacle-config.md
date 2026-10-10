---
id: nav2-costmap-plugin-moving-obstacle-config
title: "Moving-obstacle costmap layer: description XML, CMake, YAML and launch"
domain: nav2
area: plugins
distro: humble
tested: false
audience: dev
summary: "Exercise EX.1 integration: my_custom_costmap_plugininfo.xml, second library in CMake, package.xml export, my_crazy_layer parameters in the global costmap, launch fixes."
tags: [my_custom_costmap_plugininfo.xml, MyCrazyCustomCostmapLayer_Plugin_Name, my_custom_costmap_core, my_crazy_layer, my_custom_crazy_costmap, pathplanner_custom_crazy_costmap.launch.py, x_oscilation_height, y_oscilation_range, obstacle_radius]
see: ["[[nav2-costmap-plugin-moving-obstacle]]", "[[nav2-costmap-plugin-package]]", "[[nav2-plugin-description-xml]]", "[[nav2-plugin-test-launch]]"]
requires: [ros2-core]
version_notes:
  - "humble: the course's launch starts nav2_recoveries/recoveries_server (absent in Humble) and passes default_bt_xml_filename (ignored); fixed below — https://github.com/ros-navigation/docs.nav2.org/blob/rolling/docs/configuration_and_development/migration_guides/galactic/Galactic.md (NAV2-V52, NAV2-V51)"
---
# Moving-obstacle costmap layer: description XML, CMake, YAML and launch

**TL;DR** How the `MyCustomCostmap` layer of [[nav2-costmap-plugin-moving-obstacle]] is built and loaded: a second library in `custom_nav2_costmap_plugin`, its description file, its parameters in the global costmap, and a launch with Humble-correct nodes.

## Description file, build and configuration
- `my_custom_costmap_plugininfo.xml` ([[nav2-plugin-description-xml]]):
  ```xml
  <library path="my_custom_costmap_core">
    <class name="MyCrazyCustomCostmapLayer_Plugin_Name" type="my_custom_costmap_namespace_name::MyCustomCostmap" base_class_type="nav2_costmap_2d::Layer">
      <description>This is a Crazy costmap layer created for fun</description>
    </class>
  </library>
  ```
- `CMakeLists.txt` of `custom_nav2_costmap_plugin` ([[nav2-costmap-plugin-package]]) adds a second library:
  ```cmake
  set(my_custom_costmap_lib_name my_custom_costmap_core)
  add_library(${my_custom_costmap_lib_name} SHARED
    src/my_custom_costmap.cpp)
  install(TARGETS ${my_custom_costmap_lib_name}
    DESTINATION lib)
  pluginlib_export_plugin_description_file(nav2_costmap_2d my_custom_costmap_plugininfo.xml)
  ament_target_dependencies(${my_custom_costmap_lib_name} ${dep_pkgs})
  ```
  and its `BUILD_TESTING` block keeps the commented `ament_cmake_copyright_FOUND` / `ament_cmake_cpplint_FOUND` lines of `ros2 pkg create`. `package.xml` adds `<costmap_2d plugin="${prefix}/my_custom_costmap_plugininfo.xml" />` to its `<export>`.
- `config/my_custom_crazy_costmap/planner_server.yaml`: global costmap plugins and the layer parameters (`controller.yaml` of that folder: `controller_frequency: 5.0`, local costmap with only `voxel_layer`):
  ```yaml
        plugins: ["static_layer", "obstacle_layer", "my_crazy_layer"]
        # ...
        my_crazy_layer:
          plugin: "MyCrazyCustomCostmapLayer_Plugin_Name"
          enabled: True
          x_oscilation_height : 700.0
          y_oscilation_range : 100.0
          obstacle_radius : 15
  ```
- `launch/pathplanner_custom_crazy_costmap.launch.py`: the path planning launch with both YAML files from `config/my_custom_crazy_costmap/`, and `setup.py` installs that folder. Humble-correct nodes:
  ```python
  Node(package='nav2_behaviors', executable='behavior_server', name='behavior_server',   # course: nav2_recoveries / recoveries_server
       parameters=[recovery_yaml], output='screen'),
  Node(package='nav2_bt_navigator', executable='bt_navigator', name='bt_navigator', output='screen',
       parameters=[bt_navigator_yaml, {'default_nav_to_pose_bt_xml': default_bt_xml_path}]),
  Node(package='nav2_lifecycle_manager', executable='lifecycle_manager', name='lifecycle_manager_pathplanner',
       output='screen',
       parameters=[{'autostart': True},
                   {'node_names': ['controller_server', 'planner_server', 'behavior_server', 'bt_navigator']}])
  ```
