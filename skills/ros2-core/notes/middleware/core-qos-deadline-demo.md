---
id: core-qos-deadline-demo
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "Deadline demo: 1 Hz publisher with pauses, subscriber with deadline"
domain: core
area: middleware
distro: humble
tested: false
audience: dev
summary: "Deadline test programs: 1 Hz publisher with 2 s pauses and a subscriber, both with -deadline and event callbacks."
tags: [deadline demo, qos_tests_pkg, publisher_deadline, subscriber_deadline, deadline_qos_clb, Duration, argparse]
see: ["[[core-qos-deadline]]", "[[core-qos-events-demo]]", "[[core-qos-liveliness-demo]]", "[[core-qos-events]]"]
requires: []
version_notes:
  - "jazzy: rclpy.qos_event -> rclpy.event_handler; removed in Lyrical — https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/event_handler.py (V86)"
---
# Deadline demo: 1 Hz publisher with pauses, subscriber with deadline

**TL;DR** Both programs take `-deadline <seconds>` and register `deadline` and `incompatible_qos` callbacks. The publisher publishes every second and pauses 2 s inside its timer callback every few messages. Scenarios and results: [[core-qos-deadline]]. C++ version: `cpp-qos-deadline-demo` (ros2-cpp skill).

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

## Run
```bash
ros2 run qos_tests_pkg publisher_deadline_exe -deadline 10.0
ros2 run qos_tests_pkg subscriber_deadline_exe -deadline 10.0
```

## Pitfalls
- The 2 s pause is on purpose (it is what the scenarios test); its side effect on the publisher's own events is in [[core-qos-deadline]].
- Same `RMW_IMPLEMENTATION` in both shells ([[core-rmw-implementations]]).
