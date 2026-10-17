# imcommit conventions (pattern summary)

## Source and scope

- Source: `CodingVillainKor/manimgl-imcommit` @ `a2fe49f4284082ce6c3627cd26e5952cd1d01bb6`
- This repository has no LICENSE file. So no code is copied; only patterns and numbers are recorded.
- Scope: 30 video folders. There are 35 `.py` files under `src/`.
  - 30 `main.py` files (one per video), 1 copy `src/curseofknowledge/main copy.py`, 4 helper scripts (`src/CLIP/prepare_images.py`, `src/dunder_all/import.py`, `src/dunder_all/piui.py`, `src/turboquant2/example.py`).
  - Numbers were counted over the 34 files excluding the copy. There are 125 scene classes.
- Method: counted with Python `ast`. Calls spanning multiple lines are counted too.
  - `buff=`, `run_time=`, `lag_ratio=` count only when a numeric literal is passed to a keyword argument of that exact name (`h_buff` etc. excluded).
  - A chained `.set_color` is one whose call chain is rooted at that constructor, like `Text(...).next_to(...).set_color(...)`.
  - Paths are relative to the repository root.

## Project structure

- **Root `pyproject.toml`**
  - `requires-python ==3.10.18`
  - Dependencies: `manimgl` (fork git, no rev pin), `raenimgl` (git), `trimesh`, `pywavefront`, etc. Declared in `[tool.uv.sources]`.
  - This plugin's setup.sh installs the manimgl fork (+ trimesh, pywavefront, and raenimgl with `--with-raenimgl`) **pinned to a commit**. It does not replicate the imcommit setup exactly.
    - Python is 3.10, and matplotlib and torchvision are not included.
    - A pyproject that already points at the fork without a rev is not modified; setup.sh only warns.
- **`init_project.py --name <video>`**: creates `src/<video>/main.py`.
  - The template is one scene: three import lines (`manimlib`, `raenimgl`, `random.seed`), a fixed seed, `self.embed()`, then one `##` block (init_project.py:4-17).
  - `uv init_project.py` in the README is a typo; what actually works is `uv run init_project.py --name <video>`.
- **Run**: `cd src/<video>; uv run manimgl main.py [scene]` (README.md). Output accumulates in `src/<video>/videos/`.
- **`_mhelper.py` (20 lines)**: a tool that runs inside the IPython embed.
  - Copies everything from the file's last `##` line to the end to the clipboard (pyperclip).
  - Then calls `checkpoint_paste()` (_mhelper.py:16-20).
- **`_mupdater.py` (79 lines)**:
  - Removes `self.embed()` from every `construct` in the file, and inserts a single `self.embed()` right before the last `##` line in the whole file (_mupdater.py:55-70).
  - The target file is taken as a command-line argument (:77-79).
  - Meant to be run on the current file as a VS Code task (`mupdate` in src/floatingpoint/.vscode/tasks.json).
- This interactive flow (embed, checkpoint) is for windowed preview only.
  - In a `-w` render, `self.embed()` does nothing (fork manimlib/scene/scene.py:208).
  - This plugin's workflow uses the `-sw` last-frame check instead of the interactive flow.

## Scene structure

- One video is one `main.py`.
  - 1 to 8 classes per file, median 4. Distribution: 1 class in 4 files, 2 in 4, 3 in 5, 4 in 4, 5 in 3, 6 in 5, 7 in 3, 8 in 2.
  - Classes are placed top to bottom in narrative order.
- **All 125 classes** inherit from `(InteractiveScene, Scene2D)` (raenimgl).
  - `Scene3D`, `ThreeDScene`, `MINT` used: 0 files
  - `PythonCode` used: 1 file
- Each class renders independently. If the last state of the previous class is needed, rebuild it inside that class.
- Inside `construct`, blocks are separated by `## <short label or one line of narration>` comments (e.g. src/bondinterest/main.py:12,31,45).
  - There are 1111 `##` lines. Most are implementation notes (`## nl`, `## lines`, `## intro`); only some are narration sentences.
- File header: `from manimlib import *`, `from raenimgl import *`, `from random import seed`, `seed(41)`, `np.random.seed(41)` (init_project.py:5-10).
  - These module-level seeds are no-ops for the scenes. `Scene.__init__` reseeds both RNGs with the class attribute `random_seed`, default 0 (F:manimlib/scene/scene.py:53,139-141), and raenimgl does not override it [verified by run].
  - So a solo imcommit render runs with seed 0, and in a batch each later scene continues the previous scene's random stream. To pick a seed that also holds when several scenes are rendered in one command, make `random.seed(41); np.random.seed(41)` the first line of `construct`. A `random_seed = 41` class attribute holds only for a solo render ([cli-and-output.md](cli-and-output.md) §7) [verified by run].

## Playback wrappers (raenimgl)

- `playw`: play, then wait(1)
- `playwl`: LaggedStart version
- `addw`: add, then wait
- `self.cf` is `self.frame`.
- Usage examples: src/bondinterest/main.py:91 (`playwl`), :308 (`addw`), :127 (`self.cf.save_state`)
- To get the same effect without the wrappers, use `self.play(...)` followed by `self.wait()`.

## Layout

- Placement uses `next_to`, `arrange`, `align_to`.
- `buff=` usage frequency (top 5):
  - 0.1: 378 times
  - 0.2: 222 times
  - 0.5: 206 times
  - 0.05: 93 times
  - 0.15: 90 times
- Not everything is squeezed onto one screen. Areas are laid out on a wide canvas and the camera (`self.cf`/`self.frame`) is moved.
- `reorient(` appears in 17 files.
  - 16 of them tilt a 2D scene with φ ≠ 0 (e.g. src/bondinterest/main.py:129, src/CFMvsDiffusion/main.py:341).
  - `reorient(0, 0, 0, center, height)` is also used to pan and zoom without tilting (src/CFMvsDiffusion/main.py:323).
  - Text and flat elements (vertical lines, ticks) in a tilted region are rotated about `axis=RIGHT` by the same angle as the camera φ so they face the camera (text src/bondinterest/main.py:132, vertical line :140, ticks :150).

## Color

- Colors are almost always given as named constants. Hex literals: 0 times.
  - Otherwise there are only computed colors: `interpolate_color` 52 times, `random_color()` 29 times.
- Frequency (named constants, top 13):

| Constant | Count | Used for |
|---|---|---|
| `GREY_B` | 270 | secondary explanation |
| `RED` | 255 | wrong answer, problem |
| `GREEN` | 227 | correct answer, result |
| `BLUE` | 154 | |
| `YELLOW_B` | 86 | |
| `GREY_C` | 86 | |
| `RED_B` | 78 | |
| `YELLOW` | 77 | emphasis |
| `BLACK` | 72 | |
| `GREY_A` | 69 | |
| `WHITE` | 69 | |
| `ORANGE` | 57 | |
| `PURE_RED` | 44 | |

- Usage evidence: src/CLIP/main.py:409-411,484 (wrong answer RED, correct answer GREEN), src/justgrpo/main.py:738-741.
- `Text`/`Tex` color is given after creation via chained `.set_color(…)`: `Text` 376 times, `Tex` 152 times (raenimgl `Words` 64 times).
  - Constructor `color=` appears only 10 times, all on `Text`.
  - In the fork, `color=` on `Text`/`Tex` is ignored (SKILL.md §6).
- There are two ways to dim.
  - `set_opacity(0.2)` (e.g. src/bondinterest/main.py:500)
  - Lay down a translucent overlay (raenimgl `self.overlay`), raise what should stay visible with `set_z_index(overlay + 1)`, and `add` it again (src/bondinterest/main.py:122-150)

## Timing

- `run_time` (top 5):
  - 0.5: 179 times (most common)
  - 0.7: 58 times
  - 0.75: 41 times
  - 3: 25 times
  - 1.5: 21 times
- `lag_ratio` (top 5):
  - 0.5: 57 times
  - 0.3: 24 times
  - 0.2: 15 times
  - 0.1: 12 times
  - 0.7: 10 times
- `rate_func` is mostly the default (smooth).
- Waiting is mostly the default wait(1) in `playw`.

## Targets

- `generate_target()` is called 92 times and `MoveToTarget` 83 times, in 18 files (AST count of calls by that name).
- Typical uses:
  - Arrange several targets and a new object together, then move them in one play (src/bondinterest/main.py:546-565).
  - Chain `generate_target().arrange(...).move_to(...)` on a group (src/CFMvsDiffusion/main.py:162-165).
  - Edit `target[i]` in a loop (src/CFMvsDiffusion/main.py:350-353).
- Semantics and the failure mode without `generate_target()`: [animation-semantics.md](animation-semantics.md) §2.

## Korean text

- Korean `Text` appears 90 times, and only 1 of them sets `font=` (src/gen_model/main.py:30-32, `"Noto Sans KR"`, same as the default). In practice the fork's default font is used as is.
- Korean narration is also written with raenimgl `Words` (a `Text` subclass).
  - 14 of the 41 Korean `Words` set `font=`. 13 use `"Noto Serif KR"` and 1 uses `"Noto Sans KR"` (e.g. src/bondinterest/main.py:85-87).
- Korean inside Tex/TexText: 0 times. `TexText` is not used at all (0 files).
- When Korean and math are used together, they are placed side by side with `VGroup(Text(…), Tex(…)).arrange(RIGHT)` (src/floatingpoint/main.py:1501,1603).
- To select part of a Tex, glyph index slices are used.
  - The fork's string selectors (`tex["..."]`, `t2c`) also work [verified by run, examples/tex.py].

## Recounting

The numbers must match an AST tally under the conditions below. No script is included in the plugin.

- Scope: `src/**/*.py` excluding `main copy.py`
- Classes: module top-level `ClassDef`
- Korean `Text`: the first positional argument is a string constant (or the constant part of an f-string) and contains `[가-힣]`
- Color constants: `ast.Name` matching the manimlib color name pattern (`GREY_B`, `RED`, `PURE_RED`, etc.)
