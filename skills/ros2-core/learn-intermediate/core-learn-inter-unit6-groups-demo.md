---
id: core-learn-inter-unit6-groups-demo
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Intermediate Unit 6: callback group x thread test script"
domain: core
area: learn-intermediate
distro: humble
tested: false
audience: students
summary: "Unit 6 example 6.3: service + timer node, group type and thread count from arguments, three test runs."
tags: [course, unit 6, example_4_4_pkg, ReentrantCallbackGroup, MutuallyExclusiveCallbackGroup, MultiThreadedExecutor, default_callback_group, argparse, students]
see: ["[[core-exec-callback-groups]]", "[[core-exec-model]]", "[[core-launch-node-arguments]]", "[[core-learn-inter-project]]"]
requires: []
version_notes:
  - "humble: MultiThreadedExecutor() uses multiprocessing.cpu_count() threads; Jazzy counts the CPUs available to the process — https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/executors.py (V85)"
---
# Intermediate Unit 6: callback group x thread test script

**TL;DR** **Reentrant**: any callback of the group may run in parallel, if there are threads (three callbacks, two threads → two at once). **MutuallyExclusive** (the default of every node): one callback of the group at a time, however many threads. This script lets you try both, with the thread count as an argument ([[core-exec-callback-groups]]).

## Package
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python example_4_4_pkg --dependencies rclpy
cd ~/ros2_ws/src/example_4_4_pkg/
touch example_4_4_pkg/callback_groups_examples.py
chmod +x example_4_4_pkg/callback_groups_examples.py
```

## example_4_4_pkg/callback_groups_examples.py
```python
# import the SetBool module from std_servs service interface
from std_srvs.srv import SetBool
import rclpy
from rclpy.node import Node
import time
from rclpy.callback_groups import ReentrantCallbackGroup, MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import argparse

# Basic Docs:
# https://docs.ros2.org/foxy/api/rclpy/api/execution_and_callbacks.html


class DummyServer(Node):

    def __init__(self, args, callback_group_type="reentrant"):

        self.timer_flag = True

        super().__init__('service_start_turn')

        # More info here: https://docs.python.org/3/library/argparse.html
        parser = argparse.ArgumentParser(
            description='Dummy Server to Learn about Callback Groups and Threads')

        # All the arguments in this group will only be allowed to pass one of them as an argument
        parser.add_argument('-service_wait_time',
                            type=float,
                            #default=5.0,
                            help='Time the service will be waiting',
                            required=True)

        # Metvar will replace the default NAME_OF_ARGUMENT with the value shown in the command parser.print_help()
        # Warning: Setting the Nargs makes the variable now a list
        parser.add_argument('-timer_period',
                            type=float,
                            nargs=1,
                            metavar='TIMEOUT',
                            default=1.0,
                            help="Time period of the Callback for the timer")

        parser.add_argument('-callback_group_type',
                            type=str,
                            default="reentrant",
                            help="Type of Callback Groups REENTRANT of EXCLUSIVE")

        parser.add_argument('-threads',
                            type=int,
                            default=1,
                            help="Number of threads to use in the executor")

        self.args = parser.parse_args(args[1:])

        parser.print_help()

        # <rclpy.callback_groups.MutuallyExclusiveCallbackGroup object at 0x7ff58fc9e8e0>
        # By default, the Callbacks are mutually exclusive. This means that in each group, only
        # one Callback can be done: https://docs.ros2.org/foxy/api/rclpy/api/node.html
        print("## DEFAULT Node Callback Group="+str(self.default_callback_group))

        self.get_logger().warning("Setting "+self.args.callback_group_type+" Groups")
        if self.args.callback_group_type == "reentrant":
            # If you set the group reentrant, any Callback inside will be executed in parallel
            # If there are enough threads
            self.group1 = ReentrantCallbackGroup()
            self.get_logger().warning("ReentrantCallbackGroup Set")
            self.srv = self.create_service(SetBool, '/dummy_server_srv', self.SetBool_callback, callback_group=self.group1)
            self.timer = self.create_timer(self.args.timer_period[0], self.timer_callback, callback_group=self.group1)

        elif self.args.callback_group_type == "exclusive":
            self.group1 = MutuallyExclusiveCallbackGroup()
            self.group2 = MutuallyExclusiveCallbackGroup()
            self.get_logger().warning("MutuallyExclusiveCallbackGroup Set")
            self.srv = self.create_service(SetBool, '/dummy_server_srv', self.SetBool_callback, callback_group=self.group1)
            self.timer = self.create_timer(self.args.timer_period[0], self.timer_callback, callback_group=self.group2)

        else:
            # You do not set groups. Therefore, they will get the default group for the Node
            self.get_logger().error("NO GROUPS SET Set")
            self.srv = self.create_service(SetBool, '/dummy_server_srv', self.SetBool_callback)
            self.timer = self.create_timer(self.args.timer_period[0], self.timer_callback)

    def get_threads(self):
        return self.args.threads

    def SetBool_callback(self, request, response):
        self.get_logger().warning("Processing Server Message...")
        self.wait_for_sec(self.args.service_wait_time)
        self.get_logger().warning("Processing Server Message...DONE")
        response.message = 'TURNING'
        # return the response parameters
        return response

    def wait_for_sec(self, wait_sec, delta=1.0):
        i = 0
        while i < wait_sec:
            self.get_logger().info("..."+str(i)+"[WAITING...]")
            time.sleep(delta)
            i += delta

    def timer_callback(self):
        self.print_dummy_msgs()

    def print_dummy_msgs(self):
        if self.timer_flag:
            self.get_logger().info("TICK")
            self.timer_flag = False
        else:
            self.get_logger().info("TACK")
            self.timer_flag = True


def mutualexclusive_demo_fun(args=None):
    # To Use: ros2 service call /dummy_server_srv std_srvs/srv/SetBool "{data: false}"
    # ros2 run example_4_4_pkg mutualexclusive_demo_fun -service_wait_time 5.0 -timer_period 1.0
    # initialize the ROS communication
    rclpy.init(args=args)
    print("args==="+str(args))
    # Format the arguments given through ROS to use the arguments
    args_without_ros = rclpy.utilities.remove_ros_args(args)
    print("clean ROS args==="+str(args_without_ros))
    start_stop_service_node = DummyServer(args_without_ros)
    num_threads = start_stop_service_node.get_threads()
    start_stop_service_node.get_logger().info('DummyServer Started with threads='+str(num_threads))

    executor = MultiThreadedExecutor(num_threads=num_threads)
    executor.add_node(start_stop_service_node)

    try:
        executor.spin()
    finally:
        executor.shutdown()
        start_stop_service_node.destroy_node()

    # shutdown the ROS communication
    rclpy.shutdown()


def main(args=None):
    # initialize the ROS communication
    rclpy.init(args=args)
    # shutdown the ROS communication
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
`setup.py` entry point: `'mutualexclusive_demo_fun = example_4_4_pkg.callback_groups_examples:mutualexclusive_demo_fun'`. `print(self.default_callback_group)` shows `<rclpy.callback_groups.MutuallyExclusiveCallbackGroup object …>`: the node's default group.

## Three tests
```bash
cd ~/ros2_ws/
colcon build --packages-select example_4_4_pkg
source install/setup.bash
# Different tests
ros2 run example_4_4_pkg mutualexclusive_demo_fun -service_wait_time 5.0 -timer_period 1.0 -callback_group_type exclusive -threads 2
ros2 run example_4_4_pkg mutualexclusive_demo_fun -service_wait_time 5.0 -timer_period 1.0 -callback_group_type reentrant -threads 2
ros2 run example_4_4_pkg mutualexclusive_demo_fun -service_wait_time 5.0 -timer_period 1.0 -callback_group_type reentrant -threads 1
# in another shell, while TICK/TACK prints:
ros2 service call /dummy_server_srv std_srvs/srv/SetBool "{data: false}"
```
| Test | Threads | Groups | Service and timer at once? |
|---|---|---|---|
| 1 | 2 | 2 MutuallyExclusive, one per callback | yes |
| 2 | 2 | 1 Reentrant with both | yes |
| 3 | 1 | 1 Reentrant with both | **no**: one thread, so TICK/TACK stops while the service waits |

## Extra exercises
- **6.1**: reuse earlier code to detect circles with the laser and pass them to a second node that publishes an RViz marker per detection. Both nodes in one script, multithreading, only the **closest** circle, ignore circles farther than 5.0 m ([[core-recipe-laser-circles]]).
- **6.2**: a multithreaded `move_robot_to_point_multithreading.py` (from the services unit's `move_robot_to_point.py`) whose service server callback and odometry callback run in parallel.
- **6.3**: `search_circles_and_go.py` with a service `search_and_go_to_closest_circle` (`std_srvs/Empty`) that sends the closest circle (from `/circles`) to the `go_to_position` service client. Mind that `base_link` and `lidar_1_link` have different orientations. Run `search_circles_and_go`, `closest_circle_laser_processor`, `move_robot_to_point_multithreading` (package `extra_exercises`), call the service and watch in `rviz2`. These are also the final project ([[core-learn-inter-project]]).

## Pitfalls
- `-timer_period` has `nargs=1` (a list) but `default=1.0` (a float): leave it out and `self.args.timer_period[0]` fails. Always pass it, or use `default=[1.0]`.
- The file's `main()` does nothing: the entry point must point to `mutualexclusive_demo_fun`.
