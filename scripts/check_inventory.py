"""Diff references/api-inventory.md against the classes `from manimlib import *` exports in the installed fork.

usage: uv run --project PROJECT_DIR python scripts/check_inventory.py [INVENTORY_MD]

No GPU needed (import only). INVENTORY_MD defaults to skills/manimgl-best-practices/references/api-inventory.md.
Checks each `## Scene|Animation|Mobject (N)` section: N equals the listed count, and the listed names equal
the live subclasses of that base. Exit code: 0 match, 1 drift, 2 usage error or manimlib not importable.
"""
import re
import sys
from pathlib import Path

doc_path = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    Path(__file__).resolve().parent.parent / "skills/manimgl-best-practices/references/api-inventory.md")
if not doc_path.is_file():
    print(f"no such file: {doc_path}", file=sys.stderr)
    sys.exit(2)
del sys.argv[1:]  # importing manimlib parses sys.argv as the manimgl CLI (cli-and-output.md §1)

ns = {}
try:
    exec("from manimlib import *", ns)
except ImportError as e:  # not the fork env: a setup error, not drift
    print(f"{e} (run with: uv run --project PROJECT_DIR python scripts/check_inventory.py)", file=sys.stderr)
    sys.exit(2)
from manimlib import Animation, Mobject, Scene  # noqa: E402

live = {"Scene": set(), "Animation": set(), "Mobject": set()}
for name, obj in ns.items():
    if isinstance(obj, type):
        for base, label in ((Scene, "Scene"), (Animation, "Animation"), (Mobject, "Mobject")):
            if issubclass(obj, base):
                live[label].add(name)
                break

doc, count, cur = {}, {}, None
for line in doc_path.read_text(encoding="utf-8").splitlines():
    m = re.match(r"## (\w+) \((\d+)\)", line)
    if m:
        cur = m.group(1)
        doc[cur], count[cur] = set(), int(m.group(2))
        continue
    m = re.match(r"- `[\w.]+`: (.*)", line)
    if cur and m:
        doc[cur].update(x.strip() for x in m.group(1).split(","))

bad = 0
for k in live:
    d = doc.get(k, set())
    miss, extra = sorted(live[k] - d), sorted(d - live[k])
    stated = count.get(k)
    print(f"{k}: live {len(live[k])}, doc {len(d)} (heading says {stated}), "
          f"missing-in-doc {miss}, not-in-fork {extra}")
    bad += len(miss) + len(extra) + (stated != len(d))
sys.exit(1 if bad else 0)
