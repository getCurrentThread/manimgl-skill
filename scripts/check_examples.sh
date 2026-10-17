#!/usr/bin/env bash
# Render every Scene in skills/*/examples/*.py and skills/*/gallery/*.py twice:
# -sw (last-frame png) and -w -l (480p mp4).
#
#   bash check_examples.sh PROJECT_DIR [OUT_DIR]
#
# PROJECT_DIR is a uv project prepared by setup.sh. raenimgl_*.py is skipped unless raenimgl imports.
# Needs OpenGL, ffmpeg and LaTeX. Each render gets stdin from /dev/null (a scene-name prompt exits 1
# instead of blocking) and, when `timeout`/`gtimeout` exists, CHECK_TIMEOUT seconds (default 600).
# A Scene is a class whose base name ends in "Scene" or is an earlier Scene of the same file.
# Exit code: number of failed renders (capped at 63), 64 = usage error or the scene list could not be
# built (uv missing, an example that does not parse), 65 = two files share a Scene class name or a file
# name, ignoring case (outputs land in one OUT_DIR and OUT_DIR/videos, and NTFS ignores case).
# PNGs/MP4s/logs stay in OUT_DIR for review.
set -uo pipefail
shopt -s nullglob

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [ $# -lt 1 ] || [ ! -f "$1/pyproject.toml" ]; then
  echo "usage: check_examples.sh PROJECT_DIR [OUT_DIR]   (PROJECT_DIR: uv project from setup.sh)" >&2; exit 64
fi
PROJECT="$(cd "$1" && pwd)"
OUT="${2:-$(mktemp -d)}"
mkdir -p "$OUT" || exit 64
OUT="$(cd "$OUT" && pwd)"
TIMEOUT="$(command -v timeout || command -v gtimeout || true)"
limit() { if [ -n "$TIMEOUT" ]; then "$TIMEOUT" "${CHECK_TIMEOUT:-600}" "$@"; else "$@"; fi; }
fail=0; pass=0

files=("$ROOT"/skills/*/examples/*.py "$ROOT"/skills/*/gallery/*.py)
# "<file name>\t<Scene>" per scene, from the AST (a class header split over lines is still found)
list="$(uv run --project "$PROJECT" python - "${files[@]}" <<'PY'
import ast, os, sys
for f in sys.argv[1:]:
    scenes = set()
    for n in ast.parse(open(f, encoding="utf-8").read()).body:
        if isinstance(n, ast.ClassDef):
            bases = [b.id if isinstance(b, ast.Name) else getattr(b, "attr", "") for b in n.bases]
            if any(b.endswith("Scene") or b in scenes for b in bases):
                scenes.add(n.name)
                print(f"{os.path.basename(f)}\t{n.name}")
PY
)" || { echo "[FAIL] could not list scenes (error above: uv missing or an example that does not parse)"; exit 64; }
list="${list//$'\r'/}"  # Windows python prints CRLF

dups="$( (cut -f2 <<<"$list"; for f in "${files[@]}"; do basename "$f"; done) | sort -f | uniq -di)"
if [ -n "$dups" ]; then
  echo "[FAIL] duplicate Scene class or file names, case-insensitive (outputs would overwrite each other in OUT_DIR or OUT_DIR/videos):"
  sed 's/^/         /' <<<"$dups"; exit 65
fi

has_raenimgl=0
uv run --project "$PROJECT" python -c "import raenimgl" >/dev/null 2>&1 </dev/null && has_raenimgl=1

for f in "${files[@]}"; do
  name="$(basename "$f")"
  if [[ "$name" == raenimgl_* && "$has_raenimgl" == 0 ]]; then
    echo "[skip] $name (raenimgl not installed; setup.sh --with-raenimgl)"; continue
  fi
  cp "$f" "$OUT/"
  for scene in $(awk -F'\t' -v f="$name" '$1 == f {print $2}' <<<"$list"); do
    for mode in "-sw" "-w -l"; do
      ext=$([ "$mode" = "-sw" ] && echo png || echo mp4)
      log="$OUT/$scene.${ext}.log"
      rm -f "$OUT/videos/$scene.$ext"  # a stale file from an earlier run must not count as success
      # shellcheck disable=SC2086
      (cd "$OUT" && limit uv run --project "$PROJECT" manimgl "$name" "$scene" $mode </dev/null) >"$log" 2>&1
      rc=$?
      if [ "$rc" = 0 ] && [ -s "$OUT/videos/$scene.$ext" ]; then
        echo "[ok]   $name $scene $mode -> videos/$scene.$ext"; pass=$((pass + 1))
      else
        why="exit $rc"; [ "$rc" = 124 ] && why="timeout ${CHECK_TIMEOUT:-600}s"
        echo "[FAIL] $name $scene $mode ($why, log: $log)"; tail -n 5 "$log" | sed 's/^/         /'; fail=$((fail + 1))
      fi
    done
  done
done
echo "== $pass ok, $fail failed. outputs: $OUT/videos"
exit $((fail > 63 ? 63 : fail))
