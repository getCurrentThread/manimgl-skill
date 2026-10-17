"""Static lint for code that targets the CodingVillainKor/manimgl fork @455a420. Stdlib only, no GPU.

usage: python lint_manimgl.py FILE_OR_DIR...   (.py files, and ```python / ```bash blocks in .md)
       python lint_manimgl.py --hook           (Claude Code PostToolUse hook, reads the hook JSON on stdin)

Rules come from skills/manimgl-best-practices/SKILL.md (section numbers in the messages) and the
fork evidence cited in each message. A line ending in `# lint: ok` is exempt.
Exit code: 0 clean, 1 findings, 2 usage error or failed self-test. --hook always exits 0 and reports
findings as additionalContext (warn-only).
"""
import ast
import io
import json
import re
import sys
import textwrap
import tokenize
import warnings
from pathlib import Path

# Regexes over code with strings and comments blanked. SKILL.md section 2 (CE habits), 3 (upstream-only).
API = [
    (r"\bfrom manim import\b", "ManimCE import; use `from manimlib import *` (§1)"),
    (r"\bCreate\(", "`Create` is not in the fork; use `ShowCreation` (§2)"),
    (r"\bMathTex\(", "`MathTex` is CE; use `Tex` (§2)"),
    (r"\b(MovingCameraScene|ZoomedScene)\b", "CE scene type; use `Scene` + `self.frame` (§2)"),
    (r"\b(set_camera_orientation|move_camera)\(", "CE camera API; use `self.frame.reorient(...)` (§2)"),
    (r"\bbegin_ambient_camera_rotation\(", "CE; use `self.frame.add_ambient_rotation(...)` (§2)"),
    (r"\badd_fixed_in_frame_mobjects\(", "CE; use `mob.fix_in_frame()` (§2)"),
    (r"\bconfig\.frame_(width|height)\b", "CE config; use FRAME_WIDTH / FRAME_HEIGHT (§2)"),
    (r"(?<!plt)\.plot\(", "CE `Axes.plot`; use `get_graph` (§2)"),
    (r"\.get_area\(", "CE; use `get_area_under_graph` (§2)"),
    (r"\.add_coordinates\(", "CE; use `add_coordinate_labels` (§2)"),
    (r"\bParametricFunction\(", "CE; use `ParametricCurve` (§2)"),
    (r"\bCircumscribe\(", "CE; use `FlashAround` (§2)"),
    (r"\bWiggle\(", "CE; use `WiggleOutThenIn` (§2)"),
    (r"\b(Table|Paragraph|Unwrite|DoubleArrow|Dot3D)\(|\badd_subcaption\(", "not in the fork (§2)"),
    (r"\b(VideoMobject|Sprite|VideoSource|MandelbrotFractal|NewtonFractal|JuliaFractal|vmobject_to_svg)\b",
     "upstream-only, not in the fork (§3)"),
    (r"\.(set_sort_to_camera|set_joint_roundness|get_resolution)\(", "upstream-only method (§3)"),
]
# Shell lines in ```bash blocks: CLI habits (§2, §4)
CLI = [  # `(-\S+\s+)*`: flags may come before the file (`manim -pql f.py S`)
    (r"(^|\s)manim\s+(-\S+\s+)*\S+\.py\b", "`manim` is the CE command; use `uv run manimgl` (§2)"),
    (r"^(?!.*(\s-\w*[wo]|\s--(write_file|open|finder)\b)).*\bmanimgl\b.*\s-(ql|qm|pql|sql)\b",
     "`-ql` parses as -q -l; use `-w -l` (§2)"),
    # -qh is -q -h: argparse prints help, renders nothing and exits 0, even with -w [verified by run]
    (r"\bmanimgl\b.*\s-\w*qh\b", "`-qh` parses as -q -h: prints help and exits 0 without rendering, even with -w; use `--hd` or nothing (§2)"),
    (r"\bmanimgl\b.*\s-p\b", "`-p` is presenter mode in the fork and hangs with -w (§2)"),
    # -o / --finder turn on -w, --write_all (-a) does not (F:manimlib/config.py:138,233); else it runs in a window
    (r"^(?!.*(\s-\w*[wo]|\s--(write_file|open|finder)\b)).*\bmanimgl\s+(-\S+\s+)*\S+\.py\b",
     "no `-w`: manimgl opens a window and hangs (also with -s, -l, -a); add -w, e.g. -sw (§4)"),
    (r"^(?!.*uv run).*(^|\s)manimgl\s+(-\S+\s+)*\S+\.py\b", "run as `uv run manimgl` (a global manimgl may be PyPI) (§0)"),
]
# §6: constructor color= is ignored on these classes [verified by run]
COLOR_IGNORED = {"Text", "Tex", "TexText", "Brace", "Dot", "Arrow", "Vector", "StrokeArrow", "Circle", "Ellipse",
                 "Annulus", "MarkupText", "Sector", "AnnularSector", "Cross",
                 # built on the classes above, so color=BLUE stays white too [verified by run]
                 "SmallDot", "Title", "BulletedList", "BraceLabel", "BraceText", "Exmark", "Checkmark"}
# §3: keywords that exist only upstream; TypeError in the fork [verified by run]. Constructor keywords
# are checked on CamelCase calls, the rest on their method only (pydub's `frame_rate=` is fine).
UPSTREAM_CTOR_KW = {"sort_to_camera", "joint_roundness", "stroke_width_in_scene_units", "textures", "texture_filter"}
UPSTREAM_METHOD_KW = {"frame_rate": "update", "gradient_direction": "set_fill", "code_target": "set_color_by_code"}
# Every color constant that `from manimlib import *` exports in the fork (listed from the installed fork, F:manimlib/constants.py:78-148)
FORK_COLORS = set("""BLACK BLUE BLUE_A BLUE_B BLUE_C BLUE_D BLUE_E DARK_BROWN GOLD GOLD_A GOLD_B GOLD_C GOLD_D GOLD_E
GREEN GREEN_A GREEN_B GREEN_C GREEN_D GREEN_E GREEN_SCREEN GREY GREY_A GREY_B GREY_BROWN GREY_C GREY_D GREY_E
LIGHT_BROWN LIGHT_PINK MAROON MAROON_A MAROON_B MAROON_C MAROON_D MAROON_E ORANGE PINK PURE_BLUE PURE_GREEN PURE_RED
PURPLE PURPLE_A PURPLE_B PURPLE_C PURPLE_D PURPLE_E RED RED_A RED_B RED_C RED_D RED_E TEAL TEAL_A TEAL_B TEAL_C TEAL_D
TEAL_E WHITE YELLOW YELLOW_A YELLOW_B YELLOW_C YELLOW_D YELLOW_E""".split())
HUES = {"BLUE", "TEAL", "GREEN", "YELLOW", "GOLD", "RED", "MAROON", "PURPLE", "GREY", "GRAY", "PINK", "ORANGE",
        "BROWN", "CYAN", "MAGENTA", "WHITE", "BLACK"}
COLOR_WORDS = HUES | {"LIGHT", "DARK", "LIGHTER", "DARKER", "PURE", "SCREEN", "A", "B", "C", "D", "E"}
COLOR_HINT = {"CYAN": 'TEAL or "#00FFFF"', "MAGENTA": 'PINK / PURPLE or "#FF00FF"',
              "BROWN": "GREY_BROWN / DARK_BROWN / LIGHT_BROWN"}
IMPORTS_MANIM = re.compile(r"^\s*(from|import)\s+(manimlib|raenimgl)\b", re.M)
IMPORTS_CE = re.compile(r"^\s*(from|import)\s+manim\b", re.M)


def code_only(src):
    """Source lines with string literals and comments blanked (docstrings mention banned names on purpose)."""
    lines = src.splitlines()
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return lines
    for t in reversed(toks):  # f-string text is FSTRING_MIDDLE since Python 3.12
        if t.type in (tokenize.STRING, tokenize.COMMENT, getattr(tokenize, "FSTRING_MIDDLE", -1),
                      getattr(tokenize, "TSTRING_MIDDLE", -1)):
            (r0, c0), (r1, c1) = t.start, t.end
            if r0 == r1:
                lines[r0 - 1] = lines[r0 - 1][:c0] + '""' + lines[r0 - 1][c1:]
            else:
                lines[r0 - 1] = lines[r0 - 1][:c0] + '""'
                for r in range(r0, r1 - 1):
                    lines[r] = ""
                lines[r1 - 1] = lines[r1 - 1][c1:]
    return lines


def name_of(func):
    return func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else None


def is_seed_call(n):
    """seed(..), random.seed(..), np.random.seed(..), numpy.random.seed(..)"""
    if not isinstance(n, ast.Call):
        return False
    f = n.func
    if isinstance(f, ast.Name):
        return f.id == "seed"
    return (isinstance(f, ast.Attribute) and f.attr == "seed"
            and ((isinstance(f.value, ast.Name) and f.value.id == "random")
                 or (isinstance(f.value, ast.Attribute) and f.value.attr == "random")))


def bound_names(tree):
    """Names the file itself defines (assigned, def/class, argument, imported by name)."""
    bound = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and not isinstance(n.ctx, ast.Load):
            bound.add(n.id)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.add(n.name)
        elif isinstance(n, ast.arg):
            bound.add(n.arg)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            bound.update((a.asname or a.name).split(".")[0] for a in n.names)
    return bound


def ast_findings(tree):
    out = []
    bound = bound_names(tree)
    other_star = any(isinstance(n, ast.ImportFrom) and any(a.name == "*" for a in n.names)
                     and (n.module or "").split(".")[0] not in ("manimlib", "raenimgl") for n in ast.walk(tree))
    scene_classes = {"Scene"}
    for n in tree.body:  # a class whose base is *Scene or an earlier scene class of this file
        if isinstance(n, ast.ClassDef) and any((name_of(b) or "").endswith("Scene") or name_of(b) in scene_classes
                                               for b in n.bases):
            scene_classes.add(n.name)

    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            fn = name_of(n.func)
            kws = {k.arg for k in n.keywords if k.arg}
            if isinstance(n.func, ast.Name) and fn in COLOR_IGNORED and "color" in kws:
                out.append((n.lineno, f"`{fn}(color=...)` is ignored in the fork; chain `.set_color(...)` (§6)"))
            ctor = isinstance(n.func, ast.Name) and fn[:1].isupper()
            for k in sorted(kws):
                if (ctor and k in UPSTREAM_CTOR_KW) or (fn and UPSTREAM_METHOD_KW.get(k) == fn):
                    out.append((n.lineno, f"`{fn}({k}=...)` is upstream-only: TypeError in the fork (§3)"))
            if fn in ("AnimationGroup", "LaggedStart") and "time_span" in kws:
                out.append((n.lineno, "group-level `time_span=` is ignored in the fork; pass it to each animation "
                                      "(§3, F:manimlib/animation/composition.py:63-67,108-121)"))
            if isinstance(n.func, ast.Name) and fn == "Succession":
                out.append((n.lineno, "`Succession` shows later members early (play adds them at t=0, each begins "
                                      "only on its turn) and splits time equally; use separate plays, or "
                                      "`LaggedStart(..., lag_ratio=1)` only for independent mobjects (§11) "
                                      "(F:manimlib/animation/composition.py:133-136,144-153)"))
        elif (isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and not other_star  # a star import may define it
              and n.id not in bound and n.id not in FORK_COLORS):
            words = n.id.split("_")
            if set(words) <= COLOR_WORDS and set(words) & HUES:
                alt = n.id.replace("GRAY", "GREY")
                hint = alt if alt in FORK_COLORS else COLOR_HINT.get(n.id, "a fork color constant or a hex string")
                out.append((n.lineno, f"`{n.id}` is not a fork color (NameError); use {hint} "
                                      "(F:manimlib/constants.py:78-148)"))

    scene_defs = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name in scene_classes]
    if len(scene_defs) > 1:  # `random_seed = N` isolates a scene rendered alone, not `manimgl f.py A B`
        for c in scene_defs:
            for s in c.body:  # `random_seed = 41` or `random_seed: int = 41` (the fork's own form, F:manimlib/scene/scene.py:53)
                tgts = s.targets if isinstance(s, ast.Assign) else [s.target] if isinstance(s, ast.AnnAssign) else []
                if (any(isinstance(t, ast.Name) and t.id == "random_seed" for t in tgts) and s.value is not None
                        and not (isinstance(s.value, ast.Constant) and s.value.value is None)):
                    out.append((s.lineno, "`random_seed` is applied in Scene.__init__, and `manimgl file.py A B` builds "
                                          "every scene before the first runs, so the last scene's seed wins; seed at "
                                          "the top of construct() (F:manimlib/scene/scene.py:139-141, "
                                          "F:manimlib/extract_scene.py:106-109)"))
    if len(scene_classes) > 1:  # module-level and scene-class-body seeds (both run at import) in a file with scenes
        stack = [s for s in tree.body if not isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
        stack += [s for c in scene_defs for s in c.body
                  if not isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
        for s in stack:
            for n in ast.walk(s):
                if is_seed_call(n):
                    out.append((n.lineno, "a seed at module or class level is undone: Scene.__init__ reseeds random and np.random "
                                          "with `random_seed` (default 0), and a multi-scene run builds every scene "
                                          "before the first runs; seed at the top of construct() "
                                          "(F:manimlib/scene/scene.py:53,139-141, F:manimlib/extract_scene.py:106-109)"))

    for fn in ast.walk(tree):  # TransformMatching*(x.copy(), y) ... x = y  -> every step stacks on screen
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        rebinds, same_spot = set(), set()  # (x, y) for `x = y`; (y, x) for `y.move_to(x)` / `y = ....move_to(x)`
        for a in ast.walk(fn):
            if isinstance(a, ast.Assign) and len(a.targets) == 1 and isinstance(a.targets[0], ast.Name):
                if isinstance(a.value, ast.Name):
                    rebinds.add((a.targets[0].id, a.value.id))
                same_spot.update((a.targets[0].id, c.args[0].id) for c in ast.walk(a.value)
                                 if isinstance(c, ast.Call) and name_of(c.func) == "move_to"
                                 and c.args and isinstance(c.args[0], ast.Name))
            elif (isinstance(a, ast.Call) and name_of(a.func) == "move_to" and isinstance(a.func, ast.Attribute)
                  and isinstance(a.func.value, ast.Name) and a.args and isinstance(a.args[0], ast.Name)):
                same_spot.add((a.func.value.id, a.args[0].id))
        for c in ast.walk(fn):
            if (isinstance(c, ast.Call) and (name_of(c.func) or "").startswith("TransformMatching")
                    and len(c.args) >= 2 and isinstance(c.args[0], ast.Call) and not c.args[0].args
                    and isinstance(c.args[0].func, ast.Attribute) and c.args[0].func.attr == "copy"
                    and isinstance(c.args[0].func.value, ast.Name) and isinstance(c.args[1], ast.Name)):
                x, y = c.args[0].func.value.id, c.args[1].id
                if (x, y) in rebinds and (y, x) in same_spot:  # next_to(x, DOWN) instead: a stacked list on purpose
                    out.append((c.lineno, f"`{name_of(c.func)}({x}.copy(), {y})` with `{y}` moved onto `{x}`, then "
                                          f"`{x} = {y}`: the original `{x}` stays under every step and they overlap; "
                                          f"pass `{x}` itself (F:manimlib/animation/transform_matching_parts.py:112-115)"))
    return out


def py_findings(src, base_line=1):
    lines = src.splitlines()
    try:
        with warnings.catch_warnings():  # 3.12+ prints `<unknown>:N: SyntaxWarning` (e.g. "\s" in Tex) with no file name
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(src)
    except SyntaxError:
        tree = None
    own = bound_names(tree) if tree else set()  # a bare name the file defines is its own (a local `class Table`)
    lib = set()  # raenimgl defines `Create` and `Circumscribe` (R:raenimgl/animation.py:310,314)
    if "from raenimgl import" in src:
        lib |= {"Create", "Circumscribe"}
    if re.search(r"^\s*(import|from)\s+matplotlib\b", src, re.M):
        lib.add("plot")  # `ax.plot(` is matplotlib
    out = []
    for i, code in enumerate(code_only(src), 1):
        for rx, msg in API:
            for m in re.finditer(rx, code):
                name = re.search(r"\w+", m.group()).group()
                if name not in lib and (m.group().startswith(".") or name not in own):
                    out.append((i, msg))
                    break
    if tree:
        out += ast_findings(tree)
    keep = sorted({(ln, msg) for ln, msg in out if not (ln <= len(lines) and lines[ln - 1].rstrip().endswith("# lint: ok"))})
    return [(ln + base_line - 1, msg) for ln, msg in keep]


def sh_findings(src, base_line=1):
    out = []
    for i, line in enumerate(src.splitlines(), base_line):
        if line.rstrip().endswith("# lint: ok"):
            continue
        code = line.split(" #", 1)[0]
        for rx, msg in CLI:
            if re.search(rx, code):
                out.append((i, msg))
    return out


def lint(path):
    text = path.read_text(encoding="utf-8-sig", errors="replace")  # -sig: Windows editors write a BOM that ast.parse rejects
    if path.suffix == ".py":
        return py_findings(text)
    out = []
    for m in re.finditer(r"^[ \t]*```(\w*)[ \t]*\n(.*?)^[ \t]*```", text, re.S | re.M):
        start = text.count("\n", 0, m.start(2)) + 1
        if m.group(1) in ("python", "py"):
            out += py_findings(textwrap.dedent(m.group(2)), start)
        elif m.group(1) in ("bash", "sh", "shell", ""):
            out += sh_findings("\n".join(l.strip() for l in m.group(2).splitlines()), start)
    return out


def main(args):
    files = []
    for a in args:
        p = Path(a)
        if not p.exists():
            print(f"no such file or folder: {a}", file=sys.stderr)
            return 2
        # parts below the argument only: the plugin itself may live under ~/.claude
        files += sorted(x for x in p.rglob("*") if x.suffix in (".py", ".md") and x.is_file() and not any(
            s.startswith(".") or s in ("videos", "site-packages", "__pycache__") for s in x.relative_to(p).parts)
        ) if p.is_dir() else [p]
    total = 0
    for f in files:
        for ln, msg in lint(f):
            total += 1
            print(f"{f.as_posix()}:{ln}: {msg}")
    print(f"== {total} finding(s) in {len(files)} file(s)")
    return 1 if total else 0


def manimgl_project(p):
    """The nearest pyproject.toml above p names manimgl (a ManimCE project must not be told to switch)."""
    for d in p.resolve().parents:
        if (d / "pyproject.toml").is_file():
            return "manimgl" in (d / "pyproject.toml").read_text(encoding="utf-8", errors="replace").lower()
    return False


def hook():
    """PostToolUse hook: lint the written .py if it imports manimlib/raenimgl, or imports `manim` (CE) inside
    a manimgl project. Warn-only: always exit 0."""
    try:
        fp = (json.loads(sys.stdin.buffer.read().decode("utf-8", "replace")).get("tool_input") or {}).get("file_path") or ""
        p = Path(fp)
        if p.suffix != ".py" or not p.is_file():
            return 0
        src = p.read_text(encoding="utf-8-sig", errors="replace")
        if not (IMPORTS_MANIM.search(src) or (IMPORTS_CE.search(src) and manimgl_project(p))):
            return 0
        found = py_findings(src)
    except Exception:  # a lint bug must never break the user's session
        return 0
    if found:
        msg = "\n".join([f"manimgl-skill lint (warn-only) found {len(found)} issue(s) in {p.name}:"]
                        + [f"{p.name}:{ln}: {m}" for ln, m in found[:20]]
                        + ["Fix them, or end the line with `# lint: ok` if it is intended."])
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}}))
    return 0


def self_test():
    """Each rule fires on a known-bad snippet; known-good fork code stays clean."""
    def rules(src):
        return [m for _, m in py_findings(src)]
    bad = ('from manim import *\nclass A(MovingCameraScene):\n    def construct(self):\n'
           '        self.play(Create(Text("x", color=RED)))\n')
    assert len(rules(bad)) == 4, rules(bad)
    assert len(rules("c = [GRAY, GRAY_A, CYAN, MAGENTA, BROWN, LIGHT_GRAY, DARK_BLUE]")) == 7
    assert "GREY_B" in rules("c = GRAY_B")[0]
    assert rules("GREY_BROWN, LIGHT_PINK, PURE_RED, GREY_A, BLACK") == []
    assert rules("GRAY = '#888888'\nx = GRAY") == []  # a name the file defines is not the fork's
    assert rules("from palette import *\nx = CYAN") == []
    seeds = "from random import seed\nseed(41)\nnp.random.seed(41)\nclass S(Scene):\n    def construct(self):\n        seed(1)\n"
    assert [ln for ln, _ in py_findings(seeds)] == [2, 3]
    assert py_findings("seed(41)\n") == []  # no scene in the file
    attr = "class A(Scene):\n    random_seed = 41\nclass B(Scene):\n    pass\n"
    assert [ln for ln, _ in py_findings(attr)] == [2]
    assert py_findings(attr.split("class B")[0]) == []  # a single scene is rendered alone
    assert [ln for ln, _ in py_findings(attr.replace("random_seed =", "random_seed: int ="))] == [2]
    assert [ln for ln, _ in py_findings("class A(Scene):\n    np.random.seed(41)\n    def construct(self): pass\n")] == [2]
    assert rules("(FadeIn if a else FadeOut)(sq, shift=UP)\n[FadeIn][0](sq, run_time=2)") == []  # no callee name
    assert len(rules("SmallDot(color=RED)\nTitle('x', color=RED)\nBraceLabel(m, 'x', color=RED)")) == 3
    chain = ("class S(Scene):\n    def construct(self):\n        for nxt in steps:\n            nxt.move_to(cur)\n"
             "            self.play(TransformMatchingTex(cur.copy(), nxt))\n            cur = nxt\n")
    assert len(rules(chain)) == 1
    assert len(rules(chain.replace("nxt.move_to(cur)", "nxt = Tex(s).move_to(cur)"))) == 1
    assert rules(chain.replace("cur = nxt", "pass")) == []  # copy kept on purpose (stays beside the source)
    assert rules(chain.replace("nxt.move_to(cur)", "nxt.next_to(cur, DOWN)")) == []  # stacked list on purpose
    assert len(rules("Succession(FadeIn(a), FadeIn(b))\nAnimationGroup(FadeIn(a), time_span=(1, 2))")) == 2
    assert len(rules("Surface(sort_to_camera=True)\nmob.update(0, frame_rate=30)")) == 2
    assert rules("AudioSegment.silent(0, frame_rate=24000)") == []
    assert rules('t = Text("x").set_color(RED)\nself.play(ShowCreation(Square(color=RED)))\n'
                 'self.play(FadeIn(sq, time_span=(1, 2)))\nplt.plot(x)\n"""Create( in a docstring"""\n') == []
    assert rules('Text("x", color=RED)  # lint: ok') == []
    assert rules("from raenimgl import *\nself.play(Create(sq))\nself.play(Circumscribe(sq))") == []
    assert rules("class Table(VGroup):\n    pass\nt = Table()\nCreate = ShowCreation\nCreate(t)") == []
    assert len(rules("t = Table()\nplot = axes.plot(f)")) == 2  # binding `plot` does not make `.plot(` fork API
    assert rules("import matplotlib.pyplot as plt\nfig, ax = plt.subplots()\nax.plot(x)") == []
    assert rules('x = 1\nm = f"Create( MathTex( {x}"') == []  # f-string text (FSTRING_MIDDLE on 3.12+)
    assert len(rules("Sector(color=BLUE)\nAnnularSector(color=BLUE)\nCross(sq, color=BLUE)")) == 3
    assert len(sh_findings("manim f.py S -ql\nuv run manimgl main.py S -s\nuv run manimgl main.py S -sw")) == 2
    assert all(sh_findings(c) for c in ["manim -pql f.py S", "uv run manimgl -s main.py S", "manimgl -w main.py S"])
    assert sh_findings("uv run manimgl main.py S -s  # lint: ok\npip install manimgl && python x.py") == []
    hangs = ["-s", "-a", "-l", "", "-sl", "-ql", "-p", "--write_all"]
    writes = ["-sw", "-w -l", "-s -o", "-s --open", "-s --finder", "-w -ql", "-a -w", "-wl", "--write_file"]
    assert all(sh_findings(f"uv run manimgl main.py S {f}") for f in hangs)
    assert not any(sh_findings(f"uv run manimgl main.py S {f}") for f in writes)
    assert len(sh_findings("uv run manimgl main.py S -w -qh")) == 1


if __name__ == "__main__":
    if "--hook" in sys.argv:
        sys.exit(hook())
    try:
        self_test()
    except AssertionError as e:
        print(f"lint_manimgl.py self-test failed: {e!r}", file=sys.stderr)
        sys.exit(2)  # exit 1 would read as 'findings'
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
