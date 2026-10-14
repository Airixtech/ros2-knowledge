---
id: core-dds-loss-test
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Message-loss and latency test between RMW implementations"
domain: core
area: middleware
distro: humble
tested: false
audience: dev
summary: "Publisher with sequence ids and timestamps, subscriber that counts lost messages and pub-to-sub delay; flood test per RMW."
tags: [message loss, latency, sequence id, RMW comparison, Fast DDS, Cyclone DDS, BEST_EFFORT, rclpy.time.Time, ClockType, benchmark]
see: ["[[core-rmw-implementations]]", "[[core-ros2-daemon]]", "[[core-qos-usage]]", "[[core-time-timers]]"]
requires: []
version_notes: []
---
# Message-loss and latency test between RMW implementations

**TL;DR** The publisher sends `"<id>:<seconds>,<nanoseconds>"` with a growing id; the subscriber checks that each id is the expected one (counting the gap as lost messages) and prints the delay between publication and reception. Run the pair with each `RMW_IMPLEMENTATION` ([[core-rmw-implementations]]) and with a faster timer to see how each one copes.

## publisher_dds.py
```python
import rclpy
# import the ROS2 python libraries
from rclpy.node import Node
from std_msgs.msg import String


class PublisherDDS(Node):

    def __init__(self):
        # Here you have the class constructor
        # call super() in the constructor to initialize the Node object
        # the parameter you pass is the Node name
        super().__init__('publisher_dds_obj')
        # create the publisher object
        # in this case, the publisher will publish on /dds_test topic with a queue size of one message.
        self.publisher_ = self.create_publisher(String, '/dds_test', 1)
        # This is the Unique id for each of the messages that will be sent
        self.msgs_id = 0
        #self.current_time = self.get_clock().now()
        self.current_time_s = 0
        self.current_time_ns = 0
        # define the timer period for 0.05 seconds
        timer_period = 0.05
        # create a timer sending two parameters:
        # - the duration between two Callbacks (0.05 seconds)
        # - the timer function (timer_callback)
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        # here you have the Callback method
        # create a String message
        msg = String()
        test_time = self.get_clock().now()
        self.current_time_s, self.current_time_ns = test_time.seconds_nanoseconds()
        time_str = str(self.current_time_s)+","+str(self.current_time_ns)
        dds_msg_str = str(self.msgs_id)+":"+time_str
        msg.data = dds_msg_str
        # publish the message to the topic
        self.publisher_.publish(msg)
        # display the message on the console
        self.get_logger().info('Publishing: "%s"' % msg)
        self.msgs_id += 1


def main(args=None):
    # initialize the ROS communication
    rclpy.init(args=args)
    # declare the Node constructor
    publisher_dds_obj = PublisherDDS()
    # pause the program execution, waits for a request to kill the Node (ctrl+c)
    rclpy.spin(publisher_dds_obj)
    # Explicity destroy the Node
    publisher_dds_obj.destroy_node()
    # shutdown the ROS communication
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## subscriber_dds.py
```python
import rclpy
# import the ROS2 python libraries
from rclpy.node import Node
from std_msgs.msg import String
# import QoS library, to set the correct profile and reliability to read sensor data.
from rclpy.qos import ReliabilityPolicy, QoSProfile
# Time
from rclpy.clock import ClockType
from rclpy.time import Time


class SubscriberDDS(Node):

    def __init__(self):
        # here you have the class constructor
        # call super() in the constructor to initialize the Node object
        # the parameter you pass is the Node name
        super().__init__('subscriber_dds_obj')
        self.id = 0
        self.id_next = -1
        self.lost_messages_counter = 0
        # create the subscriber object
        self.subscriber = self.create_subscription(
            String,
            '/dds_test',
            self.listener_callback,
            QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT))  # is the most used to read LaserScan data and some sensor data.
        # prevent unused variable warning
        self.subscriber

    def listener_callback(self, msg):
        # print the log info in the terminal
        # self.get_logger().info('I receive: "%s"' % str(msg))
        # save the received data
        self.process_dds_test_data(msg.data)

    def process_dds_test_data(self, data):
        """
        The data has the format ID:Seconds,NanoSeconds
        return:
        ID
        TIME Object
        """
        array = data.split(":")
        self.id = int(array[0])

        if self.id == 0:
            self.id_next = 0

        if self.id == self.id_next:
            # The message ID is what you were waiting for
            # Therefore, you have not lost any message
            self.get_logger().warning("MESSAGE OK: ID="+str(self.id)+" ,Next ID="+str(self.id_next)+", TOTAL MSG LOST="+str(self.lost_messages_counter))
        else:
            if self.id_next != -1:
                # The message ID is not the one you hoped for
                # Calculate how many messages have been lost
                delta_messages_lost = self.id - self.id_next
                self.lost_messages_counter += delta_messages_lost
                self.get_logger().error("Message LOST: ID="+str(self.id)+" ,Next ID="+str(self.id_next)+", DELTA MSG LOST="+str(delta_messages_lost)+", TOTAL MSG LOST="+str(self.lost_messages_counter))
            else:
                # This is to avoid error in the first init message
                pass

        self.id_next = self.id + 1

        seconds = int(array[1].split(",")[0])
        nano_seconds = int(array[1].split(",")[1])
        time_obj = Time(seconds=seconds, nanoseconds=nano_seconds, clock_type=ClockType.ROS_TIME)
        time_now_obj = self.get_clock().now()
        delta = time_now_obj - time_obj
        self.get_logger().info("DELTA Between PUB and SUB ="+str(delta))


def main(args=None):
    # initialize the ROS communication
    rclpy.init(args=args)
    # declare the Node constructor
    subscriber_dds_obj = SubscriberDDS()
    # pause the program execution, waits for a request to kill the Node (ctrl+c)
    rclpy.spin(subscriber_dds_obj)
    # explicity destroy the Node
    subscriber_dds_obj.destroy_node()
    # shutdown the ROS communication
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Package, launch and run
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python dds_tests_pkg --dependencies rclpy std_msgs
```
```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='dds_tests_pkg',
            executable='publisher_dds_exe',
            output='screen',
            emulate_tty=True),
    ])
```
`subscriber_dds.launch.py` is the same with `executable='subscriber_dds_exe'`. Entry points: `'publisher_dds_exe = dds_tests_pkg.publisher_dds:main'`, `'subscriber_dds_exe = dds_tests_pkg.subscriber_dds:main'`; install `launch/*.launch.py` in `data_files`.
```bash
cd ~/ros2_ws/
colcon build --packages-select dds_tests_pkg
source ~/ros2_ws/install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ros2 daemon stop
ros2 daemon start
ps faux | grep "rmw-implementation"
ros2 launch dds_tests_pkg publisher_dds.launch.py        # shell 1
ros2 launch dds_tests_pkg subscriber_dds.launch.py       # shell 2, same export
```
The subscriber prints, per message, whether it was lost, the total lost and the publication-to-reception delay.

## Force losses
Set `timer_period = 0.0` in `publisher_dds.py`, rebuild, and run again: the publisher floods the topic. Results vary with the machine (in the course: up to ~9 lost messages on an 8-core system, 1 on a 12-core system). Repeat with `export RMW_IMPLEMENTATION=rmw_fastrtps_cpp` (and `ros2 run dds_tests_pkg publisher_dds_exe` / `subscriber_dds_exe`) to compare: both RMWs lose messages under flood, with no clear winner on that system; the course's tests on bigger systems favored Fast DDS.

## Pitfalls
- The subscriber is BEST_EFFORT with a publisher queue of 1: losses are expected by design; a RELIABLE subscriber would show back-pressure instead.
- Check the daemon's RMW (`ps faux | grep "rmw-implementation"`) after every switch ([[core-ros2-daemon]]).
- The delay uses the clocks of both nodes: compare only on one machine or with synchronized clocks.
