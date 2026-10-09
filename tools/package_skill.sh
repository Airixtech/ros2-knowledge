#!/usr/bin/env bash
# Package a skill for Claude Desktop / claude.ai (.zip) and link it for Claude Code.
#
# Usage: tools/package_skill.sh <skill> [--no-zip] [--no-link]
#   zip  -> dist/<skill>.zip containing <skill>/SKILL.md, notes/, learn/, ... (areas.yaml excluded)
#   link -> $SKILLS_DIR/<skill> pointing to skills/<skill> (default SKILLS_DIR=~/.claude/skills)
#           Linux/macOS: symlink (ln -sfn). Windows (Git Bash/MSYS): directory junction (mklink /J),
#           which needs no admin rights or Developer Mode.
# The script validates and rebuilds the indexes first, and refuses to package if validation fails.
# It never deletes a real directory at the link location: it only replaces an existing link.
set -euo pipefail

usage() { echo "usage: $0 <skill> [--no-zip] [--no-link]" >&2; exit 2; }
[ $# -ge 1 ] || usage
SKILL="$1"; shift
DO_ZIP=1; DO_LINK=1
for arg in "$@"; do
  case "$arg" in
    --no-zip) DO_ZIP=0 ;;
    --no-link) DO_LINK=0 ;;
    *) usage ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/skills/$SKILL"
[ -f "$SRC/SKILL.md" ] || { echo "error: $SRC/SKILL.md not found" >&2; exit 1; }

# Pick a working Python (on Windows 'python3' may be the Microsoft Store stub).
PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys' >/dev/null 2>&1; then PY="$c"; break; fi
done
[ -n "$PY" ] || { echo "error: no working python found" >&2; exit 1; }

"$PY" "$ROOT/tools/build_index.py" "$SKILL"
"$PY" "$ROOT/tools/validate.py" || { echo "error: validation failed; not packaging" >&2; exit 1; }

if [ "$DO_ZIP" -eq 1 ]; then
  mkdir -p "$ROOT/dist"
  ZIP="$ROOT/dist/$SKILL.zip"
  "$PY" - "$SRC" "$ZIP" "$SKILL" <<'PYEOF'
import sys, zipfile
from pathlib import Path
src, out, name = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
skip_names = {'areas.yaml', '.DS_Store'}
skip_dirs = {'.obsidian', '.trash', '__pycache__', '.git'}
count = 0
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(src.rglob('*')):
        rel = p.relative_to(src)
        if p.is_dir() or p.name in skip_names or any(part in skip_dirs for part in rel.parts):
            continue
        z.write(p, (Path(name) / rel).as_posix())
        count += 1
print(f'zip: {out} ({count} files, {out.stat().st_size // 1024} KiB)')
PYEOF
fi

if [ "$DO_LINK" -eq 1 ]; then
  DEST_DIR="${SKILLS_DIR:-$HOME/.claude/skills}"
  DEST="$DEST_DIR/$SKILL"
  mkdir -p "$DEST_DIR"
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
      WIN_DEST="$(cygpath -w "$DEST")"; WIN_SRC="$(cygpath -w "$SRC")"
      ps() { powershell.exe -NoProfile -NonInteractive -Command "$1" | tr -d '\r'; }
      if [ -e "$DEST" ] || [ -L "$DEST" ]; then
        LINK_TYPE="$(ps "(Get-Item -LiteralPath '$WIN_DEST' -Force).LinkType")"
        if [ "$LINK_TYPE" = "Junction" ] || [ "$LINK_TYPE" = "SymbolicLink" ]; then
          ps "[System.IO.Directory]::Delete('$WIN_DEST')"   # removes the link only, never the target
        else
          echo "error: $DEST exists and is not a link/junction; remove it manually" >&2; exit 1
        fi
      fi
      ps "New-Item -ItemType Junction -Path '$WIN_DEST' -Target '$WIN_SRC' | Out-Null"
      echo "link: $DEST -> $SRC (junction)"
      ;;
    *)
      if [ -e "$DEST" ] && [ ! -L "$DEST" ]; then
        echo "error: $DEST exists and is not a symlink; remove it manually" >&2; exit 1
      fi
      ln -sfn "$SRC" "$DEST"
      echo "link: $DEST -> $SRC (symlink)"
      ;;
  esac
fi
