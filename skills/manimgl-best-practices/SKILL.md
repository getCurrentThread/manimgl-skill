---
name: manimgl-best-practices
description: Rules for writing manimgl scenes against the CodingVillainKor/manimgl fork (a 3b1b/manim fork with Korean defaults). Use whenever writing, editing, reviewing or debugging `from manimlib import *` code or `manimgl` commands, and whenever ManimCE habits (Create, MathTex, `manim` command, MovingCameraScene, -ql/-p) might leak in. Covers fork defaults, APIs the fork lacks, CLI/output paths, color pitfalls, Korean text, Tex, camera/3D and the imcommit project conventions.
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
| `begin_ambient_camera_rotation` | `self.frame.add_ambient_rotation(10 * DEG)` (angle per second), then `self.frame.clear_updaters()`. If the next scene must inherit the end orientation, set it exactly with `self.play(self.frame.animate.reorient(θ, φ), run_time=t)` | F:manimlib/camera/camera_frame.py:251 |
| `add_fixed_in_frame_mobjects` | `mob.fix_in_frame()` | F:manimlib/mobject/mobject.py:1924 |
| `config.frame_width` | `FRAME_WIDTH` (≈14.22), `FRAME_HEIGHT` (8) | F:manimlib/constants.py:19-20 |
| `Axes.plot`, `get_area`, `add_coordinates` | `get_graph`, `get_area_under_graph`, `add_coordinate_labels` | F:manimlib/mobject/coordinate_systems.py:184,417,520 |
| `ParametricFunction` | `ParametricCurve(f, t_range=(a, b, step))` | F:manimlib/mobject/functions.py:17 |
| `Circumscribe` | `FlashAround` | F:manimlib/animation/indication.py:255 |
| `Wiggle` | `WiggleOutThenIn` | F:manimlib/animation/indication.py:355 |
| `Table`, `Paragraph`, `Unwrite`, `DoubleArrow`, `Dot3D`, `add_subcaption` | not in the fork | 0 grep hits (only `CurvedDoubleArrow` exists) |

To see which Scene/Animation/Mobject classes the fork has, check [references/api-inventory.md](references/api-inventory.md). It is a list generated from the installed fork.

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

## 4. Render CLI and output

- Always give the exact scene name.
  - If there are several scenes and the name is missing or wrong, an `input()` prompt appears (F:manimlib/extract_scene.py:48,103-104).
  - In an interactive terminal it stops right there. In a shell with no stdin (an agent), it renders nothing and ends with exit 1 [verified by run].
- Check the last frame with `uv run manimgl main.py S -sw`. The result is `videos/S.png` (1920x1080) [verified by run].
  - With `-s` alone, nothing is saved and a window opens.
  - Reason: `save_last_frame = skip_animations and write_file` (F:manimlib/config.py:278-280), and the window opens when `-w` is absent (F:manimlib/config.py:331).
  - The PNG is **the last frame only**. For problems mid-animation and for the starting composition of scenes where the camera moves, extract frames from the mp4 and look at them (manimgl-workflow step 2).
- Make the video with `-w`. The result is `videos/S.mp4`, 1920x1080 30fps by default (F:manimlib/default_config.yml:55,57).
  - Make drafts with `-w -l` (854x480) (F:manimlib/default_config.yml:101).
- Output piles up flat **directly under `videos/` relative to the cwd you ran from** (F:manimlib/default_config.yml:23, F:manimlib/config.py:391-393). So run inside `src/<video>/`.
- Judge success by the **exit code**. If `construct()` raises, the exit code is 1 and `<Scene>_temp.mp4` is left behind, but the previous `<Scene>.mp4` stays as it was [verified by run]. A file existing does not mean success.
- `-a` does not turn on `-w`. For several scenes, list the names, as in `manimgl main.py A B C -w` [verified by run].
- Config merge order (F:manimlib/config.py:37-38):
  1. default yml
  2. `custom_config.yml` in the cwd
  3. `--config_file` (silently ignored if the path does not exist)
  4. CLI arguments
  5. the scene class attribute `default_camera_config`. It takes precedence over the CLI `-c` and `--fps` [verified by run]
  - Details are in [references/cli-and-output.md](references/cli-and-output.md) §5.
- `self.embed()` does nothing when there is no window (F:manimlib/scene/scene.py:208). So it is fine to leave it in for `-w` renders.
- If the Tex result looks wrong, re-render with `--clear-cache` (F:manimlib/config.py:222).

## 5. Fork defaults (different from upstream)

- Background `#000000` (yml:56)
- `default_stroke_width` 2.0 (yml:78)
- `text.font` "Noto Sans KR" (yml:91)

The upstream defaults are, in order, `#333333`, 4.0, Consolas.

## 6. Color pitfalls [verified by run]

**Rule: create the object, then give the color with `.set_color(X)`.** The constructor `color=` is ignored depending on the class. `.set_color()` works on all the classes below and matches the imcommit approach.

Classes where the constructor `color=` is ignored. This is because the constructor sets the fill/stroke colors directly, and VMobject picks them in the order `fill_color or color`, `stroke_color or color` (F:manimlib/mobject/types/vectorized_mobject.py:100-102).

| Class | Result of `color=BLUE` | Evidence |
|---|---|---|
| `Text`, `Tex`, `TexText`, `Brace` | white | StringMobject calls `set_fill(white default)` again at the end of construction (F:manimlib/mobject/svg/string_mobject.py:49,72) |
| `Dot` | white | F:manimlib/mobject/geometry.py:446 |
| `Arrow`, `Vector` | gray #BBBBBB | F:manimlib/mobject/geometry.py:1083,1085 |
| `StrokeArrow` | gray #BBBBBB | F:manimlib/mobject/geometry.py:945 |
| `Circle`, `Ellipse` | **red** outline | `stroke_color=RED` (F:manimlib/mobject/geometry.py:392) |
| `Annulus` | gray fill #BBBBBB | F:manimlib/mobject/geometry.py:636 |

- Where `color=` is applied as given: `Square`, `Rectangle`, `SurroundingRectangle`, `Line`, `DashedLine`, `Arc`, `Polygon`, `Triangle`, `RegularPolygon`, `CurvedArrow`, `NumberLine`, `axes.get_graph(color=)`, `ParametricCurve(color=)`.
- `fill_color=X` also works on `Text`, `Tex`, `Dot`, `Arrow`. But it cannot change a `Circle` outline, so `.set_color()` is safer.
- Upstream has the same code.
- imcommit usage counts (AST, excluding `main copy.py`):
  - `.set_color(` chained after `Text(...)`/`Tex(...)`: 376 times / 152 times
  - Constructor `color=`: only 10 times, on `Text`. All 10 are ignored in the fork.
- Color part of a string with `t2c={"loss": RED}` or `t["정밀도"].set_color(YELLOW)` (F:manimlib/mobject/svg/string_mobject.py:549,575).

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
- `Brace.get_text("한글")` makes a `Text`, so Korean works (F:manimlib/mobject/svg/brace.py:87).
- The Korean results in this document were confirmed only under the system UTF-8 locale (Windows ACP 65001).
- Details on Korean, Tex templates, and 3D are in [references/korean-tex-3d.md](references/korean-tex-3d.md).

## 8. Tex

- Write strings as raw strings `R"..."`. Use `Tex` for math and `TexText` for sentences.
- Select parts by string: `eq["m"]`, `eq["(p c)^2"]`, `t2c={"m": BLUE}`.
  - For a transformation that carries the same symbols over, use `TransformMatchingTex` (F:manimlib/animation/transform_matching_parts.py:189). For an example, see [examples/tex.py](examples/tex.py).
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
- The imcommit way to tilt a 2D scene (I:src/bondinterest/main.py:129-150):
  - Tilt with `self.frame.animate.reorient(θ, φ, γ, center, height)`.
  - Labels and flat elements in the tilted area are `rotate(φ * DEG, axis=RIGHT)`-ed by the same φ so they face the camera.
  - This rotation is exact only when θ = 0. When θ is not 0, rotate at the origin with `label.rotate(φ, RIGHT).rotate(θ, OUT)` (when γ = 0) or `label.apply_matrix(self.frame.get_orientation().as_matrix())`, then `move_to` [verified by run].
- For real 3D, use `ThreeDScene` [verified by run, examples/three_d.py].
  - The default orientation is (-30, 70), and depth test is turned on when you add (F:manimlib/scene/scene.py:946-953).
  - Use `fix_in_frame()` for a title that should stay fixed on screen.
  - Make a surface with `ThreeDAxes.get_graph(lambda x, y: ...)`.
  - **Depth test is turned on again on every add.** This also holds when `play` adds an object.
    - Text that has depth test is hidden when it overlaps a surface or filled shape drawn earlier on screen, even if it is closer to the camera than that shape [verified by run].
    - For objects that flicker from overlapping in the same plane, or that must always be visible (labels), call `mob.deactivate_depth_test()` **after** the animation that adds them ends.
    - Or add it with `self.add(mob, set_depth_test=False)` (F:manimlib/scene/scene.py:951-953).
    - `become()` also copies the depth test setting (F:manimlib/mobject/mobject.py:735).
  - `ThreeDAxes` is placed at the center of its ranges. If the ranges are asymmetric, the axes origin is not ORIGIN [verified by run].
    - Example: for x(-1,4), y(-2,3), `c2p(0,0,0)` is (-1.5, -0.5, 0).
    - Write all coordinates with `axes.c2p`, or align the origin with `axes.shift(-axes.c2p(0, 0, 0))`.
  - `Arrow` is a flat shape, so when the camera turns it lies sideways and gets thin. Use `arrow.set_perpendicular_to_camera(self.frame)` (`Arrow` is a `Line` subclass, F:manimlib/mobject/geometry.py:798). While the camera is moving, attach it with an updater.
  - The x and y labels of `ThreeDAxes.add_axis_labels()` lie in the xy plane and only the z label stands up (F:manimlib/mobject/coordinate_systems.py:574-583). Rotate the labels that must be readable with the billboard method from the 2D tilt above.
  - The `-sw` PNG of a scene where the camera moves shows the composition after the move ends.
- `Scene.clear()` empties `self.mobjects`, so `self.frame` is removed too (F:manimlib/scene/scene.py:117,400).
  - After that, frame updaters such as `add_ambient_rotation` stop [verified by run].
  - Doing `self.add(self.frame)` after `clear()` makes it spin again [verified by run].
  - `remove_all_except(...)` also calls `clear()` internally, so it has the same problem (F:manimlib/scene/scene.py:385-387).
  - To remove things, name the targets explicitly and use `FadeOut` or `remove`.

## 10. Updaters

- `dt` is detected by **name** (F:manimlib/mobject/mobject.py:834).
  - If a function parameter or local variable is named `dt`, pass `dt=` as a keyword.
  - Always name the second parameter of a time updater `dt` (`lambda m, dt: m.rotate(dt)`), and do not use a local variable named `dt` in other updaters.
- `add_updater` runs as soon as it is attached. It runs once even with `call=False` (F:manimlib/mobject/mobject.py:848).
  - On an object that already has updaters, using `call=True` (the default) runs the new updater twice and runs the existing updaters again (same file :845-848).
  - So write updaters so the result is the same even if they are called several times.
- In `-sw` (skip), `dt` updaters are called twice per `play`, with dt=run_time. The PNG of a scene with time updaters may differ from the video's end state, so check with the mp4 [verified by run, references/cli-and-output.md §7].
- `number.f_always.set_value(tracker.get_value)` (F:manimlib/mobject/mobject.py:186).
- `always_redraw` rebuilds the object every frame.
- Call `clear_updaters()` when the animation ends. For an example, see [examples/updaters.py](examples/updaters.py).

## 11. Structure, layout, color, timing

A summary of imcommit conventions. Details and evidence are in [references/imcommit-patterns.md](references/imcommit-patterns.md).

- **Structure**
  - One video is one `src/<video>/main.py`.
  - Put several scene classes in narrative order (imcommit has 1 to 8 per file, median 4).
  - Each class rebuilds the previous scene's end state by itself.
  - Inside `construct`, split blocks with `## <short label or one line of narration>` comments.
  - 15 to 30 seconds per scene is this plugin's recommendation. It is not a value measured in imcommit.
- Fix the seeds at the top of the file: `from random import seed`, `seed(41)`, `np.random.seed(41)` (I:init_project.py:5-10). For an example, see [examples/structure.py](examples/structure.py).
- **Layout**
  - Use `next_to` and `arrange`, with buff mostly 0.1, 0.2, 0.5.
  - Split regions on a wide canvas and move the camera.
- **Color**
  - Almost only named constants. imcommit has 0 hex literals, and the only others are colors computed with `interpolate_color`/`random_color`.
  - Usage: `GREY_B` is secondary, `GREEN` is correct, `RED` is wrong, `YELLOW` is emphasis.
  - To dim, use `set_opacity(0.2~0.3)`, or lay a semi-transparent overlay, raise what should stay with `set_z_index`, and `add` it again.
    - `set_opacity` also changes fill opacity. On an outline-only shape (`Square()` etc., fill opacity 0), it creates a gray (#888888) background at fill 0.2 [verified by run].
    - To dim only the outline, use `set_stroke(opacity=0.2)`.
- **Timing**
  - Use `run_time=0.5` for short actions (most common in imcommit).
  - Use `lag_ratio` of 0.3 to 0.5, and the default rate_func.
  - Within one `self.play`, give an object only one `.animate`.
    - If you give `.animate` separately to a parent VGroup and its children, both build their targets from the pre-play state, and the later one overwrites the earlier change (reproduced in E2E tests).
    - Chain the methods in one `.animate` (`mob.animate.set_stroke(...).set_opacity(...)`) or split the play.
    - To treat just one differently, give `.animate` to the sibling group without it (`VGroup(*(w for w in group if w is not focus))`) ([examples/structure.py](examples/structure.py)).

## 12. Examples (all render-verified with `-sw` and `-w -l`)

You can re-verify with `bash ${CLAUDE_PLUGIN_ROOT}/scripts/check_examples.sh <uv project>`.

| File | What it shows |
|---|---|
| [examples/structure.py](examples/structure.py) | Several scenes in one file, `##` blocks, seeds, emphasis and dimming, overlay + z_index, `set_color` |
| [examples/korean.py](examples/korean.py) | Korean Text, partial color, Text+Tex side by side, Korean inside Tex via kotex |
| [examples/tex.py](examples/tex.py) | t2c, string selection, TransformMatchingTex, Brace+Korean |
| [examples/camera.py](examples/camera.py) | `self.frame` move/restore, tilting a 2D scene + label rotation |
| [examples/three_d.py](examples/three_d.py) | ThreeDScene, surface, `fix_in_frame`, ambient rotation |
| [examples/updaters.py](examples/updaters.py) | ValueTracker, `dt` updater, `f_always`, `always_redraw`, `Dot(fill_color=)` |
| [examples/graphs.py](examples/graphs.py) | Axes, `get_graph`, graph labels, area, ParametricCurve |
| [examples/raenimgl_optional.py](examples/raenimgl_optional.py) | When using raenimgl: `(InteractiveScene, Scene2D)`, `playw` |
