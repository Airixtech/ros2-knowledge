---
id: core-testing-ci-docker
title: "Testing, linters, releases, CI & Docker"
domain: core
area: architecture
distro: humble
tested: false
audience: dev
summary: "pytest/gtest/launch_testing and ament linters, SemVer and bloom releases, GitHub Actions CI with action-ros-ci, multi-stage Docker."
tags: [testing, pytest, gtest, launch_testing, CI, action-ros-ci, Docker, bloom]
see: ["[[core-colcon-build]]", "[[core-pkg-ament-cmake]]", "[[core-production-checklist]]"]
requires: []
version_notes:
  - "all: action-ros-ci major v0.4; Jazzy uses ubuntu-noble images — https://github.com/ros-tooling/action-ros-ci (V74)"
  - "all: ros:humble == humble-ros-base — https://github.com/docker-library/official-images/blob/master/library/ros (V75)"
---
# Testing, linters, releases, CI & Docker

**TL;DR** Unit-test with pytest/gtest, test systems with `launch_testing`, lint with `ament_lint_auto`. Run them all on every PR with action-ros-ci. Ship a multi-stage Docker image without `--symlink-install`.

## Testing
```python
# test/test_calc.py (pytest; run: colcon test --packages-select my_pkg && colcon test-result --verbose)
from my_pkg.calc import add
def test_add():
    assert add(2, 3) == 5
```
```cmake
if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  ament_add_gtest(test_calc test/test_calc.cpp)
  target_link_libraries(test_calc my_lib)
endif()
```
- Integration: `launch_testing` (`@pytest.mark.launch_test`, `generate_test_description()` returning `LaunchDescription([..., launch_testing.actions.ReadyToTest()])`).
- Linters via `ament_lint_auto`: flake8, pep257, copyright, cpplint, uncrustify, xmllint.

## Versioning & docs
SemVer: MAJOR = breaking (msg change, removed topic) · MINOR = compatible feature · PATCH = fix. Release tools: `catkin_generate_changelog`, `catkin_prepare_release`, `bloom-release --rosdistro humble --track humble my_pkg`. Docs: Google-style docstrings / Doxygen; `rosdoc2`. The README should cover install, `ros2 launch` usage, a topics/services table and a params table with defaults.

## CI/CD (GitHub Actions)
```yaml
jobs:
  build-test:
    runs-on: ubuntu-latest
    container: {image: rostooling/setup-ros-docker:ubuntu-jammy-latest}
    steps:
      - uses: actions/checkout@v4
      - uses: ros-tooling/action-ros-ci@v0.4
        with:
          package-name: my_pkg my_pkg_interfaces
          target-ros2-distro: humble
```
The old `@v0.3` pin still runs; current major is v0.4. Jazzy: `ubuntu-noble-latest` + `target-ros2-distro: jazzy`. Alternatives: industrial_ci (multi-distro matrices), colcon-coverage, bloom-release.

## Docker
```dockerfile
ARG ROS_DISTRO=humble
FROM ros:${ROS_DISTRO} AS builder
WORKDIR /opt/ws
RUN apt-get update && apt-get install -y --no-install-recommends python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*
COPY src/ src/
RUN rosdep update && rosdep install --from-paths src --ignore-src -y -r
RUN . /opt/ros/${ROS_DISTRO}/setup.sh && colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release

FROM ros:${ROS_DISTRO}-ros-base AS runtime
COPY --from=builder /opt/ws/install /opt/ws/install
RUN sed -i '$isource "/opt/ws/install/setup.bash"' /ros_entrypoint.sh
CMD ["ros2", "launch", "my_pkg", "bringup.launch.py"]
```
- `ros:humble` **is** `humble-ros-base`, so this runtime stage is not slimmer than the builder. For a smaller image, use `ros:${ROS_DISTRO}-ros-core` and install the runtime deps (`rosdep install --dependency-types exec`) [verify].
- Do not use `--symlink-install` when copying `install/` to another stage.
- Compose: one service per layer; shared env (`ROS_DOMAIN_ID`, `RMW_IMPLEMENTATION`, `CYCLONEDDS_URI`); `network_mode: host` (simple) + `ipc: host` (SHM). Bridge networks need peer lists or a discovery server ([[core-multi-pc-dds]]).
- GPU (Isaac Sim): `deploy.resources.reservations.devices: [{driver: nvidia, count: all, capabilities: [gpu]}]`. Dev: mount `./src:/opt/ws/src`.
