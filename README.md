# manimgl-skill

**English** | [한국어](README-ko.md)

A Claude Code plugin that targets **only** the [CodingVillainKor/manimgl](https://github.com/CodingVillainKor/manimgl) fork. The fork is based on 3b1b/manim, with defaults adjusted for a Korean environment.

- Target commit: fork `455a4201669cd68ff5e522c7fcd1a7ac31aadff0` (2026-10-11)
- Not for PyPI `manimgl` or ManimCE (`manim`).
- Every rule is based on the fork source, actual usage patterns in manimgl-imcommit, and real render results. Evidence is cited as `file:line`.
- The skill documents (`SKILL.md`, `references/`, templates) are written in English. Korean sample strings in them are intentional.

## Contents

| Path | Contents |
|---|---|
| `skills/manimgl-best-practices/` | Writing rules (SKILL.md), evidence documents (`references/`), render-verified examples (`examples/*.py`) |
| `skills/manimgl-workflow/` | Plan → Code & Render → Iterate workflow, `templates/scenes.md`, local viewer `tools/` |
| `commands/scene.md` | `/manimgl-skill:scene <topic>` starts the workflow |
| `agents/scene-reviewer.md` | Agent that reviews rendered frames, read-only |
| `scripts/setup.sh` | Installs the fork, pinned to a commit, into a uv project and verifies it. If the project already has the fork at another commit, it warns and leaves the commit unchanged (it only adds a missing `trimesh`/`pywavefront`) |
| `scripts/check_examples.sh` | Renders every example with `-sw` and `-w -l` to verify them |

## Installation

After it is on GitHub:

```
/plugin marketplace add <user>/manimgl-skill
/plugin install manimgl-skill@manimgl-skill
```

From a local folder:

```
/plugin marketplace add ./manimgl-skill
/plugin install manimgl-skill@manimgl-skill
```

From the CLI: `claude plugin marketplace add ./manimgl-skill`, then `claude plugin install manimgl-skill@manimgl-skill`.

- Plugin commands are namespaced, so the command is **`/manimgl-skill:scene`**.
- The marketplace and the plugin are both named `manimgl-skill`.
- `owner`/`author` in `.claude-plugin/*.json` are placeholders (`manimgl-skill maintainers`), to be replaced on publishing.

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

## Sources and licenses

| Source | Commit | How it was used |
|---|---|---|
| [CodingVillainKor/manimgl](https://github.com/CodingVillainKor/manimgl) | `455a4201669cd68ff5e522c7fcd1a7ac31aadff0` | The target. Rules and evidence come from reading its source. setup.sh installs the code from git |
| [3b1b/manim](https://github.com/3b1b/manim) upstream | `fafa083a` | Compared against the fork |
| [CodingVillainKor/manimgl-imcommit](https://github.com/CodingVillainKor/manimgl-imcommit) | `a2fe49f4284082ce6c3627cd26e5952cd1d01bb6` | No LICENSE file, so **no code was copied.** Only patterns and usage counts are summarized (`references/imcommit-patterns.md`) |
| [CodingVillainKor/raenimgl](https://github.com/CodingVillainKor/raenimgl) | `177affc69311d13fcad3404b2599a7714de1d4f2` | No LICENSE file, so only its API and behavior are described. An optional dependency, installed from the original repo |
| [3b1b/videos](https://github.com/3b1b/videos) | `306a1346a356c7a7b097875ceb51c5cd67d0a56c` | `custom_config.yml` and usage examples were only compared with the fork. No code was copied |
| [Yusuke710/manim-skill](https://github.com/Yusuke710/manim-skill) | `a0048d9e265499038f34a9aa58ff16d306b5034c` | **MIT**, Copyright (c) 2025 Yusuke Miyashita. What was referenced is listed below |

Referenced from Yusuke710/manim-skill:
- The plugin layout (marketplace and plugin in one repo under `.claude-plugin`)
- The workflow structure and wording (step-by-step progress, the `[M:SS] Scene: note` feedback format, re-rendering only that scene)
- The viewer `skills/manimgl-workflow/tools/video_viewer.py`, `ui.html`
  - Copied from the original and modified. The changes are listed in `tools/README.md`.
  - The license text is in `tools/LICENSE-manim-skill`.

This plugin has no license file of its own yet. One will be added once the copyright holder is decided.

## Adjustments where the request differed from the facts

| Request / common belief | Verified fact | Applied as |
|---|---|---|
| Check the last frame with `-s` | In the fork, `-s` alone saves nothing and opens a window (`config.py:278-280`, window at `config.py:331`) | The workflow uses `-sw` → `videos/<Scene>.png` |
| `self.camera.frame` is a CE API, so ban it | It is valid in the fork too, and the same object as `self.frame` (`scene.py:112`) | Documented as "use `self.frame` (a style preference)" |
| Ban `Create` | Not in the fork, but raenimgl provides an alias | Fork alone: `ShowCreation`. The alias is noted in the raenimgl doc |
| imcommit patterns: Scene3D, PythonCode, MINT | imcommit actually uses them in 0, 1 and 0 files | Based on what it does use: `(InteractiveScene, Scene2D)` and camera tilts inside 2D scenes |
| `/scene` | The plugin command is `/manimgl-skill:scene` | Reflected in the README and the command file |
| `/plugin install manimgl-skill/manimgl-skill` | The documented form is `<plugin>@<marketplace>` | `/plugin install manimgl-skill@manimgl-skill` |

## Verified

Test environment:

| Item | Value |
|---|---|
| OS / shell | Windows 11 Pro, Git Bash |
| uv / Python | uv 0.13.0, Python 3.10.18 |
| ffmpeg | 2025-12-24 gyan build |
| LaTeX | MiKTeX 25.12 (XeTeX 4.16, dvisvgm 3.4.3) |
| GPU | NVIDIA RTX 4070 Ti (OpenGL 3.3) |
| Claude Code | 2.1.301 |
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
  - Result: 10 scenes × (`-sw`, `-w -l`) = 20/20 succeeded (`check_examples.sh`, in an env with raenimgl). The last run used this commit's examples as they are.
  - Every PNG was checked by eye for overlaps, clipping, tofu (□) and colors. The circle in `camera.py` came out green, and "손실" ("loss") in `korean.py` KoreanInTex came out yellow (kotex + xcolor + `t2c`).
  - Given a missing folder, `check_examples.sh` stops right away with exit 2.
- **Color pitfalls (probes)**
  - Constructor `color=` ignored: `Text`, `Tex`, `TexText`, `Dot`, `Brace` (white), `Arrow`, `Vector`, `StrokeArrow`, `Annulus` (grey #BBBBBB), `Circle`, `Ellipse` (red outline)
  - Honored: `Square`, `Rectangle`, `SurroundingRectangle`, `Line`, `DashedLine`, `Arc`, `Polygon`, `Triangle`, `RegularPolygon`, `CurvedArrow`, `NumberLine`
  - `.set_color()` works on all of the above.
- **Other pitfalls (probes)**
  - With only the fork installed, `import manimlib` fails with `No module named 'trimesh'`.
  - After `Scene.clear()`, `self.frame` is removed from the scene and ambient rotation stops; `self.add(self.frame)` brings it back.
  - The default run_time 2 of `TransformMatchingStrings`/`Tex`, the grey fill from `Square().set_opacity(0.2)`, the origin position of an asymmetric `ThreeDAxes`, `Arrow.set_perpendicular_to_camera`
  - Unknown config keys: `scene.invert_zoom_scroll`, `camera.bundle_draws`, `camera.draw_together`, `file_writer.crf` each fail with a TypeError in their section's constructor.
- **CLI (`references/cli-and-output.md`)**: verified by running: the output file and resolution/fps per flag (ffprobe), the hang with `-s`/`-ql`/`-a` alone, the hang with `-p -w` (checked with `timeout`), the scene-selection prompt and exit 1 on stdin EOF, a failed render leaving the previous mp4 in place, the config merge order, and cache locations. Rows marked `source evidence` in the tables were not run.
- **Korean, Tex, 3D (`references/korean-tex-3d.md`)**: verified by render or probe: Korean glyph counts and sub-selection, `MarkupText` ignoring color, the Text vs Tex size difference (1.37×) and its cause (the calibration font), `Tex`/`TexText`/`Title`/`BulletedList` with kotex, when xcolor is needed, the list of classes that need LaTeX (checked with TeX removed from PATH), the depth test pitfall, and the billboard formula.
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
  - `claude plugin validate ./manimgl-skill --strict` (Claude Code 2.1.301) exits 0. A passing run prints only the marketplace.json line, but it also checks plugin.json and the frontmatter in skills/, agents/ and commands/, and prints only files with problems.
  - Checked by breaking copies one at a time. A plugin.json JSON error and a deleted SKILL.md `description` exit 1. A deleted agent `name` and a marketplace.json `source` pointing to a missing folder exit 0, so this command does not catch them.
  - It catches only some frontmatter YAML errors. When parsing fails, it wraps values containing special characters (`>`, `#`, colon+space, etc.) in quotes and parses once more, exiting 1 only if that also fails. So an unclosed quote in an LF file (`argument-hint: "<topic>`) exits 0, while a value without special characters, or a CRLF file, exits 1.
  - Install: `claude plugin marketplace add ./manimgl-skill` and `claude plugin install manimgl-skill@manimgl-skill` succeeded, and `claude plugin list` shows 0.1.0 enabled.
  - A new session (`claude -p`) recognized:
    - command `manimgl-skill:scene`
    - skills `manimgl-skill:manimgl-best-practices`, `manimgl-skill:manimgl-workflow`
    - agent `manimgl-skill:scene-reviewer`

## Not verified

- Running setup.sh on macOS and Linux. The Linux Pango check path was not run either. On these OSes, setup.sh says so in an `[info]` line.
- A TeX Live environment. Only MiKTeX was checked.
- How raenimgl's Tex patch behaves without cm-super.
- Korean Text, Tex (`working.tex` encoding), the viewer and raenimgl `PythonCode` on a non-UTF-8 Windows locale (cp949).
- The viewer's **Copy** button. It was not pressed because it overwrites the user's clipboard.
- `/plugin marketplace add <user>/manimgl-skill` from GitHub. The repo has not been pushed yet.
- Human Plan approval and feedback. In the E2E, agents wrote the feedback lines.
- The order of submitting scenes.md as the plan in plan mode and writing it to a file afterwards. Not tried in a real plan mode session.
- Making a whole video with the final 1920x1080 `-w` render. The E2E went only as far as `-w -l`. The example and smoke renders are 1080p PNGs and 480p mp4s.

## Unconfirmed (judged from source only, not run)

- The behavior of raenimgl `PythonCode.exec()`.
- `-o` and `--finder` opening the result file, `-e LINE`, `-f`, `--always_on_top` (window only).
- The exit code of Ctrl-C during a render.
- `--fps` being fixed at 30 in window mode (no `-w`), and `dt` updaters getting the whole run_time at once under `-s`.
- `always_sort_to_camera` on translucent surfaces.
- The remaining items marked `source evidence` in the `references/` docs.
