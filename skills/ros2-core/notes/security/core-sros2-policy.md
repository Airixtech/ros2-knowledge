---
id: core-sros2-policy
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "SROS2 policy XML: enclaves, profiles and name rules"
domain: core
area: security
distro: humble
tested: false
audience: dev
summary: "Policy XML format (enclaves, profiles, topics/services/actions ALLOW/DENY, XInclude profiles), name expansion, one grant per enclave."
tags: [sros2, policy, policy.xml, XInclude, profile, enclave, ALLOW, DENY, turtlebot3_demo]
see: ["[[core-sros2-generate-artifacts]]", "[[core-sros2-enclaves]]", "[[core-sros2-permissions]]"]
requires: []
version_notes:
  - "humble: policy version is fixed to 0.2.0; profile needs ns and node — https://github.com/ros2/sros2/blob/humble/sros2/sros2/policy/schemas/policy.xsd (V123)"
  - "humble: all profiles of one enclave become one grant; node/ns only expand relative and ~ names — https://github.com/ros2/sros2/blob/humble/sros2/sros2/policy/templates/dds/permissions.xsl (V124)"
  - "humble: the course's policy files match the public ros-swg/turtlebot3_demo policies (Apache-2.0) — https://github.com/ros-swg/turtlebot3_demo/tree/master/policies (V136)"
  - "humble: the policy file is not the governance document (the course calls it a governance_file.xml); governance.xml is written by create_keystore — https://github.com/ros2/sros2/blob/humble/sros2/sros2/policy/schemas/policy.xsd (V139)"
  - "jazzy: node profiles also need ~/get_type_description (sros2 example profiles: common/node/types.xml) — https://github.com/ros2/sros2/blob/jazzy/sros2/test/policies/common/node/types.xml (V125)"
---
# SROS2 policy XML: enclaves, profiles and name rules

**TL;DR** A policy XML lists the enclaves and, per enclave, node profiles with the topics, services and actions they may use. sros2 turns it into one signed permissions file per enclave ([[core-sros2-generate-artifacts]]). Shared rules live in profile files pulled in with XInclude.

## Policy of the course (TurtleBot3 in Gazebo Classic)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<policy version="0.2.0" xmlns:xi="http://www.w3.org/2001/XInclude">
  <enclaves>
    <enclave path="/gazebo">
      <profiles>
        <xi:include href="profiles/gazebo.xml" xpointer="xpointer(/profiles/*)"/>
        <xi:include href="profiles/turtlebot3.xml" xpointer="xpointer(/profiles/*)"/>
      </profiles>
    </enclave>
    <enclave path="/teleop">
      <profiles>
        <profile node="teleop_keyboard" ns="/">
          <xi:include href="profiles/common/node.xml" xpointer="xpointer(/profile/*)"/>
          <topics publish="ALLOW">
            <topic>cmd_vel</topic>
          </topics>
        </profile>
      </profiles>
    </enclave>
    <enclave path="/">
      <profiles>
        <profile node="root" ns="/">
          <services reply="ALLOW" request="ALLOW">
            <service>*</service>
          </services>
          <topics publish="ALLOW" subscribe="ALLOW">
            <topic>*</topic>
          </topics>
        </profile>
      </profiles>
    </enclave>
  </enclaves>
</policy>
```
Three enclaves: `/gazebo`, `/teleop` and the allow-all root `/` ([[core-sros2-enclaves]]). The included files sit in `profiles/` next to the policy. The same files are public in `policies/` of [ros-swg/turtlebot3_demo](https://github.com/ros-swg/turtlebot3_demo/tree/master/policies), whose `tb3_gazebo_policy.xml` adds Nav2 enclaves.

A profiles file holds several node profiles. `profiles/turtlebot3.xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<profiles xmlns:xi="http://www.w3.org/2001/XInclude">
  <profile node="robot_state_publisher" ns="/">
    <xi:include href="common/node.xml" xpointer="xpointer(/profile/*)"/>
    <topics subscribe="ALLOW"><topic>joint_states</topic></topics>
    <topics publish="ALLOW"><topic>robot_description</topic><topic>tf</topic><topic>tf_static</topic></topics>
  </profile>
  <profile node="turtlebot3_diff_drive" ns="/">
    <xi:include href="common/node.xml" xpointer="xpointer(/profile/*)"/>
    <topics subscribe="ALLOW"><topic>cmd_vel</topic></topics>
    <topics publish="ALLOW"><topic>odom</topic><topic>tf</topic></topics>
  </profile>
  <profile node="turtlebot3_imu" ns="/">
    <xi:include href="common/node.xml" xpointer="xpointer(/profile/*)"/>
    <topics publish="ALLOW"><topic>imu</topic></topics>
  </profile>
  <profile node="turtlebot3_joint_state" ns="/">
    <xi:include href="common/node.xml" xpointer="xpointer(/profile/*)"/>
    <topics publish="ALLOW"><topic>joint_states</topic></topics>
  </profile>
  <profile node="turtlebot3_laserscan" ns="/">
    <xi:include href="common/node.xml" xpointer="xpointer(/profile/*)"/>
    <topics publish="ALLOW"><topic>scan</topic></topics>
  </profile>
</profiles>
```
`common/node.xml` (not shown in the course; contents as in the public demo) holds what every node needs: publish `rosout`, subscribe `/clock`, publish and subscribe `parameter_events`, and reply/request on the six `~/…parameters…` services. The course's teleop permissions show exactly these names ([[core-sros2-permissions]]).

## Elements
| Element | Attributes |
|---|---|
| `<policy>` | `version="0.2.0"` (the only accepted value) |
| `<enclave>` | `path` = enclave name (`/gazebo`) |
| `<profile>` | `ns`, `node` (both required) |
| `<topics>` / `<topic>` | `publish`, `subscribe` = `ALLOW` or `DENY` |
| `<services>` / `<service>` | `reply` (server), `request` (client) |
| `<actions>` / `<action>` | `execute` (server), `call` (client) |

## Name rules
- `/x` is absolute; `x` becomes `<ns>x`; `~x` becomes `<ns><node>x` (private names, such as the parameter services).
- All profiles of one enclave are merged into **one** grant for that enclave. `node` and `ns` only expand names: they do not restrict which node uses the grant.

## Pitfalls
- A policy is not the governance document: the course calls `turtlebot3_gazebo_policy.xml` a "governance file", but the DDS governance is `enclaves/governance.xml`, written by `create_keystore` ([[core-sros2-governance]]).
- The profile's `node` must be the real node name, otherwise its `~` parameter services get no permission [verify: whether the node then fails with `Enforce`].
- `*` in the root enclave allows every topic and service: any node that ends up in `/` can do anything.
- The Gazebo Classic node names (`gazebo`, `turtlebot3_diff_drive`…) do not exist with the new Gazebo of Jazzy: those profiles must be rebuilt ([[core-learn-sec-unit2-tb3]]).
- [changed in Jazzy: node profiles also need `~/get_type_description`; sros2's example profiles add `common/node/types.xml`] [verify: effect when missing].
