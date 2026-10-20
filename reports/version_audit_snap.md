# Version audit — ros2-snap (Phase 1)

> Date: 2026-10-20.
> Scope: every version-dependent statement of the workshop "Distributing ROS apps with snaps, part 1" (course wiki,
> not published): snapd and snapcraft install, `snapcraft.yaml` keys, build/install/run, confinement, grade,
> interfaces, daemons, ROS plugins, ROS extensions and bases. Section IDs = the course's section numbers (1.3, 1.4.1.1…).
> Baseline: **Humble is canonical** = base `core22` + extension `ros2-humble`. Jazzy (`core24`, `ros2-jazzy`) and
> Lyrical (`core26`, `ros2-lyrical`) are annotated, not substituted. Snapcraft has its own release line: the
> baseline table lists the Snapcraft version each extension needs.
> Extended 2026-10-20 (SNAP-V29–V49) with the official material that completes the topic, all in its current
> version: part 3 of the series (Snap Store, Humble), 13 pages of the Canonical robotics documentation (robot app
> design, orchestration, environment and data, configuration and hooks, ROS 2 architectures and content sharing,
> distros without an extension, CI with GitHub Actions, debugging, Ubuntu Core) and the Ubuntu Core image tutorial.
> Those official pages are audited like the course: where they disagree with the code, the code wins.
> Generic ROS 2 rows are in [version_audit.md](version_audit.md) (IDs `Vnn`); this report cites them instead of repeating them.

## Method
- Origin first: the workshop is part 1 of Canonical's tutorial series "From zero to hero: deploy a robot with snaps
  and Ubuntu Core" ([robotics docs][rd-series], source repo [canonical/robotics_documentation][rd-repo], docs under
  CC-BY-SA 3.0). Its current part 1 and the example repository [ubuntu-robotics/ros2-humble-talker-listener-snap][tl]
  (branches `main`, `confined`, `daemon`) were compared line by line with the course. Where the tutorial text and the
  repository files disagree, the files win.
- Primary sources: `canonical/snapcraft` on `main` (9.x, 2026-10-19: `snapcraft/extensions/ros2_*.py`,
  `snapcraft/models/project.py`, `schema/snapcraft.json`, `snapcraft/commands/`, and its `docs/`: extensions, bases,
  colcon plugin, build providers, "Craft an ROS 2 app"), the extension file on the release tags 7.2.9 and 7.3.1,
  `canonical/snapd` on `master` (`wrappers/internal/service_unit_gen.go`, `snap/info.go`, `interfaces/builtin/`),
  `ros2/demos` (`humble`, `jazzy`), REP 2000 (EOL dates).
- Extension sources: [canonical/robotics_documentation][rd-repo] (commit 0fb8368, 2026-10-08), `canonical/snapd`
  (`overlord/snapstate/backend/copydata.go`, `overlord/snapstate/autorefresh.go`), `canonical/snapcraft`
  (`snapcraft/templates/ros2`, `snapcraft/commands/`, `docs/reference/channels.rst`, content extensions),
  [canonical/robotics-actions-workflows][raw] (`snap.yaml`), [canonical/ubuntu-core-docs][ucd] (tutorial "Build your
  first image", gadget snap format; CC-BY-SA 4.0), the Snap Store API (provider snaps), the GitHub changelog and the
  POSIX shell specification.
- Actions: **keep** = correct for Humble/core22 · **annotate** = correct, add a mark or a missing detail · **fix** =
  wrong or outdated for the current Humble/core22 workflow (or a course mistake). Confidence: High (read in
  code/docs) · Medium (inferred) · `[verify]` (needs a real build).

## Baseline (snaps per ROS 2 distro)
| | Humble | Jazzy | Kilted | Lyrical |
|---|---|---|---|---|
| Base snap | `core22` (Ubuntu 22.04) | `core24` (Ubuntu 24.04) | — (no extension; non-LTS) | `core26` (Ubuntu 26.04) |
| Extension | `ros2-humble` | `ros2-jazzy` | — | `ros2-lyrical` (**experimental**) |
| Snapcraft needed | ≥ 7.3 (experimental before 7.3) | ≥ 7.3 | — | ≥ 9 |
| Content-sharing extensions (experimental) | `ros2-humble-ros-core`, `-ros-base`, `-desktop` | `ros2-jazzy-ros-core`, `-ros-base`, `-desktop` | — | `ros2-lyrical-ros-core`, `-ros-base`, `-desktop` |
| Launch file of `demo_nodes_cpp` | `talker_listener.launch.py` | `talker_listener_launch.py` | | `talker_listener_launch.py` |
| Sources | [ros2_humble.py][ext-h], [extensions doc][ext-doc] | [ros2_jazzy.py][ext-j] | [how-to][howto-ros2] | [ros2_lyrical.py][ext-l] |

Older ROS 2 distros: `core20` + `ros2-foxy` (Foxy EOL May 2023), `core18` + Dashing (no extension; EOL May 2021).

## Real Humble errors (fix)
| ID | Section | Origin | Error | Correct statement |
|---|---|---|---|---|
| SNAP-V01 | 1.4.2.1, 1.5.4, 1.6, 1.9.2.3 | true for Snapcraft 7.1–7.2 (2022) | "`ros2-humble` is an experimental extension: build with `SNAPCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS=1 snapcraft`" | The extension is stable since Snapcraft 7.3 (`is_experimental` returns `False` from tag 7.3.1, `True` on 7.2.9). Build with `snapcraft` (same as `snapcraft pack`, the default command), as the current official tutorial does. The variable is still needed for experimental extensions: `ros2-lyrical` and the content-sharing ones. Code: [ros2_humble.py][ext-h], [7.2.9][ext-h-729], [7.3.1][ext-h-731]; docs: [extensions][ext-doc] |
| SNAP-V02 | 1.5.4, 1.6, 1.7.2 | course mistake (also in the tutorial text) | Diffs of the confined, daemon and exercise versions: `command: opt/ros/humble/bin/ros2 launch talker-listener talker_listener.launch.py` | There is no package `talker-listener`: every branch of the example repository keeps `ros2 launch demo_nodes_cpp talker_listener.launch.py`. Files: [main][tl-main], [confined][tl-conf], [daemon][tl-daemon] |
| SNAP-V03 | 1.4.1.1 | course claim (also in the tutorial text) | "The summary cannot exceed 79 characters" | Maximum **78** characters (schema `maxLength: 78`, "Maximum length 78 characters"). Code: [snapcraft.json][schema] |
| SNAP-V04 | 1.6 | course mistake | "`enabled` means that it will automatically start at boot and restart in case of failure" | `enabled` = started at boot. Restarting after a failure is the default `restart-condition` of every snap service (`on-failure`; `no` for `oneshot`), enabled or not, and can be changed with `restart-condition`. Code: [service_unit_gen.go][snapd-unit], [project.py][model] |
| SNAP-V29 | official: snap data and file storage | official doc error (contradicts snapd) | Table and text: `SNAP_DATA` / `SNAP_USER_DATA` are "not kept over updates", "the data stored here won't be available for the next update"; `SNAP_USER_COMMON` for "revision specific configuration files" | On refresh snapd **copies** the data of the old revision into the new revision's `SNAP_DATA` / `SNAP_USER_DATA` (the old copy stays for `snap revert`); `SNAP_COMMON` / `SNAP_USER_COMMON` are shared by all revisions and never copied. Revision-specific files go to the revisioned dirs, files that must not be rolled back to the `common` ones. Code: [copydata.go][snapd-copy] |
| SNAP-V30 | official: build and publish with GitHub Actions | outdated (2022 workflow) | `actions/upload-artifact@v3` / `download-artifact@v3`, `snapcore/action-build@v1`, `snapcore/action-publish@v1`; key `Workflow_dispatch` in the breakdown | Artifact actions v3 stopped working on GitHub.com on 2025-01-30: use v4 or later. The snap actions now live at `canonical/action-build` and `canonical/action-publish` (the old names redirect). Keys are case-sensitive: `workflow_dispatch`. The maintained option is the reusable workflow `canonical/robotics-actions-workflows/.github/workflows/snap.yaml`. Sources: [GitHub changelog][gh-artifacts], [snap.yaml][raw-snap] |
| SNAP-V31 | official: ROS distributions with no extensions | official doc error | The final `ros2-…-extension` part has `build-packages` and `override-build` indented under `plugin: nil` (invalid YAML); in the apps example `command` is not indented under the app; the text says `roslaunch` for `ros2launch` | Same indentation for every key of a part and of an app (rebuilt in the note); the stage package is `ros-<distro>-ros2launch`. Source: the page's own earlier blocks and [colcon plugin][colcon] |
| SNAP-V32 | official: snap configurations and hooks | official doc error | `configure` hook rejects a value with `return 1` at the top level of the script | `return` outside a function or a sourced script is unspecified in POSIX `sh`: use `exit 1` so the hook fails and `snap set` reports the error. Source: [POSIX return][posix-return] |
| SNAP-V33 | official part 3: requirements | outdated | "Ubuntu Desktop (20.04 being the minimum version, as it is still under maintenance)" | Ubuntu 20.04 left standard support at the end of May 2025 (ESM only): use 22.04 LTS or later, as the current part 1 asks. Source: [Ubuntu blog][u2004-eol] |

## Full table
| # | Section | Statement | Humble (core22) | Jazzy (core24) | Lyrical (core26) | Action | Source | Confidence |
|---|---|---|---|---|---|---|---|---|
| SNAP-V01 | 1.4.2.1 | `SNAPCRAFT_ENABLE_EXPERIMENTAL_EXTENSIONS=1 snapcraft` | ✗ not needed since Snapcraft 7.3 | not needed | **needed** (`ros2-lyrical` experimental) | **fix** | [ros2_humble.py][ext-h], [ros2_lyrical.py][ext-l] | High |
| SNAP-V02 | 1.5.4, 1.6, 1.7.2 | `ros2 launch talker-listener talker_listener.launch.py` | ✗ `demo_nodes_cpp` | `demo_nodes_cpp talker_listener_launch.py` | same as Jazzy | **fix** | [tl confined][tl-conf], [demos jazzy][demos-j] | High |
| SNAP-V03 | 1.4.1.1 | summary ≤ 79 characters | ✗ ≤ 78 | same | same | **fix** | [schema][schema] | High |
| SNAP-V04 | 1.6 | `enabled` = start at boot + restart on failure | ✗ restart = `restart-condition` (default `on-failure`) | same | same | **fix** | [snapd][snapd-unit] | High |
| SNAP-V05 | 1.1.2 | host "at least Ubuntu 16.04" to reproduce the course | the current tutorial asks Ubuntu 22.04 LTS or similar (16.04 is ESM); running the snap only needs snapd | 24.04 for core24 builds in destructive mode | 26.04 for core26 | annotate | [part 1][rd-p1] | High |
| SNAP-V06 | 1.3, 1.4.2.1 | `snapcraft` builds after installing snapd + snapcraft | needs a build provider: **LXD** by default on Linux since Snapcraft 7 (`snap install lxd`, user in group `lxd`, `lxd init --auto`); `--destructive-mode` builds on the host (not recommended) | same | same | annotate | [set up snapcraft][setup], [build provider][provider] | High |
| SNAP-V07 | 1.3.2 | `sudo snap install snapcraft --classic`; remove the old deb `snapcraft` | ✓ | ✓ | ✓ | keep | [set up snapcraft][setup] | High |
| SNAP-V08 | 1.4.1.1 | names: lower-case alphanumeric and hyphens, not all numbers, no leading/trailing hyphen | ✓ + no two hyphens in a row, at most 40 characters | same | same | annotate | [project.py][model], [schema][schema] | High |
| SNAP-V09 | 1.4.1.1 | `version` is declarative, may come from a script or git | ✓ + at most 32 characters | same | same | annotate | [schema][schema] | High |
| SNAP-V10 | 1.4.1.3, 1.9.3 | "core22 is the current standard base" | ✓ base for Humble; newer bases: `core24`, `core26` | `core24` | `core26` | annotate | [bases][bases] | High |
| SNAP-V11 | 1.4.1.4 | colcon plugin; `stage-packages: [ros-humble-ros2launch]` because the `package.xml` misses it; other deps through rosdep | ✓ (`demo_nodes_cpp` exec-depends `launch_ros`, `launch_xml`, not `ros2launch`; the plugin runs `rosdep init/update`, installs build deps, stages runtime deps); current repo adds `build-packages: [build-essential]` | `ros-jazzy-ros2launch` | `ros-lyrical-ros2launch` | keep | [colcon plugin][colcon], [demos humble][demos-h-pkg], [tl main][tl-main] | High |
| SNAP-V12 | 1.4.1.5 | app named like the snap → run it as `ros2-talker-listener`; `command` relative to the snap root | ✓ | [≥Jazzy: the official how-to writes `command: ros2 launch …` without `opt/ros/jazzy/bin/`] [verify] | same | annotate | [how-to][howto-ros2] | High (Humble), Medium (Jazzy) |
| SNAP-V13 | 1.4.1.5, 1.9.2.3 | `ros2-humble` extension sets the build and run-time environment | ✓ adds the ROS 2 apt repo (jammy), a `ros2-launch` command chain, `ROS_DISTRO`, `PYTHONPATH`, `ROS_HOME=$SNAP_USER_DATA/ros`; supports **strict and devmode only** (no classic) | same pattern (noble, Python 3.12) | same (resolute, Python 3.14) | annotate | [ros2_humble.py][ext-h] | High |
| SNAP-V14 | 1.4.2.1 | steps pull, build, stage, prime | ✓ (+ pack) | ✓ | ✓ | keep | [lifecycle][lifecycle] | High |
| SNAP-V15 | 1.4.2.1 | `Unable to determine library dependencies for …rosidl_generator_py.so` has no impact | course observation; the official how-to calls missing-library warnings false positives (stated for core18/core20) | — | — | keep (as observed) | [how-to][howto-ros2] | Medium |
| SNAP-V16 | 1.4.2.2, 1.5.4 | install with `--devmode` (unconfined) or `--dangerous` (unsigned local file); `snap info`, `snap connections` | ✓ | ✓ | ✓ | keep | [part 1][rd-p1] | High |
| SNAP-V17 | 1.5.1 | confinement devmode, classic (manual store approval; IDEs), strict | ✓ | ✓ | ✓ | keep | [project.py][model] | High |
| SNAP-V18 | 1.5.2 | grade `devel` / `stable` (default) | ✓ + `devel` can only go to the beta and edge channels; `stable` needs stable bases | same | same | annotate | [project.py][model] | High |
| SNAP-V19 | 1.5.3 | `network` and `network-bind` are auto-connected | ✓ (implicit slots on classic and core, no auto-connection restriction in the base declaration) | ✓ | ✓ | keep | [network.go][snapd-net], [network_bind.go][snapd-netbind] | Medium |
| SNAP-V20 | 1.5.4 | Fast DDS shared memory fails in a strict snap (`RTPS_TRANSPORT_SHM Error … Permission denied`), UDP still works | ✓; fixes: `shared-memory` plug with `private: true` (works inside the snap only), slot + plug pairs for `/dev/shm` across snaps, or disable Fast DDS shared memory (XML profile, or rebuild with `-DSHM_TRANSPORT_DEFAULT=OFF`) | same | same | annotate | [shared memory how-to][shm] | High |
| SNAP-V21 | 1.6 | daemon types simple, oneshot, forking, notify | ✓ + `dbus` | same | same | annotate | [project.py][model] | High |
| SNAP-V22 | 1.6.1, 1.6.2 | `snap logs [-f]`, `journalctl -fu snap.<snap>.<app>.service`, `snap stop/start/disable/enable` | ✓ (unit = `snap.<snap>.<app>.service`) | ✓ | ✓ | keep | [info.go][snapd-info] | High |
| SNAP-V23 | 1.7 | exercise: second app `ros2topic` with `ros-humble-ros2topic` in `stage-packages` | ✓ (topic tools only know the message types inside the snap) | `ros-jazzy-ros2topic` | `ros-lyrical-ros2topic` | keep | [part 1][rd-p1] | High |
| SNAP-V24 | 1.9.1 | `snapcraft help <plugin_name>` | current CLI: `snapcraft list-plugins` (or `snapcraft plugins --base <base>`); plugin keys in the plugin reference; `snapcraft help <plugin> --base <base>` is documented for the core20 migration `[verify]` on Snapcraft 9 | same | same | annotate | [plugins.py][cmd-plugins], [core18→core20][core20-mig] | Medium |
| SNAP-V25 | 1.9.2.2 | `ros2-foxy` extension (core20) | still documented, but Foxy EOL May 2023 | — | — | annotate | [extensions doc][ext-doc], [REP 2000][rep2000] | High |
| SNAP-V26 | 1.9.2 | ROS 2 extensions `ros2-foxy`, `ros2-humble`; none for Dashing (core18) | ✓; today also `ros2-jazzy`, `ros2-lyrical` and the content-sharing variants | ✓ | ✓ | annotate | [extensions doc][ext-doc], [content extensions][ext-content] | High |
| SNAP-V27 | 1.9.2 | `snapcraft expand-extensions` shows what an extension adds | ✓ (no experimental flag needed for `ros2-humble`) | ✓ | needs the experimental flag | keep | [extensions.py][cmd-ext] | High |
| SNAP-V28 | 1.8 | parts 2 and 3 of the series "coming" | the current series has 5 parts: complex robot software, Snap Store, content sharing, Ubuntu Core image for TurtleBot3 | — | — | annotate | [series][rd-series] | High |
| SNAP-V29 | official: data storage | `SNAP_DATA`/`SNAP_USER_DATA` not kept over updates | ✗ copied to the new revision; `common` dirs shared, not copied | same | same | **fix** | [copydata.go][snapd-copy] | High |
| SNAP-V30 | official: GitHub Actions | artifact actions v3, `snapcore/*` actions | ✗ v3 retired 2025-01-30; `canonical/action-build`, `canonical/action-publish`; reusable workflow | same | same | **fix** | [GitHub changelog][gh-artifacts], [snap.yaml][raw-snap] | High |
| SNAP-V31 | official: no extensions | example YAML indentation, `roslaunch` | ✗ rebuilt; `ros2launch` | same | same | **fix** | — (the page's own blocks) | High |
| SNAP-V32 | official: hooks | `return 1` in a hook script | ✗ `exit 1` | same | same | **fix** | [POSIX return][posix-return] | High |
| SNAP-V33 | official part 3 | Ubuntu 20.04 "still under maintenance" | ✗ ESM since May 2025; use 22.04+ | 24.04+ | 26.04+ | **fix** | [Ubuntu blog][u2004-eol] | High |
| SNAP-V34 | official: get started | `snapcraft init --name … --profile ros2` writes a ROS 2 template (page shows core26 + `ros2-lyrical-ros-core`) | the template follows the installed Snapcraft: on `main` it is core24 + `ros2-jazzy-ros-core` (experimental) + branch `jazzy`; for Humble set `base: core22`, `extensions: [ros2-humble]`, `source-branch: humble`; its comment "79 char long summary" is wrong (78, SNAP-V03) | the template's `talker_listener.launch.py` is named `talker_listener_launch.py` on Jazzy `[verify]` | — | annotate | [template][tpl-ros2], [demos jazzy][demos-j] | High; launch name `[verify]` |
| SNAP-V35 | official: orchestration | `command-chain` runs scripts before the command; scripts end with `exec "$@"` | ✓; the ROS 2 extensions use it (`snap/command-chain/ros2-launch`) | ✓ | ✓ | annotate | [ros2_humble.py][ext-h] | High |
| SNAP-V36 | official: orchestration | `stop-command`, `post-stop-command` (daemons only) | ✓ | ✓ | ✓ | keep | [project.py][model] | High |
| SNAP-V37 | official: hooks | hooks in `snap/hooks/` (install, configure, pre/post-refresh, remove…), `snapctl get/set/start/stop/restart`, `snap set/get [-d]`, configuration kept over updates | ✓ | ✓ | ✓ | keep | [robotics docs: hooks][rd-hooks] | High |
| SNAP-V38 | official: architectures | monolithic (recommended first), multi-snap, multi-snap with content sharing; validation sets on Ubuntu Core | ✓ | ✓ | ✓ | keep | [robotics docs: architectures][rd-arch] | High |
| SNAP-V39 | official: architectures | content sharing through the ROS extensions | ✓ `ros2-humble-ros-core` / `-ros-base` / `-desktop`: **experimental**, Snapcraft ≥ 8; content plug mounted at `$SNAP/opt/ros/underlay_ws`, default provider `ros-humble-ros-base` (on the store); drop `stage-packages: [ros-humble-ros2launch]`; rebuild app snaps when the provider updates | `ros2-jazzy-*` (≥ 8) | `ros2-lyrical-*` (≥ 9) | annotate | [content extensions][ext-content], [how-to][howto-ros2] | High |
| SNAP-V40 | official: no extensions | rebuild an extension by hand: ROS apt repository, `nil` part with the 4 build packages + the `ros2-launch` script, `build-environment` `ROS_VERSION`/`ROS_DISTRO`, `command-chain`, `environment` (`PYTHONPATH`, `ROS_DISTRO`, `ROS_VERSION`) | ✓ (Humble has its extension) | ✓ | Kilted (non-LTS, no extension): suite `noble`, Python 3.12 `[verify]` | annotate | [no-extension how-to][rd-noext], [ros2_jazzy.py][ext-j] | High; Kilted example `[verify]` |
| SNAP-V41 | official: track and risk | reusable workflow inputs `snap-track` (default `latest`), `snap-risk` (default `edge`, `candidate` on tags), secret `snapstore-login`; the track must exist on the store | ✓ | ✓ | ✓ | keep | [snap.yaml][raw-snap] | High |
| SNAP-V42 | official: GitHub Actions | `snapcraft export-login --snaps=… --acls package_access,package_push,package_update,package_release <file>`; `SNAPCRAFT_STORE_CREDENTIALS` | ✓ | ✓ | ✓ | keep | [account.py][cmd-account] | High |
| SNAP-V43 | official: debug the build | build instance dirs (`parts`, `stage`, `prime`, `project`), `snapcraft --debug`, `--shell-after`, `snapcraft try` + `snap try prime` | ✓ | ✓ | ✓ | keep | [lifecycle.py][cmd-lifecycle] | High |
| SNAP-V44 | official: debug the app | `snap logs -n 100 [-f]`, `journalctl -u snap.<snap>.<app>.service`, `/snap/<snap>/current`, `snap run --shell <snap>.<app>`, `ldd`, `snap connect/disconnect`, `snappy-debug` | ✓ | ✓ | ✓ | keep | [robotics docs: debug app][rd-debug] | High |
| SNAP-V45 | official part 3 | `snapcraft login` (on the host, not a container), `register`, `upload` (automated review), `release <snap> <revision> <channel>`, `upload --release=<channel>`, visibility, install without `--dangerous` | ✓ (+ `snapcraft status`, `revisions`, `close`) | ✓ | ✓ | keep | [snapcraft commands][cmd-dir] | High |
| SNAP-V46 | official part 3 | channels = track/risk/branch; default track `latest`; branches close after 30 days without revisions; one track per ROS distro; automatic refresh 4 times a day; `snap refresh` | ✓ (`00:00~24:00/4`; installs use `stable` by default; `devel` grade never reaches candidate/stable) | ✓ | ✓ | keep | [channels][channels], [autorefresh.go][snapd-refresh] | High |
| SNAP-V47 | official part 3 | the update diff still shows `name: ros2-talker-listener` after renaming the snap | use the renamed snap (`yourname-test-ros2-snapstore`) | — | — | annotate | — (the page's own earlier step) | High |
| SNAP-V48 | Ubuntu Core image | model assertion → `snapcraft create-key` / `register-key` → `snap sign -k <key> model.json > model.model` → `ubuntu-image snap model.model`; gadget `defaults` (applied when each snap installs; `system:` at once) and `connections` (first boot only) | ✓ (current tutorial: Ubuntu Core 26 on a Raspberry Pi) | ✓ | ✓ | annotate | [UC tutorial][uc-tut], [gadget format][uc-gadget] | High |
| SNAP-V49 | official: Ubuntu Core | automatic transactional updates with rollback, delta updates, full disk encryption; snaps only | ✓ | ✓ | ✓ | keep | [robotics docs: Ubuntu Core][rd-uc] | High |

## Open `[verify]` (Phase 5 or a real machine)
1. SNAP-V12: on core24, does `command: ros2 launch …` (no `opt/ros/jazzy/bin/` prefix) resolve through the extension's
   command chain? Build the official Jazzy example.
2. SNAP-V24: `snapcraft help colcon` (or `--base core22`) output on Snapcraft 9.
3. Build and run the three branches of the example repository on Ubuntu 22.04 with LXD (Phase 5).
4. SNAP-V34: does the `snapcraft init --profile ros2` template build on Jazzy with `talker_listener.launch.py`?
5. SNAP-V40: a Kilted snap built without an extension (suite `noble`, Python 3.12 paths).

## Sources
[rd-series]: https://canonical-robotics.readthedocs-hosted.com/en/latest/tutorials/snaps-core/
[rd-p1]: https://canonical-robotics.readthedocs-hosted.com/en/latest/tutorials/snaps-core/packaging-ros-application-as-snap/
[rd-repo]: https://github.com/canonical/robotics_documentation
[tl]: https://github.com/ubuntu-robotics/ros2-humble-talker-listener-snap
[tl-main]: https://github.com/ubuntu-robotics/ros2-humble-talker-listener-snap/blob/main/snap/snapcraft.yaml
[tl-conf]: https://github.com/ubuntu-robotics/ros2-humble-talker-listener-snap/blob/confined/snap/snapcraft.yaml
[tl-daemon]: https://github.com/ubuntu-robotics/ros2-humble-talker-listener-snap/blob/daemon/snap/snapcraft.yaml
[ext-h]: https://github.com/canonical/snapcraft/blob/main/snapcraft/extensions/ros2_humble.py
[ext-h-729]: https://github.com/canonical/snapcraft/blob/7.2.9/snapcraft/extensions/ros2_humble.py
[ext-h-731]: https://github.com/canonical/snapcraft/blob/7.3.1/snapcraft/extensions/ros2_humble.py
[ext-j]: https://github.com/canonical/snapcraft/blob/main/snapcraft/extensions/ros2_jazzy.py
[ext-l]: https://github.com/canonical/snapcraft/blob/main/snapcraft/extensions/ros2_lyrical.py
[ext-doc]: https://github.com/canonical/snapcraft/blob/main/docs/reference/extensions/ros-2-extensions.rst
[ext-content]: https://github.com/canonical/snapcraft/blob/main/docs/reference/extensions/ros-2-content-extensions.rst
[howto-ros2]: https://github.com/canonical/snapcraft/blob/main/docs/how-to/integrations/craft-an-ros-2-app.rst
[schema]: https://github.com/canonical/snapcraft/blob/main/schema/snapcraft.json
[model]: https://github.com/canonical/snapcraft/blob/main/snapcraft/models/project.py
[bases]: https://github.com/canonical/snapcraft/blob/main/docs/reference/bases.rst
[colcon]: https://github.com/canonical/snapcraft/blob/main/docs/reference/plugins/colcon_plugin.rst
[setup]: https://github.com/canonical/snapcraft/blob/main/docs/how-to/set-up-snapcraft.rst
[provider]: https://github.com/canonical/snapcraft/blob/main/docs/how-to/select-a-build-provider.rst
[lifecycle]: https://github.com/canonical/snapcraft/blob/main/docs/explanation/parts-lifecycle.rst
[cmd-plugins]: https://github.com/canonical/snapcraft/blob/main/snapcraft/commands/plugins.py
[cmd-ext]: https://github.com/canonical/snapcraft/blob/main/snapcraft/commands/extensions.py
[core20-mig]: https://github.com/canonical/snapcraft/blob/main/docs/how-to/change-bases/change-from-core18-to-core20.rst
[snapd-unit]: https://github.com/canonical/snapd/blob/master/wrappers/internal/service_unit_gen.go
[snapd-info]: https://github.com/canonical/snapd/blob/master/snap/info.go
[snapd-net]: https://github.com/canonical/snapd/blob/master/interfaces/builtin/network.go
[snapd-netbind]: https://github.com/canonical/snapd/blob/master/interfaces/builtin/network_bind.go
[shm]: https://canonical-robotics.readthedocs-hosted.com/en/latest/how-to-guides/packaging/ros-2-shared-memory-in-snaps/
[demos-h-pkg]: https://github.com/ros2/demos/blob/humble/demo_nodes_cpp/package.xml
[demos-j]: https://github.com/ros2/demos/tree/jazzy/demo_nodes_cpp/launch/topics
[rep2000]: https://www.ros.org/reps/rep-2000.html
[raw]: https://github.com/canonical/robotics-actions-workflows
[raw-snap]: https://github.com/canonical/robotics-actions-workflows/blob/main/.github/workflows/snap.yaml
[ucd]: https://github.com/canonical/ubuntu-core-docs
[uc-tut]: https://documentation.ubuntu.com/core/tutorials/build-your-first-image/
[uc-gadget]: https://github.com/canonical/ubuntu-core-docs/blob/main/docs/reference/gadget-snap-format.md
[snapd-copy]: https://github.com/canonical/snapd/blob/master/overlord/snapstate/backend/copydata.go
[snapd-refresh]: https://github.com/canonical/snapd/blob/master/overlord/snapstate/autorefresh.go
[gh-artifacts]: https://github.blog/changelog/2024-04-16-deprecation-notice-v3-of-the-artifact-actions/
[posix-return]: https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html#return
[u2004-eol]: https://ubuntu.com/blog/ubuntu-20-04-lts-end-of-life-standard-support-is-coming-to-an-end-heres-how-to-prepare
[tpl-ros2]: https://github.com/canonical/snapcraft/blob/main/snapcraft/templates/ros2/snap/snapcraft.yaml.j2
[cmd-account]: https://github.com/canonical/snapcraft/blob/main/snapcraft/commands/account.py
[cmd-lifecycle]: https://github.com/canonical/snapcraft/blob/main/snapcraft/commands/core22/lifecycle.py
[cmd-dir]: https://github.com/canonical/snapcraft/tree/main/snapcraft/commands
[channels]: https://github.com/canonical/snapcraft/blob/main/docs/reference/channels.rst
[rd-hooks]: https://canonical-robotics.readthedocs-hosted.com/en/latest/explanations/snaps/snap-configurations-and-hooks/
[rd-arch]: https://canonical-robotics.readthedocs-hosted.com/en/latest/explanations/snaps/ros-architectures-with-snaps/
[rd-noext]: https://canonical-robotics.readthedocs-hosted.com/en/latest/how-to-guides/packaging/ros-distributions-with-no-extensions/
[rd-debug]: https://canonical-robotics.readthedocs-hosted.com/en/latest/explanations/snaps/debug-a-snap-application/
[rd-uc]: https://canonical-robotics.readthedocs-hosted.com/en/latest/explanations/ubuntu-core/
