---
id: nav2-commander-picking-demo
title: "Simple Commander demo: warehouse item picking with goToPose"
domain: nav2
area: commander
distro: humble
tested: false
audience: dev
summary: "navigate_to_pose.py: BasicNavigator goToPose from staging point to a shelf, ETA from feedback, then to the shipping destination; TaskResult handling."
tags: [nav2_simple_commander, goToPose, picking demo, warehouse, navigate_to_pose.py, TaskResult, estimated_time_remaining, nav2_new_features]
see: ["[[nav2-simple-commander]]", "[[nav2-navigate-to-pose-action]]", "[[nav2-commander-inspection-demo]]", "[[nav2-learn-adv-unit1-features]]"]
requires: [ros2-core]
version_notes:
  - "humble: older revision of upstream demo_picking.py; uses isTaskComplete() (course text: isNavComplete(), Galactic) — https://github.com/ros-navigation/navigation2/blob/humble/nav2_simple_commander/nav2_simple_commander/demo_picking.py (NAV2-V42, NAV2-V57)"
---
# Simple Commander demo: warehouse item picking with goToPose

**TL;DR** In this demo you use the `NavigateToPose` action to have your robot drive from its staging point to a shelf for a human to place an item on the robot. Then you drive to the pallet jack for shipping on the next truck out of the warehouse.

Create a new package named **nav2_new_features**, where you place all the scripts of this unit, and inside it a folder **scripts** with **navigate_to_pose.py**:
```bash
cd ~/ros2_ws/
ros2 pkg create --build-type ament_python nav2_new_features --dependencies rclpy geometry_msgs
```

## scripts/navigate_to_pose.py
```python
#! /usr/bin/env python3
# Copyright 2021 Samsung Research America
# Licensed under the Apache License, Version 2.0 (SPDX: Apache-2.0): http://www.apache.org/licenses/LICENSE-2.0
from geometry_msgs.msg import PoseStamped
from rclpy.duration import Duration
import rclpy

from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

# Shelf positions for picking
shelf_positions = {
    "shelf_A": [-3.829, -7.604],
    "shelf_B": [-3.791, -3.287],
    "shelf_C": [-3.791, 1.254],
    "shelf_D": [-3.24, 5.861]}

# Shipping destination for picked products
shipping_destinations = {
    "recycling": [-0.205, 7.403],
    "pallet_jack7": [-0.073, -8.497],
    "conveyer_432": [6.217, 2.153],
    "frieght_bay_3": [-6.349, 9.147]}

'''
Basic item picking demo. In this demonstration, the expectation
is that a person is waiting at the item shelf to put the item on the robot
and at the pallet jack to remove it
(probably with a button for 'got item, robot go do next task').
'''


def main():
    # Recieved virtual request for picking item at Shelf A and bringing to
    # worker at the pallet jack 7 for shipping. This request would
    # contain the shelf ID ("shelf_A") and shipping destination ("pallet_jack7")
    ####################
    request_item_location = 'shelf_C'
    request_destination = 'pallet_jack7'
    ####################

    rclpy.init()

    navigator = BasicNavigator()

    # Set your demo's initial pose
    initial_pose = PoseStamped()
    initial_pose.header.frame_id = 'map'
    initial_pose.header.stamp = navigator.get_clock().now().to_msg()
    initial_pose.pose.position.x = 3.45
    initial_pose.pose.position.y = 2.15
    initial_pose.pose.orientation.z = 1.0
    initial_pose.pose.orientation.w = 0.0
    navigator.setInitialPose(initial_pose)

    # Wait for navigation to activate fully
    navigator.waitUntilNav2Active()

    shelf_item_pose = PoseStamped()
    shelf_item_pose.header.frame_id = 'map'
    shelf_item_pose.header.stamp = navigator.get_clock().now().to_msg()
    shelf_item_pose.pose.position.x = shelf_positions[request_item_location][0]
    shelf_item_pose.pose.position.y = shelf_positions[request_item_location][1]
    shelf_item_pose.pose.orientation.z = 1.0
    shelf_item_pose.pose.orientation.w = 0.0
    print('Received request for item picking at ' + request_item_location + '.')
    navigator.goToPose(shelf_item_pose)

    # Do something during your route
    # (e.x. queue up future tasks or detect person for fine-tuned positioning)
    # Print information for workers on the robot's ETA for the demonstration
    i = 0
    while not navigator.isTaskComplete():
        i = i + 1
        feedback = navigator.getFeedback()
        if feedback and i % 5 == 0:
            print('Estimated time of arrival at ' + request_item_location +
                  ' for worker: ' + '{0:.0f}'.format(
                      Duration.from_msg(feedback.estimated_time_remaining).nanoseconds / 1e9)
                  + ' seconds.')

    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print('Got product from ' + request_item_location +
              '! Bringing product to shipping destination (' + request_destination + ')...')
        shipping_destination = PoseStamped()
        shipping_destination.header.frame_id = 'map'
        shipping_destination.header.stamp = navigator.get_clock().now().to_msg()
        shipping_destination.pose.position.x = shipping_destinations[request_destination][0]
        shipping_destination.pose.position.y = shipping_destinations[request_destination][1]
        shipping_destination.pose.orientation.z = 1.0
        shipping_destination.pose.orientation.w = 0.0
        navigator.goToPose(shipping_destination)

    elif result == TaskResult.CANCELED:
        print('Task at ' + request_item_location +
              ' was canceled. Returning to staging point...')
        initial_pose.header.stamp = navigator.get_clock().now().to_msg()
        navigator.goToPose(initial_pose)

    elif result == TaskResult.FAILED:
        print('Task at ' + request_item_location + ' failed!')
        exit(-1)

    while not navigator.isTaskComplete():
        pass

    exit(0)


if __name__ == '__main__':
    main()
```
Code adapted from the official Nav2 demo [demo_picking.py (humble)](https://github.com/ros-navigation/navigation2/blob/humble/nav2_simple_commander/nav2_simple_commander/demo_picking.py). The course version also imported `time` and `deepcopy`, which it never uses. The Simple Commander calls are explained in [[nav2-simple-commander]]. You don't need to set the initial pose from RViz2: the script does it.

## Pitfalls
- Orientation `z: 1.0, w: 0.0` is a yaw of 180° (facing −x) for every goal of the demo.
- The final `while … pass` loop is not a CPU busy-wait: each `isTaskComplete()` call spins the node for up to 100 ms.
- If the robot was moved in the simulation, put it back at the staging point (3.45, 2.15) before launching Nav2, or AMCL starts from a wrong pose.
