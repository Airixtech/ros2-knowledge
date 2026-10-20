---
id: core-sros2-permissions
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "permissions.xml and permissions.p7s: per-enclave grants"
domain: core
area: security
distro: humble
tested: false
audience: dev
summary: "Generated grant (CN, validity, allow rules, default DENY), DDS names rt/ rq/ rr/, ros_discovery_info, why only permissions.p7s counts, re-signing."
tags: [sros2, permissions.xml, permissions.p7s, grant, rt/, rq/, rr/, ros_discovery_info, default DENY, openssl smime -sign]
see: ["[[core-sros2-policy]]", "[[core-sros2-governance]]", "[[core-sros2-enclaves]]", "[[core-sros2-openssl-inspect]]"]
requires: []
version_notes:
  - "humble: editing permissions.p7s breaks its signature (node fails with Enforce); editing permissions.xml alone changes nothing — https://docs.ros.org/en/humble/Tutorials/Advanced/Security/The-Keystore.html (V108)"
  - "humble: grant per enclave (CN=<path>), validity = certificate, DDS names rt/ rq/…Request rr/…Reply, ros_discovery_info rule only for Fast DDS/Cyclone/Connext — https://github.com/ros2/sros2/blob/humble/sros2/sros2/keystore/_permission.py (V125)"
  - "jazzy: nodes also offer ~/get_type_description; sros2's example node profiles grant it (common/node/types.xml) — https://github.com/ros2/sros2/blob/jazzy/sros2/test/policies/common/node/types.xml (V125)"
---
# permissions.xml and permissions.p7s: per-enclave grants

**TL;DR** `generate_artifacts` turns the policy of each enclave into a DDS permissions document: one grant for the enclave's certificate name, allow rules in DDS topic names, then `DENY` for everything else. The RMW only reads the signed copy `permissions.p7s`. To change permissions, change the policy and regenerate.

## Generated permissions of the `/teleop` enclave (one repeated list shortened)
```xml
<dds xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.omg.org/spec/DDS-SECURITY/20170901/omg_shared_ca_permissions.xsd">
  <permissions>
    <grant name="/teleop">
      <subject_name>CN=/teleop</subject_name>
      <validity>
        <not_before>2022-10-14T09:22:17</not_before>
        <not_after>2032-10-12T09:22:17</not_after>
      </validity>
      <allow_rule>
        <domains>
          <id>0</id>
        </domains>
        <publish>
          <topics>
            <topic>rq/teleop_keyboard/describe_parametersRequest</topic>
            <topic>rq/teleop_keyboard/get_parameter_typesRequest</topic>
            <topic>rq/teleop_keyboard/get_parametersRequest</topic>
            <topic>rq/teleop_keyboard/list_parametersRequest</topic>
            <topic>rq/teleop_keyboard/set_parametersRequest</topic>
            <topic>rq/teleop_keyboard/set_parameters_atomicallyRequest</topic>
            <topic>rr/teleop_keyboard/describe_parametersReply</topic>
            <topic>rr/teleop_keyboard/get_parameter_typesReply</topic>
            <topic>rr/teleop_keyboard/get_parametersReply</topic>
            <topic>rr/teleop_keyboard/list_parametersReply</topic>
            <topic>rr/teleop_keyboard/set_parametersReply</topic>
            <topic>rr/teleop_keyboard/set_parameters_atomicallyReply</topic>
            <topic>rt/cmd_vel</topic>
            <topic>rt/parameter_events</topic>
            <topic>rt/rosout</topic>
          </topics>
        </publish>
        <subscribe>
          <topics>
            <!-- the same 12 rq/…Request and rr/…Reply parameter topics as under <publish> -->
            <topic>rt/clock</topic>
            <topic>rt/parameter_events</topic>
          </topics>
        </subscribe>
      </allow_rule>
      <allow_rule>
        <domains>
          <id>0</id>
        </domains>
        <publish>
          <topics>
            <topic>ros_discovery_info</topic>
          </topics>
        </publish>
        <subscribe>
          <topics>
            <topic>ros_discovery_info</topic>
          </topics>
        </subscribe>
      </allow_rule>
      <default>DENY</default>
    </grant>
  </permissions>
</dds>
```

## How to read it
- `grant name` and `subject_name` = `CN=<enclave path>`: the grant applies to the participant whose certificate has that subject. `validity` is copied from the enclave certificate; `domains/id` from `ROS_DOMAIN_ID`.
- Names are DDS names, not ROS names: topic `/cmd_vel` → `rt/cmd_vel`; a service is two topics, `rq/<name>Request` and `rr/<name>Reply`. A service **server** publishes replies and subscribes requests; a client does the opposite. Here both directions come from the `reply="ALLOW" request="ALLOW"` parameter services of `common/node.xml` ([[core-sros2-policy]]).
- The second rule allows `ros_discovery_info`, the topic where each participant announces which nodes it contains (`rmw_dds_common/ParticipantEntitiesInfo`). sros2 adds it only when generating with Fast DDS, Cyclone DDS or Connext.
- Rules are tried in order and the first match decides. Anything no rule matches gets `<default>DENY</default>`.

## Changing permissions
- Edit the policy and rerun `generate_artifacts` (or `ros2 security create_permission <keystore> <enclave> <policy.xml>`).
- Or edit `permissions.xml` and re-sign it with the Permissions CA key (official access-control tutorial):
```bash
openssl smime -sign -text -in permissions.xml -out permissions.p7s \
  --signer permissions_ca.cert.pem \
  -inkey ~/security_ws/turtlebot_keystore/private/permissions_ca.key.pem
```

## Pitfalls
- Editing `permissions.p7s` by hand, even one space, invalidates the signature: with `Enforce` the node does not start. Editing only `permissions.xml` has **no effect**, because DDS reads the signed file. (The course attributes the broken signature to `permissions.xml`.)
- With `Enforce`, a node that tries to use a topic outside its grant fails to start (the official tutorial shows this with a remapped topic).
- [changed in Jazzy: every node also offers the `~/get_type_description` service; include it in the node profiles, as sros2's example profiles do] [verify: effect when missing].
