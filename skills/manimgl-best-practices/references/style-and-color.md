# Style and color reference

Target: fork @455a420. Evidence notation is the same as in SKILL.md (`F:` fork, `U:` upstream @fafa083, `[verified by run]`).

- `[verified by run]` means a probe printed the value or I looked at the `-sw` PNG (Windows 11, MiKTeX).
- `tex_mobject.py`, `shape_matchers.py`, `constants.py`, `utils/color.py` and `utils/tex.py` are identical upstream, and `set_stroke`/`set_backstroke` have the same signatures (U:manimlib/mobject/types/vectorized_mobject.py:326-362). So §C, §E and §G use the same API upstream. §A's `set_fill` signature and §D's single-shape gradient are fork-specific: upstream `set_fill` takes `gradient_direction` and keeps a two-color linear fill (U:manimlib/mobject/types/vectorized_mobject.py:266-294). §B's default box color differs (#333333 upstream). §F is fork-specific: upstream takes WGSL.
- The "Do not use" rows are snippets that circulate in other manimgl guides and fail or misbehave in the fork.

---

## A. Stroke and backstroke [verified by run]

- `set_backstroke(color=BLACK, width=3)` is `set_stroke(color, width, behind=True)`: the stroke is drawn behind the fill (F:manimlib/mobject/types/vectorized_mobject.py:204-210).
  - Use it for labels over graphs, grids and surfaces. The fork background is black (SKILL.md §5), so a black backstroke only shows where the text overlaps something.
- Signatures: `set_fill(color, opacity, border_width)` (:157), `set_stroke(color, width, opacity, behind, flat)` (:172-178).
- `set_color` sets fill **and** stroke (:287-295). So the order decides whether the outline survives:

| Code | Result |
|---|---|
| `Text("a").set_color(RED).set_backstroke(BLACK, 5)` | red letters, black outline |
| `Text("a").set_backstroke(BLACK, 5).set_color(RED)` | stroke #FC6255 width 5. The outline becomes a fat red halo and the letters merge into a blob |
| backstroked text, then `set_fill(YELLOW)` or `.animate.set_fill(YELLOW)` | yellow letters, outline stays #000000 |
| backstroked text, then `.animate.set_color(YELLOW)` | stroke #FFFF00, outline gone |

- Rule: color first (`set_color`, `t2c=`), then `set_backstroke`. To recolor a backstroked text later, use `set_fill(X)` / `.animate.set_fill(X)`.
- `Write` keeps the backstroke (Text and Tex: stroke #000000 width 6 after `Write`).
- `eq["x"].set_color(...)` goes through the same `set_color`, so it overwrites the outline of those glyphs. Source evidence.
- A VMobject has **one** stroke. The last call wins:

| Do not use | What happens |
|---|---|
| `set_stroke(WHITE, width=4)` then `set_backstroke(BLACK, width=6)`, expecting both | only #000000 width 6, behind |
| `set_backstroke(BLACK, width=8)` then `set_stroke(WHITE, width=1)`, expecting both | #FFFFFF width 1, still `behind=True`. The black outline is gone |
| `set_backstroke(BLACK, width=8, opacity=1.0)` | `TypeError: ... unexpected keyword argument 'opacity'`. For a translucent outline: `set_stroke(BLACK, 8, opacity=0.5, behind=True)` |
| `set_stroke(WHITE, width=6, opacity=1, background=True)` | `TypeError: ... unexpected keyword argument 'background'`. The keyword is `behind=` |

- For an outline plus a backstroke on one object, stack a copy or use `VHighlight` (§C).
- Label helper. Pattern from `create_label` in adithya-s-k/manim_skill (`skills/manimgl-best-practices/rules/text.md:206-210`), rewritten: its constructor `color=` (ignored by Text, SKILL.md §6) becomes `fill_color=`, which Text honors and which a `t2c=` in `**kw` still overrides. A trailing `.set_fill(color)` would repaint the `t2c` parts [verified by run]:

```python
def label(s, color=WHITE, **kw):
    return Text(s, font_size=40, fill_color=color, **kw).set_backstroke(BLACK, 5)
```

---

## B. Background boxes [verified by run]

- `BackgroundRectangle(mob, color=None, stroke_width=0, stroke_opacity=0, fill_opacity=0.75, buff=0)` (F:manimlib/mobject/shape_matchers.py:48-70).
  - It comes with `from manimlib import *`. `from manimlib.mobject.svg.tex_mobject import BackgroundRectangle` fails.
  - `color=None` uses the yml `camera.background_color` (:59-60): #000000 in the fork (F:manimlib/default_config.yml:56), #333333 upstream.
  - It does not follow `self.set_background_color(...)`: after `set_background_color(GREY_E)` the default box was still #000000. Pass `color=` when you change the background.
- Make the box a separate object: `VGroup(BackgroundRectangle(t, fill_opacity=0.8, buff=0.1), t)`.
- Do not call `t.add_background_rectangle()` on a Text/Tex you will index or recolor.
  - Signature: `add_background_rectangle(color=None, opacity=1.0, **kwargs)` (F:manimlib/mobject/mobject.py:1485-1498). It inserts the box as submobject 0 with `add_to_back` (:490-492).
  - Both selection paths index submobjects by position: labelled spans use `self.submobjects[index]` (F:manimlib/mobject/svg/string_mobject.py:525-534), and unlisted substrings use `self[start:end]` (:563-573). So after the box is added, selection shifts by one glyph: `Text("alpha beta gamma")` goes from 14 to 15 submobjects, and `t["beta"].set_color(RED)` colors "a bet".
  - `t.set_color(YELLOW)` paints the box too (fill #FFFF00, opacity 1.0). The text vanishes into a yellow block.
  - `DecimalNumber(..., include_background_rectangle=True)` calls the same method, so `num[0]` is the box (F:manimlib/mobject/numbers.py:120-121).

---

## C. Glow [verified by run]

- `VHighlight(vmobject, n_layers=5, color_bounds=(GREY_C, GREY_E), max_stroke_addition=5.0)` (F:manimlib/mobject/types/vectorized_mobject.py:1391-1409).
  - It makes `n_layers` copies with fill opacity 0. Each copy gets a wider stroke, colored along a gradient over `color_bounds`.
- Put it behind the object: `glow = VHighlight(word, n_layers=6, color_bounds=(YELLOW, BLACK), max_stroke_addition=12).set_stroke(behind=True)`, then `self.add(VGroup(glow, word))`.
  - Without `behind=True`, glow and word share one shader wrapper (`get_shader_wrapper_list`, F:manimlib/mobject/mobject.py:2056-2066; the id includes `stroke_behind`: F:manimlib/shader_wrapper.py:352-354). That wrapper draws all fills, then all strokes (:486-492), so the glow strokes cover the word's fill: hollow yellow letters [verified by run].
  - `self.add(glow, word)` (two separate mobjects) also works [verified by run].
- The copies are made once, at construction. Keep glow and object in one VGroup so they move together.
- A hand-rolled glow built from `set_backstroke(..., opacity=)` raises TypeError (§A).

---

## D. Color values

- Named constants (F:manimlib/constants.py:79-148):
  - Families BLUE, TEAL, GREEN, YELLOW, GOLD, RED, MAROON, PURPLE, GREY, each `_A` (light) to `_E` (dark). The bare name is `_C` (:140-148).
  - Also WHITE, BLACK, GREY_BROWN, DARK_BROWN, LIGHT_BROWN, PINK, LIGHT_PINK, GREEN_SCREEN, ORANGE, PURE_RED, PURE_GREEN, PURE_BLUE (:124-135).
- Only the GREY spelling exists. These names are not in the star import and raise NameError [verified by run]:

| Do not use (ManimCE / other libraries) | Use |
|---|---|
| `GRAY`, `GRAY_A` ... `GRAY_E` | `GREY`, `GREY_A` ... `GREY_E` |
| `LIGHT_GRAY`, `DARK_GRAY`, `LIGHT_GREY`, `DARK_GREY` | `GREY_B`, `GREY_D` (or any `GREY_A`...`GREY_E`) |
| `CYAN` | `TEAL`, or `"#00FFFF"` |
| `MAGENTA` | `PINK`, `PURPLE`, or `"#FF00FF"` |
| `BROWN` | `GREY_BROWN`, `DARK_BROWN`, `LIGHT_BROWN` |
| `DARK_BLUE` | `BLUE_E` |

- A hex string works wherever a color is accepted: `Square().set_color("#FF5733").get_color()` returns `'#FF5733'` [verified by run]. No `hex_to_rgb` → `rgb_to_color` round trip is needed.
  - House style still prefers named constants: imcommit has 0 hex literals (SKILL.md §11).
- `interpolate_color(a, b, t)`, `color_gradient(colors, n)`, `average_color`, `random_bright_color` come with the star import [verified by run].
- `set_color_by_gradient(*colors)` (F:manimlib/mobject/mobject.py:1415-1420) [verified by run]:
  - On a mobject with no points of its own (VGroup, Text, Tex) it colors each direct child (`set_submobject_colors_by_gradient`, :1422-1434). `Text("abc").set_color_by_gradient(BLUE, RED)` gives #58C4DD, #BD9BA7, #FC6255.
  - On a single shape it spreads the colors along the point order of the outline. A `Rectangle` gets a diagonal-looking gradient, not left to right. For a left-to-right fill use `set_color_by_code` (§F).
  - `t2g=` on Text only prints a warning (korean-tex-3d.md A3).
- Background color [verified by run]:
  - `self.set_background_color(GREY_E)` at the top of `construct` (F:manimlib/scene/scene.py:892-895).
  - Or the class attribute `default_camera_config = dict(background_color=GREY_E)` (the `Camera` keyword, F:manimlib/camera/camera.py:34). A probe printed `camera.background_rgba` = 0.133 (#222222).
  - Do not use: a module variable such as `BACKGROUND_COLOR = "#0a0a0a"`. Nothing in the fork reads it.
  - `BackgroundRectangle` keeps the yml #000000 (§B).

---

## E. Method names that do not exist [verified by run]

| Do not use | Use | Error |
|---|---|---|
| `set_fill_opacity(x)` | `set_fill(opacity=x)` | AttributeError |
| `set_stroke_opacity(x)` | `set_stroke(opacity=x)` | AttributeError |
| `match_fill(m)` | `set_fill(m.get_fill_color(), m.get_fill_opacity())` | AttributeError |
| `match_stroke(m)` | `set_stroke(m.get_stroke_color(), m.get_stroke_width())` | AttributeError |
| `set_stroke(..., background=True)` | `set_stroke(..., behind=True)` | TypeError |
| `set_backstroke(..., opacity=o)` | `set_stroke(c, w, opacity=o, behind=True)` | TypeError |

- Methods that do exist:
  - `match_style(vmobject)` copies fill, stroke and shading, recursively by submobject (F:manimlib/mobject/types/vectorized_mobject.py:273-285).
  - `match_color(mobject)` (F:manimlib/mobject/mobject.py:1645-1646).
  - Getters `get_fill_opacity`, `get_stroke_width`, `get_stroke_opacity` (F:manimlib/mobject/types/vectorized_mobject.py:360,372,376).

---

## F. Shader-side color (GLSL) [verified by run]

- Fork-specific: the fork takes GLSL (F:manimlib/mobject/mobject.py:1989), upstream takes WGSL (U:manimlib/mobject/mobject.py:1956).
- `set_color_by_code(glsl_code)` pastes the snippet into `finalize_color(vec4 color, vec3 point, vec3 unit_normal)` (F:manimlib/mobject/mobject.py:1989-2000, F:manimlib/shaders/inserts/finalize_color.glsl:48-52).
  - Assign to `color` and read `point.x`, `point.y`, `point.z` (scene units). Bare `x`, `y` are undefined.
  - It reaches the VMobject fill/stroke, surface, textured surface and dot shaders (the files that include `finalize_color`).
  - Works: `Square(3).set_fill(WHITE, 1).set_color_by_code("color.rgb = vec3(0.5 + 0.3 * point.x, 0.5 + 0.3 * point.y, 1.0);")` gives a gradient square.
- `set_color_by_xyz_func(glsl_snippet, min_value=-5.0, max_value=5.0, colormap="viridis")` (F:manimlib/mobject/mobject.py:2002-2025):
  - The snippet is one GLSL float expression, wrapped as `color.rgb = float_to_color(<snippet>, min, max, <colormap>);`. Statements such as `float v = ...; return v;` fail.
  - **Every letter x, y, z in the snippet is replaced** with `point.x`/`point.y`/`point.z` (:2015-2016). So `exp` becomes `epoint.xp`. `max` and `mix` break the same way (source evidence). Write such expressions with `set_color_by_code`.
  - Works: `Sphere(radius=2).set_color_by_xyz_func("z", min_value=-2, max_value=2)` in a ThreeDScene (viridis by height).
- A bad snippet passes when `set_color_by_code` is called. It fails when the mobject first reaches the scene: `self.add`/`self.play` calls `assemble_render_groups`, which compiles the shader (F:manimlib/scene/scene.py:306-308,323), with `_moderngl.Error: GLSL Compiler failed`, exit 1. Check with a `-sw` render, not just by building the mobject.

| Do not use | Error at render |
|---|---|
| `set_color_by_code("color.r = x; color.g = y; color.b = 1.0;")` | `undefined variable "x"` |
| `set_color_by_xyz_func(glsl_snippet="float value = sqrt(x*x + y*y + z*z); return value;", ...)` | syntax error at `"value"` |
| `set_color_by_xyz_func("exp(-x*x)", ...)` | `undefined variable "epoint"` |

---

## G. Tex string selection [verified by run]

`examples/tex.py` applies the rules below.

### G1. List what you select in `t2c=` or `isolate=`

- Two code paths (F:manimlib/mobject/svg/string_mobject.py:542-547):
  - Substrings given in `t2c=`, `isolate=` or as separate string arguments become labelled spans. `eq[...]` on them maps labels to glyphs and is exact.
  - Any other substring goes through `select_unisolated_substring` (:563-573). It slices `eq[start:end]`, where `start` is `num_tex_symbols` of the source text before the match (F:manimlib/mobject/svg/tex_mobject.py:219-223, F:manimlib/utils/tex.py:9-33).
- That count assumes glyph order = source order. It is false inside a `\frac` numerator (each numerator glyph lands one step later, the last on the bar; the denominator and what follows the fraction count right again) and around `\sum`/`\int` limits: dvisvgm writes the numerator before the fraction bar, the upper limit of `\sum` before Σ, and the upper limit of `\int` before its lower limit [verified by run].
- The plain-text search also matches inside command names (`a` in `\frac`, `n` in `\infty`). Labelled spans skip such matches (string_mobject.py:303).
- The result is wrong glyphs with no warning. **Rule: when you create the Tex, list every substring you will later select, color or brace in `t2c=` or `isolate=`.**
- Exceptions. Each listed key is wrapped in `{{\color[RGB]{...} ... }}` (F:manimlib/mobject/svg/tex_mobject.py:170-178) [verified by run]:
  - A key that is, starts with, or ends with a binary operator or relation (`+`, `-`, `=`, `\pm`) loses the TeX spacing on that side, with no warning. `Tex(R"a + b = c")` is 1.886 wide. With `isolate=["="]` it is 1.617, with `["+ b"]` or `["a +"]` 1.671, and with `["b ="]` or `["= c"]` 1.751. Keep operators strictly inside a key (`"a + b"`, `"b = c"`: 1.886), or select them by index (`eq[3]`). Separate string arguments are keys too (§G2).
  - A key that starts with an operator name (`\cos`, `\sin`, `\log`) loses the thin space before it, with no warning. `Tex(R"|\vec a|\,|\vec b|\cos\theta")` is 2.050 wide; with `t2c={R"\cos\theta": YELLOW}` or `isolate=[R"\cos\theta"]` it is 1.970. Write `\,` before it in the source: `Tex(R"|\vec a|\,|\vec b|\,\cos\theta", t2c={R"\cos\theta": YELLOW})` is 2.050 again [verified by run].
  - Keys must be whole TeX groups and must not contain `&` or `\\`: `isolate=[R"\frac{a}"]` raises `LatexError: Argument of \frac has an extra }.`, and `"&= x^2"` or `t2c={"&=": RED}` in a multi-line Tex raises `LatexError: Missing } inserted.`
  - A key that crosses braces (`"a}{b"`) only logs `Cannot handle substrings` (string_mobject.py:324-330) and falls back to counting.

| Source | Selector | Post-hoc (`eq[s]` / `set_color_by_tex`) | With `isolate=` / `t2c=` |
|---|---|---|---|
| `\frac{a}{b} + c` | `"a"` | fraction bar (twice) | a |
| `\frac{a}{b} + c` | `"c"` | bar + c | c |
| `\frac{a+1}{b} = y` | `"1"` | bar | 1 |
| `\sum_{i=1}^{N} i` | `"N"` | lower-limit 1 | N |
| `\sum_{n=1}^{\infty} \frac{1}{n^2}` | `"n"` | Sigma, numerator 1, the n of n^2. Misses the lower n | both n |
| `x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}` | `"a"` | the b of -b, c, the a of 2a. Misses the a of 4ac | both a |
| `\nabla \times \vec{E} = -\frac{\partial \vec{B}}{\partial t}` | `"t"` | 3 glyphs, one of them the real t | t |
| `E^2 = (m c^2)^2 + (p c)^2` | `"(p c)^2"` | correct (no `\frac` or limits before it) | correct |

- `set_color_by_tex`, `get_part_by_tex` and `get_parts_by_tex` are aliases of the same selection (F:manimlib/mobject/svg/tex_mobject.py:201-213). They have the same problem.
- `Text` counts non-space characters instead (string_mobject.py:557-558), so post-hoc selection on Text is fine (korean-tex-3d.md A2).

### G2. Indices, occurrences, exact keys

- `eq[0]`, `eq[2:5]` are always glyphs (string_mobject.py:549-551).
  - `Tex(R"a^2 + b^2 = c^2")` and `Tex(R"a^2", "+", R"b^2", "=", R"c^2")` both have 8 glyphs, and `[0]` is the glyph `a`. But the second is squeezed: 2.008 wide instead of 2.491.
  - Several string arguments are joined with `" "` and added to `isolate` (tex_mobject.py:51-57), so each argument is a key and the §G1 operator exception applies: a lone `"+"`, or an argument that ends in one (`Tex(R"a^2 +", R"b^2 =", R"c^2")`: 2.142), loses that spacing. To make parts exact, list the operands instead: `Tex(R"a^2 + b^2 = c^2", isolate=["a^2", "b^2", "c^2"])` (2.491).
- A string selector matches every occurrence, also inside words in TexText prose.
  - `TexText("Einstein's $E = mc^2$", isolate=["E", "m", "c"]).set_color_by_tex("E", BLUE)` colors the E of "Einstein's" too.
  - `select_part("E", 1)` (string_mobject.py:554-555) picks the second occurrence only, here the math E.
- Selectors and keys are matched literally against the source, spaces included (string_mobject.py:169-175).
  - `Tex(R"a+b", t2c={"a + b": RED})` colors nothing. `Tex(R"a + b")["a+b"]` is an empty VGroup. No warning, and `.set_color` on it is a silent no-op.
  - Copy keys from the Tex string exactly.
- Keys that partly overlap (`"E = m"` and `"m c"`) only log `Partly overlapping substrings detected` (string_mobject.py:316-323). Make keys nest or keep them disjoint. Nesting works: `isolate=["(p c)^2"]` with `t2c={"c": YELLOW}` in examples/tex.py.
- `t2c` keys may contain `$...$` for TexText: `TexText("The area is ", R"$\pi r^2$", ".", t2c={R"$\pi r^2$": YELLOW})` colors pi, r, 2.

### G3. Multi-line equations

- `Tex` already wraps its string in `align*` (F:manimlib/mobject/svg/tex_mobject.py:36,191-193). Write `&` and `\\` directly:
  - `Tex(R"f(x) &= x^2 + 2x + 1 \\ &= (x + 1)^2")` gives 2 lines (height 1.329; one line is 0.545), and both `=` sit at x = -0.74.
  - The same works with `t2c=` (keys without `&`, §G1), and with `\begin{aligned} ... \end{aligned}` inside `Tex`.
- `TexText` has no environment (tex_mobject.py:276-277), so it accepts a full `\begin{align*} ... \end{align*}`.

| Do not use | Result |
|---|---|
| `Tex(R"""\begin{align*} f(x) &= ... \\ &= ... \end{align*}""")` | `LatexError: Argument of \align* has an extra }.` |
| a scene file written through a shell heredoc | in this plugin's Windows agent shell a heredoc turned `\\` into `\`. LaTeX reads `\ ` as a space: one line (height 0.545), no error. Write .py files with an editor or file-write tool |

---

## H. Other wrong snippets (covered elsewhere)

| Do not use | Fork behavior | Where |
|---|---|---|
| `Text("x", color=BLUE)`, `Circle(color=BLUE)` | ignored: white text, red circle outline | SKILL.md §6 |
| `self.play(sq.animate.set_fill(...), sq.animate.set_stroke(...))` | the later `.animate` wins; the fill change is lost | SKILL.md §11 |
| "check the intermediate .tex files in the output directory" | `working.tex`/`.log` go to `<cwd>/latex_cache/` | korean-tex-3d.md B6 |
