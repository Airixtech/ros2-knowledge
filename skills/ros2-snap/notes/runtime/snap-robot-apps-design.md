---
id: snap-robot-apps-design
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Design the apps of a robot snap: functionalities, daemons, command-chain, stop commands"
domain: snap
area: runtime
distro: humble
tested: false
audience: dev
summary: "From robot functionalities to snap apps (daemons vs commands, a shared bring-up), command-chain with exec \"$@\", stop-command, post-stop-command."
tags: [snap apps, functionalities, bring-up, daemon, command-chain, stop-command, post-stop-command, orchestration, launch file]
see: ["[[snap-daemon]]", "[[snap-ros2-architectures]]", "[[snap-config-hooks]]", "[[snap-ros2-extensions-bases]]"]
requires: [ros2-core]
version_notes:
  - "humble: command-chain runs scripts before the command and each must end with exec \"$@\"; the ROS 2 extensions use it (snap/command-chain/ros2-launch) — https://github.com/canonical/snapcraft/blob/main/snapcraft/extensions/ros2_humble.py (SNAP-V35)"
  - "humble: stop-command and post-stop-command exist for daemons only — https://github.com/canonical/snapcraft/blob/main/snapcraft/models/project.py (SNAP-V36)"
---
# Design the apps of a robot snap: functionalities, daemons, command-chain, stop commands

**TL;DR** Design a robot snap like a library API: start from the product's functionalities, map each one to snap apps, share one bring-up service, and decide which apps are boot daemons and which are terminal commands. Then use `command-chain`, `stop-command` and `post-stop-command` to orchestrate them.

## From functionalities to apps
- **Functionalities** come from the product and the customer's needs: what a person can do with the robot. Example: a supermarket robot must clean the floor and patrol at night.
- **Apps** fulfil them. One functionality may need several apps, and one app may serve several functionalities.
- A snap app is a command to call from a terminal or a daemon that starts at boot or runs in the background. One snap can hold many apps.

Example, "supermarket-robot-snap" (all OS and ROS dependencies plus the needed files in one snap):
| App | Kind | Role |
|---|---|---|
| `core` | daemon, always running | bring-up: robot model, motor controllers; used by the other apps |
| `patrol` | daemon, can be enabled/disabled | sends navigation goals, reports suspicious activity |
| `clean` | daemon, can be enabled/disabled | navigates and drives the cleaning actuators |

## Design rules
- Make each app independent enough to make sense alone, and modular enough to combine with the others.
- **Think about the final user**: one app can replace several launch files and calls. A `patrol` app that runs a launch file and calls a service at start is one command for the user.
- Most functionality apps start as daemons at boot ([[snap-daemon]]); keep routines such as calibration as terminal commands.
- One snap with all apps is the simplest architecture; splitting into several snaps is covered in [[snap-ros2-architectures]].

## Orchestration keys
| Key | CLI app | Daemon | Runs |
|---|---|---|---|
| `command-chain` | yes | yes | listed scripts before the command |
| `stop-command` | no | yes | right before `snap stop` sends the stop signal |
| `post-stop-command` | no | yes | after the service has stopped |

```yaml
apps:
  my-app:
    command-chain: [command_chain_script1, command_chain_script2]
    command: main_command
```
The call becomes `./command_chain_script1 command_chain_script2 main_command`: each script receives the rest as arguments, so it must end with `exec "$@"`. snapd knows the chain, so `snap run --shell my-snap.my-app` still runs it ([[snap-debug-app]]); that is the difference from putting the same lines in a launcher script. The ROS 2 extensions source the ROS environment this way (`snap/command-chain/ros2-launch`).

Uses:
- `command-chain`: set up a shell environment, wait for another service.
- `stop-command`: synchronise, wait for a job to finish, save before exiting.
- `post-stop-command`: clean temporary files, notify another system, move generated files.

## Pitfalls
- A command-chain script without `exec "$@"` never starts the real command.
- `stop-command` and `post-stop-command` are ignored for plain commands: they only exist for daemons.

Adapted from the Canonical robotics documentation (CC-BY-SA 3.0).
