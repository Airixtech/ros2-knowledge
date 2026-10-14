---
id: core-qos-lifespan
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Lifespan: message expiry"
domain: core
area: middleware
distro: humble
tested: false
audience: dev
summary: "QoS lifespan: messages older than the duration are dropped and never delivered; demo that measures message age with transient_local."
tags: [lifespan, QoS lifespan, message age, stale data, expiry, TRANSIENT_LOCAL, RELIABLE, seconds_nanoseconds]
see: ["[[core-qos-durability-demo]]", "[[core-qos-policies]]", "[[core-qos-events]]", "[[core-time-timers]]"]
requires: []
version_notes:
  - "all: lifespan applies whatever the durability; it matters most when old samples are stored (transient_local) — https://docs.ros.org/en/humble/Concepts/Intermediate/About-Quality-of-Service-Settings.html (V95)"
  - "jazzy: rclpy.qos_event -> rclpy.event_handler; removed in Lyrical — https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/event_handler.py (V86)"
---
# Lifespan: message expiry

**TL;DR** `lifespan` is the maximum time between publishing and receiving a message: older messages are silently dropped, as if they never arrived. It matters for sensor data (laser, camera), where late data is useless. The **publisher's** lifespan decides; the DDS layer drops the message before the subscriber callback. The demo uses RELIABLE + TRANSIENT_LOCAL so a stored message waits for a late subscriber, and the subscriber prints its age.

## Subscriber that prints the message age (`subscriber_lifespan.py`)
```python
import argparse
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos_event import SubscriptionEventCallbacks
from rclpy.qos import QoSProfile
from rclpy.qos import QoSDurabilityPolicy
from rclpy.qos import QoSReliabilityPolicy
from rclpy.duration import Duration


class SubscriberQoS(Node):

    def __init__(self, qos_profile, node_name="subscriber_qos_obj"):

        super().__init__(node_name)

        rclpy.logging.set_logger_level(node_name,
                                       rclpy.logging.LoggingSeverity.INFO)

        event_callbacks = SubscriptionEventCallbacks(incompatible_qos=self.incompatible_qos_clb)

        # create the subscriber object
        self.subscriber = self.create_subscription(msg_type=String,
                                                   topic='/qos_test',
                                                   callback=self.listener_callback,
                                                   qos_profile=qos_profile,
                                                   event_callbacks=event_callbacks)

    def listener_callback(self, msg):
        """
        Parse it and calculate the time passed
        1644948035,948696546
        """
        raw_data = msg.data
        self.get_logger().info("Data Received ="+str(raw_data))
        split_data = raw_data.split(",")
        self.get_logger().info("SPLIT ="+str(split_data))
        seconds = float(split_data[0])
        nseconds = float(split_data[1])
        self.get_logger().info("seconds ="+str(seconds)+", nseconds = "+str(nseconds))
        total_seconds = seconds + nseconds * (10 ** -9)
        self.get_logger().info("total_seconds ="+str(total_seconds))
        # Get time now
        test_time = self.get_clock().now()
        current_time_s, current_time_ns = test_time.seconds_nanoseconds()
        total_current_time = float(current_time_s) + \
            (float(current_time_ns) * (10 ** -9))
        self.get_logger().info("total_current_time ="+str(total_current_time))
        delta = total_current_time - total_seconds
        self.get_logger().info("Message Age ="+str(delta))

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
        '-lifespan',
        type=float,
        help='Select Policy for lifespan, use ros2 run qos_tests_pkg name_of_exe -lifespan 3.2')
    return parser


def main(args=None):

    parser = get_parser()
    parsed_args = parser.parse_args()

    # Depth of History is Compulsory
    qos_profile_subscriber = QoSProfile(depth=1)

    lifespan_seconds = float(parsed_args.lifespan)
    lifespan = Duration(seconds=lifespan_seconds)
    print("lifespan=="+str(lifespan))
    qos_profile_subscriber.lifespan = lifespan
    # Reliability set to reliable
    qos_profile_subscriber.reliability = QoSReliabilityPolicy.RELIABLE
    # Durability Set to Transient Local
    qos_profile_subscriber.durability = QoSDurabilityPolicy.TRANSIENT_LOCAL

    rclpy.init(args=args)

    sub_qos_obj = SubscriberQoS(qos_profile_subscriber)
    rclpy.spin(sub_qos_obj)
    sub_qos_obj.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Publisher (`publisher_lifespan.py`)
Same as `publisher_durability.py` in [[core-qos-durability-demo]] (one message, then spin), with this QoS in `main()` and the parser argument `-lifespan` (`type=float`):
```python
    # Depth of History is Compulsory
    qos_profile_publisher = QoSProfile(depth=1)

    lifespan_seconds = float(parsed_args.lifespan)
    lifespan = Duration(seconds=lifespan_seconds)
    print("lifespan=="+str(lifespan))
    qos_profile_publisher.lifespan = lifespan
    # Reliability set to reliable
    qos_profile_publisher.reliability = QoSReliabilityPolicy.RELIABLE
    # Durability Set to Transient Local
    qos_profile_publisher.durability = QoSDurabilityPolicy.TRANSIENT_LOCAL
```
Imports: `QoSProfile`, `QoSDurabilityPolicy`, `QoSReliabilityPolicy` from `rclpy.qos`, `Duration` from `rclpy.duration`. Entry points: `'subscriber_lifespan_exe = qos_tests_pkg.subscriber_lifespan:main'`, `'publisher_lifespan_exe = qos_tests_pkg.publisher_lifespan:main'`.

## Scenarios
```bash
ros2 run qos_tests_pkg publisher_lifespan_exe -lifespan 20.0     # shell 1
ros2 run qos_tests_pkg subscriber_lifespan_exe -lifespan 1.0     # shell 2, within 20 s
```
```text
[INFO] [1644949766.033457458] [subscriber_qos_obj]: Message Age =10.363516569137573
```
- Publisher lifespan 20 s: a subscriber started 10 s later still receives the stored message. The subscriber's own lifespan (1.0) changes nothing.
- Start the subscriber **first**, then `-lifespan 0.001`: the message still arrives (the logged age, 0.02 s, includes the time the callback spent logging), because delivery took less than 1 ms.
- `-lifespan 0.00001`: the message expires before delivery and the subscriber callback never runs.

## Pitfalls
- The age is measured with `self.get_clock().now()` on both sides: fine on one machine, misleading across computers with unsynchronized clocks.
- With VOLATILE + BEST_EFFORT, messages are delivered at once or not at all, so a lifespan rarely drops anything visible.
