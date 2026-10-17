"""Check every file:line citation in the plugin (.md and .py) against the reference repos at the pinned commits.

usage: python scripts/check_citations.py REF_DIR [--fetch] [--all] [--show]

REF_DIR holds the checkouts fork/ upstream/ raenimgl/ imcommit/. Each must be at the commit pinned in REFS
below; a checkout at another commit is an error. With --fetch, a missing checkout is cloned into REF_DIR at
its pinned commit (shallow, needs git and network), so REF_DIR doubles as a cache dir across runs.

Citation forms: F:/U:/R:/I:<path>:<lines>, untagged <path>.py:<lines> (tried in fork, then upstream),
`yml:NN` (fork default_config.yml), `same file :NN`, and the `:NN` cells of cli-and-output.md section 2.
Per citation: the file exists, every cited line exists, and an "anchor" (an identifier written on the
same doc line) appears within +-2 lines of the cited lines or is the enclosing def/class name. A citation
whose doc line carries no identifier counts as ok after the file and line checks.
Output: EOF / NOFILE / BLANK (a single cited line that is empty) are errors; WEAK (anchor not found near the lines) and UNKNOWN (an untagged path in
no reference repo) are a review list for a human. --show prints the cited source lines of WEAK hits.
Exit code: 0 no errors, 1 errors, 2 usage error or a reference checkout at the wrong commit.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFS = {  # tag: (dir, url, pinned commit) -- same commits as docs/details.md "Sources and licenses"
    "F": ("fork", "https://github.com/CodingVillainKor/manimgl", "455a4201669cd68ff5e522c7fcd1a7ac31aadff0"),
    "U": ("upstream", "https://github.com/3b1b/manim", "fafa083a4fb274bba9cabde0b6e2f50ba6da0622"),
    "R": ("raenimgl", "https://github.com/CodingVillainKor/raenimgl", "177affc69311d13fcad3404b2599a7714de1d4f2"),
    "I": ("imcommit", "https://github.com/CodingVillainKor/manimgl-imcommit", "a2fe49f4284082ce6c3627cd26e5952cd1d01bb6"),
}
LINES = r"\d+(?:-\d+)?(?:,\s?\d+(?:-\d+)?)*"
CIT = re.compile(rf"(?<![\w/])(?:(?P<tag>[FURI]):)?(?P<path>[\w./-]+\.(?:py|yml|yaml|cfg|toml|glsl|txt))(?::(?P<lines>{LINES}))")
SHORT_YML = re.compile(rf"(?<![\w.])yml:(?P<lines>{LINES})")
SAME_FILE = re.compile(rf"same file :(?P<lines>{LINES})")
TABLE_NN = re.compile(rf"\|\s*:(?P<lines>{LINES})\s*\|")
STOP = {"self", "the", "and", "for", "not", "with", "from", "import", "true", "false", "none",
        "def", "return", "class", "this", "that", "only", "same", "line", "lines", "file", "evidence",
        "source", "verified", "run", "fork", "upstream", "manimlib", "manimgl", "py", "yml"}
SKIP_DIRS = {".git", "videos", "__pycache__"}
_cache = {}


def read(p):
    if p not in _cache:
        _cache[p] = p.read_text(encoding="utf-8", errors="replace").splitlines()
    return _cache[p]


def prepare(ref, fetch):
    """Return an error message, or None when every checkout is at its pinned commit."""
    for tag, (name, url, sha) in REFS.items():
        d = ref / name
        if not d.is_dir() and fetch:
            print(f"[fetch] {url} @ {sha[:8]} -> {d}", flush=True)
            tmp = ref / (name + ".partial")  # renamed to d only on success, so a failed fetch is retried next run
            for cmd in (["git", "init", "-q", str(tmp)], ["git", "-C", str(tmp), "fetch", "-q", "--depth", "1", url, sha],
                        ["git", "-C", str(tmp), "checkout", "-q", "FETCH_HEAD"]):
                if subprocess.run(cmd).returncode != 0:
                    return f"failed: {' '.join(cmd)}"
            tmp.rename(d)
        if not d.is_dir():
            return f"missing checkout {d} (pass --fetch to clone it at {sha[:8]})"
        head = subprocess.run(["git", "-C", str(d), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        if head != sha:
            return f"{d} is at {head[:8] or '?'}, pinned {sha[:8]} (git -C {d} checkout {sha})"
    return None


def candidates(ref, tag, path, default_tag):
    if tag:
        tags = [tag]
    elif path.startswith("raenimgl/"):
        tags = ["R"]
    elif path.startswith("src/") or path in ("init_project.py", "_mhelper.py", "_mupdater.py", "pyproject.toml"):
        tags = ["I"]
    else:
        tags = ([default_tag] if default_tag else []) + ["F", "U"]
    out = []
    for t in dict.fromkeys(tags):
        base = ref / REFS[t][0]
        if (base / path).is_file():
            out.append((t, base / path))
            continue
        hits = [h for h in base.rglob(Path(path).name)
                if ".git" not in h.parts and h.as_posix().endswith("/" + path)]
        if len(hits) == 1:  # short form like composition.py
            out.append((t, hits[0]))
    return out


def parse_lines(s):
    out = []
    for part in re.split(r",\s?", s):
        a, _, b = part.partition("-")
        out.append((int(a), int(b) if b else int(a)))
    return out


def anchors(doc_line, span):
    before = doc_line[max(0, span[0] - 160):span[0]]
    ticks = re.findall(r"`([^`]+)`", before) or re.findall(r"`([^`]+)`", doc_line)
    words = set()
    for t in ticks:
        words.update(re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", t))
    if not words:
        words.update(re.findall(r"\b(?:[A-Z][a-z0-9]+[A-Z]\w*|[a-z0-9]+_[a-z0-9_]+)\b", before))
    return {w for w in words if w.lower() not in STOP}


def enclosing(src, a):
    names = []
    for i in range(min(a, len(src)) - 1, -1, -1):
        m = re.match(r"\s*(class|def)\s+(\w+)", src[i])
        if m and m.group(2) not in names:
            names.append(m.group(2))
            if m.group(1) == "class" or len(names) >= 2:
                break
    return names


def window(src, ranges):
    return "\n".join("\n".join(src[max(0, a - 3):b + 2] + enclosing(src, a)) for a, b in ranges)


def main(argv):
    pos = [a for a in argv if not a.startswith("-")]
    if len(pos) != 1:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    ref = Path(pos[0]).resolve()
    try:
        err = prepare(ref, "--fetch" in argv)
    except FileNotFoundError as e:  # no git on PATH: a setup error (exit 2), not a finding
        err = f"cannot run git: {e}"
    if err:
        print(f"[error] {err}", file=sys.stderr)
        return 2
    show_all, show_src = "--all" in argv, "--show" in argv
    hard = weak = ok = unknown = 0
    files = sorted(p for p in list(ROOT.rglob("*.md")) + list(ROOT.rglob("*.py"))
                   if not SKIP_DIRS & set(p.parts) and ref not in p.parents)  # REF_DIR may sit inside the plugin
    for md in files:
        rel = md.relative_to(ROOT).as_posix()
        dtag = "R" if rel.endswith("raenimgl.md") else "I" if rel.endswith("imcommit-patterns.md") else None
        last_file = None
        for no, line in enumerate(read(md), 1):
            found = [(m.group("tag"), m.group("path"), m.group("lines"), m.span()) for m in CIT.finditer(line)]
            found += [("F", "manimlib/default_config.yml", m.group("lines"), m.span()) for m in SHORT_YML.finditer(line)]
            if last_file:
                found += [(last_file[0], last_file[1], m.group("lines"), m.span()) for m in SAME_FILE.finditer(line)]
            if rel.endswith("cli-and-output.md"):
                found += [("F", "manimlib/config.py", m.group("lines"), m.span()) for m in TABLE_NN.finditer(line)]
            for tag, path, lines, span in found:
                where, cite = f"{rel}:{no}", f"{tag or '?'}:{path}:{lines}"
                cands = candidates(ref, tag, path, dtag)
                if not cands:
                    if tag:
                        hard += 1
                        print(f"NOFILE  {where}  {cite}")
                    else:
                        unknown += 1
                        print(f"UNKNOWN {where}  {cite}  (untagged, in no reference repo)")
                    continue
                words, ranges = anchors(line, span), parse_lines(lines)
                in_range = [(t, p) for t, p in cands if all(1 <= a <= b <= len(read(p)) for a, b in ranges)]
                if not in_range:
                    hard += 1
                    print(f"EOF     {where}  {cite}  (lengths: {[(t, len(read(p))) for t, p in cands]})")
                    continue
                if all(a == b and not read(p)[a - 1].strip() for t, p in in_range for a, b in ranges):
                    hard += 1  # a single cited line that is blank is an off-by-one
                    print(f"BLANK   {where}  {cite}  (the cited line is empty)")
                    continue
                hit_c = [(t, p) for t, p in in_range if not words or any(w in window(read(p), ranges) for w in words)]
                t, p = (hit_c or in_range)[0]
                last_file = (t, p.relative_to(ref / REFS[t][0]).as_posix())
                if hit_c:
                    ok += 1
                    if show_all:
                        print(f"OK      {where}  {cite} [{t}]")
                    continue
                weak += 1
                print(f"WEAK    {where}  {cite} [{t}]  anchors={sorted(words)[:6]}")
                if show_src:
                    src = read(p)
                    for a, b in ranges:
                        for k in range(a, min(b, a + 2) + 1):
                            print(f"            {k}: {src[k - 1].strip()[:110]}")
    print(f"== {ok} ok, {weak} weak, {unknown} unknown, {hard} errors in {len(files)} files")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
