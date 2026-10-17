"""Execute the Python code in the skill docs against the installed fork and assert documented results.

usage: python scripts/check_docs.py PROJECT_DIR [OUT_DIR] [-v]

PROJECT_DIR is a uv project prepared by setup.sh. Docs: skills/*/SKILL.md and skills/*/references/*.md.
Needs an OpenGL context (one `manimgl ... -sw` render per run) and LaTeX for the Tex snippets.

  * Collects fenced ```python blocks and inline `spans` that parse as Python and contain a call, an
    assignment or an import. `kwarg=value` mentions are counted, not run.
  * All snippets of one doc share a namespace and run in reading order, seeded with a few stubs
    (mob, label, axes, t, ...). Everything runs inside ONE generated scene rendered with -sw.
  * A snippet is skipped (with the reason printed under -v) when it has a free name the namespace does
    not define (method mentions such as `clear()`, placeholders such as `target`), an Ellipsis, a
    blocking or structural call (input, Window, construct, ...) or an os/shutil/subprocess/sys call.
  * `Cls.meth(kw=...)` quoted as a signature (TypeError about 'self') is checked with inspect.signature.
  * Table rows whose result cell says the code errors, or whose row says "Do not use `X`", must raise;
    rows under a "Do not use" header are not treated specially. Result cells that are a number or
    "`len` N" are asserted.
  * raenimgl.md runs in a second scene `(InteractiveScene, Scene2D)` with `from raenimgl import *`,
    only when raenimgl is installed (setup.sh --with-raenimgl).
  * In-doc annotation, on the snippet's line or alone on the line before it (or before the fence):
    `<!-- snippet: skip <reason> -->`, or `<!-- snippet: name=expr name2=expr -->` to bind stub
    values for that snippet only.
This script never imports manimlib (importing manimlib parses sys.argv as the manimgl CLI).
Exit code: 0 all ran snippets pass, 1 any FAIL or MISMATCH, 2 usage error or the render itself failed.
Snippet runner idea (blocks wrapped in a generated Scene) adapted from adithya-s-k/manim_skill @cef0450
tests/manimgl/test_utils.py, lines 8-19 and 191-211 (MIT, Copyright (c) 2026 Adithya S Kolavi). No code was copied.
"""
import ast
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAE_DOCS = {"raenimgl.md"}
BLOCKING = {"input", "checkpoint_paste", "interact", "hold_loop", "open", "main", "run", "construct",
            "exit", "quit", "Window"}  # Window(...) opens a real pyglet window and breaks the render's GL context
ERR_WORDS = re.compile(r"\b(\w*Error|\w*Exception|fails?|raises?)\b")
NO_ERR = re.compile(r"^\**(Works|No error)|raises no|(does )?not raise|no exception|without (an )?error", re.I)
JOINERS = {"and", "or", ",", ", and", "/"}  # "`A` and `B` raise X": A takes B's expectation
ANNOT = re.compile(r"<!--\s*snippet:\s*(.*?)\s*-->")
# shortcut: stub collisions in docs this script's owner cannot edit, keyed by snippet text (first line for a
# fenced block); move each to a <!-- snippet: ... --> annotation in its doc when that doc is next edited
OVERRIDES = {"ParametricCurve(f, t_range=(a, b, step))": ("bind", {"a": "0", "b": "1"}),
             "self.wait(t)": ("bind", {"t": "1"}),
             "interpolate_color(a, b, t)": ("bind", {"a": "RED", "b": "BLUE", "t": "0.5"}),
             "TexturedSurface(s, f)": ("skip", "notation; needs an image file"),
             'TexturedSurface(Sphere(radius=2), "file.png")': ("skip", "needs an image file"),
             R'for tex in (R"x^2 = 4", R"x = \pm 2"):': ("bind", {"eq": 'Tex(R"x^2-4=0")'})}


def directive(lines, i):
    """Annotation on line i, or alone on line i-1 -> ('skip', reason) / ('bind', {name: expr}) / None."""
    m = ANNOT.search(lines[i]) or (ANNOT.fullmatch(lines[i - 1].strip()) if i else None)
    if not m:
        return None
    text = m.group(1)
    if text.split()[:1] == ["skip"]:
        return ("skip", text[4:].strip() or "annotated")
    return ("bind", dict(p.split("=", 1) for p in text.split() if "=" in p))


def collect(docs):
    out = []
    for d in docs:
        rel = d.relative_to(ROOT).as_posix()
        lines = d.read_text(encoding="utf-8").splitlines()
        i = 0
        while i < len(lines):
            m = re.match(r"^\s*```(\w*)\s*$", lines[i])
            if m:
                j = i + 1
                while j < len(lines) and not re.match(r"^\s*```\s*$", lines[j]):
                    j += 1
                if m.group(1) in ("python", "py"):
                    block = lines[i + 1:j]
                    indent = min((len(l) - len(l.lstrip()) for l in block if l.strip()), default=0)
                    code = "\n".join(l[indent:] for l in block)
                    out.append(dict(doc=rel, line=i + 2, code=code, kind="fenced",
                                    directive=directive(lines, i) or OVERRIDES.get(code.split("\n", 1)[0])))
                i = j + 1
                continue
            row = lines[i]
            cells = [c.strip() for c in row.strip().strip("|").split("|")] if row.lstrip().startswith("|") else None
            spans = list(re.finditer(r"`([^`\n]+)`", row))
            prose_expect = [None] * len(spans)  # outside tables: "`X` fails ..." / "`X` and `Y` raise ..."
            # soft: prose is often conditional ("with only the fork installed, `import manimlib` fails"), so a
            # clean run passes; a raise passes unless the line names a different exception type
            for k in range(len(spans) - 1, -1, -1) if not cells else ():
                seg = row[spans[k].end():spans[k + 1].start() if k + 1 < len(spans) else len(row)]
                seg = re.split(r"\.(?:\s|$)", seg)[0]
                if k + 1 < len(spans) and seg.strip() in JOINERS:
                    prose_expect[k] = prose_expect[k + 1]
                elif ERR_WORDS.search(seg) and not NO_ERR.search(seg):
                    prose_expect[k] = ["prose-error", seg]
            for k, sm in enumerate(spans):
                s = sm.group(1).strip()
                try:
                    tree = ast.parse(s)
                except SyntaxError:
                    continue
                if not any(isinstance(n, (ast.Call, ast.Assign, ast.Import, ast.ImportFrom)) for n in ast.walk(tree)):
                    continue
                body = tree.body
                if (len(body) == 1 and isinstance(body[0], ast.Assign) and s[:1].islower()
                        and not any(isinstance(n, ast.Call) for n in ast.walk(body[0]))):
                    out.append(dict(doc=rel, line=i + 1, code=s, kind="kwarg"))  # `color=BLUE` style mention
                    continue
                expect = prose_expect[k]
                if cells and len(cells) >= 2 and cells[0].startswith(f"`{s}`"):
                    res = cells[1]  # result cell: a silent-behavior cell ("ignored: ...") is just run
                    if ERR_WORDS.search(res) and not NO_ERR.search(res):
                        expect = "error"
                    elif re.match(r"^(\d+)(?!\.?\d)", res):
                        expect = int(re.match(r"^(\d+)", res).group(1))
                    elif re.search(r"`len` (\d+)", res):
                        expect = ("len", int(re.search(r"`len` (\d+)", res).group(1)))
                elif re.search(r"Do not use `" + re.escape(s) + "`", row):
                    expect = "error"
                dv = directive(lines, i) or OVERRIDES.get(s)
                out.append(dict(doc=rel, line=i + 1, code=s, kind="inline", expect=expect, directive=dv))
            i += 1
    return out


SCENE = r'''
import ast, builtins, inspect, json, re, sys, traceback, types
from random import seed
IMPORTS_LINE

SNIPPETS = json.loads(SNIPPETS_JSON)
BLOCKING = set(BLOCKING_JSON)
UNSAFE_MODULES = {"os", "shutil", "subprocess", "sys"}
RESULTS = []


def stubs(scene):
    return dict(
        self=scene, frame=scene.frame, mob=Square(), m=Square(), sq=Square(), target=Circle(),
        label=Text("label"), t=Text("정밀도 abc"), a=Text("16 bit"), b=Text("8 bit"),
        group=VGroup(Square(), Circle()), arrow=Arrow(LEFT, RIGHT), axes=ThreeDAxes(),
        tracker=ValueTracker(1), number=DecimalNumber(0), p=np.array([1.0, 1.0, 0.0]),
        x=Dot(2 * RIGHT), h=4, θ=-30, φ=70, γ=0, center=ORIGIN, height=8, s="한글",
        f=lambda t: np.array([t, t ** 2, 0]), step=0.1, overlay=FullScreenRectangle(),
        fixed_text=Text("fixed").fix_in_frame(), fixed_label=Text("fl").fix_in_frame(),
        surface=Sphere(), dt=1 / 30,
    )


def free_names(tree):
    """Names read before the snippet binds them. An assignment binds after its value is read, so the
    loop body `nxt = Tex(..).move_to(eq) ... eq = nxt` reads a free `eq`."""
    scoped, stores, loads = set(), {}, {}
    assign_end = {}
    for st in ast.walk(tree):
        if isinstance(st, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            for t in (st.targets if isinstance(st, ast.Assign) else [st.target]):
                for n in ast.walk(t):
                    assign_end[id(n)] = (st.end_lineno, st.end_col_offset)
        elif isinstance(st, (ast.Import, ast.ImportFrom)):
            for a in st.names:
                k = (a.asname or a.name).split(".")[0]
                stores[k] = min(stores.get(k, (st.lineno, st.col_offset)), (st.lineno, st.col_offset))
        elif isinstance(st, ast.Lambda):
            scoped.update(a.arg for a in st.args.args)
        elif isinstance(st, ast.comprehension):
            scoped.update(x.id for x in ast.walk(st.target) if isinstance(x, ast.Name))
        elif isinstance(st, (ast.FunctionDef, ast.ClassDef)):
            scoped.add(st.name)
            scoped.update(a.arg for a in ast.walk(st) if isinstance(a, ast.arg))
    for n in ast.walk(tree):
        if isinstance(n, ast.Name):
            pos = assign_end.get(id(n), (n.lineno, n.col_offset))
            d = loads if isinstance(n.ctx, ast.Load) else stores
            d[n.id] = min(d.get(n.id, pos), pos)
    return [k for k, pos in sorted(loads.items(), key=lambda kv: kv[1])
            if k not in scoped and (k not in stores or pos < stores[k])]


def signature_check(tree, ns):
    """`Cls.meth(kw=...)` quoted as a signature: compare keyword names with inspect.signature."""
    call = tree.body[0].value
    owner = eval(compile(ast.Expression(call.func.value), "<sig>", "eval"), ns)
    fn = getattr(owner, call.func.attr)
    params = inspect.signature(fn).parameters
    if any(p.kind == p.VAR_KEYWORD for p in params.values()):
        return "pass", "signature has **kwargs"
    bad = [k.arg for k in call.keywords if k.arg and k.arg not in params]
    return ("fail", f"unknown keywords {bad} for {call.func.attr}{inspect.signature(fn)}") if bad else ("pass", "signature ok")


def run_one(scene, sn, ns, res):
    tree = ast.parse(sn["code"])
    calls = {getattr(n.func, "id", getattr(n.func, "attr", None)) for n in ast.walk(tree) if isinstance(n, ast.Call)}
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    dv = sn.get("directive") or [None, None]
    if dv[0] == "skip":
        return res.update(status="skip", why="annotated: " + dv[1])
    if any(isinstance(n, ast.Constant) and n.value is Ellipsis for n in ast.walk(tree)):
        return res.update(status="skip", why="Ellipsis placeholder")
    if calls & BLOCKING:
        return res.update(status="skip", why=f"blocking/structural call {sorted(calls & BLOCKING)}")
    if names & UNSAFE_MODULES:
        return res.update(status="skip", why=f"touches {sorted(names & UNSAFE_MODULES)}")
    bind = dv[1] if dv[0] == "bind" else {}
    missing = [x for x in free_names(tree) if x not in ns and x not in bind and x not in dir(builtins)]
    if missing:
        return res.update(status="skip", why="unbound " + ",".join(missing))
    for n in ast.walk(tree):  # `copy()`, `id()`: a method or value mention that resolves to a module or builtin
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and (
                isinstance(ns.get(n.func.id), types.ModuleType)
                or (n.func.id not in ns and not n.args and not n.keywords and n.func.id in dir(builtins))):
            return res.update(status="skip", why=f"mention of module/builtin {n.func.id}()")
    scene.clear(); scene.add(scene.frame); scene.frame.to_default_state()
    saved = {k: ns[k] for k in bind if k in ns}
    try:
        ns.update({k: eval(v, ns) for k, v in bind.items()})
        if isinstance(tree.body[-1], ast.Expr):
            *head, last = tree.body
            exec(compile(ast.Module(head, []), sn["doc"], "exec"), ns)
            val = eval(compile(ast.Expression(last.value), sn["doc"], "eval"), ns)
        else:
            exec(compile(tree, sn["doc"], "exec"), ns)
            val = None
        exp = sn.get("expect")
        if exp == "error":
            res.update(status="mismatch", why="doc says this errors, it did not")
        elif isinstance(exp, int) and not isinstance(exp, bool):
            got = len(val) if hasattr(val, "__len__") and not isinstance(val, (int, float)) else val
            res.update(status="pass" if got == exp else "mismatch", why=f"expected {exp}, got {got}")
        elif isinstance(exp, list) and exp[0] == "prose-error":
            res.update(status="pass", why="the line mentions an error (conditional); ran without one")
        elif isinstance(exp, list):
            got = len(val) if val is not None else None
            res.update(status="pass" if got == exp[1] else "mismatch", why=f"expected len {exp[1]}, got {got}")
        else:
            res.update(status="pass")
    except (Exception, SystemExit) as e:  # SystemExit: a doc span such as `exit()` must not end the run
        msg = f"{type(e).__name__}: {str(e).splitlines()[0][:160] if str(e) else ''}"
        exp = sn.get("expect")
        named = re.findall(r"\b\w*(?:Error|Exception)\b", exp[1]) if isinstance(exp, list) and exp[0] == "prose-error" else []
        if exp == "error" or (isinstance(exp, list) and exp[0] == "prose-error" and (not named or type(e).__name__ in named)):
            res.update(status="pass", why="raised as documented: " + msg)
        elif named:
            res.update(status="fail", why=f"the line names {named}, got {msg}")
        elif isinstance(e, TypeError) and "required positional argument: 'self'" in str(e):
            try:
                st, why = signature_check(tree, ns)
            except Exception as e2:
                st, why = "fail", f"signature check: {type(e2).__name__}: {e2}"
            res.update(status=st, why="(signature quote) " + why)
        else:
            res.update(status="fail", why=msg)
    finally:
        for k in bind:
            if k in saved:
                ns[k] = saved[k]
            else:
                ns.pop(k, None)


class SCENE_NAME(SCENE_BASES):
    def construct(self):
        ns_by_doc = {}
        for sn in SNIPPETS:
            if sn["doc"] not in ns_by_doc:
                ns = ns_by_doc[sn["doc"]] = {k: v for k, v in globals().items() if not k.startswith("_")}
                ns.update(stubs(self))
            res = dict(doc=sn["doc"], line=sn["line"], code=sn["code"], expect=sn.get("expect"))
            run_one(self, sn, ns_by_doc[sn["doc"]], res)
            RESULTS.append(res)
        self.clear(); self.add(self.frame)
        with open("SCENE_NAME_results.json", "w", encoding="utf-8") as fh:
            json.dump(RESULTS, fh, ensure_ascii=False, indent=1)
'''


def render(project, out, name, imports, bases, snippets):
    """Write one scene file holding `snippets`, render it with -sw, return its results (None on failure)."""
    src = (SCENE.replace("IMPORTS_LINE", imports).replace("SCENE_BASES", bases).replace("SCENE_NAME", name)
           .replace("SNIPPETS_JSON", repr(json.dumps(snippets, ensure_ascii=False)))
           .replace("BLOCKING_JSON", repr(sorted(BLOCKING))))
    (out / f"{name}.py").write_text(src, encoding="utf-8")
    res_file = out / f"{name}_results.json"
    res_file.unlink(missing_ok=True)
    cmd = ["uv", "run", "--project", str(project), "manimgl", f"{name}.py", name, "-sw"]
    try:
        proc = subprocess.run(cmd, cwd=out, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=900)
    except subprocess.TimeoutExpired:
        print(f"[FAIL] {name}: render timed out after 900 s (scene file: {out / (name + '.py')})")
        return None
    except FileNotFoundError as e:  # no uv on PATH: a setup error (exit 2), not a finding
        print(f"[FAIL] {name}: cannot run uv: {e}")
        return None
    if proc.returncode != 0 or not res_file.exists():
        print(proc.stdout[-3000:], proc.stderr[-3000:])
        print(f"[FAIL] {name}: render failed (exit {proc.returncode}); scene file: {out / (name + '.py')}")
        return None
    return json.loads(res_file.read_text(encoding="utf-8"))


def main(argv):
    pos = [a for a in argv if not a.startswith("-")]
    if not pos or not Path(pos[0]).is_dir() or not (Path(pos[0]) / "pyproject.toml").is_file():
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        print("PROJECT_DIR must be a uv project folder (with pyproject.toml)", file=sys.stderr)
        return 2
    project = Path(pos[0]).resolve()
    out = Path(pos[1]).resolve() if len(pos) > 1 else Path(tempfile.mkdtemp(prefix="check_docs_"))
    verbose = "-v" in argv
    out.mkdir(parents=True, exist_ok=True)
    docs = sorted(ROOT.glob("skills/*/SKILL.md")) + sorted(ROOT.glob("skills/*/references/*.md"))
    snippets = collect(docs)
    run = [s for s in snippets if s["kind"] != "kwarg"]
    main_part = [s for s in run if s["doc"].rsplit("/", 1)[-1] not in RAE_DOCS]
    rae_part = [s for s in run if s["doc"].rsplit("/", 1)[-1] in RAE_DOCS]

    results = render(project, out, "DocSnippets", "from manimlib import *", "ThreeDScene", main_part)
    if results is None:
        return 2
    has_rae = subprocess.run(["uv", "run", "--project", str(project), "python", "-c", "import raenimgl"],
                             stdin=subprocess.DEVNULL, capture_output=True).returncode == 0
    if rae_part and has_rae:
        rae = render(project, out, "DocSnippetsRae", "from manimlib import *\nfrom raenimgl import *",
                     "InteractiveScene, Scene2D", rae_part)
        if rae is None:
            return 2
        results += rae
    elif rae_part:
        print(f"[skip] {len(rae_part)} snippets of {', '.join(sorted(RAE_DOCS))} (raenimgl not installed; setup.sh --with-raenimgl)")

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        if r["status"] in ("fail", "mismatch") or verbose:
            print(f"{r['status'].upper():9s} {r['doc']}:{r['line']}  {r['code'][:90]}\n          {r.get('why', '')}")
    print(f"== {len(docs)} docs, {len(snippets)} snippets ({sum(s['kind'] == 'fenced' for s in snippets)} fenced): "
          + ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
          + f", kwarg mentions not run {len(snippets) - len(run)}. scene files: {out}")
    return 1 if counts.get("fail") or counts.get("mismatch") else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
