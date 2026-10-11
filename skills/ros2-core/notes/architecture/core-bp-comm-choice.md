---
id: core-bp-comm-choice
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Choosing topic vs service vs action vs parameter"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "Decision table and rules for picking topics, services, actions or parameters, including the heavy-data-on-demand exception."
tags: [design, topic, service, action, parameter, communication patterns]
see: ["[[core-topic-pub-sub-py]]", "[[core-srv-server]]", "[[core-action-server]]", "[[core-param-api]]", "[[core-learn-concepts-comm]]"]
requires: []
version_notes: []
---
# Choosing topic vs service vs action vs parameter

**TL;DR** Continuous data → topic. One-off request with an answer in under ~1 s → service. Longer than 1 s, with progress or cancel → action. Configuration → parameters with a validation callback.

## Comparison
| | Topic | Service | Action | Parameter |
|---|---|---|---|---|
| Pattern | pub/sub N:M | req/resp 1:1 | goal+feedback+result | key/value per node |
| Blocking | no | async (call_async) | no | no |
| Feedback / cancel | no / – | no / no | yes / yes | – |
| Use | sensors, state, continuous cmds | quick query, toggle, IK | navigation, trajectories, grasp | configuration |

## Rules
- Continuous → topic; one-off with an ACK (<1 s) → service; >1 s with progress/cancel → action; config → params with validation ([[core-param-api]]).
- Golden rule: use a topic if possible, else a service, else an action.
- Exception: heavy data needed only on demand (e.g. image analysis only when asked) is better as a service than as a 30 Hz topic.
- Services suit on-demand short queries and commands: get status, trigger detection, set mode, IK. There is one server per service name and many clients ([[core-srv-server]]).
- If the task needs no feedback, cancel or parallel work → service. Fire-and-forget → topic ([[core-action-server]]).
Student explanation with analogies: [[core-learn-concepts-comm]].

## Pitfalls
- Polling a service at high rate to emulate a stream adds latency and load. Publish a topic instead.
- A service callback that takes seconds blocks its executor and gives no progress. Use an action ([[core-action-server]]).
