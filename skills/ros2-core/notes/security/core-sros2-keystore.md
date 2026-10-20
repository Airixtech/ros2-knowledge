---
id: core-sros2-keystore
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "SROS2 keystore: create_keystore and the public/private/enclaves layout"
domain: core
area: security
distro: humble
tested: false
audience: dev
summary: "ros2 security create_keystore; public/ CA certificates, private/ CA key (root of trust), enclaves/ governance; production handling."
tags: [sros2, keystore, create_keystore, ca.cert.pem, ca.key.pem, identity_ca, permissions_ca, root of trust, deployment]
see: ["[[core-sros2-overview]]", "[[core-sros2-openssl-inspect]]", "[[core-sros2-enclaves]]", "[[core-sros2-governance]]"]
requires: []
version_notes:
  - "humble: copied key materials work on any machine; the CA may be unique per robot or shared by a fleet (the course said keys 'will not work on another robot') — https://docs.ros.org/en/humble/Tutorials/Advanced/Security/The-Keystore.html (V112)"
  - "humble: create_keystore layout and symlinks; fails if the keystore exists — https://github.com/ros2/sros2/blob/humble/sros2/sros2/keystore/_keystore.py (V118)"
  - "humble: ca.key.pem is written as unencrypted PKCS#8 PEM; needed only to add enclaves or change permissions — https://github.com/ros2/sros2/blob/humble/sros2/sros2/_utilities.py (V120)"
  - "lyrical: on Windows, enclave links are hard links or copies instead of symlinks — https://github.com/ros2/sros2/blob/lyrical/sros2/sros2/_utilities.py (V118)"
---
# SROS2 keystore: create_keystore and the public/private/enclaves layout

**TL;DR** A keystore is the folder that holds every key and certificate of a secured ROS system. `ros2 security create_keystore <dir>` creates one CA (used as Identity CA and Permissions CA) and the domain governance. `ROS_SECURITY_KEYSTORE` points to it at runtime.

## Create it
```bash
mkdir ~/security_ws
cd ~/security_ws
ros2 security create_keystore turtlebot_keystore
ls turtlebot_keystore        # enclaves  private  public
```

## Layout
```text
turtlebot_keystore/
├── public/                         # low sensitivity: can be copied anywhere
│   ├── ca.cert.pem                 # CA certificate = root of trust
│   ├── identity_ca.cert.pem -> ca.cert.pem
│   └── permissions_ca.cert.pem -> ca.cert.pem
├── private/                        # high sensitivity
│   ├── ca.key.pem                  # CA private key
│   ├── identity_ca.key.pem -> ca.key.pem
│   └── permissions_ca.key.pem -> ca.key.pem
└── enclaves/
    ├── governance.xml              # domain-wide rules
    └── governance.p7s              # the same XML signed by the Permissions CA
```
`ros2 security generate_artifacts` later adds one folder per enclave under `enclaves/` ([[core-sros2-enclaves]]).

## public/: certificates
- DDS separates **identity** (who is in the graph and may join) from **permissions** (what each participant may do once it joins). Every node that joins is authenticated with a certificate.
- By default both CA certificates are links to the same `ca.cert.pem`. The CA validates the identities and permissions of every node in the graph.
- Every participant needs the CA certificate, because it is the source of trust. In production, the CA is created offline or on another machine and placed on the robot during the initial setup.
- Inspect it with openssl: [[core-sros2-openssl-inspect]].

## private/: the CA key
- `ca.key.pem` (plus its two links) is the key of the Identity and Permissions CA, and the anchor for all the security of the system. sros2 writes it as an **unencrypted** PEM file.
- You need it only to add new enclaves or change permissions, not to run the robot. Those steps can run on another machine that has the key and the policy files; the key can also be kept on dedicated hardware or removable media.
- If it is lost, you can no longer add nodes or change permissions. Anyone who can read it can add participants and change policies.

## Production handling (official deployment guidelines)
1. Create the CA inside your organization, for internal use only.
2. Generate the enclaves; ship only the ones a device needs (one enclave per application is a reasonable split).
3. Ship `public/` and the needed `enclaves/` to the devices; keep `private/` in the organization.
4. Make `enclaves/` read-only on the device.

## Pitfalls
- Copied key materials work on any machine: a stolen keystore is a valid identity. Separation comes from the CA: a CA unique per robot, or shared by a fleet that must trust each other. Participants only accept certificates signed by their own Identity CA.
- `create_keystore` on an existing keystore fails with `Unable to create keystore: …`. `generate_artifacts` creates the keystore itself if it is missing.
- The governance takes its domain from `ROS_DOMAIN_ID` when the keystore is created (default `0`): set it first ([[core-sros2-governance]]).
- Never commit `private/` to a repository or bake it into a robot image.
