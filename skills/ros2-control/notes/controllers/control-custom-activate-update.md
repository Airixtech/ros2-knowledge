---
id: control-custom-activate-update
type: reference
owner: equipo-ros2
updated: 2026-10-24
review_by: 2027-04-22
source: manual
confidentiality: internal
title: "Custom controller on_activate (NaN default command), on_deactivate, update (readFromRT, set_value, state publisher)"
domain: control
area: controllers
distro: jazzy
tested: false
audience: dev
summary: "on_activate writes a NaN JointJog default, on_deactivate returns SUCCESS, update forwards displacements with set_value, publishes JointControllerState via trylock."
tags: [custom controller, on_activate, on_deactivate, update, quiet_NaN, writeFromNonRT, readFromRT, set_value, get_optional, get_value, nodiscard, trylock, unlockAndPublish, JointControllerState, set_point, return_type]
see: ["[[control-custom-configure]]", "[[control-custom-interfaces]]", "[[control-custom-plugin-export]]", "[[control-controller-lifecycle]]", "[[control-humble-to-jazzy]]", "[[control-jazzy-to-lyrical]]"]
requires: [ros2-core]
version_notes:
  - "jazzy: the writeFromNonRT condition the course quotes does not hold (the ~/commands callback writes too); the controller manager normally runs on_activate inside its real-time update(); Jazzy's example_7 uses RealtimeThreadSafeBox — https://github.com/ros-controls/ros2_control_demos/blob/jazzy/example_7/controller/r6bot_controller.cpp (CONTROL-V56)"
  - "jazzy: bool set_value and get_optional (7.13); humble: void set_value and get_value (the appendix form); kilted/lyrical: double get_value removed — https://github.com/ros-controls/ros2_control/blob/jazzy/hardware_interface/include/hardware_interface/handle.hpp (CONTROL-V74)"
  - "jazzy: update() reads displacements[i] without checking the message size (CONTROL-V57)"
  - "jazzy: an update() ERROR deactivates the controller and activates its fallback controllers; humble: only logged — https://github.com/ros-controls/ros2_control/blob/jazzy/controller_manager/src/controller_manager.cpp (CONTROL-V77)"
  - "lyrical: trylock/unlockAndPublish/msg_ removed, use try_publish — https://github.com/ros-controls/realtime_tools/blob/master/realtime_tools/include/realtime_tools/realtime_publisher.hpp (CONTROL-V73)"
---
# Custom controller on_activate (NaN default command), on_deactivate, update (readFromRT, set_value, state publisher)

**TL;DR** `on_activate()` stores a "no command yet" message, `on_deactivate()` has nothing to clean up, and `update()`, called in every control cycle, writes the newest command to the joints and publishes a state message. The controller is a forward command controller for `JointJog` messages.

## on_activate() and on_deactivate()
```cpp
CallbackReturn RRBotController::on_activate(
    const rclcpp_lifecycle::State & /*previous_state*/) {
  // Set default value in command
  std::shared_ptr<ControllerCommandMsg> msg =
      std::make_shared<ControllerCommandMsg>();
  msg->joint_names = joint_names_;
  msg->displacements.resize(joint_names_.size(),
                            std::numeric_limits<double>::quiet_NaN());
  input_command_.writeFromNonRT(msg);

  return CallbackReturn::SUCCESS;
}

CallbackReturn RRBotController::on_deactivate(
    const rclcpp_lifecycle::State & /*previous_state*/) {
  return CallbackReturn::SUCCESS;
}
```
- The default command has one `quiet_NaN` (quiet not-a-number) per joint: `update()` skips NaN values, so until the first message nothing is written.
- The course explains that `writeFromNonRT()` may be used in real time if no non-real-time thread calls it at the same moment and there is a single real-time thread. That condition does not hold here: the `~/commands` callback ([[control-custom-configure]]) calls it too. It waits for the buffer's mutex (retrying every 0.5 ms), and the controller manager normally runs the switch, and with it `on_activate()`, inside its real-time loop. Jazzy's official custom controller (ros2_control_demos example_7) uses `realtime_tools::RealtimeThreadSafeBox` instead: `set(msg)` in the callback, `try_get()` in `update()`.
- `on_deactivate()` is called when the controller is stopped. Often it only returns success; code for a graceful stop must be as real-time friendly as the rest.

## update()
```cpp
controller_interface::return_type
RRBotController::update(const rclcpp::Time &time,
                        const rclcpp::Duration & /*period*/) {
  auto current_command = input_command_.readFromRT();

  for (size_t i = 0; i < command_interfaces_.size(); ++i) {
    if (!std::isnan((*current_command)->displacements[i])) {
      bool ok = command_interfaces_[i].set_value((*current_command)->displacements[i]);
      if (!ok) {
        RCLCPP_WARN(get_node()->get_logger(),
                    "Failed to set command for joint %zu", i);
      }
    }
  }

  if (state_publisher_ && state_publisher_->trylock()) {
    state_publisher_->msg_.header.stamp = time;
    auto opt_value = command_interfaces_[0].get_optional();
    if (opt_value.has_value()) {
      state_publisher_->msg_.set_point = opt_value.value();
    } else {
      // fallback if no value available yet
      state_publisher_->msg_.set_point =
          std::numeric_limits<double>::quiet_NaN();
    }
    state_publisher_->unlockAndPublish();
  }

  return controller_interface::return_type::OK;
}
```
- `readFromRT()` returns a pointer to the newest message without blocking.
- Each `displacements[i]` goes unchanged to `command_interfaces_[i]` (joint `joint_names_[i]`, [[control-custom-interfaces]]). `set_value()` returns `false` when another thread holds the interface's lock at that moment; `get_optional()` then returns no value. The interface named by `interface_name` receives the numbers whatever it is: with `velocity` the "displacements" become velocities.
- The state message carries the time and the first joint's command as `set_point`; `trylock()` skips publishing when the publisher thread is still busy, and `unlockAndPublish()` hands the message over.

## The appendix's update()
The course's complete `rrbot_controller.cpp` (appendix of 7.20) has the older form of two lines:
```cpp
      command_interfaces_[i].set_value((*current_command)->displacements[i]);
```
```cpp
    state_publisher_->msg_.set_point = command_interfaces_[0].get_value();
```
[Humble: this is the form that compiles: `set_value()` returns nothing and `get_optional()` does not exist]. [changed in Jazzy: it compiles with warnings (`[[nodiscard]]` result ignored, deprecated `get_value()`)]. [changed in Kilted: `double get_value()` is removed, the appendix does not compile]. The rest of the appendix is the code of these notes in one file.

## Pitfalls
- A `JointJog` with fewer `displacements` than joints makes the loop read past the vector: check the size in the callback ([[control-custom-configure]]).
- Returning `return_type::ERROR` from `update()` makes the controller manager deactivate the controller ("Deactivating controllers : [ … ] as their update resulted in an error!") and start its fallback controllers if any [Humble: it only logs "The update call of the following controller returned an error"]. To skip a cycle, write nothing and return `OK`.
- [changed in Lyrical: `trylock()`, `msg_` and `unlockAndPublish()` are removed; fill a member message and call `try_publish(msg)`: [[control-jazzy-to-lyrical]]].
