---
id: core-iface-syntax-usage
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Interface definition syntax & use in Python/C++"
domain: core
area: core-api
distro: humble
tested: false
audience: dev
summary: ".msg/.srv/.action field syntax (arrays, bounds, defaults, constants) and how to build and fill messages in Python and C++."
tags: [msg, srv, action, rosidl, field types, Request, Goal]
see: ["[[core-iface-package]]", "[[core-iface-std-types]]", "[[core-srv-server]]", "[[core-action-server]]"]
requires: []
version_notes: []
---
# Interface definition syntax & use in Python/C++

**TL;DR** Types are `PascalCase` and fields `snake_case`. A `.srv` is request `---` response, and an `.action` is goal `---` result `---` feedback. In Python, use `Type.Request()`, `Type.Goal()`, etc., or keyword constructors.

## Definition syntax
```
# comment
int32 count                 # primitives: bool byte char float32 float64 int8..int64 uint8..uint64 string wstring
float64[] values            # unbounded array (Python list)
float64[3] xyz              # fixed array
int32[<=10] small           # bounded array
string<=32 name             # bounded string
geometry_msgs/Pose pose     # nested type from another pkg (pkg/Type)
Header header               # std_msgs/Header (same-pkg types need no prefix)
int32 speed 5               # default value
int32 MAX_SPEED=10          # constant (UPPER_CASE)
```
Type names are `PascalCase`, field names `snake_case`. `int32` (a primitive) ≠ `std_msgs/Int32` (a message with `.data`).
`.srv`: `request` `---` `response`. `.action`: `goal` `---` `result` `---` `feedback`. The separators are mandatory even if a part is empty.

## Use in Python
```python
from custom_interfaces.msg import RoverEvents
from custom_interfaces.srv import TextRecognition
from custom_interfaces.action import GoToPose

ev = RoverEvents()
ev.info.data = 'plant found'                       # nested std_msgs/String
ev.rover_location = odom_msg.pose.pose             # assign whole nested msg
ev.rover_location.position.x = 1.0

req = TextRecognition.Request(); req.label = 'FOOD'   # srv: .Request() / .Response()
goal = GoToPose.Goal(x=-8.0, y=6.0, yaw=1.57)          # action: .Goal() .Result() .Feedback()
res = GoToPose.Result(success=True)                    # kwargs constructor works for all
```
C++: `#include "custom_interfaces/msg/rover_events.hpp"` → `custom_interfaces::msg::RoverEvents` (the header is the snake_case of the type).
The definitions of these example types and their package setup: [[core-iface-package]].

## Pitfalls
- Assigning a value of the wrong Python type (e.g. an `int` to a `float64` field) raises an `AssertionError` at assignment time.
- A missing `---` in a `.srv`/`.action` makes rosidl fail at build time with a parse error.
