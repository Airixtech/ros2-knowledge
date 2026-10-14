---
id: core-launch-testing
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "launch_testing: test a node from a launch description; launch_test vs colcon test"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "Integration test with launch_testing: start a node, subscribe from the test, assert a message arrives; launch_test vs colcon test."
tags: [launch_testing, launch_test, colcon test, pytest, ReadyToTest, keep_alive, unittest, test folder, test_flake8, ament_python tests]
see: ["[[core-testing-ci-docker]]", "[[core-colcon-build]]", "[[core-pkg-ament-index]]", "[[core-node-skeleton]]"]
requires: []
version_notes:
  - "lyrical: the ament_python template adds test_mypy.py and test_xmllint.py (Kilted) to the default tests — https://github.com/ros2/ros2cli/tree/kilted/ros2pkg/ros2pkg/resource/ament_python (V101)"
---
# launch_testing: test a node from a launch description; launch_test vs colcon test

**TL;DR** Put tests in the package's `test/` folder. A `launch_testing` test file defines `generate_test_description()` (decorated with `@pytest.mark.launch_test`) that starts the node under test, plus `unittest` classes that check its behavior. Run one file with `launch_test` while you develop it, and every test of the package with `colcon test --packages-select <pkg>`. Overview of unit tests, linters and CI: [[core-testing-ci-docker]].

## Default tests and the test folder
`ros2 pkg create --build-type ament_python` adds `test/test_copyright.py`, `test/test_flake8.py` and `test/test_pep257.py`. On an old flake8 they print `Warning: Using or importing the ABCs from 'collections' instead of from 'collections.abc' is deprecated…`; delete them only if they hide your own results.
```bash
cd ~/ros2_ws/
touch src/build_test_pkg/test/check_dummy_scan_msgs_test.py
touch src/build_test_pkg/test/dummy_laser.py
rm -rf src/build_test_pkg/test/test_copyright.py src/build_test_pkg/test/test_flake8.py src/build_test_pkg/test/test_pep257.py
```

## Node under test (`test/dummy_laser.py`)
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import random


class DummyLaser(Node):

    def __init__(self):
        super().__init__('DummyLaser')
        self.count = 0
        self.publisher = self.create_publisher(LaserScan, '/dummy_scan', 10)
        self.timer = self.create_timer(1.0, self.callback)

    def callback(self):
        data = random.random()
        data2 = random.random()
        msg = LaserScan()
        msg.ranges = [data, data2]
        self.get_logger().info('Publishing: '+str((msg.ranges)))
        self.publisher.publish(msg)
        self.count += 1


def main(args=None):
    rclpy.init(args=args)
    node = DummyLaser()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Test (`test/check_dummy_scan_msgs_test.py`)
```python
import os
import sys
from threading import Event
from threading import Thread
import unittest

import launch
import launch.actions
import launch_ros.actions
import launch_testing.actions
import launch_testing.markers
import pytest
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


@pytest.mark.launch_test
@launch_testing.markers.keep_alive
def generate_test_description():
    path_to_test = os.path.dirname(__file__)

    return launch.LaunchDescription([
        launch_ros.actions.Node(
            executable=sys.executable,
            arguments=[os.path.join(path_to_test, 'dummy_laser.py')],
            name='testing_node_dummy_scan',
        ),
        launch_testing.actions.ReadyToTest()
    ])


class TestFixture(unittest.TestCase):

    def test_check_if_msgs_published(self, proc_output):
        rclpy.init()
        try:
            node = MakeTestNode('test_node')
            node.start_subscriber()
            msgs_received_flag = node.msg_event_object.wait(timeout=5.0)
            assert msgs_received_flag, 'ERROR in TEST: Did not get any message!'
        finally:
            rclpy.shutdown()


class MakeTestNode(Node):

    def __init__(self, name='test_node'):
        super().__init__(name)
        self.msg_event_object = Event()

    def start_subscriber(self):
        # Create a subscriber
        self.subscription = self.create_subscription(
            LaserScan,
            '/dummy_scan',
            self.subscriber_callback,
            10
        )

        # Add a spin thread
        self.ros_spin_thread = Thread(target=lambda node: rclpy.spin(node), args=(self,))
        self.ros_spin_thread.start()

    def subscriber_callback(self, data):
        self.msg_event_object.set()
```
- `@pytest.mark.launch_test` is what lets `colcon test` (pytest) recognize the file as a launch test.
- `Node(executable=sys.executable, arguments=[script])` runs a plain Python file with no package or entry point.
- The test node spins in its own thread and waits on a `threading.Event` with a timeout.

## Run it
```bash
cd ~/ros2_ws/
colcon build --symlink-install --packages-select build_test_pkg
source install/setup.bash
launch_test ~/ros2_ws/src/build_test_pkg/test/check_dummy_scan_msgs_test.py   # one file, full output
colcon test --packages-select build_test_pkg                                   # every test of the package
colcon test-result --verbose                                                   # which assertion failed
```
`launch_test` prints the node output and `Ran 1 test in 1.364s … OK`. Run `colcon test` from the workspace root: it builds, and from another folder it would create `build/install/log` there. `colcon test` only reports `1 package had test failures: build_test_pkg`; the assertion text is in `colcon test-result --verbose`. The `Warning: There is no current event loop` lines in the summary come from [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio/issues/212).
To see a failure, comment out `self.publisher.publish(msg)` in `dummy_laser.py`: the test ends with `AssertionError: ERROR in TEST: Did not get any message!` and `FAILED (failures=1)`.

## Pitfalls
- `RCLError: failed to shutdown: rcl_shutdown already called on the given context` at the end of the test: `launch_testing` stops the node with SIGINT, rclpy already shut the context down, and a second `rclpy.shutdown()` fails. Guard it with `if rclpy.ok()` as above.
- Declare the test tools in `package.xml` (for example `<test_depend>launch_testing</test_depend>`) so CI installs them.
