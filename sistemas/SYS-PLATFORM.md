---
id: SYS-PLATFORM
type: system
title: Plataforma del rover
aliases: [Plataforma del rover]
owner: equipo-plataforma
updated: 2026-10-10
review_by: 2027-01-10
source: manual
confidentiality: internal
stack: [python]
depends_on: []
---
# Plataforma del rover
Backend en Python que recibe la telemetría del rover y la expone al resto de sistemas.

- Consumidores: SYS-VISION, SYS-WEB y SYS-MOBILE dependen de él.
- Transporte de telemetría: ver ADR-001.
- Por confirmar: formato de los mensajes y frecuencia de envío.
