# Animation semantics on the fork

What `play` actually does with transforms, `.animate`, groups and timing kwargs. Most of it is manimgl-wide: where upstream behaves the same, it is cited with `U:` so nobody tries to "fix" it through [fork-diff.md](fork-diff.md).

- Render-verified example: [examples/compositions.py](../examples/compositions.py). Its asserts check the scene membership after `TransformMatchingTex`, `Transform` and `ReplacementTransform` and after clearing the screen, so exit 0 verifies those §1 rows.
- `[verified by run, no render]`: constructed the animation in the fork env and called `begin`/`interpolate` like `Scene.play` does (F:manimlib/scene/scene.py:542-566).

## 1. What is on screen after each transform

`play` adds any animated mobject that is not on screen yet (F:manimlib/scene/scene.py:551-553). What stays afterwards depends on the animation:

| Call | On screen after the play | Keep using | Evidence |
|---|---|---|---|
| `Transform(a, b)` | `a`, now shaped like `b`. `b` is never added | `a` | F:manimlib/animation/transform.py:25,89-93 [verified by run] |
| `ReplacementTransform(a, b)` | `b`. `a` is removed | `b` | F:manimlib/animation/transform.py:132-133 [verified by run] |
| `TransformFromCopy(a, b)` | `a` and `b` | both | F:manimlib/animation/transform.py:136-140 |
| `FadeTransform(a, b)` | `b`. `a` is removed and restored to its pre-play state | `b` | F:manimlib/animation/fading.py:104,132-137 |
| `TransformMatchingTex/Strings/Shapes(a, b)` | `b`. The pieces of `a` are removed | `b` | F:manimlib/animation/transform_matching_parts.py:112-115 [verified by run] |
| `FadeOut(x)`, `Uncreate(x)` | nothing. `x` is removed. `FadeOut` also resets `x` to its pre-play state (`final_alpha_value=0`) | after `FadeOut`, `self.add(x)` brings it back as it was | F:manimlib/animation/fading.py:47-61, F:manimlib/animation/animation.py:79-80,85-87, F:manimlib/animation/creation.py:56-71 |

- After `Transform(a, b)`, `b` is not on screen. `FadeOut(b)` adds `b`, fades it out and removes it, so a second copy flashes. `b.animate...` adds `b` and **leaves it on screen**, so a second copy stays next to `a` [verified by run]. Animate `a`, the on-screen object.
- Equation chains: pass the on-screen object and rebind the name [verified by run, examples/compositions.py `RebindDerivation`].
  ```python
  for tex in (R"x^2 = 4", R"x = \pm 2"):
      nxt = Tex(tex).move_to(eq)
      self.play(TransformMatchingTex(eq, nxt, run_time=1))
      eq = nxt
  ```
- Never pass `eq.copy()` as the source. The copy is transformed and the original stays, so every step stacks on the previous ones. A 3-step chain ended with three overlapping Tex objects [verified by run].

## 2. `.animate` and targets

### Same mobject, last target wins

- `mob.animate` calls `mob.generate_target()` as soon as it is accessed (F:manimlib/mobject/mobject.py:2254). The chained methods edit that target (:2260-2281).
- `.animate` builders are built (and read `mob.target`) when `play` or the group constructor runs (F:manimlib/mobject/mobject.py:2322-2328). `MoveToTarget(mob)` reads `mob.target` when it is constructed (F:manimlib/animation/transform.py:146). So two `.animate` on one mobject both go to the **last** target, and a `MoveToTarget` built earlier keeps its own target. Which one wins then depends on list order [verified by run, no render].
- This holds inside `AnimationGroup`, `LaggedStart` and `Succession` too [verified by run, no render]:
  - `AnimationGroup(sq.animate.shift(RIGHT * 3), sq.animate.set_color(RED))` only recolours. `sq` ends at the origin.
  - `Succession(d.animate.shift(UP), d.animate.shift(DOWN))` moves `d` down by 1 and never up (y = -1.0 at mid and at the end).
- For a sequence on one mobject, use separate `self.play` calls, or chain the methods in one `.animate`.
- Do not mix `MoveToTarget(mob)` and `mob.animate` in one play: `.animate` regenerates `mob.target`.
- Parent and child `.animate` in one play: SKILL.md §11 Timing.

### `generate_target` / `MoveToTarget`

- `mob.generate_target()` stores a copy in `mob.target` and returns it (F:manimlib/mobject/mobject.py:705-708). Edit it, then `self.play(MoveToTarget(mob))` (F:manimlib/animation/transform.py:143-146).
- Use it when final positions depend on each other. `.animate` cannot lay out several objects jointly [verified by run, examples/compositions.py `JointTargets`]:
  ```python
  VGroup(a.generate_target(), b.generate_target(), new).arrange(RIGHT, buff=0.5)
  self.play(MoveToTarget(a), MoveToTarget(b), FadeIn(new))
  ```
- Per-submobject edits: call `g.generate_target()` once, then edit `g.target[i]` in a loop, then `MoveToTarget(g)`.
- Without a prior `generate_target()`, `MoveToTarget(mob)` still constructs. `Mobject.__init__` sets `target = None` (F:manimlib/mobject/mobject.py:106), so the `hasattr` check (F:manimlib/animation/transform.py:148-152) never fires.
  - The play then fails with the misleading `Exception: MoveToTarget.create_target not properly implemented` (F:manimlib/animation/transform.py:83-87) [verified by run, no render].
- imcommit uses this heavily: [imcommit-patterns.md](imcommit-patterns.md) Targets.

### Rotations

- `.animate.rotate(θ)` moves each point in a straight line to its rotated position. The shape shrinks mid-way by cos(θ/2) [verified by run]:
  - 90°: corner radius 1.0 instead of 1.414 at mid (0.71)
  - 180°: the whole shape collapses to a point at mid
- For turns of about 90° or more, use one of:
  - `Rotate(mob, θ, axis=...)`: rigid, 1 s, smooth, about the center (F:manimlib/animation/rotation.py:58-75). Next to a longer animation, give it the play's run_time (§3 Timings)
  - `mob.animate(path_arc=θ, path_arc_axis=axis).rotate(θ, axis=axis)`: `.animate(**kw)` passes `path_arc` to the Transform (F:manimlib/mobject/mobject.py:2283-2284, F:manimlib/animation/transform.py:31-52)
- The arc axis must match the rotation axis. For `rotate(PI, axis=RIGHT)`, `path_arc_axis=RIGHT` stays rigid (1.414), and the default OUT axis distorts the shape (2.0) [verified by run, no render].
- imcommit uses `.animate.rotate` 24 times, up to `PI / 1.8` (I:src/curseofknowledge/main.py:630). At that angle the shrink is visible (0.64 at mid).

## 3. Composition

### Succession is not separate plays

- `play` adds every member's mobject at the start (F:manimlib/scene/scene.py:542-553), but `Succession.begin` begins only the first member (F:manimlib/animation/composition.py:133-136).
  - Later members are drawn as they currently are until their turn, then jump to their start state.
  - `Succession(ShowCreation(a), FadeIn(b))` shows `b` fully opaque while `a` is being drawn [verified by run, examples/compositions.py `LaggedVsSuccession`].
- Time is split equally between members (F:manimlib/animation/composition.py:144-147). The members' own `run_time` values only set the total.
  - `Succession(FadeIn(a, run_time=3), FadeIn(b, run_time=1))` lasts 4 s, and `b` starts at 2 s [verified by run, no render].
- Upstream behaves the same (U:manimlib/animation/composition.py:145-148).
- Under `-s`/`-sw`, `play` interpolates once at alpha=1 (F:manimlib/scene/scene.py:474-475), and `Succession.interpolate` jumps from the first member straight to the last (F:manimlib/animation/composition.py:144-153, F:manimlib/utils/bezier.py:144-145). Middle members never run, so the `-sw` PNG can differ from the mp4: `Succession(FadeIn(sq), Rotate(sq, PI / 4), Indicate(sq))` ends unrotated with `-sw` and rotated 45° in the movie [verified by run].
- Instead, use `LaggedStart(A, B, lag_ratio=1)` [verified by run, examples/compositions.py `LaggedVsSuccession`]:
  - All members begin at t=0, so later ones wait at their start state (invisible for `FadeIn`, `ShowCreation`, `Write`).
  - Each member keeps its own run_time.
  - Only when the members animate independent mobjects: not the same one, not a group and one of its members, and no member placed or targeted relative to an earlier member's result.
  - Because every member begins at t=0 (F:manimlib/animation/composition.py:63-66), a later member resets its mobject to its begin-time copy every frame until its turn. `LaggedStart(FadeIn(sq), sq.animate.shift(RIGHT * 2), lag_ratio=1)` keeps `sq` at opacity 0 for the first second, then fades and moves it at once [verified by run]. `LaggedStart(FadeIn(g), g[1].animate.shift(UP), lag_ratio=1)` keeps `g[1]` at opacity 0 while the rest of `g` fades in [verified by run, no render].
  - Every member, its arguments and its `.animate` target are evaluated when the `LaggedStart(...)` expression runs (F:manimlib/animation/composition.py:38). `LaggedStart(eq.animate.shift(UP * 2), FadeIn(new.next_to(eq, DOWN)), lag_ratio=1)` puts `new` under the old `eq`, 2.25 below the moved one [verified by run].
  - For a chain on one mobject, or steps that depend on each other, use separate `self.play` calls.
- Or use separate `self.play` calls.

### Play-level and group-level kwargs

- `self.play(..., run_time=, rate_func=, lag_ratio=)` writes these onto each animation passed to `play` (F:manimlib/scene/scene.py:588-589, F:manimlib/animation/animation.py:126-135).
- `rate_func` on an `AnimationGroup`, `LaggedStart` or `Succession` is ignored. The group's `interpolate` never calls it (F:manimlib/animation/composition.py:108-121). Upstream is the same (U:manimlib/animation/composition.py:113).
  - Exception: the `LaggedStartMap` and `TransformMatching*` constructors forward `rate_func=` to each member, where it works (F:manimlib/animation/composition.py:175-178, F:manimlib/animation/transform_matching_parts.py:37,95) [verified by run, no render].
  - `self.play(AnimationGroup(sq.animate.shift(RIGHT * 4)), rate_func=there_and_back)` ends at x=4. Without the group it ends at x=0 [verified by run, no render].
  - Give `rate_func=` to each member: `mob.animate(rate_func=there_and_back).shift(UP)`, `FadeIn(m, rate_func=linear)`.
- `lag_ratio` staggers the submobjects inside one animation, not the animations against each other (F:manimlib/animation/animation.py:168-182).
  - `self.play(FadeIn(a), FadeIn(b), lag_ratio=0.5)` plays `a` and `b` together [verified by run, no render]. Use `LaggedStart`.
  - On a group it does nothing: member timings are fixed in the constructor (F:manimlib/animation/composition.py:39,90-106).
- The values are merged with `or`, so `lag_ratio=0` and `run_time=0` at play level are silently dropped (F:manimlib/animation/animation.py:132-134).
  - `ShowCreation` defaults to `lag_ratio=1.0` (F:manimlib/animation/creation.py:49). `self.play(ShowCreation(group), lag_ratio=0)` still draws the members one after another [verified by run, no render].
  - Use `ShowCreation(group, lag_ratio=0)`.

### Delays without `Wait`

- The fork has no `Wait` animation (0 grep hits in the fork, upstream and raenimgl). To delay one member inside a play, use either:
  - `time_span=(start, end)` on that member (F:manimlib/animation/animation.py:29,68-70,148-152). `FadeIn(c, time_span=(1, 2))` runs 2 s, with opacity 0 at 0.5 s and 0.5 at 1.5 s [verified by run].
  - `rate_func=squish_rate_func(smooth, a, b)` with a matching `run_time` (F:manimlib/utils/rate_functions.py:79-94) [verified by run], but only for animations with `lag_ratio=0` (FadeIn, `.animate`, Transform) or a single piece. The rate_func is applied per submobject after the lag split (F:manimlib/animation/animation.py:154-157,168-182), so on `Write`, or on `ShowCreation` of Text/Tex/a group, each piece is squished inside its own window and drawing starts early: `Write(Text("이 문장은 열다섯 글자를 넘는 긴 문장입니다"), run_time=3, rate_func=squish_rate_func(linear, 2 / 3, 1))` already has 10 of 18 glyphs filled at t=1.95 [verified by run, no render]. Use `time_span` there.
- Before its span the member sits at its start state, so a delayed `FadeIn` stays invisible [verified by run, examples/compositions.py `SpanDelays`].
- `time_span=` on the group itself is ignored in the fork ([fork-diff.md](fork-diff.md)).
- Wave: `LaggedStart(*[d.animate(rate_func=there_and_back).shift(UP) for d in dots], lag_ratio=0.1)`. The easing goes on each member because the group's rate_func is ignored [verified by run, examples/compositions.py `SpanDelays`].

### Timings

- A play lasts as long as its longest animation (F:manimlib/scene/scene.py:493-494). `play` passes each animation alpha = t / its own run_time (F:manimlib/scene/scene.py:562), so a shorter one sees alpha above 1. Most clip it and hold (F:manimlib/animation/animation.py:181).
  - `Rotate`/`Rotating`, `UpdateFromAlphaFunc` and `ChangingDecimal`/`ChangeDecimalToValue`/`CountInFrom` use the unclipped alpha (F:manimlib/animation/rotation.py:51, F:manimlib/animation/update.py:49, F:manimlib/animation/numbers.py:32-34; same upstream, U:manimlib/animation/rotation.py:51, U:manimlib/scene/scene.py:557). They keep going after their run_time and snap back only at `finish`.
  - `self.play(Rotate(sq, PI / 4), FadeIn(c, run_time=2))` spun `sq` about 4 extra turns between t=1 and t=2, and the movie's last frame shows it unrotated. The `-sw` PNG still looks right [verified by run].
  - Give these the play's run_time (`self.play(..., run_time=2)`) or `time_span=(0, 1)` [verified by run], wrap them in `AnimationGroup(...)` [verified by run, no render], or play them on their own.
- Member timings: `[(s, e) for _, s, e in group.anims_with_timings]` (F:manimlib/animation/composition.py:90-106).
- A `LaggedStart` of n members of T s with lag r lasts (n-1)·r·T + T, and member i starts at i·r·T. 5 × 1 s at 0.2 gives 1.8 s, starts 0, 0.2 … 0.8 [verified by run, no render].
- `run_time=` on a group rescales every time by run_time / max_end_time (F:manimlib/animation/composition.py:41,114).

## 4. Default durations

Measured by constructing each animation in the fork env [verified by run, no render].

| Animation | run_time | rate_func / note |
|---|---|---|
| Most: `FadeIn/Out`, `FadeTransform`, `Transform`, `ReplacementTransform`, `ShowCreation`, `Uncreate`, `GrowFrom*`, `GrowArrow`, `Indicate`, `Flash`, `FlashAround`, `MoveAlongPath`, `Rotate`, `Restore`, `MoveToTarget`, `.animate` | 1 | smooth. `Indicate`, `CircleIndicate`: there_and_back |
| `Write` | 1 below 15 path pieces, else 2 | linear. For `Text`, about one piece per glyph (F:manimlib/animation/creation.py:144-174) |
| `DrawBorderThenFill` | 2 | double_smooth (F:manimlib/animation/creation.py:74-97) |
| `TransformMatchingTex/Strings/Shapes` | 2 | F:manimlib/animation/transform_matching_parts.py:29 |
| `LaggedStartMap` | 2 | lag 0.05 (F:manimlib/animation/composition.py:166-174) |
| `ShowCreationThenFadeOut`, `ShowCreationThenFadeAround`, `WiggleOutThenIn`, `FocusOn` | 2 | |
| `ApplyPointwiseFunction`, `ApplyMatrix`, `Homotopy`, `ApplyWave`, `Broadcast` | 3 | F:manimlib/animation/transform.py:198-206,272-284, F:manimlib/animation/movement.py:24, F:manimlib/animation/specialized.py:25. `ApplyWave` drops its own `run_time` (F:manimlib/animation/indication.py:338,352, U:manimlib/animation/indication.py:338,352), so `ApplyWave(m, run_time=1)` still lasts 3 s; use `self.play(ApplyWave(m), run_time=1)` |
| `Rotating` | 5 | linear, `angle=TAU` (F:manimlib/animation/rotation.py:17-29) |
| `AnimationGroup` | longest member | |
| `LaggedStart` | (n-1)·r·T + T | default lag 0.05 (F:manimlib/animation/composition.py:24). Two 1-s members: 1.05 s |
| `Succession` | sum | time split equally (§3) |

- `ShowCreation` and `Uncreate` default to `lag_ratio=1.0`, so a group is drawn one member after another.
- A Korean sentence of 15 or more glyphs makes `Write` take 2 s. `Text("이 문장은 열다섯 글자를 넘는 긴 문장입니다")` has 18 pieces [verified by run, no render]. The whole play then lasts 2 s, so pass `run_time` explicitly.

## 5. Small semantics

- `FadeIn(m, scale=s)` starts at 1/s of the final size (F:manimlib/animation/fading.py:39-44) [verified by run, no render].
  - `scale=0.5` starts at double size and shrinks in. `scale=2` starts at half size and grows.
  - `FadeOut(m, scale=s)` ends at s times the size (F:manimlib/animation/fading.py:63-68).
- `NumberPlane`/`ComplexPlane` grid lines are single curves. Call `plane.prepare_for_nonlinear_transform()` before `apply_function`, `apply_complex_function`, `ApplyPointwiseFunction`, `ApplyComplexFunction` or `Homotopy` (F:manimlib/mobject/coordinate_systems.py:722-728).
  - It inserts curves up to 50 per line. Without it, only the endpoints move and the lines stay straight [verified by run].
  - For other low-curve VMobjects (`Line`, `Polygon`), call `mob.insert_n_curves(n)` first.
- Rate functions (F:manimlib/utils/rate_functions.py:13-109): `linear`, `smooth` (default), `rush_into`, `rush_from`, `slow_into`, `double_smooth`, `there_and_back`, `there_and_back_with_pause`, `running_start`, `overshoot`, `not_quite_there`, `wiggle`, `squish_rate_func`, `lingering`, `exponential_decay`.
  - `rush_into` starts slow and ends fast, `rush_from` starts fast and ends slow: rush_into(0.1)=0.002, rush_from(0.1)=0.186 [verified by run, no render].
  - There are no CE `ease_in_*`/`ease_out_*` functions (0 grep hits).
- `always` vs `f_always`:
  - `label.always.next_to(dot, UP)` re-runs `next_to(dot, UP)` every frame with the same arguments, so it follows `dot` (F:manimlib/mobject/mobject.py:176-183,2339-2349) [verified by run, no render].
  - The function form is `always(label.next_to, dot, UP)` (F:manimlib/mobject/mobject_update_utils.py:26-31).
  - `f_always` calls every argument first, so each argument must be a zero-argument callable (F:manimlib/mobject/mobject.py:2352-2368): `number.f_always.set_value(tracker.get_value)`.
  - `label.f_always.next_to(dot, UP)` fails as soon as it is attached with `TypeError: 'Dot' object is not callable`, because `add_updater` runs the updater once [verified by run, no render].
- `VGroup` accepts only VMobjects (F:manimlib/mobject/types/vectorized_mobject.py:1312-1316).
  - `VGroup(Circle(), Sphere())` and `VGroup(Circle(), GlowDot())` raise `Exception: Only VMobjects can be passed into VGroup` [verified by run, no render].
  - Group surfaces, `DotCloud`/`GlowDot`/`TrueDot` and images with `Group(...)`. `AnimationGroup` falls back to `Group` when the animations are passed as separate arguments or a list (F:manimlib/animation/composition.py:48-51). A bare generator (`LaggedStart(FadeIn(m) for m in mobs)`) is consumed before that check (:37-38) and raises the same exception, so unpack it: `LaggedStart(*(FadeIn(m) for m in mobs))` [verified by run, no render].
- `self.mobjects` starts with `self.frame` (F:manimlib/scene/scene.py:117). `InteractiveScene` also adds `selection_highlight` (F:manimlib/scene/interactive_scene.py:133).
  - So `FadeOut(m) for m in self.mobjects` also removes the frame, like `clear()` (SKILL.md §9). Ambient rotation then stops: θ stayed 0.0 after 1 s, 30.0 with the frame excluded [verified by run].
  - To clear the screen: `self.play(FadeOut(Group(*(m for m in self.mobjects if m is not self.frame and m is not getattr(self, "selection_highlight", None)))))`, or name the targets explicitly [verified by run, examples/compositions.py `SpanDelays`]. Excluding only the frame also removes an `InteractiveScene`'s `selection_highlight`, so selections are no longer highlighted in the preview window [verified by run].
- Seeds: `Scene.__init__` reseeds `random` and `np.random` with the class attribute `random_seed`, default 0 (F:manimlib/scene/scene.py:53,139-141).
  - Module-level `seed(41)` / `np.random.seed(41)` never reach `construct()`. Module seeds 41 and 99 gave identical `random_color()` values [verified by run].
  - A `random_seed = 41` class attribute holds only for a solo render. `manimgl main.py A B` builds every scene before the first runs, so the next scene's `__init__` reseeds the stream ([cli-and-output.md](cli-and-output.md) §7) [verified by run].
  - Make `random.seed(41); np.random.seed(41)` the first line of `construct` ([examples/structure.py](../examples/structure.py)). `random_seed = None` turns the reseed off.
  - raenimgl does not override it (0 grep hits in R:).

## 6. Generic manimgl docs vs the fork

Claims seen in generic manimgl guides that fail or behave differently on the fork.

- Source of the claims: adithya-s-k/manim_skill @cef0450, `skills/manimgl-best-practices/rules/` (CC BY-NC-SA 4.0). The left column quotes short fragments only. The fork behaviour and fixes are this plugin's own probes.

| Generic docs say | On the fork | Evidence |
|---|---|---|
| `Succession` is equivalent to separate play calls | Later members show early, time is split equally (§3) | F:manimlib/animation/composition.py:133-147 [verified by run] |
| `self.play(LaggedStart(...), rate_func=smooth)` eases the whole group | Ignored. Put `rate_func` on each member | F:manimlib/animation/composition.py:108-121 [verified by run, no render] |
| Wave: `Succession(Wait(delay), dot.animate.shift(UP), dot.animate.shift(DOWN))` | `Wait` is a NameError. Both builders go to the last target, so the dot only moves down. Use `.animate(rate_func=there_and_back)` in a `LaggedStart` | §2, §3 [verified by run, no render] |
| `AnimationGroup(sq.animate.shift(RIGHT * 3), sq.animate.set_color(c))` shifts and recolours | Only recolours | F:manimlib/mobject/mobject.py:2254,2328 [verified by run, no render] |
| Derivation: `TransformMatchingTex(eq.copy(), nxt)` | The original stays, steps stack. Pass `eq` and rebind | §1 [verified by run] |
| Fade out everything: `FadeOut(mob) for mob in self.mobjects` | Also removes `self.frame` | F:manimlib/scene/scene.py:117 [verified by run] |
| Animation i starts at `i * lag * group.get_run_time()` | Starts at i·lag·T (T = member run_time). Read `anims_with_timings` | F:manimlib/animation/composition.py:90-106 [verified by run, no render] |
| `FadeIn(m, scale=0.5)` starts at half size | Starts at double size (1/scale) | F:manimlib/animation/fading.py:39-44 [verified by run, no render] |
| `rush_into` is fast then slow, `rush_from` slow then fast | Swapped | F:manimlib/utils/rate_functions.py:24-29 [verified by run, no render] |
| `grid.animate.apply_function(f)` makes a NumberPlane wavy | Lines stay straight without `prepare_for_nonlinear_transform()` | F:manimlib/mobject/coordinate_systems.py:722-728 [verified by run] |
| `label.f_always.next_to(dot, UP)` | TypeError on attach. Use `label.always.next_to(dot, UP)` | F:manimlib/mobject/mobject.py:2352-2368 [verified by run, no render] |
| `ShowCreation(m, reverse=True)` | TypeError. `Uncreate(m)` (also removes `m`) | F:manimlib/animation/creation.py:48-71 [verified by run, no render] |
| `FadeIn(m, introducer=True)` | TypeError. `play` adds non-scene mobjects by itself | F:manimlib/animation/animation.py:23-44 [verified by run, no render] |
| `Rotating(m, radians=TAU)` | TypeError. `Rotating(m, angle=TAU)` | F:manimlib/animation/rotation.py:17-29 [verified by run, no render] |
| `ScaleInPlace(m, 0.5, about_point=p)` | TypeError. `m.animate.scale(0.5, about_point=p)` | F:manimlib/animation/transform.py:233-240 [verified by run, no render] |
| `arrange_in_grid(rows=2, cols=3)` | TypeError. `n_rows=`, `n_cols=` or positional | F:manimlib/mobject/mobject.py:538-550 [verified by run, no render] |
| `Star()`, `SpinInFromNothing(m)` | NameError (CE classes; not in the fork, upstream or raenimgl) | 0 grep hits [verified by run, no render] |
| `camera_class = ThreeDCamera` gives a 3D camera | Silently ignored. `Scene` always builds `Camera`. Use `ThreeDScene` or `samples = 4` | F:manimlib/scene/scene.py:107-111, F:manimlib/camera/camera.py:258-261 [verified by run] |
| Module-level `np.random.seed(n)` fixes the scene's randomness | Overwritten by `Scene.random_seed` (default 0). Seed inside `construct` | F:manimlib/scene/scene.py:53,139-141 [verified by run] |
