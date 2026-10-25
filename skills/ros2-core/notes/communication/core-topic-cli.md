---
id: core-topic-cli
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Topic CLI: list, info, echo, pub, hz"
domain: core
area: communication
distro: humble
tested: false
audience: dev
summary: "ros2 topic list/info/echo/pub/hz/bw/delay with QoS flags, message YAML syntax, debug flow, stopping a robot."
tags: [ros2 topic, echo, pub, hz, interface proto, qos-reliability]
see: ["[[core-topic-pub-sub-py]]", "[[core-qos-usage]]", "[[core-iface-std-types]]", "[[core-debug-triage]]"]
requires: []
version_notes:
  - "jazzy: echo --timeout, pub --max-wait-time, 'now'/'auto' stamp keywords, hz/bw/pub honor use_sim_time (Iron); lyrical: bw on several topics — https://docs.ros.org/en/rolling/Releases/Release-Iron-Irwini.html (V26)"
---
# Topic CLI: list, info, echo, pub, hz

**TL;DR** Debug flow: `topic list` → `topic info -v` (type, counts, QoS) → `interface show <type>` → `topic echo` / `hz`. `ros2 topic pub` keeps publishing until Ctrl+C, so stop a robot with a zero Twist.

## CLI
```bash
ros2 topic list [-t]                         # -t shows types; --include-hidden-topics
ros2 topic info /scan [-v|--verbose]         # pub/sub count, node names, QoS per endpoint
ros2 topic type /scan
ros2 topic find geometry_msgs/msg/Twist      # topics of a type
ros2 interface show sensor_msgs/msg/LaserScan
ros2 interface proto geometry_msgs/msg/Twist # YAML template for pub
ros2 topic echo /cmd_vel
ros2 topic echo /cmd_vel --once
ros2 topic echo /scan --field ranges         # one field
ros2 topic echo /scan --no-arr               # hide arrays (also --no-str, --flow-style)
ros2 topic echo /scan --qos-reliability best_effort      # BEST_EFFORT publishers
ros2 topic echo /map  --qos-durability transient_local   # latched topics
ros2 topic hz /scan [--window 50]            # rate
ros2 topic bw /scan                          # bandwidth
ros2 topic delay /odom                       # needs header.stamp
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.3}}"
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2}}"
ros2 topic pub --times 5 /chatter std_msgs/msg/String "{data: 'hi'}"
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{}"   # all zeros = stop
ros2 run rqt_image_view rqt_image_view /camera/image_raw      # view images
```
- The robot keeps executing the last `cmd_vel` it received, so send a zero Twist to stop it.
- `ros2 topic -h` lists the verbs (`bw`, `delay`, `echo`, `find`, `hz`, `info`, `list`, `pub`, `type`); `ros2 topic info` gives the type plus `Publisher count` (nodes sending) and `Subscription count` (subscriptions listening, CLI echoes included). `--field header.stamp.sec` selects sub-fields with `.`; on Humble `--field ranges` prints the raw array (`array('f', [inf, …, 3.8130645751953125, …])`).
- Message YAML: nested dicts; unspecified fields are 0/empty. CLI nodes appear as `_ros2cli_<pid>`.
- [≥Jazzy (since Iron): `echo --timeout`, `pub --max-wait-time`, the `now` keyword for `builtin_interfaces/Time` and `auto` for `std_msgs/Header` in `pub`; `hz/bw/pub` honor `use_sim_time`] [≥Lyrical: `ros2 topic bw` accepts several topics]

## Pitfalls
- The topic is listed but `echo` stays silent → QoS mismatch. Retry with `--qos-reliability best_effort` ([[core-qos-usage]]).
- Under `use_sim_time`, Humble's `hz` uses wall time. Rates from replayed bags at `-r 2` look doubled.
- Quote YAML strings inside the payload: `"{data: 'hi'}"`.
