---
id: core-param-api
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Parameters API: declare, descriptors, set callback (py & cpp)"
domain: core
area: core-api
distro: humble
tested: false
audience: dev
summary: "Declare/get parameters with descriptors and ranges, validate changes in add_on_set_parameters_callback, set from code; rclcpp equivalent."
tags: [parameters, declare_parameter, ParameterDescriptor, add_on_set_parameters_callback, SetParametersResult]
see: ["[[core-param-yaml-cli]]", "[[core-node-skeleton]]", "[[core-launch-args-include]]"]
requires: []
version_notes:
  - "jazzy: declare_parameter rejects a statically typed parameter without a default — https://docs.ros.org/en/rolling/Releases/Release-Jazzy-Jalisco.html (V37)"
  - "jazzy: pre/post set-parameter callbacks added (Iron) — https://docs.ros.org/en/rolling/Releases/Release-Iron-Irwini.html (V38)"
---
# Parameters API: declare, descriptors, set callback

**TL;DR** ALWAYS declare a parameter before reading it. The default value fixes the type. Validate and apply runtime changes in `add_on_set_parameters_callback`.

## Python API
```python
from rcl_interfaces.msg import FloatingPointRange, ParameterDescriptor, SetParametersResult
from rclpy.node import Node
from rclpy.parameter import Parameter

class Controller(Node):
    def __init__(self):
        super().__init__('controller')
        self.declare_parameter('rate_hz', 10.0)                               # ALWAYS declare before get
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('kp', 1.0, ParameterDescriptor(
            description='Proportional gain',
            floating_point_range=[FloatingPointRange(from_value=0.0, to_value=10.0, step=0.0)]))
        self.declare_parameters(namespace='', parameters=[('ki', 0.0), ('kd', 0.0)])
        self.kp = self.get_parameter('kp').value                                # .value -> python type
        self.add_on_set_parameters_callback(self.on_set_params)                # runtime validation/update

    def on_set_params(self, params):
        for p in params:
            if p.name == 'kp':
                if p.value < 0.0:
                    return SetParametersResult(successful=False, reason='kp must be >= 0')
                self.kp = p.value                                               # apply new value
        return SetParametersResult(successful=True)

    def set_kp(self, value):                       # set from code (also triggers on_set_params)
        self.set_parameters([Parameter('kp', Parameter.Type.DOUBLE, value)])
```
- The default value fixes the type: `1.0` → double, `1` → int. Lists: `self.declare_parameter('frames', ['base_link', 'laser'])`.
- Every node has the built-in parameter `use_sim_time` (bool) ([[core-time-timers]]).
- [≥Jazzy (since Iron): `add_pre_set_parameters_callback` / `add_post_set_parameters_callback` are also available.]

## C++ API
```cpp
declare_parameter<double>("kp", 1.0);
double kp = get_parameter("kp").as_double();
param_cb_ = add_on_set_parameters_callback(
  [this](const std::vector<rclcpp::Parameter> & ps) {
    rcl_interfaces::msg::SetParametersResult r; r.successful = true;
    for (const auto & p : ps) if (p.get_name() == "kp" && p.as_double() < 0.0) { r.successful = false; r.reason = "kp>=0"; }
    return r; });   // keep param_cb_ (OnSetParametersCallbackHandle::SharedPtr) alive
```

## Pitfalls
- `get_parameter` on an undeclared name → `ParameterNotDeclaredException`. Declare it first, or pass `automatically_declare_parameters_from_overrides=True` in the Node kwargs.
- The set callback only validates. Store the new value yourself (`self.kp = p.value`), or the code keeps using the old one.
- [changed in Jazzy: `declare_parameter('x')` with a static type but no default value is rejected]
