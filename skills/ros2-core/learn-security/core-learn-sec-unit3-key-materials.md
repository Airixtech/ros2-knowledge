---
id: core-learn-sec-unit3-key-materials
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Security Unit 3 (part 1): tour of the keystore files"
domain: core
area: learn-security
distro: humble
tested: false
audience: students
summary: "Unit 3, sections 3.0–3.3: commands to explore public/, private/, enclaves/, governance and the teleop enclave, with the note explaining each."
tags: [course, security, keystore, openssl, governance, permissions, enclave, turtlebot_keystore]
see: ["[[core-learn-sec-start-here]]", "[[core-sros2-keystore]]", "[[core-sros2-openssl-inspect]]", "[[core-sros2-enclaves]]", "[[core-learn-sec-unit3-cmd-listener]]"]
requires: []
version_notes: []
---
# Security Unit 3 (part 1): tour of the keystore files

**TL;DR** Unit 3 starts by exploring what Unit 2 generated in `turtlebot_keystore`: the public CA certificates, the private CA key, the policy and its profiles, the enclaves, the governance and the teleop permissions. Run each command, then read the note that explains the output. The corrections of the course's explanations are in those notes.

## Steps
| Step | Command | Explained in |
|---|---|---|
| Keystore folders | `cd ~/security_ws/turtlebot_keystore && ls` → `enclaves private public` | [[core-sros2-keystore]] |
| Public CA certificate | `cd public && ll`, `openssl x509 -in ca.cert.pem -text -noout` | [[core-sros2-openssl-inspect]] |
| Private CA key | `cd private && ll`, `openssl ec -in ca.key.pem -text -noout` | [[core-sros2-openssl-inspect]] |
| Policy and profiles | `cat ~/ros2_ws/src/turtlebot3_security_policy/policies/turtlebot3_gazebo_policy.xml`, `cat ~/ros2_ws/src/turtlebot3_security_policy/policies/profiles/turtlebot3.xml` | [[core-sros2-policy]] |
| Enclaves folder | `cd ~/security_ws/turtlebot_keystore/enclaves && ll` | [[core-sros2-enclaves]] |
| Governance | `cat governance.xml`, `cat governance.p7s`, `openssl smime -verify -in governance.p7s -CAfile ../public/permissions_ca.cert.pem` | [[core-sros2-governance]] |
| Teleop enclave | `cd teleop && ll`, `cat permissions.xml` | [[core-sros2-enclaves]], [[core-sros2-permissions]] |

## Pitfalls
- `openssl ec` and `cat` on `private/ca.key.pem` print the CA's secret key: fine on your course machine, never in a shared screen or document ([[core-sros2-openssl-inspect]]).
- The course counts two enclaves and calls `permissions.xml` the signed file: there are three enclaves, and the signed file is `permissions.p7s` ([[core-sros2-enclaves]]).

Next: [[core-learn-sec-unit3-cmd-listener]].
