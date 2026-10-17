# Visual techniques (Plan reference, fork-verified)

Adapted from adithya-s-k/manim_skill @cef0450 `skills/manim-composer/references/visual-techniques.md` and the transition patterns in `scene-examples.md` (MIT, Copyright (c) 2026 Adithya S Kolavi; license text in [LICENSE-manim_skill](LICENSE-manim_skill)). Changed: every API replaced with its fork @455a4201 equivalent and checked (CE-only names replaced: `MathTex`, `Circumscribe`, `get_area`, `RightAngle`; the CE classes the composer's matrix and zoom ideas presuppose, `LinearTransformationScene` and `ZoomedScene`, noted as absent); recipes added for the composer's empty "Substitution", "Projection" and metaphor entries; hex palettes replaced with named constants; timing table extended with fork defaults and imcommit counts; transitions limited to what works when each scene renders on its own.

- Evidence notation as in best-practices SKILL.md: `F:` fork @455a420, `I:` imcommit @a2fe49f.
- "best-practices §N" is a section of [../../manimgl-best-practices/SKILL.md](../../manimgl-best-practices/SKILL.md). `style-and-color.md` and `imcommit-patterns.md` are in [../../manimgl-best-practices/references/](../../manimgl-best-practices/references/).
- `[verified by run]`: rendered with `-sw` and/or `-w -l` in this plugin's probes (fork env, Windows, MiKTeX) and the PNG or frame sheet checked, or, for constructor/keyword facts, printed by a probe script.
- Use the entry names here in the scenes.md **Technique** line.
- Recipes built on `Tex`/`Brace` need LaTeX; with **Uses Tex: no** use only Text, shapes and numbers.

## Core principles

1. **Progressive disclosure**: never show everything at once. Build `f(x) = x^2` → `ax^2` → `ax^2 + bx + c` term by term, each step one `##` block.
2. **Transform, don't replace**: `self.play(TransformMatchingTex(eq1, eq2, run_time=1))` instead of `FadeOut` + `FadeIn`.
   - `TransformMatchingTex` is an alias of `TransformMatchingStrings` (F:manimlib/animation/transform_matching_parts.py:189-191).
   - It works on Korean `Text` too: `Text("정밀도가 낮은 모델")` → `Text("정밀도가 높은 모델")` keeps the shared words in place and morphs only 낮 → 높 [verified by run].
   - Its default `run_time` is 2 (F:manimlib/animation/transform_matching_parts.py:29). Write `run_time` (best-practices §8).
3. **Color as meaning**: one meaning per named constant for the whole video, written in the scenes.md **Color roles** line.
   - imcommit roles: GREY_B secondary, GREEN correct/result, RED wrong, YELLOW emphasis (imcommit-patterns.md Color).
   - The composer adds BLUE for input/given values. It fits as an extra role.
4. **Spatial relationships**: left → right = transformation, time, causation; top → bottom = hierarchy, derivation; center = focus; periphery = context.

## Highlight

| Composer (CE) | Fork | Evidence |
|---|---|---|
| `Indicate(term)` | same. Defaults: scale 1.2, YELLOW, `there_and_back` | F:manimlib/animation/indication.py:73-80 [verified by run] |
| `Circumscribe(eq, color=YELLOW)` | `FlashAround(eq, color=YELLOW)`. No `Circumscribe` in the fork | F:manimlib/animation/indication.py:255-266 [verified by run] |
| `FlashAround(result)` | same. `color=` is honored | same lines [verified by run] |

- Parts work as targets: `Indicate(eq[R"\cos\theta"])`, `FlashAround(t["높은"], color=YELLOW)` [verified by run]. List a Tex part in `isolate=`/`t2c=` when you create it (Equations). A listed key that starts with an operator name (`\cos`, `\sin`, `\log`) loses the thin space before it: write `\,` before it in the source, as in `Tex(R"|\vec a|\,|\vec b|\,\cos\theta", t2c={R"\cos\theta": YELLOW})` (same width as the unlisted formula) [verified by run].

## Equations

- `MathTex(r"...")` → `Tex(R"...")` (math mode, best-practices §2).
- `eq.set_color_by_tex("x", BLUE)` exists and colors every match (F:manimlib/mobject/svg/tex_mobject.py:207). It selects by counting source symbols: wrong glyphs inside a `\frac` numerator or `\sum`/`\int` limits, and matches inside command names. List the substring in `t2c=`/`isolate=` when you create the Tex (style-and-color.md §G1).
- Step-by-step derivation [verified by run]:
  ```python
  steps = [Tex(s, t2c={"x": BLUE}) for s in (R"2x + 4 = 10", R"2x = 6", R"x = 3")]
  self.add(steps[0])
  for a, b in zip(steps, steps[1:]):
      self.play(TransformMatchingTex(a, b), run_time=1)
  ```
- Substitution: the `x` turns into `3` in place and the rest stays [verified by run]:
  ```python
  eq = Tex(R"2x + 4 = 10", isolate=["x"])
  sub = Tex(R"2 \cdot 3 + 4 = 10", isolate=["3"])
  self.play(TransformMatchingStrings(eq, sub, key_map={"x": "3"}), run_time=1)
  ```
- Numbers dropping into a symbolic formula, one `TransformFromCopy` per symbol [verified by run]:
  ```python
  num = Tex(R"= 3 \cdot 1 + 1 \cdot 2 = 5", isolate=["3", "1", "2", "5"])  # eq built with isolate=["a_1", "b_1", "a_2", "b_2"]
  pairs = [("a_1", num.select_part("3")), ("b_1", num.select_part("1", 0)),
           ("a_2", num.select_part("1", 1)), ("b_2", num.select_part("2"))]
  self.play(*(TransformFromCopy(eq[s], t) for s, t in pairs), run_time=1.5)
  ```
  - `select_part(s, k)` is the k-th match of `s` (F:manimlib/mobject/svg/string_mobject.py:554-555).
  - Matches count in source order and include digits inside longer numbers: in `\sqrt{10}\,\sqrt{5}\cos 45^\circ = 5`, `select_part("5", 1)` is the 5 of 45. Use `-1` for the last one [verified by run].

## Graphs

- `Axes(x_range=(-3, 3), y_range=(-2, 2))`: a two-element range works; the step defaults to 1 (F:manimlib/mobject/number_line.py:78) [verified by run].
- Axis labels: `axes.get_axis_labels("x", "f(x)")`. The parameters are positional `x_label_tex`, `y_label_tex` (F:manimlib/mobject/coordinate_systems.py:152-162). Needs LaTeX.
  - `get_axis_labels(x_label="x")` raises `TypeError: Mobject.__init__() got an unexpected keyword argument 'x_label'` [verified by run].
- Area: `axes.get_area_under_graph(graph, x_range=(a, b), fill_color=BLUE, fill_opacity=0.5)` (F:manimlib/mobject/coordinate_systems.py:417).
  - `get_area` raises AttributeError; `color=`/`opacity=` raise TypeError [verified by run].
- **Riemann → area** (integral as accumulation) [verified by run]:
  ```python
  rects = axes.get_riemann_rectangles(graph, x_range=[0, 3], dx=0.5)
  self.play(FadeIn(rects, lag_ratio=0.1))
  for dx in [0.25, 0.1, 0.05]:
      self.play(Transform(rects, axes.get_riemann_rectangles(graph, x_range=[0, 3], dx=dx)), run_time=0.7)
  area = axes.get_area_under_graph(graph, x_range=[0, 3], fill_color=BLUE, fill_opacity=0.5)
  self.play(FadeOut(rects), FadeIn(area))
  ```
  - `Transform` splits the rectangles smoothly when their count changes (6 → 12 → 30 → 60) [verified by run].
  - The rectangles default to a BLUE → GREEN gradient (`colors=(BLUE, GREEN)`, F:manimlib/mobject/coordinate_systems.py:363-375).
- **Tangent sweep** (derivative as slope) [verified by run]:
  ```python
  x = ValueTracker(-2)
  line = always_redraw(lambda: axes.get_tangent_line(x.get_value(), graph, length=3).set_stroke(YELLOW, 3))
  dot = always_redraw(lambda: Dot(axes.i2gp(x.get_value(), graph)).set_color(YELLOW))
  self.add(line, dot)
  self.play(x.animate.set_value(2), run_time=3)
  ```
  - `get_tangent_line` (F:manimlib/mobject/coordinate_systems.py:350).
- **Traced path**: `TracedPath(dot.get_center, stroke_color=YELLOW, stroke_width=4)` (F:manimlib/mobject/changing.py:98).
  - It grows through a time updater, so its `-sw` PNG is wrong: a dot moved right and then rotated 180° gave a straight chord in the PNG and a half circle in the mp4 [verified by run]. Judge it from the mp4 frames (best-practices §10).

## Vectors and geometry

- Position vectors: `Vector(v)` starts exactly at the origin (buff 0, F:manimlib/mobject/geometry.py:1231) [verified by run].
- `Arrow(a, b)` leaves a 0.25 gap at both ends (`buff=MED_SMALL_BUFF`, F:manimlib/mobject/geometry.py:1081): `Arrow(ORIGIN, 3 * RIGHT)` spans x 0.25–2.75 [verified by run]. Pass `buff=0` for vectors.
- Color both with `.set_color()`. Constructor `color=` makes them gray (best-practices §6).
- **Tip-to-tail sum** [verified by run]:
  <!-- snippet: a=Vector(RIGHT+UP) b=Vector(2*RIGHT) -->
  ```python
  self.play(b.animate.shift(a.get_end() - b.get_start()))  # b now starts at a's tip
  s = Arrow(a.get_start(), b.get_end(), buff=0).set_color(YELLOW)
  self.play(GrowArrow(s))
  ```
- Stretch or turn a vector with `vec.animate.put_start_and_end_on(start, end)` (F:manimlib/mobject/geometry.py:1198). It keeps the tip shape (see the matrix recipe).
- **Projection + Elbow** (right-angle mark). The fork has no CE `RightAngle` [verified by run]:
  ```python
  a_line = Line(o, a_end)
  foot = a_line.get_projection(b_end)
  proj = DashedLine(b_end, foot).set_color(GREY_B)
  mark = Elbow(width=0.3, angle=a_line.get_angle() + (0 if np.cross(a_end - o, b_end - o)[2] >= 0 else -PI / 2)).shift(foot).set_color(GREY_B)
  shadow = Line(o, foot).set_stroke(YELLOW, 6)
  ```
  - `Line.get_projection` (F:manimlib/mobject/geometry.py:768).
  - `Elbow(width=w, angle=α)` draws the two outer sides of a w×w square with one corner at ORIGIN, filling the quadrant between directions α and α + 90° (F:manimlib/mobject/geometry.py:934-937). Shift it to the vertex. `color=` is honored [verified by run]. The angle above fills the quadrant between the perpendicular toward b and the direction of a's tip, for b on either side of a, so the mark stays on drawn lines from acute angles through 90° (where it sits between a and b) to obtuse angles (where it sits on the shadow). It leaves them only when the foot is within `width` of a's tip or beyond it (|b| cos θ > |a| − width); there use `+ PI / 2` (`+ PI` when b is clockwise of a), which turns it back along the shadow [verified by run].
  - Moving version: wrap `b`, `proj`, `mark` and `shadow` in `always_redraw` and drive the angle with a `ValueTracker`. At 90° the shadow shrinks to a point without errors [verified by run].
  - Introduce an `always_redraw` object with `ShowCreation(proj, suspend_mobject_updating=True)`. Without it the updater redraws the whole object every frame, so `ShowCreation` is invisible and the object pops in on the first frame. The default is `False` (F:manimlib/animation/animation.py:43) [verified by run]. The updater resumes after the animation.
  - Before fading them out, call `clear_updaters()` on them (best-practices §10).
- **Brace along a slanted segment**: `Brace(seg, rotate_vector(DOWN, seg.get_angle()))`. Brace turns the target so `direction` points down, fits itself, then turns both back (F:manimlib/mobject/svg/brace.py:43-53) [verified by run].
  - Label it with `t = Text("그림자"); brace.put_at_tip(t, use_next_to=False)` (same for a `Tex`). `brace.get_text`/`get_tex` place the label with `next_to(tip, np.round(direction))`, an axis direction, so on a slanted brace a wide label overlaps the brace (F:manimlib/mobject/svg/brace.py:68-97) [verified by run].
  - `Brace` is a `Tex` subclass and needs LaTeX (F:manimlib/mobject/svg/brace.py:32); with **Uses Tex: no**, label the segment with a `Text` placed by `next_to` instead.

## Matrices as transformations

The fork has no CE `LinearTransformationScene` [verified by run]. Transform the plane, and move the basis vectors to their images:

<!-- snippet: plane=NumberPlane(x_range=(-1,4),y_range=(-1,3),width=6,height=4.8).to_corner(DL) i_hat=Vector(RIGHT) j_hat=Vector(UP) -->
```python
M = np.array([[2, 1], [0, 1.5]])  # an ndarray: M @ [1, 0] fails on a nested list
o = plane.c2p(0, 0)              # the plane origin, not plane.get_center()
self.play(
    plane.animate.apply_matrix(M, about_point=o),
    i_hat.animate.put_start_and_end_on(o, plane.c2p(*(M @ [1, 0]))),
    j_hat.animate.put_start_and_end_on(o, plane.c2p(*(M @ [0, 1]))),
)
```

- `plane.c2p` is evaluated before the play, on the untransformed plane, so the tips land on the transformed axes' 1 marks also on a moved, rescaled plane (`to_corner`, `width=`) [verified by run]. This needs equal x and y unit lengths: with x unit 1.2 and y unit 0.75, j_hat ended 0.45 off the transformed y axis [verified by run].
- Do not apply the matrix to arrows: `apply_matrix` on a `Vector` shears its tip [verified by run].
- `ApplyMatrix(M, mob)` has no `about_point` (TypeError) and always uses ORIGIN (F:manimlib/animation/transform.py:272-284). `mob.animate.apply_matrix(M, about_point=o)` accepts it (F:manimlib/mobject/mobject.py:1012-1015) [verified by run].
- **Determinant as area**: a `Square` filled YELLOW with its lower-left corner on the origin (`sq.move_to(o, DL)`), plus `sq.animate.apply_matrix(M, about_point=o)` in the same play, so it stays on the grid. For `M = np.array([[2, 1], [0, 1.5]])` its area grew by 3.0 = det M [verified by run].
- After `self.play(group.animate.apply_matrix(M))`, a child Vector's `get_width()` still returned its pre-play value (0.225 while its points spanned 1.023) [verified by run, cause not investigated]. Place labels with `plane.c2p(...)`, not with child bounding boxes.
- Before a nonlinear `apply_function`, call `plane.prepare_for_nonlinear_transform()` (F:manimlib/mobject/coordinate_systems.py:722) (source evidence).

## 3D

- Orbit: `self.play(self.frame.animate.reorient(60, 70, 0), run_time=3)` for turns under 180°. Angles are in degrees (F:manimlib/camera/camera_frame.py:211); write all three or the current roll is kept (best-practices §9). For 180° or more, use the `UpdateFromAlphaFunc` + `set_theta` or `add_ambient_rotation` recipes in ../../manimgl-best-practices/references/korean-tex-3d.md §C8 and ../../manimgl-best-practices/examples/camera_orbit.py.
- **Shadow on the xy plane** (3D → 2D projection) [verified by run]:
  ```python
  shadow = helix.copy().apply_function(lambda p: p * np.array([1, 1, 0])).set_stroke(GREY_B, 2)
  self.play(TransformFromCopy(helix, shadow), run_time=1.5)
  ```
- Slicing (cross-sections): no fork-verified recipe. Probe it before planning it.
- Depth test, labels and camera pitfalls: best-practices §9.

## Visual metaphors → recipe

| Metaphor (composer) | Show | Recipe |
|---|---|---|
| Vectors as arrows | position from the origin; tip-to-tail addition; scaling | `Vector`, Tip-to-tail sum, `put_start_and_end_on` |
| Functions as machines | input goes in, transformation, output comes out | boxes and arrows (`Rectangle`, `Text`, `Arrow(buff=0)`); no special API |
| Matrices as transformations | grid transformed, basis vectors tracked, determinant as area | Matrices as transformations, Determinant as area |
| Derivatives as slopes | tangent touching the curve; zoom in for local linearity; slope changing as the point moves | Tangent sweep; zoom with `self.frame` (Scene composition) |
| Integrals as accumulation | Riemann rectangles; width → 0; area filling | Riemann → area |

## Scene composition

```
Golden layout                    Side by side
┌───────────────────────────┐    ┌─────────────┬─────────────┐
│       TITLE / CONTEXT     │    │  BEFORE /   │  AFTER /    │
├───────────────────────────┤    │  CONCEPT A  │  CONCEPT B  │
│     MAIN VISUALIZATION    │    └─────────────┴─────────────┘
├───────────────────────────┤
│     EQUATION / FORMULA    │
└───────────────────────────┘
```

- Golden layout: title `to_edge(UP)`. If the camera moves, `title.fix_in_frame()` keeps it on screen (F:manimlib/mobject/mobject.py:1924).
- Side by side: `VGroup(a, b).arrange(RIGHT, buff=1)`, or the imcommit wide canvas with `self.frame` moving between regions (imcommit-patterns.md Layout).
- Zoomed detail: the fork has no `ZoomedScene` or `MovingCameraScene` (best-practices §2), so there is no picture-in-picture inset. Zoom the whole frame [verified by run, examples/camera.py]:
  1. `self.frame.save_state()`
  2. `self.play(self.frame.animate.move_to(x).set_height(h))`
  3. `self.play(Restore(self.frame))`

## Transitions

| Composer pattern | Fork |
|---|---|
| Zoom focus: full → zoom into detail → explain → zoom out | the frame `save_state` / `Restore` above, inside one scene |
| Side-by-side build: fill left, fill right, connect | `arrange(RIGHT)`; build left, then right, then connect (`Arrow(buff=0)`, matching colors) |
| Transform chain: A → B → C | only inside one scene. At a scene boundary the next class rebuilds the previous End state (workflow §2.1); plan the cut in the scenes.md **Next** line |
| Reset and rebuild: fade most, focus on one, build again | `self.play(FadeOut(VGroup(a, b, c)))` on named targets. Never `self.clear()` or `remove_all_except()`: both also remove `self.frame` (best-practices §9) |

## Timing

| Action | Composer | Fork default / imcommit |
|---|---|---|
| Simple shape creation | 0.5–1 s | `run_time` 1.0 (F:manimlib/animation/animation.py:19). imcommit's most common value is 0.5 (179×) |
| Text/equation writing | 1–2 s | `Write`: 1 s for fewer than 15 parts with points (glyphs), else 2 s (F:manimlib/animation/creation.py:156,166-169) |
| Transformation | 1–2 s | `TransformMatching*` 2 s (F:manimlib/animation/transform_matching_parts.py:29) |
| Camera movement | 2–3 s | write `run_time`. imcommit leaves 114 of its 128 camera plays (`cf.animate`/`frame.animate`) at the default 1 s, faster than the composer's 2–3 s |
| Pause for absorption | 0.5–1 s | `self.wait()` = 1 s (F:manimlib/default_config.yml:76). imcommit's `playw` waits 1 s after each play |
| Complex animation | 2–4 s | write `run_time` |

- Rhythm: fast-fast-SLOW-fast-fast-SLOW. Quick for setup, slow for the key insight: the **Aha moment** block gets the SLOW beat.
- imcommit counts: imcommit-patterns.md Timing.

## Colors (replaces the composer's hex palettes)

- Use named constants. imcommit has 0 hex literals (imcommit-patterns.md Color).
- The composer's "Classic 3b1b" palette maps to constants: #58C4DD = `BLUE` (F:manimlib/default_config.yml:138), #83C167 = `GREEN` (:148), #FFFF00 = `YELLOW` (:153). Its #FF6666 is no constant: use `RED` #FC6255 (:163) or `RED_B` #FF8080 (:164).
- Its background #1C1C1C is not the fork's #000000 (F:manimlib/default_config.yml:56). Keep black unless the user asks; to change it, see style-and-color.md §D, then recheck contrast.
- The "High Contrast" and "Soft Academic" palettes are not ported (hex only).
