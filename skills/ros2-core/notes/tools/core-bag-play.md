---
id: core-bag-play
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "rosbag2 info, play with sim time & convert"
domain: core
area: tools
distro: humble
tested: false
audience: dev
summary: "ros2 bag info/play flags (rate, loop, topics, clock, offset, pause), replaying with use_sim_time, converting sqlite3↔mcap."
tags: [rosbag2, ros2 bag play, clock, use_sim_time, convert, rqt_bag]
see: ["[[core-bag-record]]", "[[core-time-timers]]", "[[core-tf-basics]]"]
requires: []
version_notes:
  - "jazzy: play adds --exclude-regex/-x, --services, --publish-service-requests, --playback-duration — https://docs.ros.org/en/rolling/Releases/Release-Jazzy-Jalisco.html (V49)"
  - "lyrical: play several bags with -i (Kilted), progress bar — https://docs.ros.org/en/rolling/Releases/Release-Kilted-Kaiju.html (V49)"
---
# rosbag2 info, play with sim time & convert

**TL;DR** Replay with `ros2 bag play name --clock`, and run your nodes with `use_sim_time:=true`. Otherwise TF fails with extrapolation errors. In Humble, `ros2 bag convert -o` takes a YAML options file.

## Inspect / play
```bash
ros2 bag info my_run                           # duration, topics, counts, size
ros2 bag play my_run
ros2 bag play my_run -r 2.0                    # rate (0.5 = slow motion)
ros2 bag play my_run -l                        # loop
ros2 bag play my_run --topics /scan /odom
ros2 bag play my_run --clock                   # publish /clock (needed for use_sim_time)
ros2 bag play my_run --start-offset 10.0       # skip first 10 s
ros2 bag play my_run --start-paused            # space = pause/resume
ros2 run rqt_bag rqt_bag                       # GUI timeline
```
Replay with your nodes in bag time:
```bash
ros2 bag play my_run --clock                                  # T1
ros2 run my_pkg my_node --ros-args -p use_sim_time:=true      # T2 (else TF extrapolation errors)
```
[≥Jazzy: `--exclude-regex/-x`, `--services`, `--publish-service-requests`, `--playback-duration`] [≥Lyrical: `ros2 bag play -i bag1 -i bag2` (Kilted), progress bar]

## QoS on replay
A bag stores the QoS each topic was **recorded** with, and `play` offers it again (`ros2 topic info /scan --verbose` shows the same profile on the replayed topic). To replay with another QoS (a profile that is too strict, or to test a stricter system), pass an override file:
```yaml
# qos_override.yaml
/scan:
  reliability: reliable
  history: keep_all
  deadline:
    sec: 1
    nsec: 100
```
```bash
ros2 bag record /scan -o neobotixs_mp400_scan_bag
ros2 bag play --remap /scan:=/scan2 --qos-profile-overrides-path qos_override.yaml -l neobotixs_mp400_scan_bag
ros2 topic info /scan2 --verbose     # Reliability: RELIABLE, Deadline: 1000000100 nanoseconds
```
`--remap /scan:=/scan2` keeps the replay apart while the robot still publishes `/scan`. Durations need both `sec` and `nsec`. In RViz2, set each laser display's QoS to match the topic you add.

## Convert storage (Humble: -o takes a YAML file)
```yaml
# out.yaml
output_bags:
  - uri: my_run_mcap
    storage_id: mcap
```
```bash
ros2 bag convert -i my_run -o out.yaml
```
The same syntax works in Jazzy, where `StorageOptions` can also trim by `start_time_ns`/`end_time_ns`.

## Pitfalls
- `--clock` without `use_sim_time:=true` on the nodes (or the reverse) → TF extrapolation errors ([[core-time-timers]]).
- Playing a bag while the real robot or sim also publishes the same topics → two publishers per topic and TF ([[core-tf-basics]]).
