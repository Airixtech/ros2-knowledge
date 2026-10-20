---
id: core-learn-sec-unit3-cmd-listener
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Security Unit 3 (part 2): a secured cmd_vel listener"
domain: core
area: learn-security
distro: humble
tested: false
audience: students
summary: "Unit 3, section 3.4: unit2_pkg cmd_vel_subscriber (cmd_listener), its enclave /cmd_listener in the policy, run next to the secured simulation."
tags: [course, security, unit2_pkg, cmd_vel_subscriber, cmd_listener, enclave, generate_artifacts, TurtleBot3]
see: ["[[core-learn-sec-start-here]]", "[[core-sros2-generate-artifacts]]", "[[core-pkg-ament-python]]", "[[core-topic-pub-sub-py]]", "[[core-learn-sec-unit2-tb3]]"]
requires: []
version_notes:
  - "humble: setup.py and package.xml are in the package root ~/ros2_ws/src/unit2_pkg/, not in unit2_pkg/unit2_pkg/ (course path) — https://github.com/ros2/ros2cli/tree/humble/ros2pkg/ros2pkg/resource/ament_python (V114)"
  - "humble: package.xml needs <exec_depend>rclpy</exec_depend> for a node that imports rclpy (missing in the course) — https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html (V115)"
  - "humble: dependencies go before <export> in package format 3 (the course put exec_depend after it) — https://github.com/ros-infrastructure/rep/blob/master/xsd/package_format3.xsd (V138)"
  - "humble: ros2 pkg create's current template uses extras_require={'test': ['pytest']}; tests_require still builds — https://github.com/ros2/ros2cli/blob/humble/ros2pkg/ros2pkg/resource/ament_python/setup.py.em (V07)"
  - "jazzy: TurtleBot3 teleop publishes geometry_msgs/TwistStamped, so a Twist subscriber gets nothing — https://github.com/ROBOTIS-GIT/turtlebot3/blob/jazzy/turtlebot3_teleop/turtlebot3_teleop/script/teleop_keyboard.py (V135)"
---
# Security Unit 3 (part 2): a secured cmd_vel listener

**TL;DR** After the keystore tour ([[core-learn-sec-unit3-key-materials]]), write a node that prints `cmd_vel`, give it its own enclave in the policy, regenerate, and run it next to the secured simulation and teleop.

## 1. The `cmd_vel` listener (3.4.1)
```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python unit2_pkg
cd ~/ros2_ws
colcon build --packages-select unit2_pkg
```
A `SetuptoolsDeprecationWarning` during the build is only a warning ([[core-colcon-errors]]). Package layout: [[core-pkg-ament-python]].

`~/ros2_ws/src/unit2_pkg/unit2_pkg/cmd_vel_subscriber.py`:
```python
# This is the cmd_vel subscriber exercise from the Unit 2 of the course Security in ROS2
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class CmdVelSubscriber(Node):

    def __init__(self):
        super().__init__('cmd_vel_subscriber')
        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        self.get_logger().info("Checking for cmd" + str(msg.linear))


def main(args=None):
    rclpy.init(args=args)
    cmd_vel_subscriber = CmdVelSubscriber()
    rclpy.spin(cmd_vel_subscriber)
    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    cmd_vel_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```
`~/ros2_ws/src/unit2_pkg/setup.py` (package root, not the inner `unit2_pkg/` folder the course names):
```python
from setuptools import setup

package_name = 'unit2_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'cmd_listener = unit2_pkg.cmd_vel_subscriber:main',
        ],
    },
)
```
`~/ros2_ws/src/unit2_pkg/package.xml`, with `rclpy` added and the dependencies moved before `<export>` (the course has only `geometry_msgs`, after `</export>`):
```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>unit2_pkg</name>
  <version>0.0.0</version>
  <description>TODO: Package description</description>
  <maintainer email="user@todo.todo">user</maintainer>
  <license>TODO: License declaration</license>

  <exec_depend>rclpy</exec_depend>
  <exec_depend>geometry_msgs</exec_depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```
```bash
cd ~/ros2_ws/
colcon build --packages-select unit2_pkg
source ~/ros2_ws/install/setup.bash
ros2 run unit2_pkg cmd_listener      # prints nothing: nobody publishes cmd_vel yet
```

## 2. Secure it (3.4.2–3.4.3)
1. Add the `/cmd_listener` enclave to `turtlebot3_gazebo_policy.xml` and rerun `generate_artifacts`: [[core-sros2-generate-artifacts]] ("Add a node later"). `enclaves/` now also has `cmd_listener/`.
2. Run three shells, each with `ROS_SECURITY_KEYSTORE`, `ROS_SECURITY_ENABLE=true` and `ROS_SECURITY_STRATEGY=Enforce`:

| Shell | Before running | Command |
|---|---|---|
| 1 | `source /home/simulations/ros2_sims_ws/install/setup.bash`, `ROS_SECURITY_ENCLAVE_OVERRIDE=/gazebo` | `ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py` |
| 2 | same `source`, `ROS_SECURITY_ENCLAVE_OVERRIDE=/teleop`, `TURTLEBOT3_MODEL=burger` | `ros2 run turtlebot3_teleop teleop_keyboard` |
| 3 | `source ~/ros2_ws/install/setup.bash`, `ROS_SECURITY_ENCLAVE_OVERRIDE=/cmd_listener` | `ros2 run unit2_pkg cmd_listener` |

Drive with teleop; Shell 3 prints:
```text
[INFO] [1666653014.036391727] [rcl]: Found security directory: /home/user/security_ws/turtlebot_keystore/enclaves/cmd_listener
[INFO] [1666653014.364387075] [cmd_vel_subscriber]: Checking for cmdgeometry_msgs.msg.Vector3(x=0.060000000000000005, y=0.0, z=0.0)
```

## Pitfalls
- The profile's `node="cmd_vel_subscriber"` must match the name in `super().__init__('cmd_vel_subscriber')`, and the enclave path must match the override (`/cmd_listener`).
- [changed in Jazzy: TurtleBot3 teleop publishes `TwistStamped`; subscribe with `geometry_msgs.msg.TwistStamped` and read `msg.twist.linear`.]
