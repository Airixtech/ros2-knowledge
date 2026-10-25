# ros2-knowledge

Base de conocimiento de **ROS 2** en notas atómicas de Markdown, con ocho skills: **ros2-core** (ROS 2 base), **ros2-bt** (behavior trees con BehaviorTree.CPP), **ros2-snap** (empaquetar y desplegar apps ROS 2 como snaps), **ros2-nav2** (navegación con Nav2), **ros2-urdf** (describir robots con URDF y xacro), **ros2-control** (controladores y hardware interfaces con ros2_control), **ros2-gazebo** (simular robots en Gazebo Sim) y **ros2-tf** (frames y transformaciones con TF2). Sirve para dos cosas:

- **Leer y estudiar** en [Obsidian](https://obsidian.md), con enlaces `[[...]]` entre las notas.
- **Usarla como Skills de Claude**, para que genere código y configuraciones ROS 2 correctas y ayude a depurar.

*ROS 2 knowledge base (core, behavior trees, snaps, Nav2, URDF, ros2_control, Gazebo, TF) as atomic Markdown notes, for Obsidian and as Claude Skills. Notes are in English.*

**Humble es la versión de referencia** (Ubuntu 22.04, Python 3.10). Las diferencias con Jazzy y Lyrical están marcadas en cada nota. No se reemplazan. Excepciones: **ros2-gazebo** toma Jazzy + Gazebo Harmonic como referencia, y marca Humble + Fortress con enlaces a las fuentes oficiales de Humble; **ros2-control** toma Jazzy como referencia (la API de su curso), y da la forma Humble de cada diferencia desde las ramas oficiales `humble`; **ros2-tf** toma Jazzy como referencia (el código y las salidas de su curso; la API de tf2 en Python es la misma en Humble).

## Contenido

| Carpeta | Qué hay |
|---|---|
| `skills/ros2-core/` | Skill base de ROS 2: 134 notas ([índice](skills/ros2-core/SKILL.md)) |
| `skills/ros2-core/notes/` | Notas técnicas por área: `build-run`, `core-api` (nodos, parámetros, executors), `communication` (topics, services, actions, interfaces), `middleware` (QoS, DDS y RMW), `security` (SROS2: keystore, enclaves, permisos), `recipes`, `tools`, `architecture` |
| `skills/ros2-core/learn/` | Material del curso: conceptos y ejercicios de las Units 2–8 ([empieza aquí](skills/ros2-core/learn/core-learn-start-here.md)) |
| `skills/ros2-core/learn-intermediate/` | Material del curso intermedio con el MP-400 en simulación: Units 2–9 y proyecto final ([empieza aquí](skills/ros2-core/learn-intermediate/core-learn-inter-start-here.md)) |
| `skills/ros2-core/learn-security/` | Material del curso de seguridad (SROS2) con TurtleBot3 en simulación: Units 2–3 ([empieza aquí](skills/ros2-core/learn-security/core-learn-sec-start-here.md)) |
| `skills/ros2-core/migration/` | Cambios Humble → Jazzy → Lyrical y una checklist para migrar proyectos |
| `skills/ros2-bt/` | Skill de behavior trees (BehaviorTree.CPP v3, con las diferencias de v4): 32 notas ([índice](skills/ros2-bt/SKILL.md)). Necesita `ros2-core` |
| `skills/ros2-bt/notes/` | Notas técnicas por área: `concepts` (qué es un BT, Sequence/Fallback, nodos reactivos y asíncronos, BT vs FSM, BT estocásticos), `btcpp` (la API: XML, factory, ports, blackboard, SubTrees, Groot), `ros2` (nodos BT que hablan con ROS 2) |
| `skills/ros2-bt/learn/` | Material del curso de behavior trees con un TurtleBot 3 en simulación: Units 1–5 y proyecto ([empieza aquí](skills/ros2-bt/learn/bt-learn-start-here.md)) |
| `skills/ros2-bt/migration/` | Cambios de BehaviorTree.CPP v3 (Humble) → v4 (Jazzy, Lyrical) |
| `skills/ros2-snap/` | Skill de snaps para ROS 2 (Humble/core22, con las diferencias de Jazzy y Lyrical): 23 notas ([índice](skills/ros2-snap/SKILL.md)). Necesita `ros2-core` |
| `skills/ros2-snap/notes/` | Notas técnicas por área: `basics` (snapcraft.yaml, build, extensiones ROS 2 y bases), `runtime` (confinement, interfaces, daemons, datos, hooks, depuración), `deployment` (Snap Store, canales, CI con GitHub Actions, arquitecturas, content sharing, Ubuntu Core) |
| `skills/ros2-snap/learn/` | Material del taller de snaps: el snap talker-listener y el ejercicio `ros2topic` ([empieza aquí](skills/ros2-snap/learn/snap-learn-start-here.md)) |
| `skills/ros2-snap/migration/` | Cambios de snaps Humble (core22) → Jazzy (core24) → Lyrical (core26) |
| `skills/ros2-urdf/` | Skill de descripción de robots (URDF y xacro, Humble): 16 notas ([índice](skills/ros2-urdf/SKILL.md)). Necesita `ros2-core` |
| `skills/ros2-urdf/notes/` | Notas técnicas por área: `model` (links, joints, mimic y otros elementos, inercia, frames en RViz2), `workflow` (paquete `*_description`, joint_state_publisher, xacro, macros, exportar desde Onshape) |
| `skills/ros2-urdf/learn/` | Material del curso de URDF: urdfbot, box_bot y el cuadrúpedo, Units 2, 3 y 8 ([empieza aquí](skills/ros2-urdf/learn/urdf-learn-start-here.md)) |
| `skills/ros2-urdf/migration/` | Cambios de URDF Humble → Jazzy → Lyrical (urdfdom, capsule, robot_state_publisher) |
| `skills/ros2-control/` | Skill de ros2_control (Jazzy, con Humble, Kilted y Lyrical marcados): 49 notas ([índice](skills/ros2-control/SKILL.md)). Necesita `ros2-core` y `ros2-urdf` |
| `skills/ros2-control/notes/` | Notas técnicas por área: `framework` (arquitectura, estados de un controlador), `setup` (YAML de controladores y parámetros de JTC, etiqueta `<ros2_control>`, launch en simulación y en hardware real), `manager` (CLI `ros2 control`, servicios, spawner), `hardware` (escribir un hardware interface: plantilla, pluginlib, CMake, ejemplo Dynamixel), `controllers` (controladores incluidos: forward, JTC, diff_drive; escribir un controlador propio) |
| `skills/ros2-control/learn/` | Material del curso de ros2_control, partes 1 y 2: el brazo rrbot, el diffbot y el cuadrúpedo Solo 8, Units 1–8 ([empieza aquí](skills/ros2-control/learn/control-learn-start-here.md)) |
| `skills/ros2-control/migration/` | La API de hardware y de controladores y las demás diferencias en Humble, y Jazzy → Kilted/Lyrical (métodos eliminados, realtime_tools, nuevos valores por defecto) |
| `skills/ros2-gazebo/` | Skill de Gazebo Sim (Jazzy + Harmonic, con Humble + Fortress marcado): 25 notas ([índice](skills/ros2-gazebo/SKILL.md)). Necesita `ros2-core`, `ros2-urdf` y `ros2-control` |
| `skills/ros2-gazebo/notes/` | Notas técnicas por área: `sim` (arrancar Gazebo, rutas de recursos, mundos SDF, spawn, fricción), `plugins` (DiffDrive, JointStatePublisher, ros_gz_bridge, varios robots, mover un modelo a un frame de TF), `control` (gz_ros2_control, controladores, acciones, velocidad), `sensors` (lidar, nube de puntos, cámaras, IMU, GPS) |
| `skills/ros2-gazebo/learn/` | Material del curso de URDF en simulación: box_bot en Gazebo, Units 4–7, y el mapa del curso completo ([empieza aquí](skills/ros2-gazebo/learn/gazebo-learn-start-here.md)) |
| `skills/ros2-gazebo/migration/` | Humble + Fortress (tabla de nombres y fuentes oficiales de Humble) y Harmonic → Jetty (Lyrical) |
| `skills/ros2-tf/` | Skill de TF2 (Jazzy, con Humble y Lyrical marcados): 14 notas ([índice](skills/ros2-tf/SKILL.md)). Necesita `ros2-core` y `ros2-urdf` |
| `skills/ros2-tf/notes/` | Notas técnicas por área: `frames` (marcos, transformaciones, el árbol de TF, TF en RViz2), `tools` (view_frames, rqt_tf_tree, tf2_echo, tf2_monitor y sellos de tiempo), `broadcast` (broadcaster desde odometría, static_transform_publisher, broadcaster estático en Python) |
| `skills/ros2-tf/learn/` | Material del curso de TF: el Cam_bot, la tortuga y el unicycle en simulación, Units 1–4 ([empieza aquí](skills/ros2-tf/learn/tf-learn-start-here.md)) |
| `skills/ros2-tf/migration/` | Diferencias del curso en Humble (+ Fortress) y Lyrical (salidas, opciones de RViz, static_transform_publisher, tópicos de TF) |
| `skills/ros2-nav2/` | Skill de Nav2: 96 notas ([índice](skills/ros2-nav2/SKILL.md)). Necesita `ros2-core` y `ros2-bt` |
| `skills/ros2-nav2/notes/` | Notas técnicas por área: `bringup`, `mapping`, `localization`, `planning-control`, `behavior-trees`, `costmaps` (con filtros), `commander` (Simple Commander, waypoints), `plugins` (plugins propios de costmap, planner y controller), `multi-robot` |
| `skills/ros2-nav2/learn/` | Material de dos cursos: navegación con TurtleBot3, Units 1–6 y proyecto ([empieza aquí](skills/ros2-nav2/learn/nav2-learn-start-here.md)), y navegación avanzada en un almacén con el MP-400, Units 1–4 ([empieza aquí](skills/ros2-nav2/learn/nav2-learn-adv-start-here.md)) |
| `skills/ros2-nav2/migration/` | Cambios de Nav2 Humble → Jazzy → Lyrical y una checklist para migrar configuraciones |
| `tools/` | Scripts para generar índices, mantener los campos de revisión, validar, ver enlaces y empaquetar los skills |
| `reports/` | Auditorías de versiones con fuentes (las notas citan sus IDs: `Vxx` en core, `BT-Vxx` en behavior trees, `NAV2-Vxx` en Nav2, `SNAP-Vxx` en snaps, `URDF-Vxx` en URDF, `CONTROL-Vxx` en ros2_control, `GZ-Vxx` en Gazebo, `TF-Vxx` en TF) y reporte de enlaces |

Cada nota sigue el mismo formato: un TL;DR de 1–2 líneas, luego el código o los comandos, y al final los errores típicos. Marcas que vas a encontrar:

| Marca | Significado |
|---|---|
| `[Humble]` | Solo aplica a Humble |
| `[Humble: …]` | Qué usar en Humble, en los skills que toman Jazzy como referencia |
| `[≥Jazzy]` | Existe desde Jazzy (o una versión posterior) |
| `[changed in Jazzy: …]` / `[changed in Lyrical: …]` | Qué usar en esa versión |
| `[v4: …]` | Qué usar con BehaviorTree.CPP 4 (depende de la versión de la librería, no de la distro) |
| `[verify]` | Todavía sin confirmar con una fuente o una compilación |

## Leerlo en Obsidian

1. Clona el repo, dentro de tu bóveda o como una bóveda propia:
   ```bash
   git clone https://github.com/Airixtech/ros2-knowledge.git
   ```
2. En Obsidian, abre la carpeta como bóveda, o simplemente ábrela si ya está dentro de la tuya.
3. Por dónde empezar:
   - **Estudiantes:** `skills/ros2-core/learn/core-learn-start-here.md` (ROS 2 base), `skills/ros2-core/learn-intermediate/core-learn-inter-start-here.md` (ROS 2 intermedio), `skills/ros2-core/learn-security/core-learn-sec-start-here.md` (seguridad con SROS2), `skills/ros2-bt/learn/bt-learn-start-here.md` (behavior trees), `skills/ros2-nav2/learn/nav2-learn-start-here.md` (navegación) y `skills/ros2-nav2/learn/nav2-learn-adv-start-here.md` (navegación avanzada) , `skills/ros2-snap/learn/snap-learn-start-here.md` (snaps), `skills/ros2-gazebo/learn/gazebo-learn-start-here.md` (curso de URDF y simulación; las unidades de URDF están en `skills/ros2-urdf/learn/`), `skills/ros2-control/learn/control-learn-start-here.md` (ros2_control) y `skills/ros2-tf/learn/tf-learn-start-here.md` (TF).
   - **Consulta técnica:** el índice de áreas en `skills/ros2-core/SKILL.md`, `skills/ros2-bt/SKILL.md`, `skills/ros2-snap/SKILL.md`, `skills/ros2-nav2/SKILL.md`, `skills/ros2-urdf/SKILL.md`, `skills/ros2-control/SKILL.md`, `skills/ros2-gazebo/SKILL.md` y `skills/ros2-tf/SKILL.md`.
4. Para actualizar: `git pull`.

## Usarlo como Skill de Claude

Requisitos: Python 3.10+ y bash (en Windows, Git Bash), y los paquetes de `requirements.txt` (PyYAML y pyflakes): `python -m pip install -r requirements.txt`, mejor dentro de un entorno virtual. Sin ellos, `validate.py` no revisa los bloques YAML ni los programas Python de las notas, y lo avisa al final de su resumen con `NOT CHECKED: …`.

Instala siempre `ros2-core`. `ros2-bt`, `ros2-snap` y `ros2-urdf` lo necesitan, `ros2-nav2` necesita core y bt, `ros2-control` y `ros2-tf` necesitan core y urdf, y `ros2-gazebo` necesita core, urdf y control: sus notas enlazan a las de esos skills. Lo más simple es instalar los ocho juntos; un skill instalado solo ocupa su descripción hasta que el agente lo usa.

**Claude Code** (un acceso directo a la carpeta del repo, así que cada `git pull` se ve al instante):
```bash
bash tools/package_skill.sh ros2-core --no-zip
bash tools/package_skill.sh ros2-bt --no-zip
bash tools/package_skill.sh ros2-nav2 --no-zip
bash tools/package_skill.sh ros2-snap --no-zip
bash tools/package_skill.sh ros2-urdf --no-zip
bash tools/package_skill.sh ros2-control --no-zip
bash tools/package_skill.sh ros2-gazebo --no-zip
bash tools/package_skill.sh ros2-tf --no-zip
```
Esto crea `~/.claude/skills/ros2-core`, `~/.claude/skills/ros2-bt`, `~/.claude/skills/ros2-nav2`, `~/.claude/skills/ros2-snap`, `~/.claude/skills/ros2-urdf`, `~/.claude/skills/ros2-control`, `~/.claude/skills/ros2-gazebo` y `~/.claude/skills/ros2-tf`: un *junction* en Windows y un *symlink* en Linux/macOS.

**Claude Desktop / claude.ai** (genera un zip para subir):
```bash
bash tools/package_skill.sh ros2-core --no-link
bash tools/package_skill.sh ros2-bt --no-link
bash tools/package_skill.sh ros2-nav2 --no-link
bash tools/package_skill.sh ros2-snap --no-link
bash tools/package_skill.sh ros2-urdf --no-link
bash tools/package_skill.sh ros2-control --no-link
bash tools/package_skill.sh ros2-gazebo --no-link
bash tools/package_skill.sh ros2-tf --no-link
```
Sube `dist/ros2-core.zip`, `dist/ros2-bt.zip`, `dist/ros2-nav2.zip`, `dist/ros2-snap.zip`, `dist/ros2-urdf.zip`, `dist/ros2-control.zip`, `dist/ros2-gazebo.zip` y `dist/ros2-tf.zip` en la configuración de Skills de Claude (los ocho). Si subes nav2 sin bt, control o tf sin urdf, o gazebo sin urdf y control, sus enlaces a esas notas quedan rotos. Cuando cambien las notas, vuelve a generarlos y a subirlos.

> No uses las dos vías a la vez: un zip subido a claude.ai también aparece en Claude Code y el skill quedaría duplicado.

## Para quienes editan

- **Una idea por nota, sin duplicar.** Si un concepto ya existe, enlázalo con `[[id-de-la-nota]]`.
- **Formato:** el `id` es igual al nombre del archivo y lleva el prefijo del dominio (`core-…`, `bt-…`, `nav2-…`, `snap-…`, `urdf-…`, `control-…`, `gazebo-…`, `tf-…`). El frontmatter obligatorio es `id`, `title`, `domain` y `summary` (máximo 20 palabras), más 6 campos de mantenimiento que usa un servidor MCP de base de conocimiento para saber quién cuida cada nota y cuándo revisarla: `type`, `owner`, `updated`, `review_by`, `source` y `confidentiality`. No los escribas a mano: los pone `tools/kb_meta.py`.
- **Tamaño:** 400–900 tokens por nota, más o menos 1.600–3.600 caracteres.
- **Enlaces:** nunca hacia fuera del repo. Una nota solo enlaza a los skills que declara en `requires`: `ros2-bt` → core; `ros2-snap` → core; `ros2-urdf` → core; `ros2-nav2` → core y bt; `ros2-control` → core y urdf; `ros2-tf` → core y urdf; `ros2-gazebo` → core, urdf y control. Las de core nunca enlazan a los otros skills, las de bt nunca enlazan a nav2, las de urdf nunca enlazan a control, a gazebo ni a tf, las de control nunca enlazan a gazebo, y las de tf nombran las de gazebo solo en texto.
- **Antes de cada commit:**
  ```bash
  python tools/build_index.py      # regenera los _index.md y el índice de SKILL.md (no los edites a mano)
  python tools/kb_meta.py          # añade los campos de mantenimiento que falten; en las notas que cambiaste pone updated = hoy y aleja review_by (necesita git)
  python tools/validate.py --brief # debe terminar con 0 errores (revisa YAML y XML, que cada YAML de parámetros use el nombre del nodo del launch; con pyflakes, también los programas Python; que cada corrección de la auditoría esté citada en una nota)
  python tools/backlinks.py        # opcional: actualiza reports/backlinks.md
  ```

Formato del frontmatter de una nota:
```yaml
id: core-srv-client-async        # = nombre del archivo
type: reference                  # campos de mantenimiento (tools/kb_meta.py): notas de skills/ = reference
owner: equipo-ros2               # quién la mantiene
updated: 2026-10-09              # último cambio de contenido (AAAA-MM-DD)
review_by: 2027-04-08            # pasada esta fecha, la nota queda vencida (validate.py lo avisa)
source: manual                   # manual | gitlab | generated
confidentiality: internal        # internal | restricted (restricted nunca va en este repo)
title: "Service client patterns (async)"
domain: core
area: core-api                   # = carpeta de la nota
distro: humble
tested: false
audience: dev                    # dev | students
summary: "Una línea para el índice (máx. 20 palabras)."
tags: [service, call_async]
see: ["[[core-srv-server]]"]
requires: []                     # skills de dominio: [ros2-core]
version_notes: ["jazzy: X replaced by Y — <URL> (Vxx)"]
```
