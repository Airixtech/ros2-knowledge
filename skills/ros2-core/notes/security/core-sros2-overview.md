---
id: core-sros2-overview
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "ROS 2 security (SROS2): DDS-Security plugins and the enabling workflow"
domain: core
area: security
distro: humble
tested: false
audience: dev
summary: "Why an open ROS graph is unsafe, DDS-Security authentication/access control/cryptography, what sros2 does, and the four enabling steps."
tags: [security, SROS2, sros2, DDS-Security, authentication, access control, encryption, PKI, certificate, CA]
see: ["[[core-sros2-keystore]]", "[[core-sros2-enclaves]]", "[[core-sros2-policy]]", "[[core-sros2-env-vars]]", "[[core-dds-overview]]"]
requires: []
version_notes:
  - "humble: a certificate contains the public key and the subject name, signed by a CA (the course said 'a certificate is a public key') — https://docs.ros.org/en/humble/Tutorials/Advanced/Security/The-Keystore.html (V110)"
  - "humble: the ros2 security tools are the sros2 package (ros_core variant); rcl only reads ROS_SECURITY_* and finds the enclave — https://www.ros.org/reps/rep-2001.html (V116)"
  - "humble: Fast DDS loads builtin.PKI-DH, builtin.Access-Permissions and builtin.AES-GCM-GMAC; no secure communication between DDS vendors — https://github.com/ros2/rmw_fastrtps/blob/humble/rmw_fastrtps_shared_cpp/src/participant.cpp (V130)"
  - "lyrical: rmw_zenoh_cpp (Tier 1 since Kilted) is not DDS; zenoh_security_tools generate_configs builds Zenoh configs from the sros2 keystore, router enclave /zenohd — https://docs.ros.org/en/lyrical/Developer-Tools/Introspection-and-analysis/Security/Introducing-ros2-security.html (V130)"
---
# ROS 2 security (SROS2): DDS-Security plugins and the enabling workflow

**TL;DR** Without security, anyone on the same network and DDS domain can list, read and publish every topic, service and parameter of the robot. ROS 2 can secure the graph through the DDS-Security plugins of its middleware. They are **off by default**: you need a keystore, one enclave per process and four environment variables.

## What DDS-Security adds
| Plugin | What it does | Files it uses |
|---|---|---|
| Authentication | Proves the identity of each domain participant. Only authenticated participants can join the graph. | `identity_ca.cert.pem`, `cert.pem`, `key.pem` |
| Access control (authorization, permissions) | Limits what each identity may do: which domain, which topics it may read or write. | `permissions_ca.cert.pem`, `governance.p7s`, `permissions.p7s` |
| Cryptography | Encrypts and signs messages: nobody can read them without the keys, or insert bogus messages. | no files of its own; the governance sets what is encrypted or only signed |

Fast DDS loads the built-in plugins `builtin.PKI-DH`, `builtin.Access-Permissions` and `builtin.AES-GCM-GMAC`.

**Authentication** (public key infrastructure, PKI) needs:
- a public/private key pair per domain participant;
- a certificate that binds the participant's public key to a name (the enclave path);
- a shared **Identity CA**: every participant is pre-configured with it and holds a certificate signed by it.

A certificate **contains** a public key plus the subject name, signed by a CA. Share certificates; keep private keys on the robot and never share them.

**Access control** maps policies from the ROS graph into two signed XML documents:
- the **governance** document says how the whole domain is secured ([[core-sros2-governance]]);
- the **permissions** document says what one participant may do, bound to its certificate name ([[core-sros2-permissions]]).

Separate concerns: give each identity only the domain and topics it needs, so that a compromised part cannot affect the rest of the system.

Both are signed by a CA the plugin trusts (the **Permissions CA**). It may be the same CA as the Identity CA, but that is not required (sros2 uses one CA for both).

**Cryptography** cost: in complex systems, encrypting and decrypting can affect a real-time control loop unless there is dedicated hardware (the course's warning; it gives no measurement).

## Who does what
- `sros2`: the `ros2 security …` tools that create keys, certificates and signed files. It is part of the `ros_core` variant, so a normal install has it.
- rcl: reads the `ROS_SECURITY_*` variables and finds the enclave directory ([[core-sros2-env-vars]]).
- The RMW (DDS vendor): loads the security plugins with those files.

## Enabling workflow
1. Create a keystore: `ros2 security create_keystore <dir>` ([[core-sros2-keystore]]).
2. Write a policy XML: which enclaves, nodes, topics and services ([[core-sros2-policy]]).
3. Generate the enclaves: `ros2 security generate_artifacts -k <dir> -p <policy.xml>` ([[core-sros2-enclaves]]).
4. Export `ROS_SECURITY_KEYSTORE`, `ROS_SECURITY_ENABLE=true`, `ROS_SECURITY_STRATEGY=Enforce` and choose the enclave per process ([[core-sros2-env-vars]]).

Course walkthrough: [[core-learn-sec-start-here]].

## Pitfalls
- A secured participant only talks to authenticated participants. A node started without the variables neither sees nor receives the secured graph.
- Secure communication between DDS vendors is not supported: use the same `RMW_IMPLEMENTATION` everywhere ([[core-env-variables]]).
- `rmw_zenoh_cpp` does not use DDS-Security. Its package `zenoh_security_tools` (`generate_configs`) turns sros2 keystores and policies into Zenoh configs, and the router needs its own enclave (`/zenohd`) [verify: steps on Humble].
