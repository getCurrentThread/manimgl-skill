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
  - The class and function names above are not in `from manimlib import *`, so you get NameError. Importing `manimlib.event_keys` or `manimlib.renderer` directly gives ModuleNotFoundError.
  - `set_sort_to_camera`, `get_resolution`, `set_joint_roundness` raise AttributeError.
  - `sort_to_camera=`, `joint_roundness=`, `stroke_width_in_scene_units=`, `textures=`, `texture_filter=` raise `TypeError: Mobject.__init__() got an unexpected keyword argument ...`. `set_fill(gradient_direction=)`, `update(frame_rate=)`, `set_color_by_code(code_target=)` also raise TypeError.
- The `time_span=` keyword itself is accepted by every Animation in the fork (F:manimlib/animation/animation.py:29). The difference is group-level application [verified by run: measured opacity by replicating the time progression of fork scene.py:494,562 exactly].
  - Fork `AnimationGroup(FadeIn(sq), time_span=(1, 2))` raises no error. Only the playback length becomes 2 seconds. Because `AnimationGroup.interpolate` does not look at time_span (F:manimlib/animation/composition.py:114), the content finishes at its original length of 1 second from 0 s. Opacity is 0.5 at t=0.5.
  - Upstream fits the content to [1, 2] seconds (U:composition.py:43-47,113) [source only].
  - Fork `LaggedStartMap` passes `time_span` to each member's construction, not to the group (F:composition.py:175-178). The group's `time_span` is None. If `anim_func` does not accept this keyword (e.g. `lambda m: FadeIn(m)`), you get TypeError. Upstream passes it to the group (U:composition.py:174-186) [source only].
  - In the fork, pass it directly to each animation. `FadeIn(sq, time_span=(1, 2))` gives 0 at t=1 and 0.5 at t=1.5 [verified by run].
- `set_color_by_code` only shares the name. The fork takes GLSL code (F:manimlib/mobject/mobject.py:1989 `glsl_code`), and upstream takes WGSL. The fork does not check the code at call time [verified by run]. How WGSL code fails in a render was not checked, because no render was done.

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
  - `manimlib/__init__.py:1` does `import pkg_resources`, but setuptools is not in the dependencies. So `import manimlib` fails in a clean venv. Installing `setuptools<81` fixes it.
  - `Tex` always fails with `LaTeX compilation failed` on MiKTeX. 1.7.2 passes `-no-pdf` to `latex` unconditionally, but MiKTeX's latex does not know this option. The fork passes it only for xelatex.

## Packaging gap

- `manimlib/mobject/types/surface.py:5-6` imports `trimesh` and `pywavefront` at the top level.
- `manimlib/__init__.py:62` star-imports this module.
- But neither is in `setup.cfg` install_requires, and no other dependency pulls in either package (`uv tree --invert --package trimesh` shows only the project's direct dependency).
- So installing only the fork makes `import manimlib` fail with `ModuleNotFoundError: No module named 'trimesh'` [verified by run: installed only the fork in a new venv].
- 1.7.2 also does not list these two packages as dependencies, but 1.7.2 source does not import them, so there is no problem. This gap came after 1.7.2.
- Fix: install both packages together. The imcommit pyproject and setup.sh do this.
- There is no `python_requires`. imcommit uses 3.10.18 and setup.sh uses 3.10. This plugin was checked on 3.10 only.
