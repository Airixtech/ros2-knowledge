---
id: core-sros2-enclaves
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "SROS2 enclaves: what they are and the files in each enclave"
domain: core
area: security
distro: humble
tested: false
audience: dev
summary: "Enclave = one security identity + permissions per process; the six runtime files, root enclave /, create_enclave, list_enclaves."
tags: [sros2, enclave, cert.pem, key.pem, permissions.p7s, governance.p7s, root enclave, create_enclave, list_enclaves]
see: ["[[core-sros2-policy]]", "[[core-sros2-env-vars]]", "[[core-sros2-permissions]]", "[[core-sros2-keystore]]"]
requires: []
version_notes:
  - "humble: the six files the RMW loads include permissions.p7s (signed); permissions.xml is not read at runtime (the course listed permissions.xml as the signed file) — https://github.com/ros2/rmw_dds_common/blob/humble/rmw_dds_common/src/security.cpp (V107)"
  - "humble: a policy with enclave path='/' creates the root enclave in enclaves/ itself; it is the default for processes without --enclave (the course counted two enclaves, its policy has three) — https://github.com/ros2/sros2/blob/humble/sros2/sros2/keystore/_enclave.py (V109)"
  - "humble: since Foxy one participant per context, so the enclave path is independent of node names — https://design.ros2.org/articles/ros2_security_enclaves.html (V137)"
  - "jazzy: each identity/key file may instead be a *.p11 file holding a pkcs11: URI (HSM), if the RMW supports it — https://github.com/ros2/rmw_dds_common/blob/jazzy/rmw_dds_common/src/security.cpp (V133)"
---
# SROS2 enclaves: what they are and the files in each enclave

**TL;DR** An enclave is one security identity and its permissions: a folder `enclaves/<path>` in the keystore. Every process uses exactly one enclave; all nodes in that process share it. A process with no enclave set uses the root enclave `/` (the `enclaves/` folder itself).

## Concept
- The resources of an enclave operate in the same security domain, use the same Identity CA and Permissions CA, and share one security perimeter. All secure interactions use an enclave that holds its runtime security artifacts.
- An enclave does not have to be per node. You choose the scope at deployment: one node, a group of processes, a device or a whole graph. Put in one enclave the nodes that may share the same policies.
- Why per process: since Foxy, a process (context) has one DDS participant, and a participant can hold only one identity. Enclave paths therefore replaced the old per-node directories.

## Files of an enclave
| File | Role | Unique to the enclave |
|---|---|---|
| `cert.pem` | its certificate, subject `CN=<enclave path>`, signed by the Identity CA; shared with peers | yes |
| `key.pem` | its private key (signing and decryption); never shared | yes |
| `permissions.p7s` | its permissions, signed by the Permissions CA | yes |
| `governance.p7s` | link to the domain governance | link |
| `identity_ca.cert.pem` | link to the Identity CA | link |
| `permissions_ca.cert.pem` | link to the Permissions CA | link |
| `permissions.xml` | unsigned source of `permissions.p7s`; **not read at runtime** | yes |

The RMW needs the first six (plus an optional `crl.pem`, a certificate revocation list). If one is missing, Fast DDS starts the node without security (permissive) or fails (`Enforce`: "couldn't find all security files!").

## Keystore after the course's policy (three enclaves)
```text
turtlebot_keystore/enclaves/
├── governance.xml, governance.p7s
├── cert.pem, key.pem, permissions.xml, permissions.p7s       # root enclave "/"
├── identity_ca.cert.pem -> ../public/identity_ca.cert.pem
├── permissions_ca.cert.pem -> ../public/permissions_ca.cert.pem
├── gazebo/                                                  # enclave "/gazebo"
└── teleop/                                                  # enclave "/teleop"
    ├── cert.pem, key.pem, permissions.xml, permissions.p7s
    ├── governance.p7s -> ../governance.p7s
    ├── identity_ca.cert.pem -> ../../public/identity_ca.cert.pem
    └── permissions_ca.cert.pem -> ../../public/permissions_ca.cert.pem
```
The course reports "two enclaves" (gazebo, teleop). Its own policy and listing show a third one: `/`, whose files sit directly in `enclaves/`.

## Other ways to make or see enclaves
```bash
ros2 security create_enclave ~/security_ws/turtlebot_keystore /my_robot/camera   # no policy: allow-all permissions
ros2 security list_enclaves ~/security_ws/turtlebot_keystore                      # every folder that has a key.pem
```
Enclave names follow ROS namespace rules (`/a/b`).

## Pitfalls
- The root enclave `/` is what every process gets when nothing selects an enclave. If the policy gives `/` allow-all rules (the course's does), any node started with the security variables but without an enclave can do everything. Keep `/` minimal, or leave it out of the policy.
- `create_enclave` without a policy writes allow-all permissions (all topics, services and actions). Restrict them with a policy ([[core-sros2-policy]]).
- Editing `permissions.xml` has no effect: the RMW reads `permissions.p7s` ([[core-sros2-permissions]]).
- Composing nodes from different policies into one process merges them into one identity: give that process an enclave that allows the union.
