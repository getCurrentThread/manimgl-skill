# raenimgl (optional dependency)

## Overview

- Source: `CodingVillainKor/raenimgl` @ `177affc69311d13fcad3404b2599a7714de1d4f2` (2026-09-25)
- A utility library that imcommit actually imports.
- It is a different repository from `raenim`. `raenim` is for ManimCE.
- **There is no LICENSE file.** This document only describes the API and behavior; no code is copied.
- Paths are relative to the raenimgl repository root. The imcommit usage counts are name occurrences counted by AST over the same scope as [imcommit-patterns.md](imcommit-patterns.md) (34 files, excluding the copy).

## Installation

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/setup.sh <project> --with-raenimgl
```

- pyproject declares only `manimgl>=1.7.2` and has no git source (pyproject.toml).
  - So installing raenimgl on its own pulls in PyPI manimgl.
  - **It must be added to the same uv project that pins the fork as a git source** for the fork to be kept.
  - After adding it, setup.sh checks that `direct_url.json` still points to the fork @455a4201 [verified by run].
- `setuptools<71` is pinned along with it.
- If raenimgl is already in pyproject, setup.sh does not pin it again. In that case the rev follows the existing pyproject.

## Import side effects (monkey patches)

The single line `from raenimgl import *` changes the following.

| Target | Description | Location |
|---|---|---|
| `manimlib.utils.tex_file_writing.full_tex_to_svg` | Replaced. The dvisvgm `--fontmap=ps2pk.map` that the fork added is dropped | raenimgl/__init__.py:15-68 |
| `_AnimationBuilder.__init__` / `__getattr__` | `.animate` behavior is unchanged. Method calls are additionally recorded in `_recorded_calls`, and only raenimgl `SkewedAnimations` replays this record | raenimgl/animation.py:6-30 |
| `InteractiveSceneEmbed.launch` | Marks `scene._reached_embed = True` before opening the embed shell. Fast-forward is turned off after that | raenimgl/scene.py:204-215 |
| `InteractiveSceneEmbed.get_shortcuts` | Adds a `request_normal_speed_reload` function to the embed shell | raenimgl/scene.py:233-242 |
| `StringMobject.mobjects_from_svg_string` | Replaced if `StringMobject` has no `get_file_path_by_content`. The fork has no such method, so it is **always replaced** [verified by run]. Behavior matches the fork, but the `Cannot align submobjects` warning it emitted when label alignment fails is gone. So `tex["..."]`/`t2c` partial selection can be wrong without any warning | raenimgl/script.py:13-37 |
| `Code.validate_markup_string` | Added as a do-nothing method if missing. The fork lacks it, so it is always added | raenimgl/script.py:6-8 |
| `Mobject.align` | An `align(target, direction, buff)` method that the fork lacks is added to every Mobject | raenimgl/functions.py:11-31 |

- Tex compatibility: with MiKTeX + cm-super, `Tex(R"\frac{a}{b} = c")` renders correctly with `from raenimgl import *` active (examples/raenimgl_optional.py) [verified by run].
- However, MiKTeX without cm-super and TeX Live were not checked.

## Provided API

In order of how often they appear in imcommit.

| Name | Description | imcommit | Location |
|---|---|---|---|
| `self.playw(*anims, wait=1, **kw)` | play, then wait | 1197 times | raenimgl/scene.py:40 |
| `self.cf` | `self.frame` | 178 times | raenimgl/scene.py:146 |
| `self.playwl(*anims, lag_ratio=0.05, wait=1)` | play with LaggedStart, then wait | 144 times | raenimgl/scene.py:68 |
| `Transformr` | Same as `ReplacementTransform` (`replace_mobject_with_target_in_scene=True`) | 138 times | raenimgl/animation.py:284 |
| `Words` | `Text` subclass. `.words` gives word-level parts split on spaces | 122 times | raenimgl/text.py:74-80 |
| `MONO_FONT` | Per-OS monospace font name | 117 times | raenimgl/utils.py:26-37 |
| `Tensor` | A vector VGroup of colored cells laid out in a row | 79 times | raenimgl/nn.py:67 |
| `Circumscribe` | Alias of `FlashAround` | 60 times | raenimgl/animation.py:314 |
| `mob.align(target, ...)` | Attaches to the inner edge of the target (see the import side effects table) | 59 times | raenimgl/functions.py:11-31 |
| `Create` | Alias of `ShowCreation` | 46 times | raenimgl/animation.py:310 |
| `self.addw(*mobs, wait=1)` | add, then wait | 44 times | raenimgl/scene.py:50 |
| `Scene2D(Scene, …)`, `Scene3D(ThreeDScene, …)` | imcommit writes `class S(InteractiveScene, Scene2D)` (all 125 classes) | | raenimgl/scene.py:120,150 |
| `self.overlay` | Overlay object | | raenimgl/scene.py:101 |
| `PythonCode` | Code display | 2 times | raenimgl/script.py:175 |

- `Create` and `Circumscribe` exist only with raenimgl. In fork-only code, use `ShowCreation` and `FlashAround`.
- Other substitutes in fork-only code: `Transformr` → `ReplacementTransform`, `Words` → `Text` + glyph slice, `playw` → `self.play(...)` + `self.wait()`.
- `PythonCode` opens the file without specifying an encoding (raenimgl/script.py:192). On a Windows non-UTF-8 locale, Korean comments may be garbled. Not verified.

## Fast-forward

- `Scene2D.play` and `playw` cut `run_time` to `0.1` when `_fast_forward()` is true, and `playw`/`addw` also skip the wait (raenimgl/scene.py:24-55,128-131).
- This is true only when all three conditions hold.
  1. It is `interactive()` (window preview).
  2. The embed shell has not been reached yet.
  3. Normal speed has not been requested via `request_normal_speed_reload()`.
- In other words, it exists to skip ahead to the embed point in the preview window.
- Caution: previewing a scene that has no `self.embed()` without `-w` cuts every play to 0.1 s until the end and drops the waits in playw/addw (a hand-written `self.wait()` is unchanged). Source evidence.
- It does not apply in a `-w` render. The mp4 length of examples/raenimgl_optional.py was the normal 3.5 seconds [verified by run].
