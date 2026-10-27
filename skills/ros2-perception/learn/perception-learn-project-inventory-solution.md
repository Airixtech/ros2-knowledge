---
id: perception-learn-project-inventory-solution
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Course project solution: inventory check node with head moves, two counts, missing and misplaced items"
domain: perception
area: learn
distro: humble
tested: false
audience: students
order: 5
summary: "Project solution inventory_checking.py: TrajectorySender head moves, start/stop Trigger calls, upper and lower counts, sum, missing and misplaced items."
tags: [course project, solution, inventory_checking.py, TrajectorySender, Trigger, call_async, spin_until_future_complete, ObjectCount, sum_counts, check_inventory, missing items, misplaced items, final_project]
see: ["[[perception-learn-project-inventory]]", "[[perception-learn-project-detection-solution]]", "[[core-srv-client-async]]"]
requires: [ros2-core]
version_notes:
  - "course solution: `missing_items` raised KeyError for a class absent from the count, fixed with .get(item, 0) (PERC-V44)"
  - "course solution: callbacks do not run during time.sleep(10); the queued ObjectCount messages are processed by the next spin_until_future_complete (PERC-V45)"
---
# Course project solution: inventory check node

**TL;DR** Move the head to the upper shelf, start the detection, wait, stop it, keep the first count message; the same for the lower shelf; sum both counts and compare them with the AOI's expected stock to report missing and misplaced items. The detection node: [[perception-learn-project-detection-solution]]. Spec: [[perception-learn-project-inventory]]. The course's solution; fixes marked.

## `inventory_checking.py`
```python
from typing import Dict
import rclpy
from rclpy.node import Node
from final_project.trajectory_sender import TrajectorySender
from std_srvs.srv import Trigger
from custom_msgs.msg import ObjectCount
from std_msgs.msg import String
import time


class InventoryChecking(Node):
    def __init__(self) -> None:
        super().__init__('inventory_checking')
        self.trajectory_sender = TrajectorySender(self)
        self.upper_count = {}
        self.lower_count = {}
        self.detected_objects = ""
        self.aoi_choice = ""

        self.object_count_sub = self.create_subscription(
            ObjectCount,
            '/detected_object_count',
            self.object_count_callback,
            10)

        self.aoi_choice_sub = self.create_subscription(
            String,
            '/aoi_choice',
            self.aoi_choice_callback,
            10
        )

        self.start_detection_client = self.create_client(Trigger, 'start_detection')
        self.stop_detection_client = self.create_client(Trigger, 'stop_detection')

        while not self.start_detection_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('start_detection service not available, waiting...')

        while not self.stop_detection_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('stop_detection service not available, waiting...')

    def aoi_choice_callback(self, msg: String) -> None:
        self.aoi_choice = msg.data

    def object_count_callback(self, msg: ObjectCount) -> None:
        if not self.detected_objects:
            return

        object_counts = {msg.classes[i]: msg.counts[i] for i in range(len(msg.classes))}
        self.get_logger().info(f'Detected objects: {object_counts}')

        if self.detected_objects == 'upper':
            self.upper_count = object_counts
        elif self.detected_objects == 'lower':
            self.lower_count = object_counts

        self.detected_objects = ""

    def call_service(self, client, service_name: str) -> bool:
        req = Trigger.Request()
        future = client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None and future.result().success:
            self.get_logger().info(f'{service_name} service call succeeded: {future.result().message}')
            return True
        else:
            self.get_logger().info(f'{service_name} service call failed')
            return False

    def perform_inventory(self) -> None:
        # Move head to look upwards
        self.get_logger().info('Moving head upwards for upper shelf inventory...')
        if not self.trajectory_sender.send_trajectory(
                ['deepmind_robot1_head_base_joint', 'deepmind_robot1_head_joint'],
                [0.0, -0.2], 1):
            return

        # Start detection for upper shelf
        self.detected_objects = 'upper'
        if not self.call_service(self.start_detection_client, 'start_detection'):
            return

        # Wait for detection to complete
        time.sleep(10)  # Adjust the sleep time as necessary

        # Stop detection
        if not self.call_service(self.stop_detection_client, 'stop_detection'):
            return

        # Move head to look downwards
        self.get_logger().info('Moving head downwards for lower shelf inventory...')
        if not self.trajectory_sender.send_trajectory(
                ['deepmind_robot1_head_base_joint', 'deepmind_robot1_head_joint'],
                [0.0, 0.7], 1):
            return

        # Start detection for lower shelf
        if not self.call_service(self.start_detection_client, 'start_detection'):
            return

        self.detected_objects = 'lower'
        # Wait for detection to complete
        time.sleep(10)  # Adjust the sleep time as necessary

        # Stop detection
        if not self.call_service(self.stop_detection_client, 'stop_detection'):
            return

        # Sum up the counts
        total_count = self.sum_counts(self.upper_count, self.lower_count)
        self.get_logger().info(f'Total inventory count: {total_count}')

        # Perform inventory checks
        self.get_logger().info(f'Lets check the inventory: ')
        self.check_inventory(total_count)

    def sum_counts(self, upper_count: Dict[str, int], lower_count: Dict[str, int]) -> Dict[str, int]:
        total_count = upper_count.copy()
        for obj, count in lower_count.items():
            if obj in total_count:
                total_count[obj] += count
            else:
                total_count[obj] = count
        return total_count

    def check_inventory(self, total_count: Dict[str, int]) -> None:
        expected_counts = {}
        allowed_items = []

        if self.aoi_choice in ['red', 'blue']:
            expected_counts = {'banana': 6, 'pizza': 4}
            allowed_items = ['banana', 'pizza']
        elif self.aoi_choice in ['green', 'yellow']:
            expected_counts = {'cell phone': 8, 'laptop': 4}
            allowed_items = ['cell phone', 'laptop']

        # PERC-V44: .get(item, 0), the course read total_count[item] for absent classes (KeyError)
        missing_items = {item: expected_counts[item] - total_count.get(item, 0) for item in expected_counts if item not in total_count or total_count[item] < expected_counts[item]}
        misplaced_items = {item: count for item, count in total_count.items() if item not in allowed_items}

        if missing_items:
            self.get_logger().info(f'Missing items: {missing_items}')
        else:
            self.get_logger().info('No missing items.')

        if misplaced_items:
            self.get_logger().info(f'Misplaced items: {misplaced_items}')
        else:
            self.get_logger().info('No misplaced items.')


def main(args=None) -> None:
    rclpy.init(args=args)
    node = InventoryChecking()
    try:
        node.perform_inventory()
    except Exception as e:
        node.get_logger().error(f'Error during inventory: {e}')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```
- `TrajectorySender(self)` comes from the course's `trajectory_sender.py` (copied into the package, not shown); `send_trajectory(joint_names, positions, seconds)` returns whether the motion succeeded. Head positions: `[0.0, -0.2]` upper shelf, `[0.0, 0.7]` lower shelf.
- `call_service()` calls a `Trigger` asynchronously and spins until the answer arrives; that works here because `perform_inventory()` runs in `main()`, not inside a callback ([[core-srv-client-async]]).
- How the counts arrive: callbacks run only while the node spins, so nothing is processed during `time.sleep(10)`; the next `spin_until_future_complete` (the stop call) runs the queued `ObjectCount` messages, the first one fills `upper_count` / `lower_count` and clears `detected_objects`, the rest are ignored (PERC-V45). Spinning while waiting (`rclpy.spin_once` in a loop, or a timer) is clearer.
- `self.aoi_choice` is set only when a `/aoi_choice` message is processed, i.e. during the service calls' spins: keep `ros2 topic pub /aoi_choice …` running while the node works, or `check_inventory()` finds an empty choice and expects nothing.
- The expected outputs of the spec show the node name `inventory_checking_node`; this solution names it `inventory_checking`.
