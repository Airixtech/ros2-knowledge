---
id: core-bag-record
title: "rosbag2 record, storage formats & scripts"
domain: core
area: tools
distro: humble
tested: false
audience: dev
summary: "ros2 bag record flags (topics, regex, exclude, mcap, compression, splitting), sqlite3 vs mcap, recording scripts and launch."
tags: [rosbag2, ros2 bag record, mcap, sqlite3, compression, regex]
see: ["[[core-bag-play]]", "[[core-launch-basics]]", "[[core-debug-tools]]"]
requires: []
version_notes:
  - "jazzy: default storage is mcap (since Iron) — https://docs.ros.org/en/rolling/Releases/Release-Iron-Irwini.html (V46)"
  - "jazzy: -a records topics AND services; -x/--exclude renamed --exclude-regex; new --topics/--services/--topic-types — https://docs.ros.org/en/rolling/Releases/Release-Jazzy-Jalisco.html (V47)"
  - "lyrical: circular recording, remote control via services, Python API — https://docs.ros.org/en/rolling/Releases/Release-Lyrical-Luth.html (V47)"
---
# rosbag2 record, storage formats & scripts

**TL;DR** Run `ros2 bag record -o name <topics>` or `-a`, and stop it with Ctrl+C so the bag is closed. Humble writes sqlite3 by default. Use `-s mcap` for big datasets; it needs `ros-humble-rosbag2-storage-mcap`.

## Record
```bash
ros2 bag record /cmd_vel /odom /scan           # specific topics
ros2 bag record -a                             # all
ros2 bag record -o my_run /cmd_vel /odom       # output folder name
ros2 bag record -e "/sensors/.*"               # regex include
ros2 bag record -a -x "/camera/.*"             # all except regex
ros2 bag record -a -s mcap                     # MCAP storage (faster; ros-humble-rosbag2-storage-mcap)
ros2 bag record -a --compression-mode file --compression-format zstd
ros2 bag record -a -b 1000000000               # split every ~1 GB (--max-bag-size)
ros2 bag record -a -d 60                       # split every 60 s (--max-bag-duration)
```
Stop with Ctrl+C (SIGINT) so the bag is closed properly.
[changed in Jazzy: `-a` records topics **and services** (use `--all-topics` for topics only); `-x/--exclude` → `--exclude-regex` (no `-x` short form in `record`); new `--topics`, `--services`, `--topic-types`, `--exclude-topics`]

## Storage
| Format | Pros | Cons |
|---|---|---|
| sqlite3 (Humble default) | universal | slower, bigger |
| mcap | fast, Foxglove-native, good for big datasets | extra pkg in Humble [changed in Jazzy: default since Iron] |

## Scripts
```bash
# record N seconds with timestamped name
NAME="session_$(date +%Y%m%d_%H%M%S)"; ros2 bag record -a -o "$NAME" & PID=$!
sleep ${1:-30}; kill -INT $PID; wait $PID
# start recording when a topic appears
until ros2 topic list | grep -q "/scan"; do sleep 1; done; ros2 bag record -a -o "lidar_$(date +%H%M%S)"
# background, detached
nohup ros2 bag record -a -o silent_bag > /dev/null 2>&1 &
```
In launch: `ExecuteProcess(cmd=['ros2', 'bag', 'record', '-a', '-o', 'auto_bag'], output='screen')` ([[core-launch-basics]]). [≥Lyrical: circular recording with a bag limit, and control via services or the Python API]

## Pitfalls
- `kill -9` instead of SIGINT leaves the bag without proper metadata. Run `ros2 bag reindex` to recover it.
- Recording raw camera topics with `-a` over Wi-Fi fills disks fast. Exclude them, or use compression.
