# Gallery: ported scenes for ML and math topics

**License: CC BY-NC-SA 4.0 (Attribution, NonCommercial, ShareAlike). This applies to every `.py` file in this folder. It is not the license of the rest of the plugin.** See [LICENSE.txt](LICENSE.txt).

- Source: [adithya-s-k/manim_skill](https://github.com/adithya-s-k/manim_skill) @ `cef045011722d285692e3381d12d4d637da56e18`, `skills/manimgl-best-practices/examples/`.
- Original video code by Grant Sanderson (3Blue1Brown, [3b1b/videos](https://github.com/3b1b/videos)). Adapted by Adithya S Kolavi. Modified for the CodingVillainKor/manimgl fork @455a420 by manimgl-skill.
- Each file's docstring names its source file and lists the changes. The table below summarises them.
- Do not copy this code into MIT or commercial work. ShareAlike: a modified version must keep this license.

## Files

| File | Scenes | Shows | Main changes from the source |
|---|---|---|---|
| [vector_field_flow.py](vector_field_flow.py) | `VFSimpleVectorField`, `VFParticleFlow`, `VFElectricDipole`, `VFNativeStreamLines` | Arrow grids colored by magnitude, particles carried by a field, a dipole field, the fork's `VectorField`/`StreamLines`/`AnimatedStreamLines` | `stroke_color` added to `background_line_style` (KeyError otherwise), Dot colors via `set_color`, magnitude alpha clipped to 1, sub-stepped paths instead of Euler updaters so the `-sw` PNG matches the video, native stream-line scene added (seed inside `construct`), `GradientFieldDemo` dropped |
| [exponential_derivative.py](exponential_derivative.py) | `ExpDerivative`, `ExpFamilyGraph`, `ComplexExpSpiral` | Moving tangent on e^t, the e^{st} family via `bind_graph_to_func`, e^{(a+bi)t} as a spiral with a live complex readout | Graphs cut at the axes top, Tex parts via `isolate=`/`t2c=`, tracker-driven complex `s` readout, old trail dimmed after `clear_updaters` |
| [attention_softmax_mask.py](attention_softmax_mask.py) | `AttentionSoftmaxMasking` | Numeric attention grid, causal mask to -∞ via `MoveToTarget`, per-column softmax | Korean titles, numbers sized to their cells, softmax helper replaced by two numpy lines, `LaggedStart` takes a list, seed inside `construct` |
| [matrix_vector_product.py](matrix_vector_product.py) | `WeightMatrixProduct` | `DecimalMatrix` with ellipses and sign colors, row-by-vector highlight, `CountInFrom` result | Result is the true W @ x, rows paired by index past the ellipsis row, highlight covers every entry, brackets sized for final values, Korean caption |
| [neural_network.py](neural_network.py) | `NeuralNetworkBasic` | Reusable MLP `VGroup` class, weight-colored edges, layer-by-layer `VShowPassingFlash` forward pass | `get_forward_pass()` added (one `LaggedStartMap` per layer, fixed flash width), Korean labels in one row, seed inside `construct` |
| [token_sampling.py](token_sampling.py) | `TokenSamplingAnimation`, `TemperatureSampling` | Probability bars, sampling highlight, temperature reshaping one chart live through a `ValueTracker` | Korean prompt and tokens, bars share one left edge, chosen token fills the prompt, seed inside `construct`, `set_color` instead of `Text(color=)` |
| [gradient_descent.py](gradient_descent.py) | `GradientDescentBasic`, `GradientDescent3D` | Exact level sets with a GD path and counters, a ball descending a height-colored 3D loss surface | Level sets through `axes.c2p` and the true gradient (the source used 0.15 for d(0.3xy)), counters with `DecimalNumber`/`Integer`, `self.frame.reorient`, ball kept visible with `set_z_index(-1)` |
| [equation_derivation.py](equation_derivation.py) | `QuadraticFormula`, `ColorCodedSubstitution` | A stacked `TransformMatchingTex` derivation (the `.copy()` stack is intentional here), a color-coded u-substitution | Steps fit the frame, Korean step labels, boxed parts listed in `isolate=`, = signs aligned |
| [word_vector_analogy.py](word_vector_analogy.py) | `WordVectorAnalogy` | 왕 − 남자 + 여자 ≈ 여왕 as 3D arrows, billboarded Korean labels, a screen-fixed equation | Arrows colored with `set_color` and turned to the camera, labels billboarded through a rolled `reorient`, standalone 왕 picked with `select_part`, seed inside `construct` |

## Render

Copy a file into a scratch folder inside your uv project (renders write `videos/` and `__pycache__/` next to the cwd and the file), then:

```bash
uv run manimgl vector_field_flow.py VFParticleFlow -sw </dev/null     # last frame -> videos/VFParticleFlow.png
uv run manimgl vector_field_flow.py VFParticleFlow -w -l </dev/null   # 480p draft -> videos/VFParticleFlow.mp4
```

- Judge `ComplexExpSpiral` and `WordVectorAnalogy` from the mp4. ComplexExpSpiral runs on a dt updater + `TracedPath`, so its `-sw` PNG has no trail. WordVectorAnalogy's ambient rotation is a dt updater that `-sw` runs twice per play with dt=run_time, so the PNG's camera ends 10° further round (θ -64° in the PNG, -74° in the mp4) (F:manimlib/scene/scene.py:474-475,570-572).
- Verified: every scene above rendered with `-sw` and `-w -l`, exit 0, as part of `scripts/check_examples.sh` (64/64 renders with `examples/`). The porters checked each PNG and a frame sheet of each mp4 by eye.

## Pitfalls found while porting

Each was printed by a probe or seen in a render [verified by run]; the cited fork lines were opened at @455a420. Pitfalls that belong in the main rules are in SKILL.md (constructor `stroke_color=` on `Arrow`, updaters during animations, `ThreeDAxes` z placement, `set_z_index(-1)` under a translucent surface, `TransformMatchingTex` near `\frac`, `select_part`).

| Pitfall | Fix | Evidence |
|---|---|---|
| `interpolate_color(c1, c2, alpha)` with alpha > 1 extrapolates; a channel that falls below 0 becomes NaN and the color is drawn white (BLUE→YELLOW: blue channel). Only a RuntimeWarning shows | `min(alpha, 1)` | F:manimlib/utils/color.py:115 |
| `StreamLines` calls its `func` with one (2,) state (solve_ivp) and a `p2c` tuple; `VectorField` calls it with (N, 2) arrays. A `func` written as `c[:, 1]` raises `IndexError: too many indices` in StreamLines | `x, y = np.asarray(coords).T`, then return `np.array([...]).T` (works for both) | F:manimlib/mobject/vector_field.py:68-69,398,427-428 (StreamLines), F:manimlib/mobject/vector_field.py:186,263 (VectorField) |
| `AnimatedStreamLines` overrides `update`, so `clear_updaters()` and `suspend_updating()` do not stop it | `remove` or `FadeOut` it | F:manimlib/mobject/vector_field.py:471-478, F:manimlib/scene/scene.py:264-266 |
| `TracedPath` re-applies its constructor stroke on every update, so `set_stroke(opacity=0.2)` on a live trail is undone next frame | `clear_updaters()` first, then dim | F:manimlib/mobject/changing.py:121,145 |
| `TracedPath` adds one point per update call. Under `-sw` each ComplexExpSpiral trail ended with 1 traced point (1 curve point), against 240 (479 curve points) in the `-w -l` video | Judge from the mp4, or grow the path yourself with `add_line_to` in sub-steps | F:manimlib/mobject/changing.py:123-127 |
| `axes.get_graph(f)` samples `x_range` only and is not clipped to `y_range`. e^t ran out of the frame | Pass `x_range=` up to where f reaches the y max. `i2gp`/`get_tangent_line` still work past the cut | F:manimlib/mobject/coordinate_systems.py:184-213 |
| A generator passed to `LaggedStart`/`AnimationGroup` is used up before the VMobject check, so the group becomes a `VGroup` and raises `Only VMobjects can be passed into VGroup` for `FadeTransform` | Pass a list, or `group_type=Group` | F:manimlib/animation/composition.py:37-38,48-49 |
| Matrix ellipsis cells stay in `get_rows()`/`get_columns()` (still `DecimalNumber`, `get_value()` is the hidden number), but `get_entries()` drops them, so zipping the two drifts after the ellipsis row | Pair by index, or test `c in m.ellipses` | F:manimlib/mobject/matrix.py:159-165,205-206 |
| `DecimalNumber.set_value` keeps the left edge and the old style. A growing number spills out of its bracket and a sign color does not follow | Build from the final values, then count up to them | F:manimlib/mobject/numbers.py:51,207-215 |
| `CountInFrom`, `ChangeDecimalToValue`, `ChangingDecimal` ignore `rate_func` (linear at alpha 0.25 with `smooth`) | `UpdateFromAlphaFunc(d, lambda m, a: m.set_value(...))` | F:manimlib/animation/numbers.py:31-34 |
| `Integer` and 0-decimal `DecimalNumber` show `int(x)`, truncated, while `Integer.get_value()` rounds: `Integer(34.99)` shows 34 | Pass `round(x)` | F:manimlib/mobject/numbers.py:135-136,238-239 |
| A mobject stretched to width 0 cannot be stretched back: `rescale_to_fit` returns early | Floor the width at 1e-3 | F:manimlib/mobject/mobject.py:1150-1152 |
| `VShowPassingFlash` sets a width per point, so on a bare `Line` (3 points) the flash cannot travel | `insert_n_curves(20)` first. It is `remover=True`, so flash a `.copy()` | F:manimlib/animation/indication.py:200,219-245 |
| One flat `LaggedStartMap` over every edge of a multi-layer net lights all layers at once | One `LaggedStartMap` per layer inside `LaggedStart(lag_ratio=0.6)` | F:manimlib/animation/composition.py:90-106 |
| `get_width()` is the bounding-box width, not the stroke width | `get_stroke_width()` | F:manimlib/mobject/mobject.py:1578-1579, F:manimlib/mobject/types/vectorized_mobject.py:372-374 |
| `set_backstroke` on small Text (font_size 24) does not hide a line under it: width 5 is a thin ring, 10-15 draws seams | Move the label off the line | render crops |
