---
id: core-recipe-command-goals
title: "String command to goal state machine & event messages"
domain: core
area: recipes
distro: humble
tested: false
audience: dev
summary: "Map String commands to goals, drive with a 10 Hz control timer, publish status and custom events with robot pose."
tags: [state machine, String, goals, status, custom msg, event]
see: ["[[core-recipe-odom-go-to-goal]]", "[[core-iface-syntax-usage]]", "[[core-learn-unit3-topics]]"]
requires: []
version_notes: []
---
# String command to goal state machine & event messages

**TL;DR** A subscription callback only *selects* the goal and sets `active`. A 10 Hz timer does the driving and publishes `goal-reached`. It ignores unknown commands and commands for a goal the robot is already at.

## String command → goal state machine
```python
GOALS = {'Go-Home': (0.0, 0.0), 'Go-Pickup': (-2.342, -2.432)}

def on_mission(self, msg):                               # std_msgs/String on /nasa_mission
    goal = GOALS.get(msg.data)
    if goal is None:
        self.get_logger().warning(f'unknown command {msg.data}')
        return
    if math.hypot(goal[0] - self.x, goal[1] - self.y) < self.tol:
        return                                           # already there: ignore
    self.goal, self.active = goal, True
    self.status_pub.publish(String(data='moving'))

def on_control_timer(self):                              # 10 Hz
    if not self.active:
        return
    cmd = self.drive_to(*self.goal, tol=self.tol)
    if cmd.linear.x == 0.0 and cmd.angular.z == 0.0:
        self.active = False
        self.status_pub.publish(String(data='goal-reached'))
    self.cmd_pub.publish(cmd)
```
`drive_to` is in [[core-recipe-odom-go-to-goal]]. Test it with `ros2 topic pub --once /nasa_mission std_msgs/msg/String "data: 'Go-Home'"`.

## Publish an event with location (custom msg)
```python
ev = RoverEvents()
ev.info.data = f'Plant detected ({conf:.2f})'
if self.current_odom is not None:
    ev.rover_location = self.current_odom.pose.pose     # latest odom stored by on_odom
self.event_pub.publish(ev)
```
`RoverEvents` definition and package: [[core-iface-package]].

## Pitfalls
- Driving inside the subscription callback only moves the robot when a new command arrives. Keep the control loop in a timer.
- Read `self.x`/`self.y` only after the first odom message. Initialize them, or `spin_once` before starting ([[core-exec-spin]]).
