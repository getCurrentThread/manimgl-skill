---
name: manimgl-best-practices
description: Rules for writing manimgl scenes against the CodingVillainKor/manimgl fork (a 3b1b/manim fork with Korean defaults). Use whenever writing, editing, reviewing or debugging `from manimlib import *` code or `manimgl` commands, and whenever ManimCE or generic-manimgl habits (Create, MathTex, `manim` command, MovingCameraScene, -ql/-p, Succession, constructor color=, module-level seeds) might leak in. Covers fork defaults, APIs the fork lacks, CLI/output/config, the embed shell, animation semantics and timing, color/stroke/Tex-selection pitfalls, Korean text, Tex, camera/3D orbits, seeds, the imcommit project conventions, render-verified examples and gallery, and a static lint.
---

# manimgl (CodingVillainKor fork) writing rules

Target: `CodingVillainKor/manimgl` @ `455a4201` (2026-10-11). It is a 3b1b/manim fork and differs from PyPI `manimgl` and ManimCE (`manim`).

Evidence notation:
- `F:` fork @455a420
- `U:` 3b1b/manim @fafa083
- `I:` manimgl-imcommit @a2fe49f
- `R:` raenimgl @177affc
- `[verified by run]`: confirmed by rendering this plugin's `examples/` or probes on Windows

## 0. Environment

- Install and verify with `bash ${CLAUDE_PLUGIN_ROOT}/scripts/setup.sh <project folder>`. It installs the fork into a uv project, pinned to a commit.
- The version string cannot tell you whether it is the fork. It is 1.7.2, the same as PyPI.
  - Instead, check `manim_config.key_bindings.yaw == "e"` (F:manimlib/default_config.yml:121).
  - Or check the URL and commit in `direct_url.json`. setup.sh checks both.
- `surface.py` imports `trimesh` and `pywavefront`, but they are not in `setup.cfg` install_requires (F:manimlib/mobject/types/surface.py:5-6, F:setup.cfg:31).
  - So with only the fork installed, `import manimlib` fails with `ModuleNotFoundError: No module named 'trimesh'` [verified by run].
  - Add both packages yourself (I:pyproject.toml).
- Always run with `uv run manimgl ...`. A global `manimgl` may be a different install.
- CLI flags and output paths are detailed in [references/cli-and-output.md](references/cli-and-output.md).

## 1. import

- Use only `from manimlib import *`. Do not use `from manim import *` (ManimCE).
- raenimgl is an optional dependency. Read [references/raenimgl.md](references/raenimgl.md) first when using it.

## 2. ManimCE habits → fork replacements

| Do not use (CE) | In the fork | Evidence |
|---|---|---|
| `Create` | `ShowCreation` | F:manimlib/animation/creation.py:48. The fork has no `Create`. Only raenimgl provides an alias (R:raenimgl/animation.py:310) |
| `MathTex` | `Tex` (math mode) | 0 hits for `MathTex` in the fork |
| CE `Tex` (body text) | `TexText` or `Text` | §8 |
| `manim f.py S -ql` | `manimgl f.py S -w -l` | F:manimlib/config.py:69,79. `-ql` is parsed as `-q` (quiet) + `-l` |
| `-p` (CE: preview) | do not use | In the fork, `-p` is presenter mode. It waits for a key press at every wait (F:manimlib/config.py:109, F:manimlib/scene/scene.py:607,624) |
| `MovingCameraScene`, `ZoomedScene` | `Scene` + `self.frame` | F:manimlib/scene/scene.py:112 |
| `self.camera.frame` | `self.frame` | `self.camera.frame` also works (same object, F:manimlib/scene/scene.py:112). But standardize on `self.frame`. imcommit uses the raenimgl alias `self.cf`, which is also the same object as `self.frame` (R:raenimgl/scene.py:146-147) |
| `set_camera_orientation`, `move_camera` | `self.frame.reorient(θ, φ, γ, center, height)`, `.animate.reorient(...)` (angles in degrees) | F:manimlib/camera/camera_frame.py:211 |
| `begin_ambient_camera_rotation` | `self.frame.add_ambient_rotation(10 * DEG)` (angle per second), then `self.frame.clear_updaters()`. If the next scene must inherit the end orientation, set it exactly with `self.play(self.frame.animate.reorient(θ, φ, 0), run_time=t)`. It turns the short way, so keep that last turn under 180° (§9) | F:manimlib/camera/camera_frame.py:251 <!-- snippet: t=1 --> |
| `add_fixed_in_frame_mobjects` | `mob.fix_in_frame()` | F:manimlib/mobject/mobject.py:1924 |
| `config.frame_width` | `FRAME_WIDTH` (≈14.22), `FRAME_HEIGHT` (8) | F:manimlib/constants.py:19-20 |
| `Axes.plot`, `get_area`, `add_coordinates` | `get_graph`, `get_area_under_graph`, `add_coordinate_labels` | F:manimlib/mobject/coordinate_systems.py:184,417,520 |
| `ParametricFunction` | `ParametricCurve(f, t_range=(a, b, step))` | F:manimlib/mobject/functions.py:17 |
| `Circumscribe` | `FlashAround` | F:manimlib/animation/indication.py:255 |
| `Wiggle` | `WiggleOutThenIn` | F:manimlib/animation/indication.py:355 |
| `Table`, `Paragraph`, `Unwrite`, `DoubleArrow`, `Dot3D`, `add_subcaption` | not in the fork | 0 grep hits (only `CurvedDoubleArrow` exists) |
| `ShowCreation(m, reverse=True)` | `Uncreate(m)` (also removes `m`) | TypeError [verified by run]. F:manimlib/animation/creation.py:56-71 <!-- snippet: skip the row starts with the failing call --> |
| `FadeIn(m, introducer=True)` | drop it. `play` adds any animated mobject that is not on screen | TypeError [verified by run]. F:manimlib/animation/animation.py:23-44, F:manimlib/scene/scene.py:551-553 <!-- snippet: skip the row starts with the failing call --> |
| `Rotating(m, radians=...)` | `Rotating(m, angle=TAU)` (5 s, linear by default) | TypeError [verified by run]. F:manimlib/animation/rotation.py:17-29 |
| `ScaleInPlace(m, f, about_point=p)` | `m.animate.scale(f, about_point=p)` | TypeError [verified by run]. F:manimlib/animation/transform.py:233-240 <!-- snippet: skip the row starts with the failing call --> |
| `arrange_in_grid(rows=, cols=)` | `arrange_in_grid(n_rows=, n_cols=)` or positional `(2, 3)` | TypeError [verified by run]. F:manimlib/mobject/mobject.py:538-550 |
| `Wait(t)` inside a group | `time_span=(start, end)` on the member (`rate_func=squish_rate_func(smooth, a, b)` with a matching `run_time` only for `lag_ratio=0` animations such as FadeIn or `.animate`: on `Write` or `ShowCreation` of text or a group it squishes each piece separately and starts early) | NameError [verified by run]. [references/animation-semantics.md](references/animation-semantics.md) §3 |
| `Star`, `SpinInFromNothing`, `ease_in_*`/`ease_out_*` | not in the fork, upstream or raenimgl | NameError [verified by run], 0 grep hits |
| `camera_class = ThreeDCamera` | `ThreeDScene`, or the class attribute `samples = 4` | Silently ignored: `Scene` always builds `Camera` (F:manimlib/scene/scene.py:107-111). `ThreeDCamera` only sets samples=4 (F:manimlib/camera/camera.py:258-261) [verified by run] |
| `GRAY`, `GRAY_A`...`GRAY_E`, `LIGHT_GRAY`, `DARK_GRAY`, `CYAN`, `MAGENTA`, `BROWN` | `GREY`, `GREY_A`...`GREY_E`, `TEAL`, `PINK`/`PURPLE`, `GREY_BROWN`/`DARK_BROWN`/`LIGHT_BROWN`, or a hex string such as `"#00FFFF"` | F:manimlib/constants.py:79-148. Only the GREY spelling exists; the others raise NameError [verified by run] |

To see which Scene/Animation/Mobject classes the fork has, check [references/api-inventory.md](references/api-inventory.md). It is a list generated from the installed fork.

Fork recipes for common concepts (projection with a right-angle mark, Riemann sums → area, tangent sweep, a matrix acting on a grid, tip-to-tail sums, highlights, number substitution) are in [../manimgl-workflow/references/visual-techniques.md](../manimgl-workflow/references/visual-techniques.md).

## 3. Not in the fork (present in upstream 3b1b/manim or 3b1b/videos)

The fork is 112 commits behind upstream. Do not use the following. Details are in [references/fork-diff.md](references/fork-diff.md).

- `VideoMobject`, `Sprite` (U:manimlib/mobject/types/video_mobject.py:258,398)
- fractals such as `MandelbrotFractal`, `NewtonFractal` (U:manimlib/mobject/fractals.py:64-284)
- `vmobject_to_svg` (U:manimlib/utils/svg_export.py:8)
- `Surface.set_sort_to_camera` (U:manimlib/mobject/types/surface.py:267)
- `VMobject.set_joint_roundness`, `set_fill(gradient_direction=)` (U:manimlib/mobject/types/vectorized_mobject.py:591,271)
- `Updater` class (U:manimlib/mobject/mobject.py:2247)
- The keywords `sort_to_camera=`, `joint_roundness=`, `stroke_width_in_scene_units=`, `textures=`, `texture_filter=`, `update(frame_rate=)` fail with TypeError [verified by run].
- `AnimationGroup(time_span=)` silently ignores the span and plays from 0 s [verified by run]. Pass `time_span=` directly to each animation. The rest, such as `VideoSource`, `Keys`/`Mods`, `LaggedStartMap(time_span=)`, `set_color_by_code` (the fork uses GLSL), are in fork-diff.md.
- Config keys `scene.invert_zoom_scroll`, `camera.bundle_draws`, `camera.draw_together`, `file_writer.crf`
  - If the fork receives an unknown config key, it fails with TypeError in that section's constructor [verified by run]. Examples: `TypeError: Scene.__init__() got an unexpected keyword argument 'invert_zoom_scroll'`, `Camera.__init__() got an unexpected keyword argument 'bundle_draws'`
  - So the `custom_config.yml` from 3b1b/videos cannot be used as is.
- Code from other manim versions also trips over fork signatures. Of the 183 scenes in adithya-s-k/manim_skill's manimgl examples, 155 pass `-sw` [verified by run]. Each error message with its cause and fix is in fork-diff.md "Upstream/PyPI-era code that breaks on the fork". The most common:
  - `NumberPlane`/`ComplexPlane(background_line_style=...)` replaces the default dict. Include `stroke_color`, or you get `KeyError: 'stroke_color'`. Or style `plane.background_lines` afterwards.
  - `DecimalMatrix([[0.5]], num_decimal_places=2, decimal_config=dict(include_sign=True))`. `num_decimal_places` inside `decimal_config` is a TypeError.
  - `axes.get_riemann_rectangles(graph, x_range=[a, b], dx=step, colors=[BLUE])`. There is no `color=`. A 3-element `x_range` fails as a tuple. A 3-element list is extended in place on every call (by the axis step without `dx=`, so `[1, 4, 0.5]` gives 7 instead of 6; by `dx` with it), so reusing the list adds rectangles each time (fork-diff.md).
  - `Surface(func, ...)` takes `func` as its color: use `ParametricSurface(func, u_range, v_range)`. `BarChart` has no `c2p`. Use `clip_to_box(box)`, not `set_clip_path`.
  - `GlowDot`, `Sphere` and `ImageMobject` cannot go in a `VGroup` (§9).
  - `t2c` keys must be whole TeX groups (`R"\frac{1}{3}"`, not `R"\frac"`). A lone `\left[` is a LaTeX error.
  - A texture URL is fetched with urllib's default User-Agent on every render, and Wikimedia answers 403. Download the file and pass a local path.

## 4. Render CLI and output

- Always give the exact scene name.
  - If there are several scenes and the name is missing or wrong, an `input()` prompt appears (F:manimlib/extract_scene.py:48,103-104).
  - In an interactive terminal it stops right there. In a shell with no stdin (an agent), it renders nothing and ends with exit 1 [verified by run].
- Check the last frame with `uv run manimgl main.py S -sw`. The result is `videos/S.png` (1920x1080) [verified by run].
  - With `-s` alone, nothing is saved and a window opens.
  - Reason: `save_last_frame = skip_animations and write_file` (F:manimlib/config.py:278-280), and the window opens when `-w` is absent (F:manimlib/config.py:331).
  - The PNG is **the last frame only**. For problems mid-animation and for the starting composition of scenes where the camera moves, extract frames from the mp4 and look at them (manimgl-workflow §2 step 3).
- Make the video with `-w`. The result is `videos/S.mp4`, 1920x1080 30fps by default (F:manimlib/default_config.yml:55,57).
  - Make drafts with `-w -l` (854x480) (F:manimlib/default_config.yml:101).
- Flags from generic manimgl docs often fail on the fork.
  - `-h` is argparse help: it renders nothing and exits **0**.
  - `--config key=value` is read as an abbreviation of `--config_file`, then silently ignored, exit 0 (F:manimlib/config.py:56,209) [verified by run].
  - Full list (`--resolution 1920,1080`, `-o out.mp4`, `--frame_rate` …): [references/cli-and-output.md](references/cli-and-output.md) §2.1.
- Output piles up flat **directly under `videos/` relative to the cwd you ran from** (F:manimlib/default_config.yml:23, F:manimlib/config.py:391-393). So run inside `src/<video>/`.
- Judge success by the **exit code**. If `construct()` raises, the exit code is 1 and `<Scene>_temp.mp4` is left behind, but the previous `<Scene>.mp4` stays as it was [verified by run]. A file existing does not mean success.
- `-a` does not turn on `-w`. For several scenes, list the names, as in `manimgl main.py A B C -w` [verified by run].
  - All listed scenes are built before any runs (F:manimlib/extract_scene.py:106-109), so they share one random stream. Seed inside `construct` (§11).
- Config merge order (F:manimlib/config.py:37-38):
  1. default yml
  2. `custom_config.yml` in the cwd
  3. `--config_file` (silently ignored if the path does not exist)
  4. CLI arguments
  5. the scene class attribute `default_camera_config`. It takes precedence over the CLI `-c` and `--fps` [verified by run]
  - Details are in [references/cli-and-output.md](references/cli-and-output.md) §5.
  - In `custom_config.yml`, section names from other guides (`camera_config`, `window_config`, `style`, `tex_config`) are silently ignored. `camera.resolution` must be a tuple string `(854, 480)`. A YAML list exits 1, but only in renders without a resolution flag, so `-w -l` drafts pass and the final `-w` fails [verified by run]. Test with `-sw`. Keys the fork reads: cli-and-output.md §5.1.
- `self.embed()` does nothing without a window (F:manimlib/scene/scene.py:208), so it is safe in `-w` renders.
  - In the preview window, leaving the shell ends the scene, so code after the first `self.embed()` runs only in `-w` renders [verified by run].
  - Without `-w` and with stdin at EOF (an agent shell), a scene that reaches `self.embed()` exits 0 at once and writes nothing [verified by run]. Check the result file's mtime.
  - Interactive use (checkpoint_paste, `-e`/`-se`, `reload()`, window keys, Shift+D): [references/interactive.md](references/interactive.md).
- If the Tex result looks wrong, re-render with `--clear-cache` (F:manimlib/config.py:222).

## 5. Fork defaults (different from upstream)

- Background `#000000` (yml:56)
- `default_stroke_width` 2.0 (yml:78)
- `text.font` "Noto Sans KR" (yml:91)

The upstream defaults are, in order, `#333333`, 4.0, Consolas.

- To change the background, call `self.set_background_color(GREY_E)` at the top of `construct` (F:manimlib/scene/scene.py:892), or set the class attribute `default_camera_config = dict(background_color=GREY_E)` [verified by run]. `BackgroundRectangle` still defaults to the yml #000000 ([references/style-and-color.md](references/style-and-color.md) §B).

## 6. Color pitfalls [verified by run]

**Rule: create the object, then give the color with `.set_color(X)`.** The constructor `color=` is ignored depending on the class. `.set_color()` works on all the classes below and matches the imcommit approach.

- Exception, backstroked text: `set_color` also sets the stroke, so an earlier `set_backstroke(BLACK, 5)` turns into a fat halo in the text color [verified by run]. Call `set_backstroke` after `set_color`/`t2c=`, and recolor later with `set_fill(X)` / `.animate.set_fill(X)` (F:manimlib/mobject/types/vectorized_mobject.py:204-210,287-295).

Classes where the constructor `color=` is ignored. This is because the constructor sets the fill/stroke colors directly, and VMobject picks them in the order `fill_color or color`, `stroke_color or color` (F:manimlib/mobject/types/vectorized_mobject.py:100-102).

| Class | Result of `color=BLUE` | Evidence |
|---|---|---|
| `Text`, `Tex`, `TexText`, `Brace` | white | StringMobject calls `set_fill(white default)` again at the end of construction (F:manimlib/mobject/svg/string_mobject.py:49,72) |
| `Dot` | white | F:manimlib/mobject/geometry.py:446 |
| `Arrow`, `Vector` | gray #BBBBBB | F:manimlib/mobject/geometry.py:1083,1085 |
| `StrokeArrow` | gray #BBBBBB | F:manimlib/mobject/geometry.py:945 |
| `Circle`, `Ellipse` | **red** outline | `stroke_color=RED` (F:manimlib/mobject/geometry.py:392) |
| `Annulus` | gray fill #BBBBBB | F:manimlib/mobject/geometry.py:636 |
| `Sector`, `AnnularSector` | gray fill #BBBBBB, no outline | F:manimlib/mobject/geometry.py:546 |
| `Cross` | red | F:manimlib/mobject/shape_matchers.py:103 |

- Where `color=` is applied as given: `Square`, `Rectangle`, `SurroundingRectangle`, `Line`, `DashedLine`, `Arc`, `Polygon`, `Triangle`, `RegularPolygon`, `CurvedArrow`, `NumberLine`, `axes.get_graph(color=)`, `ParametricCurve(color=)`.
- 3D surfaces (`Sphere`, `Torus`, `Cylinder`, `Disk3D`, `Square3D`, `Cube`) apply `color=` and `opacity=`. They are not VMobjects, so `fill_opacity=` raises TypeError (korean-tex-3d.md §C3) [verified by run].
- `fill_color=X` also works on `Text`, `Tex`, `Dot`, `Arrow`. But it cannot change a `Circle` outline, so `.set_color()` is safer.
- `Arrow`/`Vector` are filled shapes with `stroke_width=0`; the shaft width is `thickness=` (F:manimlib/mobject/geometry.py:1083-1086). `stroke_color=`/`stroke_width=` only add an outline around the gray fill [verified by run: fill #BBBBBB, stroke #58C4DD].
- Upstream has the same code.
- Measured on adithya-s-k/manim_skill's manimgl examples: 49 of the 155 scenes that render without error give an ignored constructor `color=` (131 calls). In 8 sampled last frames, 29 of 31 such objects came out in the wrong color [verified by run, references/fork-diff.md].
- imcommit usage counts (AST, excluding `main copy.py`):
  - `.set_color(` chained after `Text(...)`/`Tex(...)`: 376 times / 152 times
  - Constructor `color=`: only 10 times, on `Text`. All 10 are ignored in the fork.
- Color part of a string with `t2c={"loss": RED}` or `t["정밀도"].set_color(YELLOW)` (F:manimlib/mobject/svg/string_mobject.py:549,575).
- Color names: only the GREY spelling exists (`GREY_B`, not `GRAY_B`). `GRAY*`, `CYAN`, `MAGENTA`, `BROWN` raise NameError (F:manimlib/constants.py:79-148). A hex string such as `"#FF5733"` works anywhere a color is accepted [verified by run].
- For a box behind a label, make it a separate object: `VGroup(BackgroundRectangle(t, fill_opacity=0.8, buff=0.1), t)`. `t.add_background_rectangle()` makes the box `t[0]`, so `t["word"]` selects glyphs shifted by one and `t.set_color(YELLOW)` paints the box [verified by run].
- Stroke/backstroke, background boxes, glow (`VHighlight`), gradients, style-method names that do not exist (`set_fill_opacity`, `match_fill`, `set_stroke(background=)`) and GLSL `set_color_by_code` are in [references/style-and-color.md](references/style-and-color.md).

## 7. Korean text [verified by run]

- Write Korean with `Text`. The fork's default font is Noto Sans KR, so `font=` is not needed (yml:91).
  - Of imcommit's 90 Korean `Text` calls, only 1 gives `font=`, and it is `"Noto Sans KR"`, the same as the default (I:src/gen_model/main.py:30-32).
  - Give `font="Noto Serif KR"` only when you need a serif face (in imcommit, 13 times via raenimgl `Words`).
  - If the font is missing, setup.sh warns.
- Build Korean and math separately and join them: `VGroup(Text("손실"), Tex(R"= \sum_i ...")).arrange(RIGHT, buff=0.15)` (I:src/floatingpoint/main.py:1501). imcommit has never put Korean inside Tex (0 cases).
  - At the same `font_size`, a Noto Sans KR `Text` is about 1.37x larger than `Tex` [verified by run]. To match heights, give the Text a `font_size` of about 0.73x the Tex (Tex 40 ↔ Text 29).
- When Korean is really needed inside Tex:
  - The default template raises a LaTeX error. On this machine, `template="ctex"` also raised a fontspec error.
  - The method confirmed to work is `Tex(R"\text{손실} = ...", template="empty_ctex", additional_preamble=R"\usepackage{amsmath}\usepackage{xcolor}\usepackage{kotex}\setmainhangulfont{Noto Sans KR}")`. It needs xelatex and kotex. For an example, see [examples/korean.py](examples/korean.py).
  - Without `xcolor`, `t2c`, `isolate`, and `BulletedList` fail with `Undefined control sequence ... {{\color` [verified by run].
  - Always wrap Korean in math mode with `\text{}`. If you do not, only the Korean disappears, with no error [verified by run].
  - `BraceText`/`BraceLabel` cannot take `template=` (TypeError). Use `Brace(...).get_tex(..., template=...)` [verified by run].
- `Brace(mob, DOWN).get_text("한글")` makes a `Text`, so Korean works (F:manimlib/mobject/svg/brace.py:87).
- A selector matches every occurrence: in `t = Text("여자 − 남자 ≈ 여왕 − 왕")`, `t["왕"]` has 2 parts. Pick one with `t.select_part("왕", 1)` (F:manimlib/mobject/svg/string_mobject.py:554) [verified by run, gallery/word_vector_analogy.py].
- The Korean results in this document were confirmed only under the system UTF-8 locale (Windows ACP 65001).
- Details on Korean, Tex templates, and 3D are in [references/korean-tex-3d.md](references/korean-tex-3d.md).

## 8. Tex

- Write strings as raw strings `R"..."`. Use `Tex` for math and `TexText` for sentences.
- `Tex` already wraps its string in `align*` (F:manimlib/mobject/svg/tex_mobject.py:36). For multi-line equations, write `&` and `\\` directly: `Tex(R"f(x) &= x^2 + 2x + 1 \\ &= (x + 1)^2")` gives two lines aligned at `=`. Wrapping it in `\begin{align*}...\end{align*}` again fails with `LatexError: Argument of \align* has an extra }.` [verified by run].
- Select parts by string, but **list every substring you will later select, color or brace in `t2c=` or `isolate=`** when you create the Tex: `eq = Tex(R"\frac{a}{b} + c", isolate=["a", "c"])`, then `eq["a"]`. Keys must be whole TeX groups without `&`/`\\`, and a key (or separate string argument) that is, starts with, or ends with `+`/`-`/`=` loses that spacing: select operators by index or keep them strictly inside a key (`"a + b"`, not `"b ="`) ([references/style-and-color.md](references/style-and-color.md) §G1).
  - An unlisted substring is found by counting symbols in the source (F:manimlib/mobject/svg/string_mobject.py:542-547,563-573). The count is wrong inside a `\frac` numerator and around `\sum`/`\int` limits, and it also matches inside command names. The result is wrong glyphs with no warning: `Tex(R"\frac{a}{b} + c")["a"]` returns the fraction bar [verified by run].
  - `eq[0]` is always one glyph, also for `Tex(R"a^2", "+", R"b^2")`, but each argument is a key, so the lone `"+"` loses its spacing (`Tex(R"a^2", "+", R"b^2", "=", R"c^2")` is 2.008 wide, the single string 2.491 [verified by run]); prefer one string with `isolate=["a^2", "b^2"]`. Selectors match every occurrence and are matched literally, spaces included. Details are in [references/style-and-color.md](references/style-and-color.md) §G.
  - For a transformation that carries the same symbols over, use `TransformMatchingTex` (F:manimlib/animation/transform_matching_parts.py:189). For an example, see [examples/tex.py](examples/tex.py).
  - Pass the on-screen object, not a `.copy()`, and keep using the target afterwards. A `.copy()` source leaves the original on screen, so each step stacks [verified by run]. Which object survives each transform: [references/animation-semantics.md](references/animation-semantics.md) §1.
  - `TransformMatchingTex` pairs pieces by counting source symbols, like an unlisted selector (F:manimlib/animation/transform_matching_parts.py:151-180). Near `\frac` it can pair a letter with a fraction bar, so the letter morphs into the bar mid-transform; the end state is exact [verified by run]. `TransformMatchingShapes` pairs glyphs by shape instead (:101-110).
  - The default `run_time` of `TransformMatchingTex`/`TransformMatchingStrings` is **2** (F:manimlib/animation/transform_matching_parts.py:29). If you put it in the same play as another 1-second animation, the whole play becomes 2 seconds, so write `run_time` [verified by run].
- Labels and counters whose text changes:
  - If you switch two strings of different widths with `FadeTransform`, the whole line stretches and looks doubled for about 1 second.
  - If only part changes, pair up the changing parts, as in `TransformMatchingStrings(a, b, key_map={"16": "8"}, run_time=1)`.
    - Without key_map, the remaining glyphs are paired by matching shape, so the same digit may fly to a different position (F:manimlib/animation/transform_matching_parts.py:101).
  - When switching to an unrelated sentence, fade out and then in, as in `LaggedStart(FadeOut(a), FadeIn(b), lag_ratio=0.6)`.
  - These items were confirmed in E2E test renders.
- Things that need LaTeX: Tex/TexText, `Brace` (a Tex subclass, F:manimlib/mobject/svg/brace.py:32), Matrix brackets, `get_graph_label`, `get_axis_labels`.
- Things that do not need LaTeX: tick numbers `add_coordinate_labels`, `add_numbers`, real-number `DecimalNumber`/`Integer`.
  - Digit glyphs are made with `Text` (F:manimlib/mobject/numbers.py:24-30).
  - But text that contains a backslash, such as `unit=R"^\circ"`, and complex numbers (`i`) are made with `Tex`, so they need LaTeX (same lines).
- A fresh MiKTeX install has no cm-super.
  - Then dvisvgm makes an empty SVG and exits with 0, and manimgl fails with `SVG has no content to measure`.
  - Install it with `miktex packages install cm-super`, then re-render with `--clear-cache`. This is because the empty SVG stays in the cache [verified by run].

## 9. Camera and 3D

- 2D camera movement [verified by run, examples/camera.py]:
  1. `self.frame.save_state()`
  2. `self.play(self.frame.animate.move_to(x).set_height(h))`
  3. `self.play(Restore(self.frame))`
- Follow a moving object with `self.frame.add_updater(lambda m: m.move_to(dot))`, then `self.frame.clear_updaters()`. It keeps following during a `self.frame.animate.set_height(...)` in the same play (korean-tex-3d.md §C8) [verified by run].
- The imcommit way to tilt a 2D scene (I:src/bondinterest/main.py:129-150):
  - Tilt with `self.frame.animate.reorient(θ, φ, γ, center, height)`.
  - Labels and flat elements in the tilted area are `rotate(φ * DEG, axis=RIGHT)`-ed by the same φ so they face the camera.
  - This rotation is exact only when θ = 0. When θ is not 0, rotate at the origin with `label.rotate(φ, RIGHT).rotate(θ, OUT)` (when γ = 0) or `label.apply_matrix(self.frame.get_orientation().as_matrix())`, then `move_to` [verified by run].
- Write all three angles, `reorient(θ, φ, 0)`. Omitted angles keep the current values, roll included. Negative φ does not look from below: it is (θ + 180, |φ|) rolled 180°, so z points down on screen. For a y-up floor, call `self.set_floor_plane("xz")` first, then use negative φ to look down. There φ = -elevation, so the default view (-30, 70) becomes `reorient(-30, -20, 0)`, not (-30, -70, 0) (korean-tex-3d.md §C2) [verified by run].
- For real 3D, use `ThreeDScene` [verified by run, examples/three_d.py]. In a plain Scene, a surface added later covers axis lines even where they are in front of it (korean-tex-3d.md §C1) [verified by run].
  - The default orientation is (-30, 70), and depth test is turned on when you add (F:manimlib/scene/scene.py:946-953).
  - Use `fix_in_frame()` for a title that should stay fixed on screen.
  - Make a surface with `ThreeDAxes.get_graph(lambda x, y: ...)`.
  - Orbiting the camera [verified by run, examples/camera_orbit.py]:
    - `self.frame.animate` turns the short way round (F:manimlib/camera/camera_frame.py:121-130). `animate.increment_theta(360 * DEG)` does not move, and `270 * DEG` turns -90°. Use `.animate` only for turns under 180°. A large θ and φ change in one `.animate` also rolls the view mid-move, though both ends have γ = 0. Split it into a θ leg and a φ leg, or drive both with `UpdateFromAlphaFunc` and `set_euler_angles(..., gamma=0)` (korean-tex-3d.md §C8) [verified by run].
    - For a full turn, use `t0 = self.frame.get_theta()` and `self.play(UpdateFromAlphaFunc(self.frame, lambda m, a: m.set_theta(t0 + a * TAU)), run_time=8, rate_func=linear)`, or chain legs under 180°, or `add_ambient_rotation`.
    - Do not use `Rotate(self.frame, ...)`. The turn piles up every frame and the camera jumps around (F:manimlib/animation/rotation.py:42-55). Details are in [references/korean-tex-3d.md](references/korean-tex-3d.md) §C8.
  - **Depth test is turned on again on every add.** This also holds when `play` adds an object.
    - Text that has depth test is hidden when it overlaps a surface or filled shape drawn earlier on screen, even if it is closer to the camera than that shape [verified by run].
    - For objects that flicker from overlapping in the same plane, or that must always be visible (labels), call `mob.deactivate_depth_test()` **after** the animation that adds them ends.
    - Or add it with `self.add(mob, set_depth_test=False)` (F:manimlib/scene/scene.py:951-953).
    - `become()` also copies the depth test setting (F:manimlib/mobject/mobject.py:735).
    - A translucent surface (`Sphere(opacity=0.4)`) still writes depth. An object added **after** it that lies inside or behind it is not drawn at all. `self.add(surface, set_depth_test=False)` does not help. Add the inner objects first, then the surface, and call `surface.always_sort_to_camera(self.camera)`, or call `set_z_index(-1)` on the later object before it is added (`Scene.add` sorts by z_index only when adding, F:manimlib/scene/scene.py:336-338; set after the add it has no effect until the next add) (korean-tex-3d.md §C7) [verified by run].
  - `ThreeDAxes` centers its x and y ranges only. If they are asymmetric, the axes origin is not ORIGIN [verified by run].
    - Example: for x(-1,4), y(-2,3), `c2p(0,0,0)` is (-1.5, -0.5, 0).
    - z = 0 stays at world z = 0, so `z_range=(0, 7)` puts the whole graph above the frame center (F:manimlib/mobject/coordinate_systems.py:489,567) [verified by run].
    - Write all coordinates with `axes.c2p`, or align the origin with `axes.shift(-axes.c2p(0, 0, 0))`.
  - `Arrow` is a flat shape, so it renders thin in any tilted view that does not look along its normal, also a static one. Use `arrow.set_perpendicular_to_camera(self.frame)` (`Arrow` is a `Line` subclass, F:manimlib/mobject/geometry.py:798). While the camera is moving, attach it with an updater.
  - The x and y labels of `ThreeDAxes.add_axis_labels()` lie in the xy plane and only the z label stands up (F:manimlib/mobject/coordinate_systems.py:574-583). Rotate the labels that must be readable with the billboard method from the 2D tilt above.
  - The `-sw` PNG of a scene where the camera moves shows the composition after the move ends.
  - `VGroup` accepts only VMobjects. A surface, `GlowDot`/`DotCloud`/`TrueDot` or an image in a `VGroup` raises `Exception: Only VMobjects can be passed into VGroup` (F:manimlib/mobject/types/vectorized_mobject.py:1312-1316) [verified by run]. Use `Group(...)`.
- `Scene.clear()` empties `self.mobjects`, so `self.frame` is removed too (F:manimlib/scene/scene.py:117,400).
  - After that, frame updaters such as `add_ambient_rotation` stop [verified by run].
  - Doing `self.add(self.frame)` after `clear()` makes it spin again [verified by run].
  - `remove_all_except(...)` also calls `clear()` internally, so it has the same problem (F:manimlib/scene/scene.py:385-387).
  - To remove things, name the targets explicitly and use `FadeOut` or `remove`.
  - `self.mobjects` starts with `self.frame` (F:manimlib/scene/scene.py:117), so `FadeOut(m) for m in self.mobjects` removes the frame too, with the same effect as `clear()` [verified by run].
  - Clear the screen with `self.play(FadeOut(Group(*(m for m in self.mobjects if m is not self.frame and m is not getattr(self, "selection_highlight", None)))))` [verified by run, examples/compositions.py]. Excluding only the frame also removes an `InteractiveScene`'s `selection_highlight` (F:manimlib/scene/interactive_scene.py:133).

## 10. Updaters

- `dt` is detected by **name** (F:manimlib/mobject/mobject.py:834).
  - If a function parameter or local variable is named `dt`, pass `dt=` as a keyword.
  - Always name the second parameter of a time updater `dt` (`lambda m, dt: m.rotate(dt)`), and do not use a local variable named `dt` in other updaters.
- `add_updater` runs as soon as it is attached. It runs once even with `call=False` (F:manimlib/mobject/mobject.py:848).
  - On an object that already has updaters, using `call=True` (the default) runs the new updater twice and runs the existing updaters again (same file :845-848).
  - So write updaters so the result is the same even if they are called several times.
- In `-sw` (skip), `dt` updaters are called twice per `play`, with dt=run_time. The PNG of a scene with time updaters may differ from the video's end state, so check with the mp4 [verified by run, references/cli-and-output.md §7].
- `number.f_always.set_value(tracker.get_value)` (F:manimlib/mobject/mobject.py:186).
  - `f_always` calls every argument first, so each must be a zero-argument callable. `label.f_always.next_to(dot, UP)` fails on attach with `TypeError: 'Dot' object is not callable` [verified by run].
- `label.always.next_to(dot, UP)` re-runs the call with the same arguments every frame, so the label follows `dot` (F:manimlib/mobject/mobject.py:2339-2349) [verified by run]. Function form: `always(label.next_to, dot, UP)`. Details: [references/animation-semantics.md](references/animation-semantics.md) §5.
- `always_redraw` rebuilds the object every frame.
- Animations do not pause updaters: `suspend_mobject_updating=False` is the default (F:manimlib/animation/animation.py:43), and the start/target copies keep them (F:manimlib/mobject/mobject.py:692).
  - `ShowCreation` on an `always_redraw` object shows it whole from the first frame. `ShowCreation(m, suspend_mobject_updating=True)` draws it progressively, and the updater resumes afterwards [verified by run].
  - An updater that calls `become()` makes `FadeIn` pop in at full opacity, even with `suspend_mobject_updating=True`, because the start copy is made before the suspension (F:manimlib/animation/animation.py:72-75). Reset only points in the updater, or add it after the animation [verified by run].
- Call `clear_updaters()` when the animation ends. For an example, see [examples/updaters.py](examples/updaters.py).

## 11. Structure, layout, color, timing

A summary of imcommit conventions. Details and evidence are in [references/imcommit-patterns.md](references/imcommit-patterns.md).

- **Structure**
  - One video is one `src/<video>/main.py`.
  - Put several scene classes in narrative order (imcommit has 1 to 8 per file, median 4).
  - Each class rebuilds the previous scene's end state by itself.
  - Inside `construct`, split blocks with `## <short label or one line of narration>` comments.
  - 15 to 30 seconds per scene is this plugin's recommendation. It is not a value measured in imcommit.
- **Seeds**: make `random.seed(41); np.random.seed(41)` the first line of `construct` (`random` and `np` come with `from manimlib import *`). For an example, see [examples/structure.py](examples/structure.py).
  - `Scene.__init__` reseeds both RNGs with the class attribute `random_seed`, default 0 (F:manimlib/scene/scene.py:53,139-141). So a file-top `seed(41)`, as in the imcommit template (I:init_project.py:5-10), never reaches `construct`: module seeds 41 and 99 gave identical colors [verified by run].
  - A `random_seed = 41` class attribute holds only for a solo render. `manimgl main.py A B` builds every scene before the first runs (F:manimlib/extract_scene.py:106-109), so the next scene's `__init__` reseeds the stream. `examples/structure.py` `Intro` gave different colors alone and batched with `random_seed = 41`, and identical ones with the seed in `construct` [verified by run, references/cli-and-output.md §7].
- **Layout**
  - Use `next_to` and `arrange`, with buff mostly 0.1, 0.2, 0.5.
  - Split regions on a wide canvas and move the camera.
- **Color**
  - Almost only named constants. imcommit has 0 hex literals, and the only others are colors computed with `interpolate_color`/`random_color`.
  - Usage: `GREY_B` is secondary, `GREEN` is correct, `RED` is wrong, `YELLOW` is emphasis.
  - To dim, use `set_opacity(0.2~0.3)`, or lay a semi-transparent overlay, raise what should stay with `set_z_index`, and `add` it again.
    - `set_opacity` also changes fill opacity. On an outline-only shape (`Square()` etc., fill opacity 0), it creates a gray (#888888) background at fill 0.2 [verified by run].
    - To dim only the outline, use `set_stroke(opacity=0.2)`.
- **Timing** (details and evidence: [references/animation-semantics.md](references/animation-semantics.md) §2-5)
  - Use `run_time=0.5` for short actions (most common in imcommit).
  - Use `lag_ratio` of 0.3 to 0.5, and the default rate_func.
  - Within one `self.play`, give an object only one `.animate`.
    - If you give `.animate` separately to a parent VGroup and its children, both build their targets from the pre-play state, and the later one overwrites the earlier change (reproduced in E2E tests).
    - Chain the methods in one `.animate` (`mob.animate.set_stroke(...).set_opacity(...)`) or split the play.
    - To treat just one differently, give `.animate` to the sibling group without it (`VGroup(*(w for w in group if w is not focus))`) ([examples/structure.py](examples/structure.py)).
    - Two `.animate` on the same mobject both go to the last target, inside `AnimationGroup`/`LaggedStart`/`Succession` too; a `MoveToTarget` built earlier keeps its own target, so list order decides [verified by run]. Use separate plays.
  - Sequences: separate plays. `LaggedStart(..., lag_ratio=1)` only for independent mobjects (not the same one, not a group and its member, no target computed from an earlier member's result): a later member on the same mobject resets it to its start every frame until its turn, so the first step never shows, and every member is built before the first one runs [verified by run]. Avoid `Succession` across different mobjects: it shows later members early and splits time equally [verified by run]. With 3+ members, `-sw` skips the middle ones, so check a Succession in the mp4 [verified by run].
  - `rate_func=` on `AnimationGroup`/`LaggedStart`/`Succession`, or on any group at play level, is ignored (`LaggedStartMap` and `TransformMatching*` forward a constructor `rate_func=` to each member), and play-level `lag_ratio=` does not stagger animations. Put `rate_func` on each member, stagger with `LaggedStart`, and pass `lag_ratio=0` to the constructor (play-level 0 is dropped).
  - To delay one member inside a play, give it `time_span=(start, end)`. There is no `Wait` animation.
  - Defaults above 1 s: `Write` with 15+ glyphs (2 s, linear), `DrawBorderThenFill`, `TransformMatching*`, `LaggedStartMap` (2 s), `ApplyPointwiseFunction`/`ApplyMatrix`/`Homotopy`/`ApplyWave`/`Broadcast` (3 s; `ApplyWave` ignores a constructor `run_time=`, so pass it to `play`; `ApplyFunction` and `ApplyComplexFunction` are 1 s), `Rotating` (5 s, linear). The longest animation sets the play's length.
  - Rotations of 90° or more: `Rotate(mob, θ, axis=RIGHT)` or `mob.animate(path_arc=θ, path_arc_axis=RIGHT).rotate(θ, axis=RIGHT)`. The arc axis must match the rotation axis ([references/animation-semantics.md](references/animation-semantics.md) §2). Plain `.animate.rotate(PI)` collapses to a point mid-way [verified by run]. `Rotate`/`Rotating` (and `UpdateFromAlphaFunc`, `ChangeDecimalToValue`) do not hold when the play runs longer than they do: they keep going past their run_time and snap back at the end. Only the mp4 shows this, not the `-sw` PNG. Pass the play's run_time (`self.play(Rotate(m, PI), Write(t), run_time=2)`), or `time_span=(0, 1)`, or play the rotation on its own ([references/animation-semantics.md](references/animation-semantics.md) §3 Timings) [verified by run].
  - `FadeIn(m, scale=s)` starts at 1/s size, so `scale=0.5` shrinks in from double size.

## 12. Examples (all render-verified with `-sw` and `-w -l`)

You can re-verify with `bash ${CLAUDE_PLUGIN_ROOT}/scripts/check_examples.sh <uv project>`. It also renders `gallery/`.

- Static check, no GPU: `python ${CLAUDE_PLUGIN_ROOT}/scripts/lint_manimgl.py <file or folder>` flags §2/§3 APIs, CLI habits, constructor `color=` on the §6 classes, color names the fork lacks (`GRAY`, `CYAN`, ...), seeds that `Scene.__init__` overrides, `Succession` and `.copy()` derivation chains. The plugin hook runs it after each Write/Edit of a `.py` that imports manimlib and shows you the findings (warn-only). End a line with `# lint: ok` when the flagged code is intended.
- Doc snippets: `python ${CLAUDE_PLUGIN_ROOT}/scripts/check_docs.py <uv project>` runs the code in SKILL.md and `references/` in one `-sw` render and asserts the documented results.

| File | What it shows |
|---|---|
| [examples/structure.py](examples/structure.py) | Several scenes in one file, `##` blocks, seed inside `construct`, emphasis and dimming, overlay + z_index, `set_color` |
| [examples/compositions.py](examples/compositions.py) | Equation chain without `.copy()`, Transform vs ReplacementTransform, LaggedStart(lag_ratio=1) vs Succession, LaggedStart wave, per-member `time_span`, clearing the screen without the frame, `generate_target`/`MoveToTarget`, `Rotate` |
| [examples/korean.py](examples/korean.py) | Korean Text, partial color, Text+Tex side by side, Korean inside Tex via kotex |
| [examples/tex.py](examples/tex.py) | t2c, `isolate=` for every substring selected later, multi-line `&`/`\\`, TransformMatchingTex, Brace+Korean |
| [examples/camera.py](examples/camera.py) | `self.frame` move/restore, tilting a 2D scene + label rotation |
| [examples/three_d.py](examples/three_d.py) | ThreeDScene, surface, `fix_in_frame`, ambient rotation |
| [examples/camera_orbit.py](examples/camera_orbit.py) | Full camera orbits without the short-path trap: legs under 180°, `UpdateFromAlphaFunc` + `set_theta`, ambient rotation, settling with `reorient(θ, φ, 0)`, and a combined θ and φ move without roll via `set_euler_angles(..., gamma=0)` |
| [examples/updaters.py](examples/updaters.py) | ValueTracker, `dt` updater, `f_always`, `always_redraw`, `Dot(fill_color=)` |
| [examples/graphs.py](examples/graphs.py) | Axes, `get_graph`, graph labels, area, ParametricCurve |
| [examples/raenimgl_optional.py](examples/raenimgl_optional.py) | When using raenimgl: `(InteractiveScene, Scene2D)`, `playw` |

Larger ported scenes for ML and math topics (vector fields, attention mask, matrix product, MLP, token sampling, gradient descent, derivations, word vectors, e^t) and the pitfalls found while porting them: [gallery/README.md](gallery/README.md). The gallery code is CC BY-NC-SA 4.0 (NonCommercial, ShareAlike). That license covers `gallery/` only.
