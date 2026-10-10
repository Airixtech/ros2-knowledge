# ros2-knowledge

Base de conocimiento de **ROS 2** en notas atómicas de Markdown, con dos skills: **ros2-core** (ROS 2 base) y **ros2-nav2** (navegación con Nav2). Sirve para dos cosas:

- **Leer y estudiar** en [Obsidian](https://obsidian.md), con enlaces `[[...]]` entre las notas.
- **Usarla como Skills de Claude**, para que genere código y configuraciones ROS 2 correctas y ayude a depurar.

*ROS 2 knowledge base (core + Nav2) as atomic Markdown notes, for Obsidian and as Claude Skills. Notes are in English.*

**Humble es la versión de referencia** (Ubuntu 22.04, Python 3.10). Las diferencias con Jazzy y Lyrical están marcadas en cada nota. No se reemplazan.

## Contenido

| Carpeta | Qué hay |
|---|---|
| `skills/ros2-core/` | Skill base de ROS 2: 84 notas ([índice](skills/ros2-core/SKILL.md)) |
| `skills/ros2-core/notes/` | Notas técnicas por área: `build-run`, `core-api`, `recipes`, `tools`, `architecture` |
| `skills/ros2-core/learn/` | Material del curso: conceptos y ejercicios de las Units 2–8 ([empieza aquí](skills/ros2-core/learn/core-learn-start-here.md)) |
| `skills/ros2-core/migration/` | Cambios Humble → Jazzy → Lyrical y una checklist para migrar proyectos |
| `skills/ros2-nav2/` | Skill de Nav2: 54 notas ([índice](skills/ros2-nav2/SKILL.md)). Necesita `ros2-core` |
| `skills/ros2-nav2/notes/` | Notas técnicas por área: `bringup`, `mapping`, `localization`, `planning-control`, `costmaps`, `multi-robot` |
| `skills/ros2-nav2/learn/` | Material del curso de navegación con TurtleBot3: Units 1–6 y proyecto ([empieza aquí](skills/ros2-nav2/learn/nav2-learn-start-here.md)) |
| `skills/ros2-nav2/migration/` | Cambios de Nav2 Humble → Jazzy → Lyrical y una checklist para migrar configuraciones |
| `tools/` | Scripts para generar índices, validar, ver enlaces y empaquetar los skills |
| `reports/` | Auditorías de versiones con fuentes (las notas citan sus IDs: `Vxx` en core, `NAV2-Vxx` en Nav2) y reporte de enlaces |

Cada nota sigue el mismo formato: un TL;DR de 1–2 líneas, luego el código o los comandos, y al final los errores típicos. Marcas que vas a encontrar:

| Marca | Significado |
|---|---|
| `[Humble]` | Solo aplica a Humble |
| `[≥Jazzy]` | Existe desde Jazzy (o una versión posterior) |
| `[changed in Jazzy: …]` / `[changed in Lyrical: …]` | Qué usar en esa versión |
| `[verify]` | Todavía sin confirmar con una fuente o una compilación |

## Leerlo en Obsidian

1. Clona el repo, dentro de tu bóveda o como una bóveda propia:
   ```bash
   git clone https://github.com/ORGANIZACION/ros2-knowledge.git
   ```
2. En Obsidian, abre la carpeta como bóveda, o simplemente ábrela si ya está dentro de la tuya.
3. Por dónde empezar:
   - **Estudiantes:** `skills/ros2-core/learn/core-learn-start-here.md` (ROS 2 base) y `skills/ros2-nav2/learn/nav2-learn-start-here.md` (navegación).
   - **Consulta técnica:** el índice de áreas en `skills/ros2-core/SKILL.md` y en `skills/ros2-nav2/SKILL.md`.
4. Para actualizar: `git pull`.

## Usarlo como Skill de Claude

Requisitos: Python 3.10+ y bash (en Windows, Git Bash). PyYAML es opcional.

Instala siempre `ros2-core`; `ros2-nav2` lo necesita, porque sus notas enlazan a las de core.

**Claude Code** (un acceso directo a la carpeta del repo, así que cada `git pull` se ve al instante):
```bash
bash tools/package_skill.sh ros2-core --no-zip
bash tools/package_skill.sh ros2-nav2 --no-zip
```
Esto crea `~/.claude/skills/ros2-core` y `~/.claude/skills/ros2-nav2`: un *junction* en Windows y un *symlink* en Linux/macOS.

**Claude Desktop / claude.ai** (genera un zip para subir):
```bash
bash tools/package_skill.sh ros2-core --no-link
bash tools/package_skill.sh ros2-nav2 --no-link
```
Sube `dist/ros2-core.zip` y `dist/ros2-nav2.zip` en la configuración de Skills de Claude (los dos). Cuando cambien las notas, vuelve a generarlos y a subirlos.

> No uses las dos vías a la vez: un zip subido a claude.ai también aparece en Claude Code y el skill quedaría duplicado.

## Para quienes editan

- **Una idea por nota, sin duplicar.** Si un concepto ya existe, enlázalo con `[[id-de-la-nota]]`.
- **Formato:** el `id` es igual al nombre del archivo y lleva el prefijo del dominio (`core-…`, `nav2-…`). El frontmatter obligatorio es `id`, `title`, `domain` y `summary` (máximo 20 palabras).
- **Tamaño:** 400–900 tokens por nota, más o menos 1.600–3.600 caracteres.
- **Enlaces:** nunca hacia fuera del repo. Las notas de `ros2-nav2` pueden enlazar a `ros2-core` (lo declaran en `requires`); las de core nunca enlazan a nav2.
- **Antes de cada commit:**
  ```bash
  python tools/build_index.py      # regenera los _index.md y el índice de SKILL.md (no los edites a mano)
  python tools/validate.py         # debe terminar con 0 errores (revisa YAML y XML; con pyflakes instalado, también los programas Python)
  python tools/backlinks.py        # opcional: actualiza reports/backlinks.md
  ```

Formato del frontmatter de una nota:
```yaml
id: core-srv-client-async        # = nombre del archivo
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
