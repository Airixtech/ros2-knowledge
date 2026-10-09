---
id: core-logging
title: "Logging: API, levels, CLI, log files"
domain: core
area: core-api
distro: humble
tested: false
audience: dev
summary: "rclpy/rclcpp logging calls, throttle/once/skip_first, setting levels in code and CLI, log files, severity rules."
tags: [logging, get_logger, warning, throttle_duration_sec, log-level, RCLCPP_INFO]
see: ["[[core-debug-triage]]", "[[core-ros-args]]", "[[core-bp-code-rules]]"]
requires: []
version_notes:
  - "lyrical: RcutilsLogger.warn() removed (deprecated alias since Humble); use warning() — https://github.com/ros2/rclpy/blob/lyrical/rclpy/rclpy/impl/rcutils_logger.py (V22)"
  - "jazzy: --ros-args --log-file-name; lyrical: logging backend selectable at runtime — https://docs.ros.org/en/rolling/Releases/Release-Jazzy-Jalisco.html (V25)"
---
# Logging: API, levels, CLI, log files

**TL;DR** Use `self.get_logger()` instead of `print()`, and throttle logs in fast callbacks. For warnings use `warning()`: `warn()` is a deprecated alias in Humble and is removed in Lyrical.

## Python
```python
log = self.get_logger()
log.debug('..'); log.info('..'); log.warning('..'); log.error('..'); log.fatal('..')
log.info('waiting for data', throttle_duration_sec=1.0)   # rate-limit in fast callbacks
log.info('first time only', once=True)
log.warning('recurrent', skip_first=True, throttle_duration_sec=5.0)

from rclpy.logging import LoggingSeverity
log.set_level(LoggingSeverity.DEBUG)                      # or:
rclpy.logging.set_logger_level('my_node', LoggingSeverity.DEBUG)
```
Levels: DEBUG < INFO < WARN < ERROR < FATAL. Setting level X shows X and above.

## C++
`RCLCPP_INFO(get_logger(), "x=%d", x)`, `RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 1000, "...")`, `RCLCPP_INFO_ONCE`, `RCLCPP_WARN_EXPRESSION(get_logger(), cond, "...")`.

## CLI, launch, files
```bash
ros2 run my_pkg my_node --ros-args --log-level debug                 # global
ros2 run my_pkg my_node --ros-args --log-level my_node:=debug        # per logger
ros2 run my_pkg my_node --ros-args --log-level info --log-level rcl:=warn
export RCUTILS_COLORIZED_OUTPUT=1
ls -lt ~/.ros/log/ | head ; tail -f ~/.ros/log/latest/launch.log
```
- In launch, `Node(..., output='screen', emulate_tty=True)` gives colored output.
- Log files are written to `~/.ros/log/` (latest run: `~/.ros/log/latest/`). [≥Jazzy: `--ros-args --log-file-name <prefix>`]
- Line format: `RCUTILS_CONSOLE_OUTPUT_FORMAT` ([[core-env-variables]]).

## Severity rules
DEBUG dev traces · INFO normal events · WARN unexpected but recoverable · ERROR operation failed, node alive · FATAL unrecoverable. Always throttle in >1 Hz callbacks (`throttle_duration_sec`, `RCLCPP_*_THROTTLE`).

## Pitfalls
- `get_logger().warn(...)` still works on Humble/Jazzy, but raises `AttributeError` on Lyrical.
- Unthrottled logging in a 30 Hz callback floods the console and slows the node.
- Logger names follow node names. After `-r __node:=x`, the per-logger level must use `x:=debug`.
