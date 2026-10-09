---
id: core-bp-code-rules
title: "Error handling & rclpy/rclcpp coding rules"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "Never let callbacks raise; retry with backoff; error-handling anti-patterns; rclpy and rclcpp coding rules incl. loaned messages."
tags: [error handling, best practices, rclpy, rclcpp, exceptions, loaned messages]
see: ["[[core-logging]]", "[[core-exec-callback-groups]]", "[[core-composition]]", "[[core-node-skeleton]]"]
requires: []
version_notes: []
---
# Error handling & rclpy/rclcpp coding rules

**TL;DR** Catch exceptions inside callbacks and log them with context, because an uncaught exception kills the spin. Follow the rclpy and rclcpp rules below to avoid deadlocks, leaks and dangling pointers.

## Error handling
```python
def on_msg(self, msg):
    try:
        self.pub.publish(self.process(msg))
    except ValueError as e:
        self.get_logger().warning(f'invalid input: {e}')
    except Exception as e:                                # never let a callback raise
        self.get_logger().error(f'unexpected: {e!r}')
```
```cpp
try { pub_->publish(process(*msg)); }
catch (const std::exception & e) { RCLCPP_ERROR(get_logger(), "%s", e.what()); }
```
- Retry with backoff: `for k in range(N): try: ...; break; except X: time.sleep(0.5 * 2**k)` (outside callbacks, or in a worker).
- Anti-patterns: bare `except: pass`; `sys.exit()` in callbacks; swallowing the original exception.
- Log severity and throttling rules: [[core-logging]].

## rclpy rules
Timers instead of `time.sleep` loops · declare params before get · `destroy_node()` + `rclpy.shutdown()` in `finally` · create pubs/subs in `__init__`, never inside callbacks · `MultiThreadedExecutor` + separate groups when a callback calls a service of the same process ([[core-exec-callback-groups]]).

## rclcpp rules
`std::make_shared` nodes · `ConstSharedPtr` in callbacks · lambdas over `std::bind` · RAII · no raw `new/delete` · never `std::shared_ptr<MyNode>(this)` · capture `weak_ptr` in long-lived lambdas · publish `std::unique_ptr` msgs for zero-copy intra-process ([[core-composition]]). Loaned msgs: `auto m = pub_->borrow_loaned_message(); m.get().data = 42; pub_->publish(std::move(m));`.

## Pitfalls
- `sys.exit()` inside a callback raises `SystemExit` in the executor thread and skips cleanup. Set a flag and exit from `main` ([[core-exec-spin]]).
- Creating publishers inside callbacks leaks entities and confuses discovery.
