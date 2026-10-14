---
id: core-qos-durability-demo
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Durability demo: transient_local for late subscribers"
domain: core
area: middleware
distro: humble
tested: false
audience: dev
summary: "Publish one message, start the subscriber later: it still gets it only when both use TRANSIENT_LOCAL; ros2 topic echo flags."
tags: [durability, TRANSIENT_LOCAL, VOLATILE, latched topic, late joiner, robot_description, QoSDurabilityPolicy, topic echo qos-durability]
see: ["[[core-qos-policies]]", "[[core-qos-usage]]", "[[core-qos-events]]", "[[core-qos-lifespan]]"]
requires: []
version_notes:
  - "humble: without QoS flags ros2 topic echo adapts reliability and durability to the publishers; with any flag the rest comes from sensor_data — https://github.com/ros2/ros2cli/blob/humble/ros2topic/ros2topic/verb/echo.py (V96)"
  - "jazzy: rclpy.qos_event -> rclpy.event_handler; removed in Lyrical — https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/event_handler.py (V86)"
---
# Durability demo: transient_local for late subscribers

**TL;DR** Durability decides whether a message stays available for subscribers that join **after** it was published. `TRANSIENT_LOCAL`: the publisher keeps its last `depth` messages for late joiners (how `robot_description`, `/map` or `/tf_static` work). `VOLATILE`: nothing is kept. A late subscriber gets the old message only if **both** sides use `TRANSIENT_LOCAL` ([[core-qos-policies]]).

## Subscriber (`subscriber_durability.py`)
```python
import argparse
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos_event import SubscriptionEventCallbacks
from rclpy.qos import QoSProfile
from rclpy.qos import QoSDurabilityPolicy


class SubscriberQoS(Node):

    def __init__(self, qos_profile, node_name="subscriber_qos_obj"):

        super().__init__(node_name)

        rclpy.logging.set_logger_level(node_name,
                                       rclpy.logging.LoggingSeverity.INFO)

        event_callbacks = SubscriptionEventCallbacks(incompatible_qos=self.incompatible_qos_clb)

        self.subscriber = self.create_subscription(msg_type=String,
                                                   topic='/qos_test',
                                                   callback=self.listener_callback,
                                                   qos_profile=qos_profile,
                                                   event_callbacks=event_callbacks)

    def listener_callback(self, msg):
        self.get_logger().info("Data Received ="+str(msg.data))

    def incompatible_qos_clb(self, event):
        """
        This is the Callback that will be executed when the event of **Incompatible QoS** is
        triggered.
        """
        self.get_logger().error("SUBSCRIBER::: INCOMPATIBLE QoS Triggered!")
        self.get_logger().error(str(event.last_policy_kind))
        self.get_logger().error("############################")


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-durability',
        type=str,
        choices=['transient_local', 'volatile'],
        help='Select Policy for durability, use ros2 run qos_tests_pkg name_of_exe -durability transient_local|volatile')
    return parser


def main(args=None):

    parser = get_parser()
    parsed_args = parser.parse_args()

    # Depth of History is Compulsory
    qos_profile_subscriber = QoSProfile(depth=1)

    # Options  QoSDurabilityPolicy.VOLATILE, QoSDurabilityPolicy.TRANSIENT_LOCAL,
    durability = parsed_args.durability
    print(durability)
    if durability == "transient_local":
        qos_profile_subscriber.durability = QoSDurabilityPolicy.TRANSIENT_LOCAL
    else:
        # Leave the one by default, which is VOLATILE
        pass

    rclpy.init(args=args)

    sub_qos_obj = SubscriberQoS(qos_profile_subscriber)
    rclpy.spin(sub_qos_obj)
    sub_qos_obj.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Publisher that sends a single message (`publisher_durability.py`)
```python
import argparse
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos_event import PublisherEventCallbacks
from rclpy.qos import QoSProfile
from rclpy.qos import QoSDurabilityPolicy


class PublisherQoS(Node):

    def __init__(self, qos_profile, node_name="publisher_qos_obj"):

        super().__init__(node_name)
        # create the publisher object
        #  create_publisher(msg_type, topic, qos_profile, *, callback_group=None, event_callbacks=None)

        rclpy.logging.set_logger_level(node_name, rclpy.logging.LoggingSeverity.INFO)

        event_callbacks = PublisherEventCallbacks(incompatible_qos=self.incompatible_qos_clb)

        self.publisher_ = self.create_publisher(msg_type=String,
                                                topic='/qos_test',
                                                qos_profile=qos_profile,
                                                event_callbacks=event_callbacks)

    def incompatible_qos_clb(self, event):
        """
        This is the Callback that will be executed when the event of **Incompatible QoS** is
        triggered.
        """
        self.get_logger().error("PUBLISHER::: INCOMPATIBLE QoS Triggered!")
        self.get_logger().error(str(event.last_policy_kind))
        self.get_logger().error("############################")

    def publish_one_message(self):
        # Here you have the Callback method
        msg = String()
        test_time = self.get_clock().now()
        self.current_time_s, self.current_time_ns = test_time.seconds_nanoseconds()
        time_str = str(self.current_time_s)+","+str(self.current_time_ns)
        msg.data = time_str
        self.publisher_.publish(msg)
        self.get_logger().info('Published: "%s"' % msg)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-durability',
        type=str,
        choices=['transient_local', 'volatile'],
        help='Select Policy for durability, use ros2 run qos_tests_pkg name_of_exe -durability transient_local|volatile')
    return parser


def main(args=None):

    parser = get_parser()
    parsed_args = parser.parse_args()

    # Depth of History is Compulsory
    qos_profile_publisher = QoSProfile(depth=1)

    # Options  QoSDurabilityPolicy.VOLATILE, QoSDurabilityPolicy.TRANSIENT_LOCAL,
    durability = parsed_args.durability
    print(durability)
    if durability == "transient_local":
        qos_profile_publisher.durability = QoSDurabilityPolicy.TRANSIENT_LOCAL
    else:
        # Leave the one by default, which is VOLATILE
        pass

    rclpy.init(args=args)

    pub_qos_obj = PublisherQoS(qos_profile_publisher)
    pub_qos_obj.publish_one_message()
    rclpy.spin(pub_qos_obj)
    pub_qos_obj.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
Entry points: `'subscriber_durability_exe = qos_tests_pkg.subscriber_durability:main'`, `'publisher_durability_exe = qos_tests_pkg.publisher_durability:main'` (package `qos_tests_pkg`, created with `--dependencies rclpy std_msgs`).

## Run
```bash
cd ~/ros2_ws/
colcon build --symlink-install --packages-select qos_tests_pkg
source install/setup.bash
ros2 run qos_tests_pkg publisher_durability_exe -durability transient_local   # shell 1: publishes once
ros2 run qos_tests_pkg subscriber_durability_exe -durability transient_local  # shell 2, started later
```
```text
transient_local
[INFO] [1644605352.435077445] [subscriber_qos_obj]: Data Received =1644605326,985073117
```
The subscriber gets the message although it started 25 s after the publication. From the terminal:
```bash
ros2 topic echo --qos-durability transient_local --qos-reliability reliable /qos_test
```
[Humble] `ros2 topic echo /qos_test` without QoS flags also works: echo copies the reliability and durability of the publishers. Once you pass a flag, the policies you omit come from the `sensor_data` preset (best effort), which is why the course had to add `--qos-reliability reliable`.

## Pitfalls
- A VOLATILE subscriber connects to a TRANSIENT_LOCAL publisher but receives only new messages; a TRANSIENT_LOCAL subscriber with a VOLATILE publisher is incompatible.
- `depth` is how many old messages a late joiner can get: depth 1 = only the last one.
