---
id: core-sros2-generate-artifacts
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "ros2 security generate_artifacts: build and update enclaves from a policy"
domain: core
area: security
distro: humble
tested: false
audience: dev
summary: "generate_artifacts -k -p (-e), adding a node's enclave and regenerating, create_permission, generate_policy, list of ros2 security verbs."
tags: [sros2, generate_artifacts, create_permission, generate_policy, create_enclave, list_enclaves, ros2 security, ROS_DOMAIN_ID]
see: ["[[core-sros2-policy]]", "[[core-sros2-enclaves]]", "[[core-sros2-keystore]]", "[[core-learn-sec-unit3-cmd-listener]]"]
requires: []
version_notes:
  - "humble: generate_artifacts -k/--keystore-root-path, -e/--enclaves, -p/--policy-files; creates a missing keystore, keeps existing cert/key, rewrites permissions; uses ROS_DOMAIN_ID and the RMW — https://github.com/ros2/sros2/blob/humble/sros2/sros2/api/_artifact_generation.py (V121)"
  - "humble: verbs create_keystore, create_enclave, create_permission, generate_artifacts, generate_policy, list_enclaves (+ deprecated create_key, list_keys) — https://github.com/ros2/sros2/blob/humble/sros2/setup.py (V122)"
  - "lyrical: deprecated verbs create_key and list_keys removed in Kilted — https://docs.ros.org/en/rolling/Releases/Kilted-Kaiju-Complete-Changelog.html (V122)"
---
# ros2 security generate_artifacts: build and update enclaves from a policy

**TL;DR** `ros2 security generate_artifacts -k <keystore> -p <policy.xml>` creates or updates one enclave per `<enclave>` of the policy: key, certificate and signed permissions. Run it again after every policy change. Run it with the same `ROS_DOMAIN_ID` and RMW as the robot.

## Generate
```bash
cd ~/security_ws
ros2 security generate_artifacts -k turtlebot_keystore/ -p ~/ros2_ws/src/turtlebot3_security_policy/policies/turtlebot3_gazebo_policy.xml
ls turtlebot_keystore/enclaves      # gazebo/ teleop/ + the root enclave's files ([[core-sros2-enclaves]])
```
| Option | Meaning |
|---|---|
| `-k`, `--keystore-root-path` | keystore; default `$ROS_SECURITY_KEYSTORE`. Created if it is not a valid keystore |
| `-p`, `--policy-files` | one or more policy XML files |
| `-e`, `--enclaves` | extra enclave names; created with allow-all permissions unless a policy file also defines them |

What it does per enclave: it creates `cert.pem`/`key.pem` only if they are missing (existing identities are kept), then writes and signs `permissions.xml` → `permissions.p7s`.

## Add a node later
Add an enclave for it to the policy (the course's `cmd_vel_subscriber`):
```xml
    <enclave path="/cmd_listener">
      <profiles>
        <profile node="cmd_vel_subscriber" ns="/">
          <xi:include href="profiles/common/node.xml" xpointer="xpointer(/profile/*)"/>
          <topics subscribe="ALLOW">
            <topic>cmd_vel</topic>
          </topics>
        </profile>
      </profiles>
    </enclave>
```
Then run the same `generate_artifacts` command: `enclaves/cmd_listener/` appears, and the permissions of every enclave in the policy are rewritten. Start the node with `--enclave /cmd_listener` or `ROS_SECURITY_ENCLAVE_OVERRIDE=/cmd_listener` ([[core-sros2-env-vars]]).

## The other verbs
| Verb | Use |
|---|---|
| `create_keystore <dir>` | new keystore ([[core-sros2-keystore]]) |
| `create_enclave <keystore> <name>` | one enclave with allow-all permissions |
| `create_permission <keystore> <name> <policy.xml>` | rewrite one enclave's permissions from a policy |
| `generate_policy <file.xml>` | write a policy from the running graph: a starting point to review and tighten |
| `list_enclaves <keystore>` | enclaves found in the keystore |

## Pitfalls
- The files take the `ROS_DOMAIN_ID` set at generation time (default 0), and the `ros_discovery_info` rule is added only when the current RMW is Fast DDS, Cyclone DDS or Connext. Generate with the runtime values ([[core-sros2-governance]]).
- Generating the artifacts needs the CA private key (`private/`): do it on the machine that holds the keystore, then copy `public/` and `enclaves/` to the robot ([[core-sros2-keystore]]).
- [changed in Lyrical: `create_key` and `list_keys` are gone (removed in Kilted); use `create_enclave` and `list_enclaves`.]
