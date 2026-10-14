---
id: core-qos-deadline
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Deadline: missed-deadline events and compatibility"
domain: core
area: middleware
distro: humble
tested: false
audience: dev
summary: "QoS deadline: maximum time between messages, deadline event callbacks on publisher and subscriber, compatibility rule, test scenarios."
tags: [deadline, QoS deadline, deadline event, offered deadline missed, requested deadline missed, Duration, cmd_vel, health monitoring]
see: ["[[core-qos-events]]", "[[core-qos-policies]]", "[[core-exec-callback-groups]]", "[[core-qos-liveliness]]"]
requires: []
version_notes:
  - "jazzy: rclpy.qos_event -> rclpy.event_handler; removed in Lyrical — https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/event_handler.py (V86)"
---
# Deadline: missed-deadline events and compatibility

**TL;DR** `deadline` is the expected maximum time between two messages of a topic. When it passes without a message, the publisher's and the subscriber's `deadline` event callbacks fire: useful for commands that must be regular (`cmd_vel`, obstacle detection). Compatible only if the publisher's deadline ≤ the subscriber's ([[core-qos-policies]]).

## Subscriber (`subscriber_deadline.py`)
```python
import argparse
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos_event import SubscriptionEventCallbacks
from rclpy.qos import QoSProfile
from rclpy.duration import Duration


class SubscriberQoS(Node):

    def __init__(self, qos_profile, node_name="subscriber_qos_obj"):

        super().__init__(node_name)

        rclpy.logging.set_logger_level(node_name,
                                       rclpy.logging.LoggingSeverity.INFO)

        event_callbacks = SubscriptionEventCallbacks(
            incompatible_qos=self.incompatible_qos_clb,
            deadline=self.deadline_qos_clb)

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

    def deadline_qos_clb(self, event):
        """
        Triggered when the deadline is achieved
        """
        self.get_logger().error("SUBSCRIBER:::  Deadline Triggered!")


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-deadline',
        type=float,
        help='Select Policy for deadline in seconds, use ros2 run qos_tests_pkg name_of_exe -deadline 1.350')
    return parser


def main(args=None):

    parser = get_parser()
    parsed_args = parser.parse_args()

    # Depth of History is Compulsory
    qos_profile_subscriber = QoSProfile(depth=1)

    deadline_seconds = float(parsed_args.deadline)
    deadline = Duration(seconds=deadline_seconds)
    print("deadline=="+str(deadline))
    qos_profile_subscriber.deadline = deadline

    rclpy.init(args=args)

    sub_qos_obj = SubscriberQoS(qos_profile_subscriber)
    rclpy.spin(sub_qos_obj)
    sub_qos_obj.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Publisher: 1 message/s, then a 2 s pause (`publisher_deadline.py`)
```python
import argparse
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos_event import PublisherEventCallbacks
from rclpy.qos import QoSProfile
import time
from rclpy.duration import Duration


class PublisherQoS(Node):

    def __init__(self, qos_profile, node_name="publisher_qos_obj"):

        super().__init__(node_name)

        rclpy.logging.set_logger_level(node_name, rclpy.logging.LoggingSeverity.INFO)

        event_callbacks = PublisherEventCallbacks(
            incompatible_qos=self.incompatible_qos_clb,
            deadline=self.deadline_qos_clb)

        self.publisher_ = self.create_publisher(msg_type=String,
                                                topic='/qos_test',
                                                qos_profile=qos_profile,
                                                event_callbacks=event_callbacks)

        # Create a timer
        self.timer_period = 1.0
        self.swap_state_time = 5.0
        self.time_pause = 2.0
        self.counter = 0
        self.create_timer(self.timer_period, self.timer_callback)

    def incompatible_qos_clb(self, event):
        """
        This is the Callback that will be executed when the event of **Incompatible QoS** is
        triggered.
        """
        self.get_logger().error("PUBLISHER::: INCOMPATIBLE QoS Triggered!")
        self.get_logger().error(str(event.last_policy_kind))
        self.get_logger().error("############################")

    def deadline_qos_clb(self, event):
        """
        Triggered when the deadline is achieved
        """
        self.get_logger().error("PUBLISHER:::  Deadline Triggered!")

    def publish_one_message(self):
        # Here you have the callback method
        msg = String()
        test_time = self.get_clock().now()
        self.current_time_s, self.current_time_ns = test_time.seconds_nanoseconds()
        time_str = str(self.current_time_s)+","+str(self.current_time_ns)
        msg.data = time_str
        self.publisher_.publish(msg)
        self.get_logger().info('Published: "%s"' % msg)

    def timer_callback(self):
        # print a ROS2 log on the terminal with a great message!
        if self.counter > int(self.swap_state_time / self.timer_period):
            delta = 0.1
            range_steps = int(self.time_pause / delta)
            for i in range(range_steps):
                time.sleep(delta)
                self.get_logger().info("Paused ="+str(i*delta)+"/"+str(self.time_pause))
            self.counter = 0
        else:
            self.publish_one_message()
            self.counter += 1
            self.get_logger().info("Counter ="+str(self.counter))


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-deadline',
        type=float,
        help='Select Policy for deadline in seconds, use ros2 run qos_tests_pkg name_of_exe -deadline 1.350')
    return parser


def main(args=None):

    parser = get_parser()
    parsed_args = parser.parse_args()

    # Depth of History is Compulsory
    qos_profile_publisher = QoSProfile(depth=1)

    deadline_seconds = float(parsed_args.deadline)
    deadline = Duration(seconds=deadline_seconds)
    print("deadline=="+str(deadline))
    qos_profile_publisher.deadline = deadline

    rclpy.init(args=args)

    pub_qos_obj = PublisherQoS(qos_profile_publisher)
    pub_qos_obj.publish_one_message()
    rclpy.spin(pub_qos_obj)
    pub_qos_obj.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
Entry points: `'subscriber_deadline_exe = qos_tests_pkg.subscriber_deadline:main'`, `'publisher_deadline_exe = qos_tests_pkg.publisher_deadline:main'`.

## Scenarios
| Publisher `-deadline` | Subscriber `-deadline` | Result |
|---|---|---|
| 10.0 | 10.0 | works: both deadlines are longer than the period (1 s) and than the pause (2 s) |
| 0.99 | — | publisher deadline event every second: even 0.99 s is shorter than its 1 s period |
| 1.0 | — | publisher event during the pause phase |
| 1.2 | 1.8 | events on both sides only during the 2 s pause |
| 1.5 | 1.0 | **incompatible** (publisher deadline > subscriber's): `RMW_QOS_POLICY_DEADLINE` in both incompatible-QoS callbacks; the publisher keeps publishing, the subscriber receives nothing |
```text
deadline==Duration(nanoseconds=990000000)
[ERROR] [1644945025.239750790] [publisher_qos_obj]: PUBLISHER:::  Deadline Triggered!
```
The subscriber's deadline only counts while a matched publisher exists: with no publisher running, nothing fires.

## Pitfalls
- The pause runs `time.sleep()` inside the timer callback of a single-threaded executor, so the publisher's deadline callback waits until the timer callback returns: with `-deadline 1.0` it is reported after ~2 s. Put event callbacks in their own callback group with a `MultiThreadedExecutor` ([[core-qos-liveliness]], [[core-exec-callback-groups]]).
- A deadline that the publisher cannot meet by design (shorter than its period) fires forever: set it from the real rate plus a margin.
