# Differences between the fork and upstream

| Item | Value |
|---|---|
| Fork HEAD | `455a4201669cd68ff5e522c7fcd1a7ac31aadff0` (2026-10-11) |
| merge-base | `2e31f79a` (2026-03-14) |
| Compared upstream/master | `fafa083a` (2026-09-09) |
| Fork-only commits | 9. 9 files, +107/−11 |
| Upstream-only commits | 112. The fork is that far behind |

Commands: `git log upstream/master..HEAD`, `git rev-list --count HEAD..upstream/master`, `git diff --stat <merge-base> HEAD`

## Fork-only changes (complete)

Paths are relative to the fork repo root.

| Commit | Change | Location |
|---|---|---|
| 355b1ea5 | Changed defaults. Background `#333333→#000000`, `default_stroke_width 4.0→2.0`, `text.font Consolas→"Noto Sans KR"` | manimlib/default_config.yml:56,78,91 |
| 2dae42f1 | Added `--fontmap=ps2pk.map` to dvisvgm (for MiKTeX) | manimlib/utils/tex_file_writing.py:138 |
| f4c60267 | Applied `os.path.normcase` to the reload path comparison (Windows) | manimlib/module_loader.py:125,132 |
| 3c7d4789 | Reads SVG as utf-8 | manimlib/mobject/svg/svg_mobject.py:159 |
| 268f44c0 | Preview window width is 1/3 of the monitor (was 1/2) | manimlib/window.py:108 |
| bde8ddca | `e` key = yaw (`key_bindings.yaw`) | manimlib/scene/scene.py:767-771, manimlib/default_config.yml:121 |
| 993b64b2 | `c` key = `pan_3d_mirror`. Added `CameraFrame.increment_mirrored_euler_angles(dtheta=0, dphi=0, units=RADIANS)` | manimlib/camera/camera_frame.py:176, manimlib/default_config.yml:120 |
| df31da90 | `CameraFrame.interpolate` takes the shorter path between quaternions | manimlib/camera/camera_frame.py:122-130 |
| 455a4201 | CLI `--always_on_top`, yml `window.always_on_top`, `Window(always_on_top=)` (Windows only) | manimlib/config.py:103-107, manimlib/window.py:40,82 |

There is one side effect.
- The `c` key is bound in two places: `pan_3d_mirror` (yml:120) and `color` (yml:132).
- This conflict only matters in the InteractiveScene preview window.

## Only in upstream/master (do not use in the fork)

Paths are as of upstream@fafa083, and the fork has no such definitions. `Updater` exists in the fork only as a type alias for TYPE_CHECKING at `manimlib/mobject/mobject.py:61`, not as a class. So `grep Updater` returns results in the fork too.

| API | upstream location |
|---|---|
| `VideoMobject`, `Sprite`, `VideoSource` | manimlib/mobject/types/video_mobject.py:258,398,31 |
| `PlaneFractal`, `MandelbrotFractal`, `JuliaFractal`, `NewtonFractal`, `MetaNewtonFractal` | manimlib/mobject/fractals.py:64,116,164,185,284 |
| `vmobject_to_svg` | manimlib/utils/svg_export.py:8 |
| `COMMON_UNIFORMS`, `uniform_block_dtype` (the fork has no `manimlib/renderer/` at all) | manimlib/renderer/uniform_block.py:21,37 |
| `Keys`, `Mods` (module `manimlib.event_keys`) | manimlib/event_keys.py:17,38 |
| `Surface.set_sort_to_camera`, `Surface(sort_to_camera=)`, `Surface.get_resolution` | manimlib/mobject/types/surface.py:267,73,98 |
| `VMobject.set_joint_roundness`, `VMobject(joint_roundness=, stroke_width_in_scene_units=)` | manimlib/mobject/types/vectorized_mobject.py:591,107,112 |
| `set_fill(..., gradient_direction=)` | manimlib/mobject/types/vectorized_mobject.py:271 |
| `Mobject(textures=, texture_filter=)` | manimlib/mobject/mobject.py:103,104 |
| `Mobject.update(..., frame_rate=)` | manimlib/mobject/mobject.py:799 |
| `AnimationGroup(time_span=)`, `LaggedStartMap(time_span=)` applied at the group level | manimlib/animation/composition.py:35-47,113,174-186 |
| WGSL code in `set_color_by_code`, `VMobject.set_color_by_code(code_target=)` | manimlib/mobject/mobject.py:1956, manimlib/mobject/types/vectorized_mobject.py:468 |
| `Updater` class | manimlib/mobject/mobject.py:2247 |
| Config `scene.invert_zoom_scroll` | manimlib/default_config.yml:87 |
| `Camera(bundle_draws=, draw_together=)`, config `camera.bundle_draws`, `camera.draw_together` | manimlib/camera/camera.py:119-120, manimlib/default_config.yml:56,59 |
| `SceneFileWriter(crf=)`, config `file_writer.crf` | manimlib/scene/scene_file_writer.py:52 |

- Using them in the fork gives these results [verified by run: construct and call only in the fork env, no render].
  - The class and function names above are not in `from manimlib import *`, so you get NameError. Importing `manimlib.event_keys` or `manimlib.renderer` directly gives ModuleNotFoundError. <!-- snippet: skip the error is for the names above, not the import -->
  - `set_sort_to_camera`, `get_resolution`, `set_joint_roundness` raise AttributeError.
  - `sort_to_camera=`, `joint_roundness=`, `stroke_width_in_scene_units=`, `textures=`, `texture_filter=` raise `TypeError: Mobject.__init__() got an unexpected keyword argument ...`. `set_fill(gradient_direction=)`, `update(frame_rate=)`, `set_color_by_code(code_target=)` also raise TypeError.
- The `time_span=` keyword itself is accepted by every Animation in the fork (F:manimlib/animation/animation.py:29). The difference is group-level application [verified by run: measured opacity by replicating the time progression of fork scene.py:494,562 exactly].
  - Fork `AnimationGroup(FadeIn(sq), time_span=(1, 2))` raises no error. Only the playback length becomes 2 seconds. Because `AnimationGroup.interpolate` does not look at time_span (F:manimlib/animation/composition.py:114), the content finishes at its original length of 1 second from 0 s. Opacity is 0.5 at t=0.5.
  - Upstream fits the content to [1, 2] seconds (U:composition.py:43-47,113) [source only].
  - Fork `LaggedStartMap` passes `time_span` to each member's construction, not to the group (F:composition.py:175-178). The group's `time_span` is None. If `anim_func` does not accept this keyword (e.g. `lambda m: FadeIn(m)`), you get TypeError. Upstream passes it to the group (U:composition.py:174-186) [source only]. <!-- snippet: skip the TypeError needs LaggedStartMap(time_span=) -->
  - In the fork, pass it directly to each animation. `FadeIn(sq, time_span=(1, 2))` gives 0 at t=1 and 0.5 at t=1.5 [verified by run].
- `set_color_by_code` only shares the name. The fork takes GLSL code (F:manimlib/mobject/mobject.py:1989 `glsl_code`), and upstream takes WGSL. The fork does not check the code at call time [verified by run]. A snippet that does not compile as GLSL (WGSL included) passes at call time and fails when the mobject is first added (`self.add`/`self.play` compile the shader) with `_moderngl.Error: GLSL Compiler failed`, exit 1 [verified by run]. Available variables and the `set_color_by_xyz_func` letter substitution are in [style-and-color.md](style-and-color.md) §F.

- If the fork gets an unknown config key, it raises TypeError in that section's constructor [verified by run]. So taking an upstream `custom_config.yml` as is means the render does not start.
  ```
  TypeError: Scene.__init__() got an unexpected keyword argument 'invert_zoom_scroll'
  TypeError: Camera.__init__() got an unexpected keyword argument 'bundle_draws'
  ```
  - `camera.draw_together` and `file_writer.crf` fail the same way. Details are in [cli-and-output.md](cli-and-output.md) §5.
- The `custom_config.yml` in 3b1b/videos uses `invert_zoom_scroll`.

## Fork vs PyPI `manimgl` 1.7.2

Below is the result of installing PyPI 1.7.2 and the fork each into a clean venv and comparing them [verified by run, Windows].

- The `manimlib/` of PyPI 1.7.2 is file-for-file identical to tag v1.7.2 (f427fc67) of the fork repo (`diff -rq`).
- Both version strings are `1.7.2`, so they cannot be told apart. `importlib.metadata.version` and `manimlib.__version__` are both the same.
- There are two ways to tell them apart.
  - Check the fork marker `manim_config.key_bindings.yaw == "e"`. 1.7.2 has no `yaw` key.
  - Check `url` and `vcs_info.commit_id` in `site-packages/manimgl-*.dist-info/direct_url.json`. A PyPI install has no such file.
- `scripts/setup.sh` checks both. In a 1.7.2 environment both show `[fail]`.
- The fork is tag v1.7.2 (f427fc67) plus 51 upstream commits and 9 fork commits (`git rev-list --count v1.7.2..2e31f79a`).
  - The 51 include 0c69ab6a, which bumped the version number to 1.7.2 (setup.cfg only), and merge commit c48c4b6a. Of the other 49, 39 commits change `manimlib/` (`git rev-list --no-merges --count v1.7.2..2e31f79a -- manimlib`). The other 10 change only README, example_scenes.py, dependency files (requirements.txt/setup.cfg), or the CI workflow (.github/workflows/publish.yml), or are an empty commit (14f5f8ea).
- APIs that entered the fork after 1.7.2 (checked with `hasattr` in both environments):
  - `Scene.remove_all_except`, `Scene.set_background_color`
  - `set_clip_planes`, `clip_to_box`, `put_start_on`/`put_end_on`
  - `LineBrace`, `Slider`, `ThreeDModel`, `TexturedGeometry`
- `set_z_index` already existed in 1.7.2.
  - 1.7.2 applies it to that object only.
  - The fork added a `recurse=True` argument, so by default it applies to all sub-objects (F:manimlib/mobject/mobject.py:1238). The children's values for `VGroup(Square(), Circle()).set_z_index(3)` are [0, 0] in 1.7.2 and [3, 3] in the fork.
- Text size basis:
  - The fork's `Tex` has a height of about 1 unit for "0" at `font_size=144` (F:manimlib/default_config.yml:88 `tex.font_size_for_unit_height`, measured 0.997).
  - `Text` has the same setting (yml:94), but the measured height depends on the font. With the fork's default Noto Sans KR it is about 1.37 units, and with Consolas about 1.18. The ratio is constant regardless of font_size.
  - So at the same font_size, `Text` is about 1.37x larger than `Tex`. To match Text size exactly, use `height=` or `set_height`.
  - 1.7.2 does not have this setting and uses fixed constants (`TEXT_MOB_SCALE_FACTOR=0.0076`, `SCALE_FACTOR_PER_FONT_POINT=0.001`). So text sizes differ between the two versions.
- The `Surface` creation-axis argument is `preferred_creation_axis` in the fork and `prefered_creation_axis` (typo) in 1.7.2 (F:manimlib/mobject/types/surface.py:55). Code written for one does not work on the other.
- CLI:
  - The only difference in `--help` is `--always_on_top`.
  - `--fps 30` is parsed as int 30 in the fork and as the string `'30'` in 1.7.2. The help text is the same, so help does not reveal it.
- Problems in 1.7.2 itself (fixed in the fork):
  - `manimlib/__init__.py:1` does `import pkg_resources`, but setuptools is not in the dependencies. So `import manimlib` fails in a clean venv. Installing `setuptools<81` fixes it. <!-- snippet: skip PyPI 1.7.2 only -->
  - `Tex` always fails with `LaTeX compilation failed` on MiKTeX. 1.7.2 passes `-no-pdf` to `latex` unconditionally, but MiKTeX's latex does not know this option. The fork passes it only for xelatex.

## Packaging gap

- `manimlib/mobject/types/surface.py:5-6` imports `trimesh` and `pywavefront` at the top level.
- `manimlib/__init__.py:62` star-imports this module.
- But neither is in `setup.cfg` install_requires, and no other dependency pulls in either package (`uv tree --invert --package trimesh` shows only the project's direct dependency).
- So installing only the fork makes `import manimlib` fail with `ModuleNotFoundError: No module named 'trimesh'` [verified by run: installed only the fork in a new venv]. <!-- snippet: skip needs a venv without trimesh -->
- 1.7.2 also does not list these two packages as dependencies, but 1.7.2 source does not import them, so there is no problem. This gap came after 1.7.2.
- Fix: install both packages together. The imcommit pyproject and setup.sh do this.
- There is no `python_requires`. imcommit uses 3.10.18 and setup.sh uses 3.10. This plugin was checked on 3.10 only.

## Upstream/PyPI-era code that breaks on the fork

Test corpus: the 183 Scene classes in adithya-s-k/manim_skill @cef0450 `skills/manimgl-best-practices/{examples,templates}/*.py`, each rendered with `-sw` on the fork [verified by run].

- 155/183 passed (84.7%). The 28 failures have 17 causes. 15 are in the table, and 2 are bugs in the examples themselves (below the table).
- One more table row, the 3-element `x_range`, was found while reading the source. It is not in the corpus.
- No failure comes from a fork-only commit. The cited fork lines match upstream @fafa083 except: F:manimlib/mobject/mobject.py:1829 (upstream blends through `StructuredArray.interpolate`, U:manimlib/mobject/mobject.py:1835), F:manimlib/mobject/mobject.py:1950 (the fork stores the clip plane as a tuple, upstream as an array, U:manimlib/mobject/mobject.py:1917), and F:manimlib/shaders/surface/frag.glsl:7 (upstream renders with WGSL, U:manimlib/shaders/surface.wgsl:37-39). So the broadcast and clip rows may behave differently upstream. Upstream was not run [source only].
- Each row was reproduced with a minimal scene: the broken pattern exits 1 with the message shown, and the fix exits 0 and was checked in its PNG [verified by run]. For the `DecimalNumber` and `always_redraw` rows the last frame cannot show the problem, so those fixes were rendered with `-w -l` and checked in mid frames [verified by run].

| Error the user sees | Cause | Fork fix | Evidence |
|---|---|---|---|
| `KeyError: 'stroke_color'` in `init_background_lines` (7 scenes) | `NumberPlane`/`ComplexPlane(background_line_style={"stroke_opacity": 0.3})`. The dict replaces the default instead of merging into it. The faded lines then copy its missing `stroke_color` | Pass the full dict (`stroke_color=`, `stroke_width=`, `stroke_opacity=`), or style afterwards: `plane.background_lines.set_stroke(opacity=0.3)` | F:manimlib/mobject/coordinate_systems.py:641-645,656,664; U:coordinate_systems.py:661,669 <!-- snippet: skip the first span is the failing pattern --> |
| `TypeError: dict() got multiple values for keyword argument 'num_decimal_places'` (3 scenes) | `DecimalMatrix(m, decimal_config=dict(num_decimal_places=2, ...))`. The constructor already passes its own `num_decimal_places` (default 2) next to `**decimal_config` | `DecimalMatrix(m, num_decimal_places=2, decimal_config=dict(include_sign=True))` | F:manimlib/mobject/matrix.py:219,226-229; U:matrix.py:229-231 <!-- snippet: m=[[0.5],[-0.5]] --> |
| `TypeError: CoordinateSystem.get_riemann_rectangles() got an unexpected keyword argument 'color'` (1) | The parameter is `colors=`, a gradient (default `(BLUE, GREEN)`) | `colors=[BLUE]` | F:manimlib/mobject/coordinate_systems.py:363-376, same lines in U |
| `TypeError: 'tuple' object does not support item assignment` from `get_riemann_rectangles` (not in the corpus) | When `dx` is omitted, a 3-element `x_range` is extended in place by the axis step `self.x_range[2]`, not by its own step. A tuple fails. A list `[1, 4, 0.5]` becomes `[1, 5, 0.5]` and gives 7 rectangles instead of 6, then 9 on a second call with the same list. With `dx=` it is extended by dx: the first call gives the right count, but the caller's list is changed, so each reuse of the same list adds a rectangle (6, then 7) | `x_range=[a, b], dx=step`. A 2-element range is copied into a new list first | F:manimlib/mobject/coordinate_systems.py:379-385 [verified by run: counts 7, 9; with `dx=0.5`, 6 and the list becomes `[1, 4.5, 0.5]`, then 7 on reuse] |
| `AttributeError: 'BarChart' object has no attribute 'c2p'` (1) | The fork's `BarChart` is a `VGroup` of `Line`s and `Rectangle`s. `c2p` exists only on `CoordinateSystem` | Read positions off its parts: `chart.x_axis`, `chart.y_axis`, `chart.bars`. `chart.y_axis[0]` holds the y ticks, and the last tick sits at `max_value` (default 1). Or draw the bars on `Axes` and use `axes.c2p` | F:manimlib/mobject/probability.py:196,251,265; F:coordinate_systems.py:54,78 |
| `AttributeError: 'VGroup' object has no attribute 'get_string'` (1) | A slice of a `Text` (`text[0:3]`) is a plain `VGroup`. `get_string` exists only on the whole `StringMobject` | Keep the Python strings (`words = phrase.split(" ")`) and build `Text(w)` from them | F:manimlib/mobject/mobject.py:401-404; F:manimlib/mobject/svg/string_mobject.py:584 |
| `AttributeError: 'Rectangle' object has no attribute 'set_clip_path'` (1) | No `set_clip_path` in the fork or upstream (0 grep hits) | `mob.clip_to_box(box)`. It keeps the part inside the box's bounding box, using 4 clip planes. For one edge, `set_clip_planes((vect, threshold))`. Avoid `set_clip_plane` in the fork: it stores a tuple (F:manimlib/mobject/mobject.py:1950), so a later `deactivate_clip_plane()`/`clip_to_box()`/`set_clip_planes()` raises `TypeError: 'tuple' object does not support item assignment`, and a Transform to an unclipped target or `.animate.set_clip_plane(...)` fails in `Mobject.interpolate` (`TypeError: can't multiply sequence by non-int of type 'numpy.float64'`, or `ValueError: operands could not be broadcast together` when the start is unclipped) [verified by run]. Upstream stores an array (U:manimlib/mobject/mobject.py:1917). PyPI 1.7.2 has `set_clip_plane` but not `clip_to_box` | F:manimlib/mobject/mobject.py:1836,1948-1950,1960-1962,1968,1971-1978; U:mobject.py:1917,1938; `git show f427fc67:manimlib/mobject/mobject.py` (v1.7.2), line 1935 |
| `Exception: Only VMobjects can be passed into VGroup`, or `All submobjects must be of type VMobject` (2) | `GlowDot`/`DotCloud` (a PMobject), `Surface`/`Sphere` and `ImageMobject` are not VMobjects. `VGroup(a, b)` raises the first message. `VGroup(generator)` and `.add()` raise the second | `Group(...)` | F:manimlib/mobject/types/vectorized_mobject.py:136,1316; F:manimlib/mobject/types/dot_cloud.py:26,183; U:vectorized_mobject.py:245,1397 |
| `Exception: Invalid color type` from `Surface.__init__` (1) | `Surface(func, u_range=..., v_range=...)`. The first parameter of `Surface` is `color`, so the function lands in `color` | `ParametricSurface(func, u_range=(a, b), v_range=(c, d))` | F:manimlib/mobject/types/surface.py:46,268-271; U:surface.py:62 |
| `NameError: name 'Dot3D' is not defined` (1) | Not in the fork or upstream (SKILL.md §2) | `Sphere(radius=0.08)` inside a `Group` (a `Sphere` is a `Surface`, see the VGroup row). Or a flat `Dot` | F:manimlib/mobject/three_dimensions.py:93 |
| `NameError: name 'DoubleArrow' is not defined` (1) | Not in the fork or upstream. Only `CurvedDoubleArrow` exists (SKILL.md §2) | `Line(a, b).add_tip().add_tip(at_start=True)` | F:manimlib/mobject/geometry.py:71,655 <!-- snippet: a=2*LEFT b=2*RIGHT --> |
| `LatexError: Extra }, or forgotten \right.` (3) | `Tex(R"\left[")` alone. Each `\left` needs a `\right` in the same Tex, in any LaTeX | `Tex("[")` and `stretch_to_fit_height(h)`. Or let `Matrix`/`DecimalMatrix` draw the brackets. The fork builds them as one paired `\left[...\right]` Tex and splits it in half | F:manimlib/mobject/matrix.py:120-127 <!-- snippet: skip the first span is the failing pattern --> |
| `LatexError: Argument of \frac has an extra }.` (1) | A `t2c` key that is a bare command (`R"\frac"`). Each match of a key is wrapped in `{{\color[RGB]{...} ... }}`, which cuts `\frac` off from its arguments | Use whole groups as keys: `t2c={R"\frac{1}{3}": YELLOW}` | F:manimlib/mobject/svg/tex_mobject.py:170-178, same file in U |
| `ValueError: could not broadcast input array from shape (57,3) into shape (77,3)`, shapes vary (1) | Two animations on one `DecimalNumber` in one `play`. `ChangeDecimalToValue` rebuilds the digit submobjects every frame (`set_value`), while `.animate.set_color` interpolates copies that keep the old point count (SKILL.md §11) | Count and recolor in one animation: `UpdateFromAlphaFunc(label, lambda m, a: m.set_value(interpolate(v0, v, a)).set_color(interpolate_color(c0, GREY, a)))`. Or color it in a separate `play`. Not `label.animate.set_value(v)`: it exits 0 but morphs the glyphs instead of counting [verified by run: mid frames]. Swapping the order is not a fix: `self.play(label.animate.set_color(GREY), ChangeDecimalToValue(label, v))` passes `-sw`, but in the video the color stays unchanged once the digit count changes (0.25 to 123.5), or it fails only in `-w` (`.animate.scale` with 9.5 to -10.25) [verified by run] | F:manimlib/animation/numbers.py:31-34; F:manimlib/animation/update.py:37,48-50; F:manimlib/mobject/numbers.py:207; F:manimlib/mobject/mobject.py:1817-1829 <!-- snippet: label=DecimalNumber(0.25) v0=0.25 v=0.0 c0=YELLOW --> |
| `AssertionError` in `set_data`, from `become` via `always_redraw` (1) | The redraw function returned an empty `Group` of `Sphere`s. `become` pads the empty side with copies of the `Group` itself, and their data dtype differs from a `Surface`'s. A count change that never reaches 0 (9→10) works | Keep the members fixed. Build the spheres once and, in an updater, hide out-of-range ones with `set_opacity(0).deactivate_depth_test()` (call `apply_depth_test()` again when they come back). An opacity-0 surface still writes depth and hides anything drawn after it (SKILL.md §9) [verified by run: mid frames] | F:manimlib/mobject/mobject.py:237,1782-1789,1937-1945; F:manimlib/shaders/surface/frag.glsl:7; U:mobject.py:221,1782 |
| `urllib.error.HTTPError: HTTP Error 403: Forbidden` (1) | `TexturedSurface(surface, "https://...")`. A URL is fetched with `urllib.request.urlretrieve` and Python's default User-Agent. upload.wikimedia.org answered 403, and the same URL with an explicit User-Agent gave 200 (2026-10-17). There is no cache check, so it downloads again on every render | Download the image once (`curl -o earth.jpg <url>`) and pass the local path | F:manimlib/utils/file_ops.py:33-42; U:file_ops.py:33,41 <!-- snippet: skip placeholder URL --> |

Failures that are bugs in the examples themselves:
- `NameError: name 'WeightMatrix' is not defined`. The helper class is defined in other example files of that repo (e.g. `examples/attention_scenes.py`), not in manimlib.
- `ValueError: The truth value of an array with more than one element is ambiguous`. `direction == RIGHT` compares numpy arrays. Use `np.array_equal(direction, RIGHT)`.

### Silent changes in the passing scenes

`-sw` exit 0 only proves that `construct()` finished.
- 49 of the 155 passing scenes (32%) give constructor `color=` to a class that ignores it (SKILL.md §6). That is 131 calls: `Text` 61, `Dot` 29, `Tex` 26, `Circle` 8, `Brace` 4, `Arrow` 2, `Vector` 1 (AST count over each Scene class).
- 8 of those 49 scenes were checked in their last-frame PNG [verified by run]. All 8 show the change.
  - 31 of these objects are visible in those frames. 29 came out in a color other than the one requested: white `Text`/`Tex`/`Dot`/`Brace`, a grey `Vector`, a red `Circle`.
  - The other 2 asked for `WHITE`, the default. They are the `+`/`-` labels on two charge `Dot`s that turned white, so they vanished (`vector_fields.py` ElectricDipole).
