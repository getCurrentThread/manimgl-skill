# manimgl-skill details

**English** | [한국어](details-ko.md)

Moved from the [README](../README.md): plugin contents, `setup.sh` internals, checks, sources and licenses, and the verification record. Paths below are relative to the plugin root.

## Contents

| Path | Contents |
|---|---|
| `skills/manimgl-best-practices/` | Writing rules (SKILL.md), render-verified examples (`examples/*.py`) |
| `skills/manimgl-best-practices/references/` | Evidence documents: CLI and output, fork vs upstream (incl. code from other manim versions that breaks), imcommit patterns, Korean/Tex/3D (incl. camera orbits, §C8), animation semantics, style and color, interactive shell, raenimgl, API inventory |
| `skills/manimgl-best-practices/gallery/` | 9 ported scene files for ML and math topics (17 scenes) with their own `README.md` and `LICENSE.txt`. **CC BY-NC-SA 4.0**, see Sources and licenses |
| `skills/manimgl-workflow/` | Plan → Code & Render → Iterate workflow, `templates/scenes.md` (worked example `templates/scenes-example.md`), planning references `references/` (narrative patterns, fork-verified visual techniques, voiceover, optional team mode `team-production.md`) |
| `skills/manimgl-workflow/tools/` | Local viewer (`video_viewer.py`, `ui.html`). Optional narration: `tts.py` (narration.txt → clips + `timestamps.json`; engines sapi, edge, gemini), `voiceover.py` (`Narrated` mixin: audio and per-scene SRT) |
| `commands/scene.md` | `/manimgl-skill:scene <topic>` starts the workflow |
| `agents/scene-reviewer.md` | Agent that reviews rendered frames, read-only |
| `hooks/hooks.json` | After Claude writes or edits a manimgl `.py` file, runs the lint and passes the findings to Claude (warn-only) |
| `scripts/setup.sh` | Installs the fork, pinned to a commit, into a uv project and verifies it. If the project already has the fork at another commit, it warns and leaves the commit unchanged (it only adds a missing `trimesh`/`pywavefront`) |
| `scripts/check_examples.sh` | Renders every Scene in `examples/` and `gallery/` with `-sw` and `-w -l` (stdin closed, per-render timeout) |
| `scripts/lint_manimgl.py` | Static lint, stdlib only, no GPU: CE-only and upstream-only APIs, CLI habits, ignored constructor `color=`, color names the fork lacks, seeds that `Scene.__init__` overrides, `Succession`, `.copy()` derivation chains |
| `scripts/check_docs.py` | Runs the Python in SKILL.md and `references/` against the fork in one `-sw` render and asserts the documented results |
| `scripts/check_citations.py` | Checks every `F:`/`U:`/`R:`/`I:` `file:line` citation against the reference repos at the pinned commits |
| `scripts/check_inventory.py` | Diffs `references/api-inventory.md` against the classes the installed fork exports |

## Environment setup (`scripts/setup.sh`)

```bash
bash scripts/setup.sh [PROJECT_DIR] [--with-raenimgl] [--smoke]
```

- Without PROJECT_DIR, the current folder (`.`) becomes the uv project. Do not run it without arguments inside the plugin folder.

### What it does

1. **System dependency checks**
   - Required: `uv`, `ffmpeg`, `git` (uv uses it to fetch the fork from git).
   - With LaTeX present, `--smoke` downloads `example_scenes.py` with `curl`.
   - Warnings only: `ffprobe`, `latex`+`dvisvgm`, cm-super (`sfrm1000.pfb`). On Linux it also checks `pkg-config pango`.
2. **Fork install**: if PROJECT_DIR has no pyproject, it creates a Python 3.10 uv project. It then adds:
   - `manimgl @ git+https://github.com/CodingVillainKor/manimgl@455a4201…`
   - `trimesh`, `pywavefront` (missing from the fork's setup.cfg)
   - If the pyproject already points to the fork, the manimgl entry is left unchanged. Only whichever of `trimesh`, `pywavefront` is not declared gets added. If both are there, the pyproject is not touched.
   - If that fork is at another commit, it warns, and warns once more if the installed commit also differs. Exit 0.
   - With `--with-raenimgl`, if raenimgl is already there at another rev, it is left unchanged with a warning.
3. **PyPI `manimgl` conflict**: prints the fix command and ends with **exit 2**, changing nothing. Double and single quotes, single-line and multi-line arrays, and any case (`'ManimGL'`) are all detected (e.g. `dependencies = ['manimgl>=1.7.2']`). This is a regex check, not a TOML parser.
   ```bash
   uv remove manimgl && uv add "manimgl @ git+https://github.com/CodingVillainKor/manimgl@455a4201669cd68ff5e522c7fcd1a7ac31aadff0" trimesh pywavefront
   ```
4. **Install verification**: after `uv sync`, it checks:
   - that `uv run python -c "import manimlib; print(manimlib.__file__)"` points into the project `.venv`
   - the URL and commit in `direct_url.json`
   - the fork marker `key_bindings.yaw == "e"`
   - an OpenGL context
   - that Pango can see Noto Sans KR
   - and it warns if a separate global `manimgl` exists
5. **`--smoke`**: does a smoke render in a temp folder and uses ffprobe to check that the length is above 0 s (fails if not, or if unreadable). Without ffprobe, only the length check is skipped.
   - With LaTeX, it renders `OpeningManimExample` from `example_scenes.py` at the pinned commit.
   - Without LaTeX, it renders a Korean Text scene.

### Notes

- **Removing PyPI manimgl**: in a project, use the command above. For a global install, remove it the way it was installed (`pip uninstall manimgl`, `uv tool uninstall manimgl`, etc.). The fork and the PyPI release use the same module name (`manimlib`) and the same version string (1.7.2), so an import alone cannot tell them apart.
- **MiKTeX (Windows)**:
  - A fresh install **has no cm-super.** Tex then produces an empty SVG and fails with `SVG has no content to measure`.
  - Install it with `miktex packages install cm-super`, then re-render with `manimgl ... --clear-cache`.
  - To keep package-install dialogs from blocking a render: `initexmf --set-config-value "[MPM]AutoInstall=1"`.
  - A per-user install may not be on PATH. Then add `%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64` to PATH.
- **Korean inside Tex**: needs xelatex and kotex (`cjk-ko`). MiKTeX fetched them through auto-install. To use `t2c`, also put `\usepackage{xcolor}` in the preamble (`examples/korean.py`).

## Checks

Run from the plugin folder. `<uv project>` is a folder prepared by `scripts/setup.sh`.

| Command | Checks | Needs |
|---|---|---|
| `python scripts/lint_manimgl.py skills agents commands README.md README-ko.md` | `.py` files and fenced python/bash blocks in `.md`: §2/§3 APIs, CLI habits (`-ql`, `-qh`, `-p`, any `manimgl` run without `-w`/`-o`/`--finder`, bare `manimgl`), constructor `color=` on the §6 classes, color names the fork lacks (`GRAY*`, `CYAN`, `MAGENTA`, `BROWN`, `DARK_BLUE`, ...), module-level seeds and `random_seed` in multi-scene files, `Succession`, group-level `time_span=`, `TransformMatching*(x.copy(), y)` chains. Runs its self-test first | Python 3 only (no fork, no GPU) |
| `python scripts/check_citations.py <ref dir> [--fetch]` | Every `F:`/`U:`/`R:`/`I:` `file:line` citation in `.md` and `.py`: the file exists, the lines exist, a single cited line is not blank. Prints WEAK lines (no identifier of the doc line near the cited lines) as a review list | `<ref dir>` holding `fork/ upstream/ raenimgl/ imcommit/` at the pinned commits. `--fetch` clones missing ones there (git, network, about 22 MB) |
| `uv run --project <uv project> python scripts/check_inventory.py` | `references/api-inventory.md` against the classes `from manimlib import *` exports | the fork env (no GPU) |
| `python scripts/check_docs.py <uv project> [OUT_DIR] [-v]` | Runs the inline code and fenced python blocks of `skills/*/SKILL.md` and `skills/*/references/*.md` in one generated scene (`-sw`). Asserts table rows whose result is an error or a number. `-v` prints every skip with its reason. `raenimgl.md` runs in a second scene when raenimgl is installed | OpenGL, LaTeX |
| `bash scripts/check_examples.sh <uv project> [OUT_DIR]` | Renders every Scene in `examples/` and `gallery/` with `-sw` and `-w -l` | OpenGL, LaTeX, ffmpeg |
| `claude plugin validate --strict .` | Manifests, frontmatter, `hooks/hooks.json` syntax | Claude Code CLI |

- Exit codes: 0 = clean.
  - `lint_manimgl.py`, `check_docs.py`, `check_citations.py`, `check_inventory.py`: 1 = findings, 2 = usage or setup error (a reference checkout at another commit, a crashed render).
  - `check_examples.sh`: the number of failed renders (at most 63), 64 = usage error or the scene list could not be built (uv missing, an example that does not parse), 65 = two files share a Scene class name or a file name, ignoring case (outputs go to one OUT_DIR and its `videos/`, and NTFS ignores case).
- Lint exemption: end the line with `# lint: ok`.
- Doc snippet annotations, on the snippet's line or alone on the line before it (or before the fence): `<!-- snippet: skip <reason> -->`, or `<!-- snippet: name=expr -->` to bind a stub value for that snippet only.
- `check_examples.sh` gives each render stdin from `/dev/null` (a scene-name prompt exits 1 instead of blocking) and stops it after `CHECK_TIMEOUT` seconds (default 600) when `timeout`/`gtimeout` exists.
- The hook runs the lint after every Write/Edit/MultiEdit while the plugin is enabled, in every project.
  - It returns at once (about 0.2 s) unless the file is a `.py` that imports manimlib or raenimgl, or imports `manim` (CE) inside a project whose nearest pyproject.toml names manimgl (a ManimCE project is left alone).
  - It never blocks. Findings reach Claude as additional context.
  - It needs `python3` or `python` on PATH and does nothing without one.

## Sources and licenses

| Source | Commit | How it was used |
|---|---|---|
| [CodingVillainKor/manimgl](https://github.com/CodingVillainKor/manimgl) | `455a4201669cd68ff5e522c7fcd1a7ac31aadff0` | The target. Rules and evidence come from reading its source. setup.sh installs the code from git |
| [3b1b/manim](https://github.com/3b1b/manim) upstream | `fafa083a` | Compared against the fork |
| [CodingVillainKor/manimgl-imcommit](https://github.com/CodingVillainKor/manimgl-imcommit) | `a2fe49f4284082ce6c3627cd26e5952cd1d01bb6` | No LICENSE file, so **no code was copied.** Only patterns and usage counts are summarized (`references/imcommit-patterns.md`) |
| [CodingVillainKor/raenimgl](https://github.com/CodingVillainKor/raenimgl) | `177affc69311d13fcad3404b2599a7714de1d4f2` | No LICENSE file, so only its API and behavior are described. An optional dependency, installed from the original repo |
| [3b1b/videos](https://github.com/3b1b/videos) | `306a1346a356c7a7b097875ceb51c5cd67d0a56c` | `custom_config.yml` and usage examples were only compared with the fork. No code was copied |
| [Yusuke710/manim-skill](https://github.com/Yusuke710/manim-skill) | `a0048d9e265499038f34a9aa58ff16d306b5034c` | **MIT**, Copyright (c) 2025 Yusuke Miyashita. What was referenced is listed below |
| [adithya-s-k/manim_skill](https://github.com/adithya-s-k/manim_skill) | `cef045011722d285692e3381d12d4d637da56e18` | Two licenses, kept apart. What was used from each is listed below |

Referenced from Yusuke710/manim-skill:
- The plugin layout (marketplace and plugin in one repo under `.claude-plugin`)
- The workflow structure and wording (step-by-step progress, the `[M:SS] Scene: note` feedback format, re-rendering only that scene)
- The viewer `skills/manimgl-workflow/tools/video_viewer.py`, `ui.html`
  - Copied from the original and modified. The changes are listed in `tools/README.md`.
  - The license text is in `tools/LICENSE-manim-skill`.
- `skills/manimgl-workflow/tools/tts.py` adapts parts of its `tts-generate.py` (sha256 cache key, ffprobe durations, cache-hit loop, the `timestamps.json` idea). Its Kokoro pipeline and single voiceover.mp3 were not taken. Listed in `tools/README.md`. `voiceover.py` is new code.

Used from adithya-s-k/manim_skill:
- **MIT** part (top-level LICENSE, Copyright (c) 2026 Adithya S Kolavi):
  - `skills/manim-composer/` was adapted to the fork in `skills/manimgl-workflow/references/narrative-patterns.md`, `visual-techniques.md` and `templates/scenes-example.md`. The changes are listed at the top of each file. License text: `skills/manimgl-workflow/references/LICENSE-manim_skill`.
  - `scripts/check_docs.py` takes the idea of wrapping doc blocks in a generated Scene from `tests/manimgl/test_utils.py`. No code was copied.
- **CC BY-NC-SA 4.0** part (`skills/manimgl-best-practices/`, example code originally by Grant Sanderson / 3Blue1Brown, adapted by Adithya S Kolavi):
  - 9 example files were ported and modified in `skills/manimgl-best-practices/gallery/`. Each file's docstring names its source and changes. The license is in `gallery/LICENSE.txt`, the index in `gallery/README.md`.
  - Its `rules/*.md` and the other examples were only tested against the fork. Short claim fragments are quoted with attribution in `references/animation-semantics.md` §6 and `references/style-and-color.md`. Its 183 example scenes were rendered as a test corpus (`references/fork-diff.md`). One 3-line `create_label` pattern was rewritten.
  - Nothing from this part is in `skills/manimgl-workflow/`.

License of this plugin:
- There is no top-level LICENSE yet. One will be added once the copyright holder is decided. Until then, the third-party parts keep the licenses listed above.
- **`skills/manimgl-best-practices/gallery/` is CC BY-NC-SA 4.0 (Attribution, NonCommercial, ShareAlike).** Whatever license the rest of the plugin gets will not cover that folder. A copy that includes `gallery/` cannot be used commercially, and modified gallery files must stay under CC BY-NC-SA 4.0.
- `docs/demo.gif` and `docs/viewer.png` show renders of `gallery/` scenes and are under CC BY-NC-SA 4.0 like gallery/ (credit: Grant Sanderson / 3Blue1Brown, adapted by Adithya S Kolavi).

## Adjustments where the request differed from the facts

| Request / common belief | Verified fact | Applied as |
|---|---|---|
| Check the last frame with `-s` | In the fork, `-s` alone saves nothing and opens a window (`config.py:278-280`, window at `config.py:331`) | The workflow uses `-sw` → `videos/<Scene>.png` |
| `self.camera.frame` is a CE API, so ban it | It is valid in the fork too, and the same object as `self.frame` (`scene.py:112`) | Documented as "use `self.frame` (a style preference)" |
| Ban `Create` | Not in the fork, but raenimgl provides an alias | Fork alone: `ShowCreation`. The alias is noted in the raenimgl doc |
| imcommit patterns: Scene3D, PythonCode, MINT | imcommit actually uses them in 0, 1 and 0 files | Based on what it does use: `(InteractiveScene, Scene2D)` and camera tilts inside 2D scenes |
| `/scene` | The plugin command is `/manimgl-skill:scene` | Reflected in the README and the command file |
| `/plugin install manimgl-skill/manimgl-skill` | The documented form is `<plugin>@<marketplace>` | `/plugin install manimgl-skill@manimgl-skill` |
| Fix seeds with a module-level `seed(41)`, `np.random.seed(41)` (imcommit template), or with the class attribute `random_seed` | `Scene.__init__` reseeds both RNGs with `random_seed` (default 0), so module seeds are no-ops (F:manimlib/scene/scene.py:53,139-141). A multi-scene command builds every scene first (F:manimlib/extract_scene.py:106-109), so the class attribute holds only for a solo render | Seed as the first line of `construct`: `examples/structure.py`, `gallery/token_sampling.py`, `gallery/matrix_vector_product.py` |
| Port adithya-s-k/manim_skill examples into the plugin | That folder is CC BY-NC-SA 4.0, not MIT | Kept in a separate `gallery/` with its own LICENSE.txt and per-file attribution |

## Verified

Test environment:

| Item | Value |
|---|---|
| OS / shell | Windows 11 Pro, Git Bash |
| uv / Python | uv 0.13.0, Python 3.10.18 |
| ffmpeg | 2025-12-24 gyan build |
| LaTeX | MiKTeX 25.12 (XeTeX 4.16, dvisvgm 3.4.3) |
| GPU | NVIDIA RTX 4070 Ti (OpenGL 3.3) |
| Claude Code | 2.1.301 (0.1.0 checks), 2.1.302 (0.2.0 checks) |
| Locale | System UTF-8 (ACP 65001) |

- **`setup.sh --smoke` (new folder, new venv)**
  - Checked: 0 warnings, `manimlib.__file__` inside `.venv`, `direct_url.json` commit `455a4201`, fork marker, OpenGL 3.3, Noto Sans KR, cm-super
  - `OpeningManimExample.mp4`: 22.0 s
  - The path in the final hint line is in `C:/...` form, inside quotes.
  - Caveat: the uv cache and MiKTeX already on this machine were reused. MiKTeX was put at the front of this shell's PATH by hand (the user PATH already had it from the install).
- **setup.sh branches**
  - PyPI conflict (multi-line array): in a project with `uv add manimgl` (PyPI), a warning, the fix command, exit 2. After running the printed command, a rerun passes with 0 warnings.
  - PyPI conflict (single-line array `dependencies = ["manimgl>=1.7.2"]`): exit 2, pyproject.toml unchanged.
  - PyPI conflict (single quotes on one line `['manimgl>=1.7.2']`, single quotes across lines `'ManimGL==1.7.2'`): both exit 2, 1 warning, pyproject.toml sha256 unchanged.
  - Project that declares only the pinned fork (only the fork added with `uv add`): adds `trimesh`, `pywavefront`, 0 warnings, exit 0, `import manimlib` succeeds. A rerun adds nothing and the sha256 is unchanged.
  - Project with the fork and only `trimesh`: adds only `pywavefront`, 0 warnings, exit 0.
  - Project that already has the fork at another commit (`df31da90`) plus `trimesh`, `pywavefront`: nothing changed, 2 warnings (pyproject, installed commit), exit 0.
  - Korean folder name (rejected by `uv init`): a `[fail]` line and a `--name` hint, exit 1.
  - `bash -n` passes. With both double and single quotes, the detection regex does not match `manimgl-extra`, `manimgl_x`, `manimpango`. The fork line (`"manimgl @ git+…CodingVillainKor/manimgl…"`) goes to the fork branch first.
- **Example renders**
  - Result: 32 scenes in 19 files (`examples/`, `gallery/`) × (`-sw`, `-w -l`) = 64/64 succeeded (`check_examples.sh`, in an env with raenimgl, 2026-10-17). The last run used this commit's files as they are.
  - Every PNG was checked by eye for overlaps, clipping, tofu (□) and colors. The circle in `camera.py` came out green, and "손실" ("loss") in `korean.py` KoreanInTex came out yellow (kotex + xcolor + `t2c`). The authors of the new examples and gallery files also checked a 2 fps frame sheet of each mp4.
  - Seeds: `examples/structure.py` `Intro` and `gallery/token_sampling.py` `TokenSamplingAnimation` gave byte-identical PNGs alone and batched with the next scene, with the seed in `construct`. With a `random_seed = 41` class attribute, `Intro` alone and batched differed.
  - Given a folder without pyproject.toml, `check_examples.sh` stops right away with exit 64. Two files with the same Scene class name stop it with exit 65 before any render.
- **Color pitfalls (probes)**
  - Constructor `color=` ignored: `Text`, `Tex`, `TexText`, `Dot`, `Brace` (white), `Arrow`, `Vector`, `StrokeArrow`, `Annulus`, `Sector`, `AnnularSector` (grey #BBBBBB), `Circle`, `Ellipse` (red outline), `Cross` (red)
  - Honored: `Square`, `Rectangle`, `SurroundingRectangle`, `Line`, `DashedLine`, `Arc`, `Polygon`, `Triangle`, `RegularPolygon`, `CurvedArrow`, `NumberLine`
  - `.set_color()` works on all of the above.
- **Other pitfalls (probes)**
  - With only the fork installed, `import manimlib` fails with `No module named 'trimesh'`.
  - After `Scene.clear()`, `self.frame` is removed from the scene and ambient rotation stops; `self.add(self.frame)` brings it back.
  - The default run_time 2 of `TransformMatchingStrings`/`Tex`, the grey fill from `Square().set_opacity(0.2)`, the origin position of an asymmetric `ThreeDAxes`, `Arrow.set_perpendicular_to_camera`
  - Unknown config keys: `scene.invert_zoom_scroll`, `camera.bundle_draws`, `camera.draw_together`, `file_writer.crf` each fail with a TypeError in their section's constructor.
- **CLI (`references/cli-and-output.md`)**: verified by running: the output file and resolution/fps per flag (ffprobe), the hang with `-s`/`-ql`/`-a` alone, the hang with `-p -w` (checked with `timeout`), the scene-selection prompt and exit 1 on stdin EOF, a failed render leaving the previous mp4 in place, the config merge order, and cache locations. Rows marked `source evidence` in the tables were not run.
- **Interactive shell and CLI pitfalls (`references/interactive.md`, `references/cli-and-output.md` §2.1, §5.1, §7)**: verified by running: code after `self.embed()` (window vs `-w`), `close_scene_on_exit=False`, the shell namespace, `checkpoint_paste` revert/skip/record (with `pyperclip.paste` patched, the real clipboard untouched), `-e`/`-se` and their failure modes, `reload(N)` stickiness, Shift+D/Shift+C output and Ctrl+Shift+Z (called headlessly), flags from other docs (`-h` and `-w -qh` exit 0 without rendering, `--config` read as `--config_file` and ignored, `--resolution 1920,1080` exit 1, ten unknown flags exit 2), `custom_config.yml` keys and tuple strings (a guide-style yml rendered 1920x1080 30 fps with exit 0), vertical video via `sizes.frame_height`, and the random stream shared by scenes rendered in one command. The shell was driven by piped stdin; window-mode runs opened a real preview window.
- **Korean, Tex, 3D (`references/korean-tex-3d.md`)**: verified by render or probe: Korean glyph counts and sub-selection, `MarkupText` ignoring color, the Text vs Tex size difference (1.37×) and its cause (the calibration font), `Tex`/`TexText`/`Title`/`BulletedList` with kotex, when xcolor is needed, the list of classes that need LaTeX (checked with TeX removed from PATH), the depth test pitfall, the billboard formula, translucent surfaces hiding later objects, `set_z_index(-1)` working only when set before the add, the (θ, φ) view table with negative φ and leftover γ, `set_floor_plane("xz")`, the light source, 3D constructor errors, and camera orbits (θ logged every frame: `animate` +360° = no motion, +270° = -90°, `Rotate(frame)` erratic, a combined θ and φ `.animate` rolling to γ = 47.3° mid-move). `examples/camera_orbit.py`: `-sw` and `-w -l` exit 0, θ logged per frame.
- **Animation semantics (`references/animation-semantics.md`, `examples/compositions.py`)**: `compositions.py` (4 scenes) asserts scene membership after `TransformMatchingTex`, `Transform`, `ReplacementTransform` and the frame-safe clear, so exit 0 checks those rules. Probes measured `.animate.rotate(PI)` collapsing (point spread 1.586/0.0/1.586), a `Rotate` shorter than its play spinning about 4 extra turns after its run_time and ending the mp4 unrotated while the `-sw` PNG looked right, `Succession` vs `LaggedStart(lag_ratio=1)` start states (b opacity 1.0 vs 0.0), `LaggedStart(lag_ratio=1)` hiding the first step when a later member animates the same mobject (opacity 0.0 at t=0.5 and t=0.97), default run_times (`ApplyWave(m, run_time=1)` still 3 s), `rate_func=` forwarded by `LaggedStartMap`/`TransformMatching*` and ignored on other groups, a `path_arc_axis` that differs from the rotation axis (radius 2.0 instead of 1.414 mid-turn), play-level vs constructor `lag_ratio=0`, `time_span` and `squish_rate_func` opacities, `f_always` vs `always`, `MoveToTarget` without a target, and the CE kwargs that raise TypeError/NameError. Module seeds 41 and 99 gave identical output.
- **Style, color, Tex selection (`references/style-and-color.md`)**: verified by probe or render: `set_backstroke` vs `set_color` order, one stroke per VMobject, the `opacity=`/`background=` TypeErrors, `add_background_rectangle` shifting string selection, the `BackgroundRectangle` default color, `VHighlight`, missing color names (`GRAY*`, `CYAN`, `MAGENTA`, `BROWN`), hex strings, gradients, background via `set_background_color` and `default_camera_config`, missing style methods, GLSL `set_color_by_code`/`set_color_by_xyz_func` failures (exit 1), post-hoc vs `isolate=` Tex selection (8 formulas), the spacing lost by keys at an operator or `\cos` (`a + b = c` 1.886 wide, 1.617 with `isolate=["="]`), multi-line `&`/`\\` and the nested `align*` LatexError.
- **Code from other manim versions (`references/fork-diff.md`)**: the 183 Scene classes in adithya-s-k/manim_skill @cef0450 `skills/manimgl-best-practices/{examples,templates}` were rendered with `-sw` on the fork: 155 passed, 28 failed. 26 failures come from 15 API/usage causes, each reproduced with a minimal failing scene (exit 1, same message) and fixed (exit 0, PNG checked); 2 are bugs in the examples. Silent color changes: 49 of the 155 passing scenes pass an ignored constructor `color=` (131 calls); in 8 sampled last frames, 29 of 31 such objects had the wrong color.
- **Plan references (`skills/manimgl-workflow/references/`)**: every `[verified by run]` recipe in `visual-techniques.md` was rendered in probes (`-sw` and/or `-w -l`, exit 0, PNG or frame sheet checked) or printed by a probe script. The worked example `templates/scenes-example.md` was implemented as its 3 scenes and rendered with `-sw` and `-w -l` (exit 0; 14 s, 16.5 s, 14.5 s without narration), and the cuts between scenes were compared frame to frame. imcommit heuristics were recounted by AST.
- **Narration (`tools/tts.py`, `tools/voiceover.py`, `references/voiceover.md`)**: E2E on Windows 11. `tts.py` (SAPI, Microsoft Heami Desktop) synthesized 3 Korean lines (2.629/3.794/4.209 s); a rerun reused all 3 from the cache. 2 scenes rendered with `-sw` and `-w -l`; each mp4 has a 48 kHz mono AAC track as long as its video; the per-scene SRT cues are frame-aligned. Concat with `+faststart` gave `full.mp4` (video 10.667 s, audio 10.688 s, moov before mdat); the viewer printed VIDEO_READY and served `/subtitles.srt` with the right offsets; soft subtitles and burn-in were checked. In a 7-scene join, `-c copy` drifted speech onsets from 21 to 225 ms, while the audio re-encoding join (`references/voiceover.md` §2 step 6) kept them at 21.3 ms and the viewer accepted it. Edge cases: overrun and unvoiced-line warnings, the stale `narration.txt` warning, `-w -n` raising, a 0.5 s scene trimmed to 0.5 s of audio, the viewer refusing scenes with different stream layouts (exit 1). `edge-tts` was run with one fixed sample sentence only.
- **Gallery (`skills/manimgl-best-practices/gallery/`)**: 9 files ported; every scene rendered with `-sw` and `-w -l` (exit 0), the PNG and a frame sheet of each mp4 checked by eye, `lint_manimgl.py` 0 findings. The pitfalls found while porting are in `gallery/README.md`, each printed by a probe or seen in a render.
- **Checks** (Claude Code 2.1.302, this tree, 2026-10-17):
  - `lint_manimgl.py skills agents commands README.md README-ko.md`: self-test passes, 0 findings in 44 files. On adithya-s-k/manim_skill `skills/manimgl-best-practices` @cef0450 it reports 397 findings in 106 files.
  - `check_docs.py`: 14 docs, 797 snippets: 329 pass, 366 skipped with a reason, 102 `kwarg=value` mentions not run, 0 failures.
  - `check_citations.py`: 656 citations ok (63 of them have no identifier on their doc line to anchor, so only the file and lines were checked), 126 WEAK (read by hand when added), 1 untagged source path in a gallery docstring, 0 errors.
  - `check_inventory.py`: Scene 3, Animation 80, Mobject 149, no drift.
  - Hook: `claude -p --plugin-dir . --model haiku` wrote a file with `Text("hi", color=RED)` and `Create(t)`, and the model quoted both findings from the hook's additional context. A non-`.py` file, a `.py` without manimlib, garbage stdin and a PATH without Python all exit 0 with no output. About 0.2 s per call on Windows.
  - `check_examples.sh`: a scene that calls `input()` exits 1 instead of hanging. With `CHECK_TIMEOUT=8`, a 100 s sleep ended as `timeout 8s`, and the uv child process was gone afterwards.
  - `claude plugin validate --strict` passes with `hooks/hooks.json`. A malformed hooks.json fails it; an unknown key passes.
- **PyPI 1.7.2 comparison**: installed PyPI 1.7.2 and the fork in separate new venvs and compared `hasattr`, `--help`, sizes, and `--fps` parsing. PyPI 1.7.2's `manimlib/` is file-for-file identical to tag v1.7.2.
- **Upstream APIs missing from the fork (`references/fork-diff.md`)**: checked only by constructing and calling them in the fork env (no render).
  - `VideoSource`, `Keys`/`Mods`, `COMMON_UNIFORMS`, `uniform_block_dtype` do not exist. `get_resolution`, `set_sort_to_camera`, `set_joint_roundness` raise AttributeError.
  - `sort_to_camera=`, `joint_roundness=`, `stroke_width_in_scene_units=`, `textures=`, `texture_filter=`, `gradient_direction=`, `update(frame_rate=)`, `code_target=` raise TypeError.
  - The fork's `AnimationGroup(time_span=(1, 2))` ignores the span without an error and plays from 0 s (opacity 0.5 at t=0.5). Measured by following the fork scene's progress calculation as is.
- **Korean rendering**
  - Korean `Text` with sub-selection (`t["정밀도"]`) and `t2c`
  - Korean inside Tex: the default template fails, `ctex`/`basic_ctex` fail for lack of the SimHei font, `empty_ctex` + kotex succeeds
- **raenimgl**
  - Rendered Tex on MiKTeX with `from raenimgl import *` (with the fork's `--fontmap` dropped).
  - Fast-forward did not apply with `-w` (mp4 3.5 s).
  - The `StringMobject` patch always applies on the fork.
- **Viewer**
  - `/` 200, 4 chapters in `/chapters.json`, `/video.mp4` Range request → 206
  - Range edge cases (curl, byte comparison): an end past the file is clamped, 206; a start at or past the end gives 416 (`bytes */<size>`); end < start and `bytes=-N` get a full 200. Before the fix, a request with an end past the file made curl exit 18. Multiple ranges get only the first range.
  - In a real browser (Chrome), pressing `t` at 9.4 s put `[0:09] Quantize: ` into the note field. The chapter name in the control bar and the 4-segment progress bar were also checked.
  - The Code tab label is `main.py`, and Korean comments are not garbled.
  - With `BROWSER=true` it does not open a browser.
  - 0 brand strings
  - Startup checks: if an order entry is missing, an mp4 length cannot be read (0 bytes, truncated file), or full.mp4 was built from a different list, it does not start the server and exits 1. The message shows the missing path, the file, or the ffmpeg command to rebuild.
  - full.mp4 joined with `-c copy` from 4, 10 and 50 entries starts fine and chapter times are correct. The difference from the sum of scene lengths was at most 0.00065 s (0.024 s for 10 synthetic clips with AAC audio), so the tolerance was set to 0.1 s.
- **Whole workflow (agent E2E)**: two new agents, reading only the docs, took 2 topics (binary search, 3D dot product) from Plan through Iterate.
  - Both: 0 setup.sh warnings, 2 scenes each rendered (34.3 s, 29.5 s), viewer started and stopped, took one feedback line, and fixed and re-rendered only that scene.
  - Doc problems found along the way (color list, mid-scene checks, viewer restart, plan mode order, etc.) were fixed in this commit.
- **Doc audit**: agents checked about 450 doc claims against the source; other agents then tried to refute the resulting findings, and only those that survived were applied.
  - After the fixes, about 430 were re-checked the same way. 8 confirmed findings were fixed (dt updaters called twice under `-sw`, setup.sh's uv error handling, the viewer restart wording, etc.).
- **Plugin**
  - `claude plugin validate ./manimgl-skill --strict` exits 0 (Claude Code 2.1.301 at 0.1.0; 2.1.302 at 0.2.0 with `hooks/hooks.json`). A passing run prints only the marketplace.json line, but it also checks plugin.json and the frontmatter in skills/, agents/ and commands/, and prints only files with problems.
  - Checked by breaking copies one at a time. A plugin.json JSON error and a deleted SKILL.md `description` exit 1. A deleted agent `name` and a marketplace.json `source` pointing to a missing folder exit 0, so this command does not catch them.
  - It catches only some frontmatter YAML errors. When parsing fails, it wraps values containing special characters (`>`, `#`, colon+space, etc.) in quotes and parses once more, exiting 1 only if that also fails. So an unclosed quote in an LF file (`argument-hint: "<topic>`) exits 0, while a value without special characters, or a CRLF file, exits 1.
  - Install (at 0.1.0): `claude plugin marketplace add ./manimgl-skill` and `claude plugin install manimgl-skill@manimgl-skill` succeeded, and `claude plugin list` showed 0.1.0 enabled. Installing 0.2.0 was not repeated; the hook was loaded with `--plugin-dir`.
  - A new session (`claude -p`, at 0.1.0) recognized:
    - command `manimgl-skill:scene`
    - skills `manimgl-skill:manimgl-best-practices`, `manimgl-skill:manimgl-workflow`
    - agent `manimgl-skill:scene-reviewer`

## Not verified

- Running setup.sh on macOS and Linux. The Linux Pango check path was not run either. On these OSes, setup.sh says so in an `[info]` line.
- A TeX Live environment. Only MiKTeX was checked.
- How raenimgl's Tex patch behaves without cm-super.
- Korean Text, Tex (`working.tex` encoding), the viewer and raenimgl `PythonCode` on a non-UTF-8 Windows locale (cp949).
- The viewer's **Copy** button. It was not pressed because it overwrites the user's clipboard.
- `/plugin marketplace add getCurrentThread/manimgl-skill` from GitHub. Only the local-folder install was tried.
- Human Plan approval and feedback. In the E2E, agents wrote the feedback lines.
- The order of submitting scenes.md as the plan in plan mode and writing it to a file afterwards. Not tried in a real plan mode session.
- Making a whole video with the final 1920x1080 `-w` render. The E2E went only as far as `-w -l`. The example, gallery and smoke renders are 1080p PNGs and 480p mp4s.
- The new Plan fields (Hook, Aha moment, Next, Assumptions) and the capped question step were not run through an agent E2E.
- `--autoreload`, `embed.exception_mode` values, the InteractiveScene selection/grab keys (Ctrl+C/V/X, `g`/`h`/`v`/`z`), Esc, and reading `custom_config.yml` under cp949 (it is opened without `encoding=`).
- Narration: local TTS engines on macOS/Linux (none shipped; the network engines `edge` and `gemini` were not run there), team mode (`references/team-production.md` is a write-up of one multi-agent production; no clean-room re-run), installing the Windows Korean voice on a machine without it, voice quality by ear, `edge-tts` beyond one sentence, narration on a cp949 locale, `--subdivide` with narration.
- Rendering the adithya-s-k/manim_skill corpus on upstream. Whether each fork-diff.md row fails the same way upstream is judged from source only, and some cited lines differ (fork-diff.md, "Upstream/PyPI-era code that breaks on the fork").
- The checks on macOS and Linux. `check_examples.sh`, `check_docs.py` and the hook command were run only in Windows Git Bash.
- The hook under PowerShell (Claude Code on Windows without Git Bash), and with a Windows Store `python3` alias stub. This machine has a real `python3`; the command falls back to `python`.
- CI. There is none; every check ran by hand on one machine.

## Unconfirmed (judged from source only, not run)

- The behavior of raenimgl `PythonCode.exec()`.
- `-o` and `--finder` opening the result file, `-f`, `--always_on_top` (window only).
- The exit code of Ctrl-C during a render.
- `--fps` being fixed at 30 in window mode (no `-w`).
- The remaining items marked `source evidence` in the `references/` docs.
