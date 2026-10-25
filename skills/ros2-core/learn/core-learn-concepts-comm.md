---
id: core-learn-concepts-comm
type: reference
owner: equipo-ros2
updated: 2026-10-25
review_by: 2027-04-23
source: manual
confidentiality: internal
title: "Concepts: topics vs services vs actions, QoS"
domain: core
area: learn
distro: humble
tested: false
audience: students
summary: "Radio/phone/delivery analogies for topics, services and actions, what is inside an action, QoS in one sentence, decision recap."
tags: [concepts, topic, service, action, QoS, students]
see: ["[[core-bp-comm-choice]]", "[[core-action-cli-status]]", "[[core-qos-policies]]"]
requires: []
version_notes: []
---
# Concepts: topics vs services vs actions, QoS

**TL;DR** A topic is a radio station, a service a phone call, and an action a delivery order with tracking. Use topics if possible → services → actions. The developer version of this decision is [[core-bp-comm-choice]].

## Nodes first
Every launched program starts at least one node, and each node handles one capability: wheel motors, a laser rangefinder, face recognition (on the rover: a lidar node, a vision node that finds rocks and hazards, a motor node). Nodes run independently and exchange data through topics, services and actions, so a robot is a network of specialized nodes.

## Topics vs services vs actions
- **Topic**: radio station. The publisher broadcasts continuously to any number of listeners, and nobody answers.
- **Service**: phone call. The client asks, and the server answers once. Good for on-demand data (e.g. a Mars→Earth link at 256 kbit/s: send the status only when asked). A face recognizer as a service runs only when a client asks "who is in front of the robot?", instead of processing images and publishing names when nobody is there; many clients can call one server.
- **Action**: delivery order with tracking. Goal → continuous feedback → final result. It can be canceled, and the client keeps working meanwhile.
Golden rule: topics if possible → services → actions. Exception: heavy data that is only needed sometimes is cheaper as a service than as a 30–50 Hz topic.

## Inside an action
An action = **Goal service** (the client sends a goal, the server accepts or rejects it) + **Feedback topic** (the server publishes progress) + **Result service** (the client requests the final result), plus a status topic and a cancel service. The server node holds the Action Server, and the caller holds the Action Client ([[core-action-server]], [[core-action-client]]).

## QoS in one sentence
The publisher decides the delivery rules (reliable vs best-effort, keep history for late joiners or not). A subscriber that asks for stricter rules than offered receives nothing ([[core-qos-policies]]).

## Decision recap (from the unit conclusions)
Use ACTIONS when you need progress feedback, a final result AND to keep doing other work meanwhile. Otherwise use SERVICES. If no result is needed, use TOPICS (a node can even publish progress on a second topic).
