---
id: nav2-learn-course-project
type: reference
owner: equipo-ros2
updated: 2026-10-14
review_by: 2027-04-12
source: manual
confidentiality: internal
title: "Course project: real robot sections I-IV and final presentation"
domain: nav2
area: learn
distro: humble
tested: false
audience: students
summary: "Course project on a real robot: Sections I-IV after Units 2-5, then a live presentation of the project."
tags: [course, students, course project, real robot, sections, presentation]
see: ["[[nav2-learn-start-here]]", "[[nav2-learn-unit2-mapping]]", "[[nav2-learn-unit5-costmaps]]"]
requires: [ros2-core]
version_notes: []
---
# Course project: real robot sections I-IV and final presentation

**TL;DR** As you learn, you apply each unit to a complete project based on a **real robot**, which you control and program remotely from anywhere through the course platform. Finish each section before the next unit, then present your project live.

## How it works
- Each course includes a project that must be solved by applying what you learned.
- The project runs in a separate development environment, closer to what you find when programming robots for companies, so it is less guided than the lessons. It is included with the course; no extra setup is needed.
- To start: copy the course project into your project area (link given in the course), open it with **Run**, and follow the instructions inside it; they appear automatically.

## Sections and when to do them
| Section | Finish it after | Uses |
|---|---|---|
| I | Unit 2, mapping | [[nav2-learn-unit2-mapping]] |
| II | Unit 3, localization | [[nav2-learn-unit3-localization]] |
| III | Unit 4, path planning | [[nav2-learn-unit4-path-planning]] |
| IV | Unit 5, obstacle avoidance | [[nav2-learn-unit5-costmaps]] |

Finish each section of the project before attempting the next unit of the course.

## Final presentation
After Section IV you are ready for a **live presentation** of your project, and then the certificate. The presentation is required because teaching others is one of the best ways to learn (the "learning pyramid").

## Tips
- Keep the same package and file names as in the exercises: the project instructions build on them.
- On the real robot, `use_sim_time` must be `false` and the robot does not drift like the simulation, but sensors are noisier: retune AMCL and the costmaps.
