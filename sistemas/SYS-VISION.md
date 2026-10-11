---
id: SYS-VISION
type: system
title: Visión del rover
aliases: [Visión del rover]
owner: equipo-vision
updated: 2026-10-10
review_by: 2027-01-10
source: manual
confidentiality: internal
stack: [python, yolo]
depends_on: [SYS-PLATFORM]
---
# Visión del rover
Módulo de visión en Python con YOLO que procesa lo que capta el rover y produce detecciones.

- Depende de SYS-PLATFORM para la telemetría.
- SYS-NAV consume sus detecciones.
- Por confirmar: clases que detecta y modelo en uso.
