---
id: control-custom-init
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Custom controller .cpp skeleton, constructor, on_init with auto_declare of joints and interface_name"
domain: control
area: controllers
distro: jazzy
tested: false
audience: dev
summary: "rrbot_controller.cpp skeleton: includes, namespace, constructor; on_init declares joints and interface_name with auto_declare; ERROR means the controller is not loaded."
tags: [custom controller, rrbot_controller.cpp, RRBotController, constructor, on_init, auto_declare, declare_parameter, joints, interface_name, CallbackReturn, Could not initialize the controller]
see: ["[[control-custom-header]]", "[[control-custom-configure]]", "[[control-controller-lifecycle]]", "[[control-custom-config-launch]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: an on_init() ERROR or FAILURE shuts the controller node down and the controller manager does not load it ('Could not initialize the controller named …'); the course only says 'finalized' — https://github.com/ros-controls/ros2_control/blob/jazzy/controller_interface/src/controller_interface_base.cpp (CONTROL-V75)"
  - "jazzy: auto_declare declares the parameter if needed and returns its value (Humble to Lyrical); controller node options: jazzy enable_logger_service only (undeclared parameters throw), humble allow_undeclared_parameters + automatically_declare_parameters_from_overrides — https://github.com/ros-controls/ros2_control/blob/jazzy/controller_interface/include/controller_interface/controller_interface_base.hpp (CONTROL-V77)"
---
# Custom controller .cpp skeleton, constructor, on_init with auto_declare of joints and interface_name

**TL;DR** `src/rrbot_controller.cpp` defines every method of the header inside the package namespace. `on_init()` only declares the parameters the controller accepts, so their names and types are fixed at startup and a wrong configuration shows up early.

## src/rrbot_controller.cpp (skeleton)
```cpp
// Copyright (c) 2021, Bence Magyar and Denis Stogl. Licensed under the Apache License, Version 2.0.
#include "rrbot_controller/rrbot_controller.hpp"

#include <cmath>  // std::isnan in update(); the course relies on other headers for it
#include <limits>
#include <memory>
#include <string>
#include <vector>

namespace rrbot_controller
{
RRBotController::RRBotController() : controller_interface::ControllerInterface() {}

// All the methods added must be inside this namespace

}  // namespace rrbot_controller
```
The constructor calls the base class's default constructor in its initializer list. Every method of the following notes goes **inside** the namespace braces; only the plugin macro goes after them ([[control-custom-plugin-export]]).

## on_init()
```cpp
CallbackReturn RRBotController::on_init() {
  try {
    auto_declare("joints", std::vector<std::string>());
    auto_declare("interface_name", std::string());
  } catch (const std::exception &e) {
    fprintf(stderr, "Exception thrown during init stage with message: %s \n",
            e.what());
    return CallbackReturn::ERROR;
  }

  return CallbackReturn::SUCCESS;
}
```
- `auto_declare(name, default)` declares the parameter on the controller's node if it is not declared yet and returns its value; a value from the controller YAML replaces the default ([[control-custom-config-launch]]). The values are read and checked later, in `on_configure()` ([[control-custom-configure]]).
- The try/catch turns a failed declaration into `CallbackReturn::ERROR`. Then the controller's node is shut down (finalized, as the course says), and the controller manager logs "Could not initialize the controller named '<name>'" and does not load the controller at all: it never appears in `ros2 control list_controllers`.

## Pitfalls
- Reading or checking parameter values in `on_init()` instead of `on_configure()`: a later reconfigure would not see new values.
- A parameter read in the code but never declared → `get_parameter()` throws `ParameterNotDeclaredException`. [Humble: controller nodes allow undeclared parameters and declare the YAML keys automatically, so it reads as unset and `as_string()` throws instead]. A misspelled YAML key is ignored without an error. Declare every parameter with a default.
