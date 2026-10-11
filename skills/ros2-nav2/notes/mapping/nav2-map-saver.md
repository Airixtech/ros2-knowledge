---
id: nav2-map-saver
type: reference
owner: equipo-ros2
updated: 2026-10-10
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Saving a map with map_saver_cli (pgm + yaml)"
domain: nav2
area: mapping
distro: humble
tested: false
audience: dev
summary: "ros2 run nav2_map_server map_saver_cli -f name: output files, thresholds, map YAML fields (resolution, origin, occupied_thresh, free_thresh, negate)."
tags: [map_saver_cli, nav2_map_server, pgm, map yaml, occupied_thresh, free_thresh, resolution, origin]
see: ["[[nav2-map-server]]", "[[nav2-cartographer-launch]]", "[[nav2-map-concepts]]"]
requires: [ros2-core]
version_notes:
  - "humble: map_saver_cli options -f, -t, --occ, --free, --mode, --fmt; defaults free 0.25 / occupied 0.65; same in Jazzy and Lyrical — https://github.com/ros-navigation/navigation2/blob/humble/nav2_map_server/src/map_saver/main_cli.cpp (NAV2-V36)"
---
# Saving a map with map_saver_cli (pgm + yaml)

**TL;DR** While SLAM is still running, `map_saver_cli` (a `map_saver` node from `nav2_map_server`) subscribes to `/map` and writes `<name>.pgm` + `<name>.yaml` **in the current directory**.

## Save
```bash
cd ~/ros2_ws/src/cartographer_slam/config
ros2 run nav2_map_server map_saver_cli -f turtlebot_area
```
Expected output:
```
[INFO] [1668679453.925832478] [map_saver]:
        map_saver lifecycle node launched.
        Waiting on external lifecycle transitions to activate
        See https://design.ros2.org/articles/node_lifecycle.html for more information.
[INFO] [1668679453.925942610] [map_saver]: Creating
[INFO] [1668679453.926403154] [map_saver]: Saving map from 'map' topic to 'turtlebot_area' file
[WARN] [1668679453.926451020] [map_saver]: Free threshold unspecified. Setting it to default value: 0.250000
[WARN] [1668679453.926488575] [map_saver]: Occupied threshold unspecified. Setting it to default value: 0.650000
[WARN] [map_io]: Image format unspecified. Setting it to: pgm
[INFO] [map_io]: Received a 160 X 141 map @ 0.05 m/pix
[INFO] [map_io]: Writing map occupancy data to turtlebot_area.pgm
[INFO] [map_io]: Writing map metadata to turtlebot_area.yaml
[INFO] [map_io]: Map saved
[INFO] [1668679454.042853506] [map_saver]: Map saved successfully
[INFO] [1668679454.042968106] [map_saver]: Destroying
```
Options: `-f <file>` (name without extension), `-t <topic>` (default `map`), `--occ <0..1>`, `--free <0..1>`, `--mode trinary|scale|raw`, `--fmt pgm|png|…`.

## Output files
- `turtlebot_area.pgm`: the occupancy grid as an image.
- `turtlebot_area.yaml`: the map metadata (resolution, origin, thresholds):
```yaml
image: turtlebot_area.pgm
mode: trinary
resolution: 0.05
origin: [-5.9, -5.22, 0]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.25
```
| Field | Meaning |
|---|---|
| `image` | name of the file with the map image |
| `resolution` | resolution of the map, in meters/pixel |
| `origin` | coordinates (x, y, yaw) of the lower-left pixel of the map; the third value is the rotation, 0 if none |
| `occupied_thresh` | pixels with a value greater than this are occupied (obstacle) |
| `free_thresh` | pixels with a value smaller than this are completely free |
| `negate` | inverts the colors; by default white = free and black = occupied |

## Pitfalls
- **Do not close the SLAM (Cartographer) node before saving**: the map exists only in its memory.
- The files land where you run the command: `cd` into the package `config/` first, then rebuild so they are installed.
- Edit the `.pgm` (e.g. with GIMP) to erase objects that should not be obstacles, such as another robot ([[nav2-multirobot-mapping]]).
