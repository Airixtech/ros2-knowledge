---
id: core-qos-liveliness-demo
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Liveliness demo: publisher with pauses and asserts, subscriber with liveliness events"
domain: core
area: middleware
distro: humble
tested: false
audience: dev
summary: "Test programs for liveliness: publisher with publish/assert periods, 3 groups and 3 threads; subscriber printing liveliness counts."
tags: [liveliness demo, qos_tests_pkg, publisher_liveliness, subscriber_liveliness, assert_liveliness, MutuallyExclusiveCallbackGroup, MultiThreadedExecutor]
see: ["[[core-qos-liveliness]]", "[[core-qos-deadline-demo]]", "[[core-exec-callback-groups]]", "[[core-qos-events]]"]
requires: []
version_notes:
  - "jazzy: rclpy.qos_event -> rclpy.event_handler; removed in Lyrical — https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/event_handler.py (V86)"
---
# Liveliness demo: publisher with pauses and asserts, subscriber with liveliness events

**TL;DR** The publisher takes `-liveliness_lease_duration`, `-publish_period`, `-topic_assert_period` (milliseconds), `--publish_assert yes|no` and `--policy AUTOMATIC|MANUAL_BY_TOPIC`; it pauses 5 s every few messages. The subscriber prints every liveliness change. Scenarios and results: [[core-qos-liveliness]].

## Subscriber that reports liveliness changes (`subscriber_liveliness.py`)
```python
import argparse
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos_event import SubscriptionEventCallbacks
from rclpy.qos import QoSProfile
from rclpy.qos import QoSLivelinessPolicy
from rclpy.duration import Duration

POLICY_MAP = {
    'AUTOMATIC': QoSLivelinessPolicy.AUTOMATIC,
    'MANUAL_BY_TOPIC': QoSLivelinessPolicy.MANUAL_BY_TOPIC,
}


class SubscriberQoS(Node):

    def __init__(self, qos_profile, node_name="publisher_qos_obj"):

        super().__init__(node_name)

        rclpy.logging.set_logger_level(node_name, rclpy.logging.LoggingSeverity.INFO)

        event_callbacks = SubscriptionEventCallbacks(
            incompatible_qos=self.incompatible_qos_clb,
            liveliness=self.liveliness_clb)

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

    def liveliness_clb(self, event):
        """
        # https://docs.ros2.org/dashing/api/rmw/types_8h_source.html
        rmw_liveliness_changed_status_t
        Liveliness triggered
            int32_t alive_count;
            int32_t not_alive_count;
            int32_t alive_count_change;
            int32_t not_alive_count_change;
        """
        self.get_logger().error("SUBSCRIBER::: Liveliness Triggered !")
        self.get_logger().error("alive_count="+str(event.alive_count))
        self.get_logger().error("not_alive_count="+str(event.not_alive_count))
        self.get_logger().error("alive_count_change="+str(event.alive_count_change))
        self.get_logger().error("not_alive_count_change="+str(event.not_alive_count_change))
        self.get_logger().error("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-liveliness_lease_duration',
        type=int,
        default=2000,
        help='Select Policy for liveliness_lease_duration in milliseconds, use ros2 run qos_tests_pkg name_of_exe -liveliness_lease_duration 3000')
    parser.add_argument(
        '--policy', type=str, choices=POLICY_MAP.keys(), default='AUTOMATIC',
        help='The Liveliness policy type. AUTOMATIC|MANUAL_BY_TOPIC')
    return parser


def main(args=None):

    parser = get_parser()
    parsed_args = parser.parse_args()

    liveliness_lease_duration = Duration(seconds=parsed_args.liveliness_lease_duration / 1000.0)
    liveliness_policy = POLICY_MAP[parsed_args.policy]

    qos_profile_subscriber = QoSProfile(
        depth=1,
        liveliness=liveliness_policy,
        liveliness_lease_duration=liveliness_lease_duration)

    rclpy.init(args=args)

    sub_qos_obj = SubscriberQoS(qos_profile=qos_profile_subscriber, node_name="subscriber_liveliness")
    rclpy.spin(sub_qos_obj)
    sub_qos_obj.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    # ros2 run qos_tests_pkg subscriber_liveliness_exe -liveliness_lease_duration 450 --policy MANUAL_BY_TOPIC
    main()
```

## Publisher with a manual "I am alive" timer (`publisher_liveliness.py`)
```python
import argparse
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos_event import PublisherEventCallbacks
from rclpy.qos import QoSProfile
from rclpy.qos import QoSLivelinessPolicy
from rclpy.duration import Duration
import time
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor

POLICY_MAP = {
    'AUTOMATIC': QoSLivelinessPolicy.AUTOMATIC,
    'MANUAL_BY_TOPIC': QoSLivelinessPolicy.MANUAL_BY_TOPIC,
}


class PublisherQoS(Node):

    def __init__(self, qos_profile, publish_period, pub_topic_assert_period, publish_assert, node_name="publisher_qos_obj"):

        self.publish_assert = publish_assert

        self.group_timer_publisher = MutuallyExclusiveCallbackGroup()
        self.group_alive_timer = MutuallyExclusiveCallbackGroup()
        self.group_events_clb = MutuallyExclusiveCallbackGroup()

        super().__init__(node_name)

        rclpy.logging.set_logger_level(node_name, rclpy.logging.LoggingSeverity.INFO)

        event_callbacks = PublisherEventCallbacks(
            incompatible_qos=self.incompatible_qos_clb,
            liveliness=self.liveliness_clb)

        self.publisher_ = self.create_publisher(msg_type=String,
                                                topic='/qos_test',
                                                qos_profile=qos_profile,
                                                event_callbacks=event_callbacks,
                                                callback_group=self.group_events_clb)

        # Create a timer
        # Set the timer period to the asserted period because it is inside the Timer Callback
        self.publish_period = float(publish_period / 1000)
        self.pub_topic_assert_period = float(pub_topic_assert_period / 1000)
        self.swap_state_time = 5.0
        self.time_pause = 5.0
        self.counter = 0

        self.create_timer(self.publish_period, self.timer_callback,
                          callback_group=self.group_timer_publisher)
        self.create_timer(self.pub_topic_assert_period, self.alive_callback,
                          callback_group=self.group_alive_timer)

    def incompatible_qos_clb(self, event):
        """
        This is the Callback that will be executed when the event of **Incompatible QoS** is
        triggered.
        """
        self.get_logger().error("PUBLISHER::: INCOMPATIBLE QoS Triggered!")
        self.get_logger().error(str(event.last_policy_kind))
        self.get_logger().error("############################")

    def liveliness_clb(self, event):
        """
        Liveliness triggered
        """
        self.get_logger().error("PUBLISHER::: Liveliness Triggered!")
        self.get_logger().error(str(event.total_count_change))
        self.get_logger().error(str(event.total_count))
        self.get_logger().error("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

    def publish_one_message(self):
        # Here you have the Callback method
        msg = String()
        test_time = self.get_clock().now()
        self.current_time_s, self.current_time_ns = test_time.seconds_nanoseconds()
        time_str = str(self.current_time_s)+","+str(self.current_time_ns)
        msg.data = time_str
        self.publisher_.publish(msg)
        self.get_logger().info('Published: "%s"' % msg)

    def timer_callback(self):
        # print a ROS2 log on the terminal with a great message!
        if self.counter > int(self.swap_state_time / self.publish_period):
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

    def alive_callback(self):
        self.i_am_alive()

    def i_am_alive(self):
        # https://docs.ros2.org/dashing/api/rclpy/api/topics.html
        # Publish that you are alive even if you do not publish any message in the pause phase
        if self.publish_assert:
            self.publisher_.assert_liveliness()
            self.get_logger().info("Publisher Alive...")


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-liveliness_lease_duration',
        type=int,
        default=2000,
        help='Select Policy for liveliness_lease_duration in milliseconds, use ros2 run qos_tests_pkg name_of_exe -liveliness_lease_duration 3000')
    parser.add_argument(
        '-publish_period', type=int,
        help='How often you publish the message in publisher topic in milliseconds')
    parser.add_argument(
        '-topic_assert_period', type=int,
        help='How often (in positive integer milliseconds) the Talker will manually assert the '
             'liveliness of its Publisher.')
    parser.add_argument(
        '--publish_assert', type=str, choices=["yes", "no"], default="yes",
        help='If you want publish, assert manually. yes|no')
    parser.add_argument(
        '--policy', type=str, choices=POLICY_MAP.keys(), default='AUTOMATIC',
        help='The Liveliness policy type. AUTOMATIC|MANUAL_BY_TOPIC')
    return parser


def main(args=None):

    parser = get_parser()
    parsed_args = parser.parse_args()

    liveliness_lease_duration = Duration(seconds=parsed_args.liveliness_lease_duration / 1000.0)
    liveliness_policy = POLICY_MAP[parsed_args.policy]
    publish_period = parsed_args.publish_period
    topic_assert_period = parsed_args.topic_assert_period
    publish_assert_str = parsed_args.publish_assert
    publish_assert = (publish_assert_str == "yes")
    print("##########################"+str(publish_assert))

    qos_profile_publisher = QoSProfile(
        depth=1,
        liveliness=liveliness_policy,
        liveliness_lease_duration=liveliness_lease_duration)

    rclpy.init(args=args)

    pub_qos_obj = PublisherQoS(qos_profile=qos_profile_publisher,
                               publish_period=publish_period,
                               pub_topic_assert_period=topic_assert_period,
                               publish_assert=publish_assert,
                               node_name="publisher_liveliness_node")

    executor = MultiThreadedExecutor(num_threads=3)
    executor.add_node(pub_qos_obj)

    try:
        executor.spin()
    finally:
        executor.shutdown()
        pub_qos_obj.destroy_node()

    # shutdown the ROS communication
    rclpy.shutdown()


if __name__ == '__main__':
    # Command example : ros2 run qos_tests_pkg publisher_liveliness_exe -liveliness_lease_duration 450 -publish_period 300 -topic_assert_period 1000 --publish_assert yes --policy MANUAL_BY_TOPIC
    main()
```
Entry points: `'publisher_liveliness_exe = qos_tests_pkg.publisher_liveliness:main'`, `'subscriber_liveliness_exe = qos_tests_pkg.subscriber_liveliness:main'`.

## Run
```bash
ros2 run qos_tests_pkg publisher_liveliness_exe -liveliness_lease_duration 2000 -publish_period 1000 -topic_assert_period 3000 --publish_assert yes --policy MANUAL_BY_TOPIC
ros2 run qos_tests_pkg subscriber_liveliness_exe -liveliness_lease_duration 3000 --policy AUTOMATIC
```

## Pitfalls
- All periods are in **milliseconds**, the lease too.
- Same `RMW_IMPLEMENTATION` in both shells ([[core-rmw-implementations]]).
