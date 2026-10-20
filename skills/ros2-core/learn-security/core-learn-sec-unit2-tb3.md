---
id: core-learn-sec-unit2-tb3
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Security Unit 2: TurtleBot3 simulation and teleop with security enabled"
domain: core
area: learn-security
distro: humble
tested: false
audience: students
summary: "Unit 2 steps: keystore, generate_artifacts from the TurtleBot3 policy, Gazebo + teleop without and with security, checking the graph."
tags: [course, security, TurtleBot3, turtlebot3_gazebo, teleop_keyboard, keystore, generate_artifacts, ROS_SECURITY_ENCLAVE_OVERRIDE]
see: ["[[core-learn-sec-start-here]]", "[[core-sros2-keystore]]", "[[core-sros2-generate-artifacts]]", "[[core-sros2-env-vars]]", "[[core-learn-sec-unit3-cmd-listener]]"]
requires: []
version_notes:
  - "humble: the policy creates three enclaves (/gazebo, /teleop and the root /), not two — https://github.com/ros2/sros2/blob/humble/sros2/sros2/keystore/_enclave.py (V109)"
  - "humble: an unsecured shell cannot discover authenticated participants; inspect with the variables, an enclave and --no-daemon — https://docs.ros.org/en/humble/Tutorials/Advanced/Security/Introducing-ros2-security.html (V129)"
  - "jazzy: turtlebot3_world.launch.py runs the new Gazebo (ros_gz_sim, ros_gz_bridge): the Gazebo Classic profiles no longer match; teleop publishes TwistStamped — https://github.com/ROBOTIS-GIT/turtlebot3_simulations/blob/jazzy/turtlebot3_gazebo/launch/turtlebot3_world.launch.py (V134)"
---
# Security Unit 2: TurtleBot3 simulation and teleop with security enabled

**TL;DR** Create a keystore, generate enclaves from the TurtleBot3 policy, then run the same Gazebo simulation and teleop twice: first open (anyone sees everything), then with security on (each shell uses its enclave, and an outside shell sees nothing).

## 1. Keystore and enclaves (Examples 2.1–2.3)
```bash
cd
mkdir ~/security_ws
cd ~/security_ws
ros2 security create_keystore turtlebot_keystore
ls turtlebot_keystore/enclaves           # governance.p7s  governance.xml

cd ~/ros2_ws/src
git clone <policy repository: link given in the course>   # → turtlebot3_security_policy/
ls turtlebot3_security_policy/policies/  # profiles  turtlebot3_gazebo_policy.xml

cd ~/security_ws
ros2 security generate_artifacts -k turtlebot_keystore/ -p ~/ros2_ws/src/turtlebot3_security_policy/policies/turtlebot3_gazebo_policy.xml
cd ~/security_ws/turtlebot_keystore/enclaves
ll
```
`enclaves/` now has `gazebo/`, `teleop/`, and the files of the root enclave `/` (`cert.pem`, `key.pem`, `permissions.*`). The policy defines **three** enclaves; the course mentions only two. Contents of each file: [[core-sros2-enclaves]]; the policy: [[core-sros2-policy]].

## 2. Without security (Examples 2.4–2.5)
```bash
# Shell 1
source /home/simulations/ros2_sims_ws/install/setup.bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
# Shell 2
source /home/simulations/ros2_sims_ws/install/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 run turtlebot3_teleop teleop_keyboard
```
Gazebo shows the TurtleBot3 spawned in its world. Teleop prints:
```text
Control Your TurtleBot3!
---------------------------
Moving around:
        w
   a    s    d
        x

w/x : increase/decrease linear velocity (Burger : ~ 0.22, Waffle and Waffle Pi : ~ 0.26)
a/d : increase/decrease angular velocity (Burger : ~ 2.84, Waffle and Waffle Pi : ~ 1.82)

space key, s : force stop

CTRL-C to quit
```
Keys (Shell 2 focused): `w`/`x` linear velocity up/down, `a`/`d` angular velocity, `s` stop.

Shell 3 sees the whole application:
```text
$ ros2 node list
/gazebo
/robot_state_publisher
/teleop_keyboard
/turtlebot3_diff_drive
/turtlebot3_imu
/turtlebot3_joint_state
/turtlebot3_laserscan
$ ros2 topic list
/clock
/cmd_vel
/imu
/joint_states
/odom
/parameter_events
/performance_metrics
/robot_description
/rosout
/scan
/tf
/tf_static
```
That is not safe. Stop shells 1 and 2 with `Ctrl+C`.

## 3. With security (Examples 2.6–2.7)
```bash
# Shell 1
export ROS_SECURITY_KEYSTORE=~/security_ws/turtlebot_keystore
export ROS_SECURITY_ENABLE=true
export ROS_SECURITY_STRATEGY=Enforce
export ROS_SECURITY_ENCLAVE_OVERRIDE=/gazebo
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
# Shell 2
export TURTLEBOT3_MODEL=burger
export ROS_SECURITY_KEYSTORE=~/security_ws/turtlebot_keystore
export ROS_SECURITY_ENABLE=true
export ROS_SECURITY_STRATEGY=Enforce
export ROS_SECURITY_ENCLAVE_OVERRIDE=/teleop
ros2 run turtlebot3_teleop teleop_keyboard
```
Each process of the launch (`gzserver`, `robot_state_publisher`, `spawn_entity.py`) logs its enclave, and so does teleop:
```text
[robot_state_publisher-3] [INFO] [1665833657.588441208] [rcl]: Found security directory: /home/user/security_ws/turtlebot_keystore/enclaves/gazebo
[INFO] [1665834714.501743104] [rcl]: Found security directory: /home/user/security_ws/turtlebot_keystore/enclaves/teleop
```
The robot moves exactly as before. Variables explained: [[core-sros2-env-vars]].

## 4. Check it (2.3.2.3)
In Shell 3, without the variables, `ros2 topic list` shows only `/parameter_events` and `/rosout`, and `ros2 node list` prints nothing. This shell is not authenticated, so it cannot discover the secured participants: the course's "the data is encrypted" is the visible effect. To look inside a secured graph, see [[core-sros2-env-vars]].

## Pitfalls
- With `Enforce`, a typo in the enclave path stops the process instead of running it unsecured: read the `Found security directory` lines.
- [changed in Jazzy: the TurtleBot3 simulation uses the new Gazebo (`ros_gz_sim`, `ros_gz_bridge` `parameter_bridge`), so the Gazebo Classic node profiles no longer match; build the policy again, e.g. starting from `ros2 security generate_policy` on the running graph] [verify].
