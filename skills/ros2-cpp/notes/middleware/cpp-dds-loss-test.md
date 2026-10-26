---
id: cpp-dds-loss-test
type: reference
owner: equipo-ros2
updated: 2026-10-26
review_by: 2027-04-24
source: manual
confidentiality: internal
title: "C++ message-loss and latency test: 50 ms publisher with IDs and stamps, BEST_EFFORT checker, launch, CMake"
domain: cpp
area: middleware
distro: humble
tested: false
audience: dev
summary: "publisher_dds.cpp sends '<id>:<s>,<ns>' every 50 ms; subscriber_dds.cpp (BEST_EFFORT) counts skipped ids and the delay; launch files, CMake, 0 ms overload."
tags: [dds_tests_pkg, publisher_dds.cpp, subscriber_dds.cpp, BEST_EFFORT, message loss, latency, RMW_IMPLEMENTATION, rmw_fastrtps_cpp, rmw_cyclonedds_cpp, rclcpp::Time, std::stoi, create_wall_timer 0ms]
see: ["[[core-dds-loss-test]]", "[[core-rmw-implementations]]", "[[core-ros2-daemon]]", "[[cpp-qos-profile]]", "[[cpp-learn-inter-unit8-dds]]"]
requires: [ros2-core]
version_notes:
  - "course: subscriber_dds.cpp built rclcpp::Time time_obj(seconds, nanoseconds) from '<s>,<ns-of-the-whole-stamp>' (the ns value overflows the uint32_t argument), left id_next and lost_messages_counter uninitialized and computed pub - now; fixed below — https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/time.hpp (CPP-V74)"
  - "humble: const MsgT::SharedPtr callbacks compile with a deprecation warning (also Lyrical); ConstSharedPtr is warning-free — https://github.com/ros2/rclcpp/blob/humble/rclcpp/include/rclcpp/any_subscription_callback.hpp (CPP-V46)"
---
# C++ message-loss and latency test

**TL;DR** The publisher sends `"<id>:<seconds>,<nanoseconds>"` every 50 ms with a growing id; the BEST_EFFORT subscriber checks that each id is the expected one, adds every gap to a loss counter and prints the delay since publication. Run the pair with each `RMW_IMPLEMENTATION` and with a 0 ms timer to see how each copes. C++ twin of [[core-dds-loss-test]]; switching middleware: [[core-rmw-implementations]].

Package: `ros2 pkg create --build-type ament_cmake dds_tests_pkg --dependencies rclcpp std_msgs`.

## `src/publisher_dds.cpp`
```cpp
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"
#include <chrono>

using namespace std::chrono_literals;

class PublisherDDS : public rclcpp::Node {
public:
  PublisherDDS() : Node("publisher_dds_obj") {
    publisher_ = this->create_publisher<std_msgs::msg::String>("dds_test", 1);
    timer_ = this->create_wall_timer(
        50ms, std::bind(&PublisherDDS::timer_callback, this));
    msgs_id = 0;
  }

private:
  void timer_callback() {
    auto msg = std_msgs::msg::String();
    auto current_time = this->now();
    auto current_time_s = current_time.seconds();
    auto current_time_ns = current_time.nanoseconds();
    time_str =
        std::to_string(current_time_s) + "," + std::to_string(current_time_ns);
    dds_msg_str = std::to_string(msgs_id) + ":" + time_str;
    msg.data = dds_msg_str;
    publisher_->publish(msg);
    RCLCPP_INFO(this->get_logger(), "Publishing: %s ", msg.data.c_str());
    ++msgs_id;
  }

  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
  int msgs_id;
  std::string time_str;
  std::string dds_msg_str;
};

int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<PublisherDDS>());
  rclcpp::shutdown();
  return 0;
}
```

## `src/subscriber_dds.cpp` (with the CPP-V74 fixes)
```cpp
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using std::placeholders::_1;

class SubscriberDDS : public rclcpp::Node {
public:
  // CPP-V74: the course leaves id_next and lost_messages_counter uninitialized
  SubscriberDDS()
  : Node("simple_subscriber"), id(0), id_next(-1),
    lost_messages_counter(0), delta_messages_lost(0) {
    rclcpp::QoS qos_profile(10);
    qos_profile.reliability(RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT);
    subscription_ = this->create_subscription<std_msgs::msg::String>(
        "dds_test", qos_profile,
        std::bind(&SubscriberDDS::listener_callback, this, _1));
  }

private:
  void listener_callback(const std_msgs::msg::String::SharedPtr msg) {
    process_dds_test_data(msg->data);
  }

  void process_dds_test_data(std::string data) {
    // The data has the format ID:Seconds,NanoSeconds
    // return:
    // ID
    // TIME Object
    delimiter = ":";
    last = 0;
    next = 0;
    while ((next = data.find(delimiter, last)) != std::string::npos) {
      id = std::stoi(data.substr(last, next - last));
      last = next + 1;
    }
    time = data.substr(last);

    if (id == 0) {
      id_next = 0;
    }

    if (id == id_next) {
      RCLCPP_WARN(this->get_logger(),
                  "MESSAGE OK: ID=%d, Next ID=%d, TOTAL MSG LOST=%d", id,
                  id_next, lost_messages_counter);
    } else {
      if (id_next != -1) {
        delta_messages_lost = id - id_next;
        lost_messages_counter = lost_messages_counter + delta_messages_lost;
        RCLCPP_ERROR(this->get_logger(),
                     "MESSAGE LOST: ID=%d, Next ID=%d, DELTA MSG LOST=%d, "
                     "TOTAL MSG LOST=%d",
                     id, id_next, delta_messages_lost, lost_messages_counter);
      } else {
      }
    }
    id_next = id + 1;

    delimiter = ",";
    last = 0;
    next = 0;
    while ((next = time.find(delimiter, last)) != std::string::npos) {
      seconds = std::stod(time.substr(last, next - last));
      last = next + 1;
    }
    nanoseconds = std::stod(time.substr(last));

    // CPP-V74: the second field is the whole stamp in ns; the course wrote
    // rclcpp::Time time_obj(seconds, nanoseconds) and
    // delta = time_obj.nanoseconds() - time_now_obj.nanoseconds()
    rclcpp::Time time_obj(static_cast<int64_t>(nanoseconds));
    rclcpp::Time time_now_obj = this->now();
    delta = time_now_obj.nanoseconds() - time_obj.nanoseconds();
    RCLCPP_INFO(this->get_logger(),
                "DELTA Between PUB and SUB = %lf nanoseconds", delta);
  }

  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
  int id;
  int id_next;
  int lost_messages_counter;
  int delta_messages_lost;
  std::string time;
  std::string delimiter;
  double seconds;
  double nanoseconds;
  size_t last;
  size_t next;
  double delta;
};

int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SubscriberDDS>());
  rclcpp::shutdown();
  return 0;
}
```
- **ID check**: `id_next` starts at −1, so the first message only sets the expectation (a subscriber started late counts no loss); `id == 0` resets it when the publisher restarts. A jump from 5 to 8 prints `MESSAGE LOST … DELTA MSG LOST=2`.
- **Delay**: subscriber time minus publication stamp, both from `this->now()` on the same machine. `.nanoseconds()` on both sides avoids subtracting `rclcpp::Time` objects of different clock types (`Time(int64_t)` is system time, `now()` ROS time), which throws.
- BEST_EFFORT on the subscriber accepts losses instead of retransmitting; the publisher's depth is 1.

## Launch files and CMake
`launch/publisher_dds.launch.py` and `launch/subscriber_dds.launch.py` each start one executable:
```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='dds_tests_pkg',
             executable='publisher_dds_exe',   # subscriber_dds_exe in the other file
             output='screen',
             emulate_tty=True),
    ])
```
```cmake
add_executable(publisher_dds_exe src/publisher_dds.cpp)
ament_target_dependencies(publisher_dds_exe rclcpp std_msgs)
add_executable(subscriber_dds_exe src/subscriber_dds.cpp)
ament_target_dependencies(subscriber_dds_exe rclcpp std_msgs)

install(TARGETS
  publisher_dds_exe
  subscriber_dds_exe
  DESTINATION lib/${PROJECT_NAME})

# Install launch files.
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}/)
```
The rest of CMakeLists.txt is the `ros2 pkg create` template with `find_package(std_msgs REQUIRED)` ([[cpp-pkg-cmake]]).

## Runs
```bash
ros2 launch dds_tests_pkg subscriber_dds.launch.py      # first
ros2 launch dds_tests_pkg publisher_dds.launch.py
```
To overload the system, change the timer to `this->create_wall_timer(0ms, std::bind(&PublisherDDS::timer_callback, this))`, rebuild and run again: the publisher sends as fast as it can and losses appear, more on weaker machines. Compare middlewares with `export RMW_IMPLEMENTATION=rmw_fastrtps_cpp` / `rmw_cyclonedds_cpp` before `ros2 run dds_tests_pkg subscriber_dds_exe` and `ros2 run dds_tests_pkg publisher_dds_exe` in each terminal: results depend on hardware, load and network; no implementation wins everywhere ([[cpp-learn-inter-unit8-dds]]).

## Pitfalls
- Different `RMW_IMPLEMENTATION` values in the two terminals: cross-vendor communication often works but is not guaranteed (Humble docs, About different middleware vendors), and then you measure the pair, not one middleware. Export the same value in both.
- After switching middleware, restart the ros2 daemon if CLI tools show stale results ([[core-ros2-daemon]]).
