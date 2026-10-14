---
id: core-qos-events
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "QoS event callbacks: incompatible QoS, defaults, topic info --verbose"
domain: core
area: middleware
distro: humble
tested: false
audience: dev
summary: "Publisher/SubscriptionEventCallbacks to catch incompatible QoS (and deadline, liveliness), a configurable QoS test publisher, /scan QoS."
tags: [QoS events, PublisherEventCallbacks, SubscriptionEventCallbacks, incompatible_qos, last_policy_kind, qos_event, event_handler, topic info verbose, RMW_IMPLEMENTATION]
see: ["[[core-qos-policies]]", "[[core-qos-usage]]", "[[core-qos-deadline]]", "[[core-qos-liveliness]]"]
requires: []
version_notes:
  - "jazzy: import the callbacks from rclpy.event_handler (Iron); rclpy.qos_event warns (Jazzy, Kilted) and is removed in Lyrical — https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/event_handler.py (V86)"
  - "humble: Fast DDS (default RMW) also raises incompatible-QoS events — https://github.com/ros2/rmw_fastrtps/blob/humble/rmw_fastrtps_shared_cpp/src/custom_publisher_info.cpp (V87)"
  - "humble: liveliness default is SYSTEM_DEFAULT, durations 'default' — https://github.com/ros2/rmw/blob/humble/rmw/include/rmw/qos_profiles.h (V36)"
---
# QoS event callbacks: incompatible QoS, defaults, topic info --verbose

**TL;DR** QoS lets you choose, per publisher and subscriber, how reliable delivery must be: ROS 1 used TCP, which suits neither lossy networks (Wi-Fi) nor critical systems, while ROS 2 rides on DDS over UDP. Both ends must have **compatible** QoS or nothing flows ([[core-qos-policies]]). Pass `event_callbacks` to `create_publisher` / `create_subscription` to be told when it happens. The same callbacks report missed deadlines ([[core-qos-deadline]]) and liveliness changes ([[core-qos-liveliness]]).

## Subscriber that requires RELIABLE (`subscriber_custom_minimal_qos.py`)
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
# import QoS library, to set the correct profile and reliability.
from rclpy.qos import ReliabilityPolicy, QoSProfile


class SubscriberQoS(Node):

    def __init__(self):

        super().__init__('subscriber_qos_obj')

        # create the subscriber object
        self.subscriber = self.create_subscription(
            String,
            '/qos_test',
            self.listener_callback,
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE))

    def listener_callback(self, msg):
        self.get_logger().info("Data Received ="+str(msg.data))


def main(args=None):
    rclpy.init(args=args)
    sub_qos_obj = SubscriberQoS()
    rclpy.spin(sub_qos_obj)
    sub_qos_obj.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Publisher with an incompatible-QoS callback (`publisher_custom_minimal_qos.py`)
```python
import argparse
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos_event import PublisherEventCallbacks
from rclpy.duration import Duration
from rclpy.qos import QoSProfile
from rclpy.qos import QoSDurabilityPolicy
from rclpy.qos import QoSLivelinessPolicy
from rclpy.qos import QoSReliabilityPolicy


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

        # This is the unique ID for each message that will be sent
        self.msgs_id = 0
        #self.current_time = self.get_clock().now()
        self.current_time_s = 0
        self.current_time_ns = 0
        # define the timer for 0.5 seconds
        timer_period = 0.5
        # create a timer sending two parameters:
        # - the duration between two Callbacks (0.5 seconds)
        # - the Timer function (timer_callback)
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def incompatible_qos_clb(self, event):
        """
        This is the Callback that will be executed when the event of **Incompatible QoS** is
        triggered.
        """
        self.get_logger().error("A subscriber is asking for an INCOMPATIBLE QoS Triggered!")
        self.get_logger().error(str(event.last_policy_kind))
        self.get_logger().error("############################")

    def timer_callback(self):
        # Here you have the Callback method
        msg = String()
        test_time = self.get_clock().now()
        self.current_time_s, self.current_time_ns = test_time.seconds_nanoseconds()
        time_str = str(self.current_time_s)+","+str(self.current_time_ns)
        dds_msg_str = str(self.msgs_id)+":"+time_str
        msg.data = dds_msg_str
        # Publish the message to the topic
        self.publisher_.publish(msg)
        # Display the message on the console
        self.get_logger().info('Publishing: "%s"' % msg)

        self.msgs_id += 1


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-reliability',
        type=str,
        choices=['best_effort', 'reliable'],
        help='Select Policy for reliability, use ros2 run qos_tests_pkg publisher_custom_minimal_qos_exe -reliability best_effort|reliable')
    return parser


def main(args=None):

    # Parse the arguments
    parser = get_parser()
    parsed_args = parser.parse_args()

    # Configuration variables
    reliability = parsed_args.reliability
    print(reliability)
    qos_profile_publisher = QoSProfile(depth=10)

    # Options  QoSDurabilityPolicy.VOLATILE, QoSDurabilityPolicy.TRANSIENT_LOCAL,
    qos_profile_publisher.durability = QoSDurabilityPolicy.VOLATILE

    qos_profile_publisher.deadline = Duration(seconds=2)

    # Options QoSLivelinessPolicy.MANUAL_BY_TOPIC, QoSLivelinessPolicy.AUTOMATIC
    qos_profile_publisher.liveliness = QoSLivelinessPolicy.AUTOMATIC

    qos_profile_publisher.liveliness_lease_duration = Duration(seconds=2)

    # Options: QoSReliabilityPolicy.RELIABLE, QoSReliabilityPolicy.BEST_EFFORT
    if reliability == "reliable":
        qos_profile_publisher.reliability = QoSReliabilityPolicy.RELIABLE
    else:
        qos_profile_publisher.reliability = QoSReliabilityPolicy.BEST_EFFORT

    # initialize the ROS communication
    rclpy.init(args=args)
    # declare the node constructor
    pub_qos_obj = PublisherQoS(qos_profile_publisher)
    # pause the program execution, waits for a request to kill the node (ctrl+c)
    rclpy.spin(pub_qos_obj)
    # Explicity destroy the node
    pub_qos_obj.destroy_node()
    # shutdown the ROS communication
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
Entry points: `'publisher_custom_minimal_qos_exe = qos_tests_pkg.publisher_custom_minimal_qos:main'`, `'subscriber_custom_minimal_qos_exe = qos_tests_pkg.subscriber_custom_minimal_qos:main'`.

## Run: compatible, then incompatible
```bash
ros2 run qos_tests_pkg publisher_custom_minimal_qos_exe -reliability reliable      # shell 1
ros2 run qos_tests_pkg subscriber_custom_minimal_qos_exe                          # shell 2: Data Received =0:1644578722,985456932 ...
ros2 run qos_tests_pkg publisher_custom_minimal_qos_exe -reliability best_effort  # shell 1 again
```
```text
[ERROR] [publisher_qos_obj]: A subscriber is asking for an INCOMPATIBLE QoS Triggered!
[ERROR] [publisher_qos_obj]: rmw_qos_policy_kind_t.RMW_QOS_POLICY_RELIABILITY
[WARN] [subscriber_qos_obj]: New publisher discovered on topic '/qos_test', offering incompatible QoS. No messages will be received from it. Last incompatible policy: RELIABILITY
```
Two things happen: the publisher's `incompatible_qos` callback fires, and the subscriber logs a warning naming the (last) incompatible policy: best-effort publisher, reliable subscriber. The course exported `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` in both shells because event support differs between DDS implementations; in Humble both Fast DDS and Cyclone DDS raise these events.

## Defaults and a real sensor
A publisher or subscriber created with only a depth gets: history KEEP_LAST, depth 10 (queue size), RELIABLE, VOLATILE, liveliness SYSTEM_DEFAULT; deadline, lifespan and lease duration "default", shown as 9223372036854775807 ns (infinite). Every QoS of a topic:
```bash
ros2 topic info /scan --verbose
```
```text
Node name: lidar_1
Topic type: sensor_msgs/msg/LaserScan
Endpoint type: PUBLISHER
QoS profile:
  Reliability: BEST_EFFORT
  Durability: VOLATILE
  Lifespan: 9223372036854775807 nanoseconds
  Deadline: 9223372036854775807 nanoseconds
  Liveliness: AUTOMATIC
  Liveliness lease duration: 9223372036854775807 nanoseconds
```
- BEST_EFFORT + VOLATILE is the usual sensor choice: a continuous flow where one or two lost messages and old data do not matter.
- AUTOMATIC liveliness: the publisher counts as alive while its node is running ([[core-qos-liveliness]]).
- Infinite deadline and lifespan: acceptable in simulation; a real sensor has a rate, so a deadline and a lifespan make sense ([[core-qos-deadline]], [[core-qos-lifespan]]).
All event types: [rclpy qos_event.py (humble)](https://github.com/ros2/rclpy/blob/humble/rclpy/rclpy/qos_event.py). Services and actions take the same QoS objects ([rclpy services](https://docs.ros2.org/foxy/api/rclpy/api/services.html), [actions](https://docs.ros2.org/foxy/api/rclpy/api/actions.html)).

## Pitfalls
- `parser.parse_args()` reads all of `sys.argv`: add `--ros-args` to the command and argparse fails. Parse `rclpy.utilities.remove_ros_args()` instead ([[core-launch-node-arguments]]).
- The event callback only reports the **last** incompatible policy: fix it and run again to find the next one.
