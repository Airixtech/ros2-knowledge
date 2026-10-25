---
id: control-custom-configure
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Custom controller on_configure: read and check parameters, ~/commands subscriber into a RealtimeBuffer, ~/state RealtimePublisher"
domain: control
area: controllers
distro: jazzy
tested: false
audience: dev
summary: "on_configure: get joints/interface_name, ERROR if empty; JointJog subscriber on ~/commands writes a RealtimeBuffer; JointControllerState RealtimePublisher on ~/state."
tags: [custom controller, on_configure, get_parameter, as_string_array, lambda, create_subscription, commands, JointJog, RealtimeBuffer, writeFromNonRT, create_publisher, RealtimePublisher, state, lock, unlock, msg_, SystemDefaultsQoS]
see: ["[[control-custom-header]]", "[[control-custom-init]]", "[[control-custom-interfaces]]", "[[control-custom-activate-update]]", "[[control-jazzy-to-lyrical]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: the callback checks only the number of joint names; a JointJog with fewer displacements makes update() read past the vector, and the names are not compared — https://github.com/ros-controls/control_msgs/blob/jazzy/control_msgs/msg/JointJog.msg (CONTROL-V57)"
  - "kilted: RealtimePublisher msg_, lock(), unlock() deprecated; lyrical: removed (try_publish only), constructor from a publisher deprecated, RealtimeBuffer deprecated — https://github.com/ros-controls/realtime_tools/blob/master/realtime_tools/include/realtime_tools/realtime_publisher.hpp (CONTROL-V73)"
---
# Custom controller on_configure: read and check parameters, ~/commands subscriber into a RealtimeBuffer, ~/state RealtimePublisher

**TL;DR** `on_configure()` runs before the controller can be activated, so `update()` later finds everything ready. It reads the parameters declared in `on_init()`, refuses empty ones, creates the command subscriber and the state publisher.

## on_configure()
```cpp
CallbackReturn RRBotController::on_configure(
    const rclcpp_lifecycle::State & /*previous_state*/) {
  auto error_if_empty = [&](const auto &parameter, const char *parameter_name) {
    if (parameter.empty()) {
      RCLCPP_ERROR(get_node()->get_logger(), "'%s' parameter was empty",
                   parameter_name);
      return true;
    }
    return false;
  };

  auto get_string_array_param_and_error_if_empty =
      [&](std::vector<std::string> &parameter, const char *parameter_name) {
        parameter = get_node()->get_parameter(parameter_name).as_string_array();
        return error_if_empty(parameter, parameter_name);
      };

  auto get_string_param_and_error_if_empty =
      [&](std::string &parameter, const char *parameter_name) {
        parameter = get_node()->get_parameter(parameter_name).as_string();
        return error_if_empty(parameter, parameter_name);
      };

  if (get_string_array_param_and_error_if_empty(joint_names_, "joints") ||
      get_string_param_and_error_if_empty(interface_name_, "interface_name")) {
    return CallbackReturn::ERROR;
  }

  // Command Subscriber and callbacks
  auto callback_command =
      [&](const std::shared_ptr<ControllerCommandMsg> msg) -> void {
    if (msg->joint_names.size() == joint_names_.size()) {
      input_command_.writeFromNonRT(msg);
    } else {
      RCLCPP_ERROR(get_node()->get_logger(),
                   "Received %zu , but expected %zu joints in command. "
                   "Ignoring message.",
                   msg->joint_names.size(), joint_names_.size());
    }
  };
  command_subscriber_ = get_node()->create_subscription<ControllerCommandMsg>(
      "~/commands", rclcpp::SystemDefaultsQoS(), callback_command);

  // State publisher
  s_publisher_ =
      get_node()->create_publisher<ControllerStateMsg>(
          "~/state", rclcpp::SystemDefaultsQoS());
  state_publisher_ = std::make_unique<ControllerStatePublisher>(s_publisher_);

  state_publisher_->lock();
  state_publisher_->msg_.header.frame_id = joint_names_[0];
  state_publisher_->unlock();

  RCLCPP_INFO_STREAM(get_node()->get_logger(), "configure successful");
  return CallbackReturn::SUCCESS;
}
```

## What it does
- Three lambdas: one returns `true` (and logs) when a value is empty; one reads a string array parameter (`joints`), one a string (`interface_name`), each followed by the empty check. Either empty → `CallbackReturn::ERROR`, the controller stays unconfigured.
- The subscriber's callback runs in the executor thread, not in the control loop. It accepts a message only when it names as many joints as the controller has and puts it into the `RealtimeBuffer`; `update()` takes the newest one from there without waiting ([[control-custom-activate-update]]).
- `~/commands` and `~/state` are relative to the controller's node: `/rrbot_controller/commands` and `/rrbot_controller/state`.
- The `RealtimePublisher` publishes from its own thread, so the control loop never blocks on the middleware. `lock()`/`unlock()` keep another thread from touching `msg_` while the header's `frame_id` is set.

## Check the values too
The callback compares only the number of names. A `JointJog` that carries the right number of names but fewer `displacements` (for example only `velocities`) makes `update()` read past the end of the vector, and a message with the joints in another order commands the wrong joints. Check both [verify build]:
```cpp
    if (msg->joint_names.size() == joint_names_.size() &&
        msg->displacements.size() == joint_names_.size()) {
      input_command_.writeFromNonRT(msg);
    } else {
      // log and ignore the message, as above
    }
```
Comparing `msg->joint_names` with `joint_names_` element by element also catches the order.

## Versions
The code is valid on Humble and Jazzy. [changed in Kilted: `msg_`, `lock()` and `unlock()` of `RealtimePublisher` are deprecated]. [changed in Lyrical: they are removed: keep your own `ControllerStateMsg` and call `try_publish(msg)`, and build the publisher with `ControllerStatePublisher(get_node(), "~/state", rclcpp::SystemDefaultsQoS())`; `RealtimeBuffer` is deprecated in favour of `RealtimeThreadSafeBox`]. The Lyrical form: [[control-jazzy-to-lyrical]].

## Pitfalls
- `joint_names_[0]` with an empty list would crash: the empty check before it is what makes it safe.
- Creating publishers or subscribers in `update()` instead of here allocates memory in the control loop.
