---
id: core-shell-workflow
type: reference
owner: equipo-ros2
updated: 2026-10-09
review_by: 2027-04-08
source: manual
confidentiality: internal
title: "Shell aliases, tmux & daily workflow"
domain: core
area: tools
distro: humble
tested: false
audience: dev
summary: "~/.bashrc build/source functions and ros2 aliases, cleaning helpers, edit-build-run loop, tmux layouts and shell tricks."
tags: [bashrc, aliases, colcon, tmux, workflow, shell]
see: ["[[core-colcon-build]]", "[[core-cli-cheatsheet]]", "[[core-env-sourcing]]"]
requires: []
version_notes: []
---
# Shell aliases, tmux & daily workflow

**TL;DR** Add build+source functions (`cb`, `cbs`, `cbup`) and short `ros2` aliases to `~/.bashrc`. Run several terminals in one tmux session. The loop is: edit → `cbs my_pkg` → launch → inspect.

## Aliases / functions (append to ~/.bashrc)
```bash
alias sros='source /opt/ros/humble/setup.bash'
alias sws='source ~/ros2_ws/install/setup.bash'
alias cdws='cd ~/ros2_ws' ; alias cdsrc='cd ~/ros2_ws/src'
cb()   { cd ~/ros2_ws && colcon build --symlink-install "$@" && source install/setup.bash; }
cbs()  { [ -z "$1" ] && { echo "usage: cbs <pkg>"; return 1; }
         cd ~/ros2_ws && colcon build --symlink-install --packages-select "$1" "${@:2}" && source install/setup.bash && echo "built: $1"; }
cbup() { [ -z "$1" ] && { echo "usage: cbup <pkg>"; return 1; }
         cd ~/ros2_ws && colcon build --symlink-install --packages-up-to "$1" "${@:2}" && source install/setup.bash; }
alias cbp='cd ~/ros2_ws && colcon build --symlink-install --packages-select'    # build only, no source
alias cbu='cd ~/ros2_ws && colcon build --symlink-install --packages-up-to'     # build only, no source
alias cclean='cd ~/ros2_ws && rm -rf build/ install/ log/'
cclean_pkg() { cd ~/ros2_ws && rm -rf build/$1 install/$1; }
alias rtl='ros2 topic list' ; alias rnl='ros2 node list' ; alias rsl='ros2 service list'
alias ral='ros2 action list' ; alias rpl='ros2 param list'
alias rdoctor='ros2 doctor' ; alias rgraph='rqt_graph &'
alias rkill='pkill -9 -f ros2'          # emergency: kill all ROS processes
```
Usage: `cbs my_pkg` builds one package and sources it. The functions above replace the older one-line aliases `alias cb='… colcon build --symlink-install'` (no sourcing) and `cbs() { … --packages-select "$@" … }` (no argument check); define each name only once.

## Daily workflow
```bash
cdsrc && code my_pkg/          # 1 edit
cbs my_pkg                     # 2 build + source (C++ changes, new exes/launch/interfaces)
ros2 launch my_pkg x.launch.py # 3 run
rtl ; rnl ; rgraph             # 4 inspect in other terminals
```

## tmux (many terminals in one)
```bash
sudo apt install tmux && tmux
# Ctrl+b "  split horizontal | Ctrl+b %  split vertical | Ctrl+b arrows  move
# Ctrl+b d  detach | tmux attach  reattach | Ctrl+b x  close pane
tmux new-session -d -s ros 'ros2 launch my_pkg x.launch.py' \; split-window -h 'ros2 topic echo /odom' \; attach -t ros
```

## Shell tricks
`!!` repeat last · `!ros2` last cmd starting with ros2 · Ctrl+R history search · Ctrl+U/Ctrl+K clear to start/end · Ctrl+L clear screen · `ros2 topic list | grep camera` · `watch -n 1 ros2 topic list`.

## Pitfalls
- Defining `cb` both as an alias and as a function in the same `.bashrc` → bash errors or the wrong one wins. Keep a single definition.
- `rkill` / `pkill -9` leaves bags unclosed. Stop recorders with Ctrl+C first ([[core-bag-record]]).
