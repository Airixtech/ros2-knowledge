---
id: urdf-onshape-export
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "CAD to URDF with onshape-to-robot: API keys, config, export, mesh paths"
domain: urdf
area: workflow
distro: humble
tested: false
audience: dev
summary: "Export an Onshape assembly to URDF with onshape-to-robot: pipx/venv install, ONSHAPE_* API keys, config.json url/output_format/package_name, mesh paths, inertia."
tags: [onshape, onshape-to-robot, cad, export, config.json, ONSHAPE_ACCESS_KEY, ONSHAPE_SECRET_KEY, package_name, assembly_name, robot_name, assets, pipx, PEP 668]
see: ["[[urdf-description-package]]", "[[urdf-inertia]]", "[[urdf-learn-unit8-quadruped]]"]
requires: [ros2-core]
version_notes:
  - "humble: install with pip in a venv or pipx, never sudo pip; on Ubuntu 24.04 (Jazzy) the system pip is externally managed — https://onshape-to-robot.readthedocs.io/en/latest/getting_started.html , https://peps.python.org/pep-0668/ (URDF-V12)"
  - "all: since 1.0 the config keys are snake_case and url is required; camelCase (documentId, outputFormat, …) is still accepted — https://onshape-to-robot.readthedocs.io/en/latest/config.html (URDF-V46)"
  - "all: a missing comma makes config.json invalid (comments are allowed) (URDF-V13)"
  - "all: 1.8.3 writes the XML declaration itself; mesh paths are package://<package_name>/<assets dir>/<file> — https://github.com/Rhoban/onshape-to-robot/blob/master/onshape_to_robot/exporter_urdf.py (URDF-V47)"
---
# CAD to URDF with onshape-to-robot: API keys, config, export, mesh paths

**TL;DR** Writing the URDF of a CAD-designed robot by hand is slow and error-prone. `onshape-to-robot` reads an assembly from Onshape (cloud CAD, free for public documents) through its API and writes `robot.urdf`, the meshes and the inertias computed from the parts' materials. You give it a folder with a `config.json`.

## Install
```bash
pipx install onshape-to-robot && pipx ensurepath     # then open a new terminal
# or in a virtual environment: python3 -m venv ~/venvs/o2r && . ~/venvs/o2r/bin/activate && pip install onshape-to-robot
```
Do not use `sudo pip install`: on Ubuntu 24.04 the system pip refuses ("externally-managed-environment"). OpenSCAD and MeshLab are needed only by optional processors (pure-shape approximation, STL simplification).

## API keys
Create a key pair in the Onshape developer portal (keys page, "New Key", the needed permissions); the secret is shown only once. Export them, e.g. in a `keys.sh` you source, never commit:
```bash
# Obtained at https://dev-portal.onshape.com/keys
export ONSHAPE_API=https://cad.onshape.com
export ONSHAPE_ACCESS_KEY=Your_Access_Key
export ONSHAPE_SECRET_KEY=Your_Secret_Key
```
A `.env` file with the same three lines in the project folder also works.

## config.json
Current format (1.x):
```json
{
  // Onshape URL of the assembly tab
  "url": "https://cad.onshape.com/documents/<document-id>/w/<workspace-id>/e/<element-id>",
  "output_format": "urdf",
  "assembly_name": "quadruped_v1",
  "package_name": "quadruped_description/quadruped",
  "robot_name": "quadruped_robot"
}
```
- The course writes the older camelCase keys (`documentId`, `outputFormat`, `assemblyName`, `packageName`, `robotName`): still accepted. With `documentId` the document id is the part of the URL after `documents/`.
- `package_name` is put in front of every mesh path: `package://quadruped_description/quadruped/assets/torso_quadruped.stl`. Without it the path has no package (`package:///assets/…` in older versions) and RViz cannot find the mesh.
- Commas between entries are required; comments are allowed.

## Export and use
```bash
cd ~/ros2_ws/src/quadruped_description
onshape-to-robot quadruped        # folder with config.json → robot.urdf + assets/
```
- Install the export folder in `CMakeLists.txt` (`install(DIRECTORY rviz launch quadruped DESTINATION share/${PROJECT_NAME}/)`) and publish `quadruped/robot.urdf` with robot_state_publisher ([[urdf-description-package]]).
- The file starts with the XML declaration and a comment with the document id; masses and inertia tensors (with cross terms) come from the CAD materials, good for simulation ([[urdf-inertia]]).

## Pitfalls
- "! ERROR (403) while using Onshape API" → the tool's hint: check your access rights (keys exported in this terminal, a document you may read) and that the computer's clock is set correctly.
- Wrong tab in the URL → it must point to the assembly, not a part studio.
- Re-exporting overwrites your manual edits of `robot.urdf`: keep extra tags in a xacro wrapper or in `additional_xml`.
