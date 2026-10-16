#!/usr/bin/env bash
# Render every Scene in skills/*/examples/*.py twice: -sw (last-frame png) and -w -l (480p mp4).
#
#   bash check_examples.sh PROJECT_DIR [OUT_DIR]
#
# PROJECT_DIR is a uv project prepared by setup.sh. raenimgl_*.py is skipped unless raenimgl imports.
# Exit code = number of failed renders. PNGs/MP4s/logs stay in OUT_DIR for review.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="$(cd "${1:?usage: check_examples.sh PROJECT_DIR [OUT_DIR]}" && pwd)" || exit 2
OUT="${2:-$(mktemp -d)}"
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"
fail=0; pass=0

has_raenimgl=0
uv run --project "$PROJECT" python -c "import raenimgl" >/dev/null 2>&1 && has_raenimgl=1

for f in "$ROOT"/skills/*/examples/*.py; do
  name="$(basename "$f")"
  if [[ "$name" == raenimgl_* && "$has_raenimgl" == 0 ]]; then
    echo "[skip] $name (raenimgl not installed; setup.sh --with-raenimgl)"; continue
  fi
  cp "$f" "$OUT/"
  for scene in $(sed -nE 's/^class ([A-Za-z_][A-Za-z0-9_]*)\(.*Scene.*\):.*/\1/p' "$f"); do
    for mode in "-sw" "-w -l"; do
      ext=$([ "$mode" = "-sw" ] && echo png || echo mp4)
      log="$OUT/$scene.${ext}.log"
      # shellcheck disable=SC2086
      if (cd "$OUT" && uv run --project "$PROJECT" manimgl "$name" "$scene" $mode) >"$log" 2>&1 \
         && [ -s "$OUT/videos/$scene.$ext" ]; then
        echo "[ok]   $name $scene $mode -> videos/$scene.$ext"; pass=$((pass + 1))
      else
        echo "[FAIL] $name $scene $mode (log: $log)"; tail -n 5 "$log" | sed 's/^/         /'; fail=$((fail + 1))
      fi
    done
  done
done
echo "== $pass ok, $fail failed. outputs: $OUT/videos"
exit "$fail"
