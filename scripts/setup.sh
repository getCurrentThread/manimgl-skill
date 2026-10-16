#!/usr/bin/env bash
# manimgl-skill setup: install the CodingVillainKor/manimgl fork into an isolated uv project and verify it.
#
#   bash setup.sh [PROJECT_DIR] [--with-raenimgl] [--smoke]
#
# PROJECT_DIR      uv project root (default: .). Created with `uv init --bare` if it has no pyproject.toml.
# --with-raenimgl  also add raenimgl (optional util lib used by imcommit), pinned to a tested commit.
# --smoke          render the fork's OpeningManimExample (or a no-LaTeX scene if LaTeX is missing) to mp4.
#
# The fork and PyPI `manimgl` ship the same `manimlib` module and the same version string (1.7.2),
# so the fork is pinned by git commit and identified via direct_url.json, never by version.
set -euo pipefail

FORK_URL="https://github.com/CodingVillainKor/manimgl"
FORK_REV="455a4201669cd68ff5e522c7fcd1a7ac31aadff0"
RAENIMGL_URL="https://github.com/CodingVillainKor/raenimgl"
RAENIMGL_REV="177affc69311d13fcad3404b2599a7714de1d4f2"
PY_VERSION="3.10"   # imcommit pins 3.10.18; fork setup.cfg classifiers stop at 3.10

PROJECT_DIR="."; WITH_RAE=0; SMOKE=0; WARNS=0
ok()   { printf '  [ok]   %s\n' "$*"; }
warn() { printf '  [warn] %s\n' "$*" >&2; WARNS=$((WARNS + 1)); }
die()  { printf '  [fail] %s\n' "$*" >&2; exit 1; }

for a in "$@"; do
  case "$a" in
    --with-raenimgl) WITH_RAE=1 ;;
    --smoke) SMOKE=1 ;;
    -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
    -*) die "unknown option: $a" ;;
    *) PROJECT_DIR="$a" ;;
  esac
done

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) OS=windows ;;
  Darwin) OS=macos ;;
  *) OS=linux ;;
esac

echo "== 1. system dependencies ($OS)"
command -v uv >/dev/null || die "uv not found: https://docs.astral.sh/uv/getting-started/installation/"
ok "$(uv --version)"
command -v git >/dev/null || die "git not found (uv needs it to fetch the fork from git)"
ok "git"
command -v ffmpeg >/dev/null || die "ffmpeg not found (needed by manimgl -w). windows: winget install Gyan.FFmpeg | macos: brew install ffmpeg | linux: apt install ffmpeg"
ok "ffmpeg"
command -v ffprobe >/dev/null && ok "ffprobe" || warn "ffprobe not found (the video viewer and the --smoke duration check need it)"
if command -v latex >/dev/null && command -v dvisvgm >/dev/null; then
  ok "latex + dvisvgm"
  # default template uses T1 fontenc; without Type1 EC fonts dvisvgm emits an empty SVG (exit 0)
  # and manimgl fails with "SVG has no content to measure"
  if [ -n "$(kpsewhich sfrm1000.pfb 2>/dev/null)" ]; then ok "Type1 EC fonts (cm-super)"
  else warn "cm-super (sfrm1000.pfb) not found: Tex/TexText can come out empty ('SVG has no content to measure'). MiKTeX: miktex packages install cm-super | TeX Live: install the cm-super package. then rerun with --clear-cache"; fi
else
  warn "latex/dvisvgm not found: Tex, TexText, Brace, Matrix brackets, axis labels will fail (Text/MarkupText/Code still work). windows: winget install MiKTeX.MiKTeX | macos: brew install --cask mactex-no-gui | linux: a TeX Live with latex + dvisvgm"
fi
if [ "$OS" = linux ]; then
  if command -v pkg-config >/dev/null && pkg-config --exists pango; then ok "pango (pkg-config)"
  else warn "pango dev headers not found; fork README requires Pango + headers on Linux (see ManimPango 'Building')"; fi
fi
if [ "$OS" != windows ]; then
  echo "  [info] manimgl-skill was verified on Windows only; these checks are untested on $OS"
fi

echo "== 2. uv project: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
PROJECT_ABS="$(pwd)"
if [ ! -f pyproject.toml ]; then
  uv init --bare --python "$PY_VERSION" >/dev/null \
    || die "uv init failed (see the uv error above). a folder name that is not a valid package name (e.g. Korean) needs: uv init --bare --name <ascii-name>, then rerun"
  uv python pin "$PY_VERSION" >/dev/null
  ok "created pyproject.toml (python $PY_VERSION)"
fi

# has_dep NAME: pyproject has a "NAME..." or 'NAME...' dependency entry, any case (also true for "manimgl @ git+...")
# shortcut: regex, not a TOML parser (python 3.10 has no tomllib); misses '''NAME''' strings and also counts entries
# outside [project].dependencies (e.g. optional-dependencies), parse if that shows up
has_dep() { grep -Eiq "(^|[[,])[[:space:]]*[\"']$1[^-_a-zA-Z0-9]" pyproject.toml; }
# trimesh/pywavefront: imported by manimlib/mobject/types/surface.py but missing from the fork's setup.cfg
if grep -q 'CodingVillainKor/manimgl' pyproject.toml; then
  grep -q "$FORK_REV" pyproject.toml && ok "manimgl source = fork @ ${FORK_REV:0:8}" \
    || warn "manimgl points to the fork but not commit ${FORK_REV:0:8}; this plugin was verified at that commit"
  EXTRA=""
  for p in trimesh pywavefront; do has_dep "$p" || EXTRA="$EXTRA $p"; done
  if [ -n "$EXTRA" ]; then
    uv add --no-sync $EXTRA >/dev/null || die "uv add of$EXTRA failed (see above)"
    ok "added$EXTRA (imported by the fork, omitted from its setup.cfg)"
  fi
elif has_dep manimgl; then
  warn "pyproject.toml depends on PyPI 'manimgl' (same 'manimlib' module, conflicts with the fork)."
  echo "         fix:  uv remove manimgl && uv add \"manimgl @ git+${FORK_URL}@${FORK_REV}\" trimesh pywavefront" >&2
  exit 2
else
  uv add --no-sync "manimgl @ git+${FORK_URL}@${FORK_REV}" trimesh pywavefront >/dev/null || die "uv add of the fork failed (see above)"
  ok "added manimgl (fork @ ${FORK_REV:0:8}) + trimesh + pywavefront"
fi
if [ "$WITH_RAE" = 1 ] && ! grep -q 'CodingVillainKor/raenimgl' pyproject.toml; then
  uv add --no-sync "raenimgl @ git+${RAENIMGL_URL}@${RAENIMGL_REV}" >/dev/null || die "uv add of raenimgl failed (see above)"
  ok "added raenimgl @ ${RAENIMGL_REV:0:8} (its 'manimgl>=1.7.2' resolves to the pinned fork)"
elif [ "$WITH_RAE" = 1 ] && ! grep -q "$RAENIMGL_REV" pyproject.toml; then
  warn "raenimgl is already in pyproject.toml but not pinned to ${RAENIMGL_REV:0:8}; left unchanged"
fi

echo "== 3. uv sync"
uv sync --quiet || die "uv sync failed"
ok "environment synced"

echo "== 4. verify the installed manimlib is the fork"
uv run python -c "import manimlib; print(manimlib.__file__)" || die "import manimlib failed (see above)"
rc=0
uv run python - "$FORK_REV" <<'PY' || rc=$?
import json, sys, importlib.metadata as md
import manimlib
from manimlib.config import manim_config
rev = sys.argv[1]
errors = []
mismatch = False
if not manimlib.__file__.startswith(sys.prefix):
    errors.append(f"manimlib is not inside this project's env ({sys.prefix})")
du = md.distribution("manimgl").read_text("direct_url.json")
if not du:
    errors.append("manimgl has no direct_url.json -> installed from an index (PyPI), not the fork. "
                  "fix: uv pip uninstall manimgl && uv sync")
else:
    info = json.loads(du)
    commit = info.get("vcs_info", {}).get("commit_id", "")
    if "CodingVillainKor/manimgl" not in info.get("url", ""):
        errors.append(f"manimgl installed from {info.get('url')} (not the fork)")
    elif commit != rev:
        print(f"  [warn] fork commit {commit[:8]} != verified {rev[:8]}", file=sys.stderr)
        mismatch = True
    else:
        print(f"  [ok]   direct_url.json: {info['url']} @ {commit[:8]}")
if manim_config.key_bindings.get("yaw") != "e":
    errors.append("fork marker key_bindings.yaw missing -> this manimlib is not the fork")
else:
    print("  [ok]   fork marker key_bindings.yaw = 'e'")
for e in errors:
    print("  [fail] " + e, file=sys.stderr)
sys.exit(1 if errors else (10 if mismatch else 0))
PY
case $rc in
  0) ;;
  10) WARNS=$((WARNS + 1)) ;;  # commit mismatch, already printed as [warn]
  *) die "fork verification failed (see above)" ;;
esac

uv run python -c "import moderngl; c = moderngl.create_standalone_context(); print('  [ok]   OpenGL', c.info['GL_VERSION'], '|', c.info['GL_RENDERER'])" \
  || warn "OpenGL standalone context failed: rendering (-w) will not work on this machine/session"
uv run python -c "import manimpango, sys; sys.exit(0 if 'Noto Sans KR' in manimpango.list_fonts() else 3)" \
  && ok "font 'Noto Sans KR' visible to Pango (fork default text.font)" \
  || warn "font 'Noto Sans KR' not visible to Pango: Text() falls back to another font (Hangul may break). install Noto Sans KR or pass font=..."
if [ "$WITH_RAE" = 1 ]; then
  uv run python -c "import raenimgl" && ok "import raenimgl" || warn "import raenimgl failed"
fi

GLOBAL_MANIMGL="$(PATH="$(printf '%s' "$PATH" | tr ':' '\n' | grep -v -i '\.venv' | paste -sd: -)" command -v manimgl || true)"
[ -n "$GLOBAL_MANIMGL" ] && warn "a global 'manimgl' is on PATH ($GLOBAL_MANIMGL), possibly PyPI. always use 'uv run manimgl' inside the project"

if [ "$SMOKE" = 1 ]; then
  echo "== 5. smoke render"
  SMOKE_DIR="$(mktemp -d)"
  if command -v latex >/dev/null && command -v dvisvgm >/dev/null; then
    curl -fsSL "https://raw.githubusercontent.com/CodingVillainKor/manimgl/${FORK_REV}/example_scenes.py" -o "$SMOKE_DIR/example_scenes.py" \
      || die "could not download example_scenes.py"
    FILE=example_scenes.py; SCENE=OpeningManimExample
  else
    cat > "$SMOKE_DIR/smoke.py" <<'PY'
from manimlib import *

class SmokeNoTex(Scene):
    def construct(self):
        title = Text("manimgl fork 확인")
        self.play(Write(title))
        self.play(ShowCreation(Square().next_to(title, DOWN)))
PY
    FILE=smoke.py; SCENE=SmokeNoTex
    warn "no LaTeX: smoke-testing $SCENE instead of OpeningManimExample"
  fi
  (cd "$SMOKE_DIR" && uv run --project "$PROJECT_ABS" manimgl "$FILE" "$SCENE" -w -l) || die "render of $SCENE failed"
  OUT="$SMOKE_DIR/videos/$SCENE.mp4"
  [ -f "$OUT" ] || die "expected $OUT"
  if command -v ffprobe >/dev/null; then
    DUR="$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$OUT" || true)"
    awk -v d="$DUR" 'BEGIN { exit !(d + 0 > 0) }' || die "$OUT has no positive duration (ffprobe: '$DUR')"
    ok "$SCENE.mp4 rendered (${DUR}s): $OUT"
  else
    ok "$SCENE.mp4 rendered: $OUT (ffprobe missing: duration not checked)"
  fi
fi

SHOW_DIR="$(pwd -W 2>/dev/null || pwd)"   # Git Bash: print a C:/... path usable from PowerShell too
echo "== done ($WARNS warning(s)). next:  cd \"$SHOW_DIR/src/<video>\" && uv run manimgl main.py <Scene> -sw"
