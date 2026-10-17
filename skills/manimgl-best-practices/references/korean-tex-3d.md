# Korean Text, Tex, 3D detailed reference

Target: fork @455a420. Evidence notation is the same as in SKILL.md (`F:` fork, `U:` upstream @fafa083, `[verified by run]`).

Test environment:
- Windows 11, Python 3.10, system UTF-8 locale (`locale.getpreferredencoding()` = cp65001)
  - `working.tex` is written without specifying an encoding (F:manimlib/utils/tex_file_writing.py:105). So on Windows with a cp949 locale, Korean Tex may be written as cp949. Source evidence.
- pango 1.58.2, manimpango 0.7.0
- MiKTeX: cm-super and kotex (`cjk-ko` package path) installed

`[verified by run]` means I looked at the `-sw` render PNG or printed the value with a Python probe while writing this document. Numbers are for this environment.

`text_mobject.py`, `tex_mobject.py`, `brace.py`, and `tex_templates.yml` are the same as upstream. The Text/Tex behavior in this document is not specific to the fork. Exceptions are marked separately.

---

## A. Korean `Text`

### A1. Defaults

| Item | Value | Evidence |
|---|---|---|
| Default font | `"Noto Sans KR"` | F:manimlib/default_config.yml:91 [verified by run: `manim_config.text.font`] |
| Default multi-line alignment | `"LEFT"` | F:manimlib/default_config.yml:92 |
| Default `font_size` | 48 | F:manimlib/mobject/svg/text_mobject.py:139 |
| Path | Pango markup → SVG → disk cache | F:manimlib/mobject/svg/text_mobject.py:53-100 |

- Check whether the font is installed with `"Noto Sans KR" in manimpango.list_fonts()`. It was True in this environment [verified by run].

### A2. Glyph count and sub-selection [verified by run]

Glyph count:

| Expression | Result |
|---|---|
| `len(Text("가나다 라"))` | 4. One syllable is one submobject, and spaces count as 0 |
| `len(Text("한글 abc 123"))` | 8 |
| `len(Text("첫 줄\n둘째 줄 길다"))` | 7. Line breaks also count as 0 |

Selection:

| Expression | Result |
|---|---|
| `t = Text("가나 가나 다가나")`, `t["가나"]` | VGroup of 3 parts. It selects all of them, not only the first, and ignores word boundaries (including the one inside `다가나`) |
| `t.select_part("가나", 1)` | Selects only the second occurrence (counted from 0) |
| `Text("값1 값2 값3")[re.compile(r"값\d")]` | 3 |

- Evidence: `__getitem__` → `select_parts` → `select_unisolated_substring` (F:manimlib/mobject/svg/string_mobject.py:542-573), `select_part` (F:manimlib/mobject/svg/string_mobject.py:554).
- Indices are counted as the number of non-space characters in the string (F:manimlib/mobject/svg/string_mobject.py:557-571).
  - So Hangul with decomposed jamo (NFD) goes out of alignment.
  - NFD `"가나다 라"` is 8 code points and 4 glyphs. Selecting with NFC `"다"` finds no match and gives an empty VGroup. Selecting with NFD `"다"` gives one part with 0 glyphs, and selecting with NFD `"가"` catches the two glyphs of `가나` [verified by run].
  - Convert strings read from outside (e.g. macOS filenames) with `unicodedata.normalize("NFC", s)` before passing them in.

### A3. Partial-style arguments

| Argument (long name) | Example | Result |
|---|---|---|
| `t2c` (`text2color`) | `t2c={"loss": RED, "평균": BLUE}` | Works [verified by run] |
| `t2w` (`text2weight`) | `t2w={"굵게": BOLD}` | Korean bold works [verified by run] |
| `t2s` (`text2slant`) | `t2s={"기울임": ITALIC}` | Korean italic works [verified by run] |
| `t2f` (`text2font`) | `t2f={"맑은고딕": "Malgun Gothic"}` | Works [verified by run] |
| `t2g` (`text2gradient`) | - | Only prints a warning. Use `set_color_by_gradient` for gradients (F:manimlib/mobject/svg/text_mobject.py:193-197) |
| `lsh` (`line_spacing_height`) | - | Line spacing. Ignored below Pango 1.50 (F:manimlib/mobject/svg/text_mobject.py:353-366) |

- Argument list: F:manimlib/mobject/svg/text_mobject.py:150-161.
- `BOLD`, `ITALIC`, `NORMAL` are manimlib constants (strings) [verified by run].
- The constructor's `color=` is ignored. Set color with `set_color` or `t2c` (SKILL.md §6).

### A4. `MarkupText` [verified by run]

- `<b>`, `<i>`, `<u>` work on Korean text.
- **Markup colors such as `<span foreground="#FF0000">` are ignored and come out white.**
  - After reading the SVG, `StringMobject.__init__` repaints everything with `set_fill(fill_color)` (F:manimlib/mobject/svg/string_mobject.py:72).
  - Set color with `MarkupText(..., t2c={"빨강": RED})` or `set_color`. Both work.
- `Text` escapes `< > & " '` automatically (F:manimlib/mobject/svg/text_mobject.py:420-431). In `MarkupText`, write `&lt;` etc. yourself.

### A5. Multiple lines and alignment [verified by run]

- Break lines with `"\n"`.
- With `alignment="LEFT" | "CENTER" | "RIGHT"`, the shorter first line was attached to the left, center, and right. The default is LEFT.
- Automatic line wrapping uses `line_width=` (manim units), converted to a Pango width (F:manimlib/mobject/svg/text_mobject.py:72-75). Source evidence.

### A6. `font_size` and actual height [verified by run]

| Object (`font_size=144`) | Height |
|---|---|
| `Tex("0")` | 0.997 |
| `Text("0")`, Noto Sans KR | 1.367 |
| `Text("가")`, Noto Sans KR | 1.628 |
| `Text("0")`, Malgun Gothic | 1.338 |
| `Text("0")`, Arial | 1.317 |
| `Text("0")`, Consolas | 1.181 |

- The rule "with `font_size_for_unit_height=144`, the height of `0` is 1 unit" (F:manimlib/default_config.yml:88,94) **held only for Tex.**
- At the same `font_size`, Text is about 1.37 times larger. Measuring again with an empty cache directory gave the same result.
  - The calibration renders `<span font_size="49152">0</span>` without `font_family` (F:manimlib/mobject/svg/text_mobject.py:103-112). The Text body always includes `font_family` (F:manimlib/mobject/svg/text_mobject.py:346-352).
  - The cause is this font difference [verified by run]. The SVG height of a 48pt `"0"` is 35.53 without `font_family`, the same as `serif`. Sans is 48.44, Noto Sans KR 48.57, Arial 46.78, Times New Roman 44.00.
  - So the ratio differs per font. `font="Sans"` is not serif either, so it gives 1.363.
- Practical rule: to match digit heights when Noto Sans KR Text and Tex are on the same line, give Text a `font_size` of about 0.73 times the Tex one (e.g. Tex 40 ↔ Text 29). Re-measure for other fonts.

### A7. Missing font [verified by run]

`Text("가나다 abc", font="Some Missing Font")` raises no exception and only prints the warning below.

```
couldn't load font "Some Missing Font Not-Rotated 48", falling back to "Sans Not-Rotated 48", expect ugly output.
```

- Korean is drawn with the fallback font. But glyph shapes and letter spacing change, and so does the width (2.954; the default font gives 2.759).
- `markup_to_svg` uses a disk cache. The key is a hash of the function name and arguments (markup string, alignment, `line_width`, etc.) (F:manimlib/mobject/svg/text_mobject.py:53-54, F:manimlib/utils/cache.py:21-30). The markup contains the font name, so the key is the same before and after installing the font.
  - So even if you install the font later, the same string may keep producing the cached fallback result. In that case use `--clear-cache`. Source evidence.

### A8. Helper objects that take Korean

- `Brace(...).get_text("한글")` creates a `Text` (F:manimlib/mobject/svg/brace.py:87-91) [verified by run].
- But `Brace` itself is a Tex subclass, so it needs LaTeX (B5).
- The default font of `Code` is Consolas (F:manimlib/mobject/svg/text_mobject.py:442).

---

## B. `Tex` / `TexText`

### B1. Render path

- `Tex(..., template="", additional_preamble="")` calls `latex_to_svg(content, template, additional_preamble)` (F:manimlib/mobject/svg/tex_mobject.py:43-44,81-82).
- Template resolution (F:manimlib/utils/tex_file_writing.py:19-37):
  - If `template=""`, it uses the setting `tex.template`. The default is `"default"` (F:manimlib/default_config.yml:86).
  - The name is lowercased and spaces are replaced with `_` before lookup.
  - An unknown name prints a warning and falls back to default: `Cannot recognize template no_such_template, falling back to 'default'.` [verified by run]
- The preamble order is `template preamble + "\n" + additional_preamble` (F:manimlib/utils/tex_file_writing.py:79).
  - The document is built with `\documentclass[preview]{standalone}` (F:manimlib/utils/tex_file_writing.py:40-47).
- Compiler (F:manimlib/utils/tex_file_writing.py:89-94):
  - `latex` produces .dvi; `xelatex` produces .xdv with `-no-pdf`.
  - Any other compiler fails with `NotImplementedError: Compiler 'lualatex' is not implemented` [verified by run, `template="chalkduster"`].
- dvisvgm gets `--fontmap=ps2pk.map`. Fork only (F:manimlib/utils/tex_file_writing.py:138).
- Environment:
  - `Tex` is placed inside `align*` (F:manimlib/mobject/svg/tex_mobject.py:36). `TexText` has no environment (F:manimlib/mobject/svg/tex_mobject.py:276-277).
  - So using `Tex` with the `empty` or `empty_ctex` template without amsmath fails with `LaTeX Error: Environment align* undefined.` [verified by run]. `TexText` works.
- Color command:
  - With `t2c`, multiple string arguments, or `isolate`, `{{\color[RGB]{r, g, b} ...}}` is inserted (F:manimlib/mobject/svg/tex_mobject.py:163-178). `BulletedList` always uses `isolate` internally (F:manimlib/mobject/svg/special_tex.py:34).
  - So using `t2c` with a preamble that lacks xcolor fails with `LatexError: Undefined control sequence. <argument> {{\color` [verified by run].
  - In that case add `\usepackage{xcolor}`.
- The size calibration compiles `"0"` without a template argument. That is, it uses the setting `tex.template` (default `default`) (F:manimlib/mobject/svg/tex_mobject.py:25-32, F:manimlib/utils/tex_file_writing.py:35).
  - So even if you only use xelatex templates, the default template (latex and its packages) must compile unless you changed the setting. Source evidence.
- Multi-line equations (`&`, `\\`) and string-selection rules (`eq["x"]` is exact only for substrings listed in `t2c=`/`isolate=`) are in [style-and-color.md](style-and-color.md) §G.

### B2. All of `tex_templates.yml` (F:manimlib/tex_templates.yml)

Base templates:

| Name (line) | Compiler | Contents | Result in this environment |
|---|---|---|---|
| `default` (3) | latex | babel, inputenc, `[T1]{fontenc}`, amsmath, amssymb, physics, xcolor, etc. | English/math work. Korean errors (B3) |
| `ctex` (29) | xelatex | ctex, xeCJK, `\setmainfont{Microsoft YaHei}` | Korean gives a `fontspec` error (B3) |
| `basic` (56) | latex | babel, amsmath, amssymb, xcolor | `Tex(R"x^2 + \alpha")` works [verified by run] |
| `basic_ctex` (65) | xelatex | ctex, amsmath, amssymb, xcolor | Same error as ctex [verified by run] |
| `empty` (74) | latex | empty | `TexText` works, `Tex` gives the `align*` error [verified by run] |
| `empty_ctex` (79) | xelatex | empty | Base of the kotex combination (B3) |

Font templates (lines 87-736):

- xelatex:
  - `american_typewriter`, `apple_chancery`, `baskerville_it`, `brushscriptx`, `chalkboard_se`, `comic_sans`, `ecf_webster`
  - `gnu_freesans_tx`, `gnu_freeserif_freesans`, `minion_pro_myriad_pro`, `minion_pro_tx`, `papyrus`, `verdana_it`
- lualatex: `chalkduster`. Unusable in the fork because of NotImplementedError [verified by run].
- latex:
  - `antykwa`, `auriocus_kalligraphicus`, `baskervald_adf_fourier`, `biolinum`, `comfortaa`
  - `droid_sans`, `droid_sans_it`, `droid_serif`, `droid_serif_px_it`
  - `ecf_augie`, `ecf_jd`, `ecf_skeetch`, `ecf_tall_paul`, `electrum_adf`, `epigrafica`, `fourier_utopia`, `french_cursive`
  - `gfs_bodoni`, `gfs_didot`, `gfs_neohellenic`, `helvetica_fourier_it`, `latin_modern_tw`, `latin_modern_tw_it`
  - `libertine`, `libris_adf_fourier`, `new_century_schoolbook`, `new_century_schoolbook_px`, `noteworthy_light`, `palatino`
  - `romande_adf_fourier_it`, `slitex`, `times_fourier_it`, `urw_avant_garde`, `urw_zapf_chancery`
  - `venturis_adf_fourier_it`, `vollkorn`, `vollkorn_fourier_it`, `zapf_chancery`

Verified in this environment [verified by run]:
- `verdana_it` and `comic_sans` work because they are Windows fonts.
- `biolinum` and `noteworthy_light` use fontspec although the compiler is latex, so they fail with `Fatal Package fontspec Error: The fontspec package requires either XeTeX or LuaTeX.`. This is a template definition error; upstream is the same.
- The remaining font templates were not checked. Many assume macOS fonts or extra TeX packages.

### B3. Korean inside Tex

With `KO = R"\usepackage{amsmath}\usepackage{kotex}\setmainhangulfont{Noto Sans KR}"` and `KW = dict(template="empty_ctex", additional_preamble=KO)`:

| Code | Result |
|---|---|
| `Tex(R"\text{손실} = x")` (default template) | `LaTeX Error: Unicode character 손 (U+C190) not set up for use with LaTeX.` [verified by run] |
| Same expression, `template="ctex"` | `Package fontspec Error: The font "SimHei" cannot be found` [verified by run]. It fails looking for SimHei, not the template's YaHei |
| Same expression, `template="basic_ctex"` | Same SimHei error as above [verified by run] |
| `Tex(R"\text{손실} = \frac{1}{N} \sum_i \ell_i", **KW)` | Works, `len` 10 [verified by run] |
| `TexText("한글 문장 with English", **KW)` | Works, `len` 15 (equal to the character count without spaces). Korean is Noto Sans KR; English is the xelatex default Latin Modern (serif) [verified by run] |
| `TexText(R"넓이는 $\pi r^2$ 이다", **KW)` | Works [verified by run] |
| `TexText(R"첫 줄\\둘째 줄", **KW)` | Two lines, centered [verified by run]. The default is `alignment=R"\centering"` (F:manimlib/mobject/svg/tex_mobject.py:42) |
| `Tex(R"손실 = x^2", **KW)` (no `\text`) | **No error, but the Korean silently disappears** and only `= x²` remains (`len` 3) [verified by run]. Always wrap math-mode Korean in `\text{}` |
| `Title("한글 제목 Title", **KW)` | Works [verified by run] |
| `BulletedList("첫째 항목", "둘째 항목 item", **KW)` | `LatexError: Undefined control sequence. ... {{\color` [verified by run]. Each item is passed `isolate`, so xcolor is required (F:manimlib/mobject/svg/special_tex.py:34). It works with `KWX` (B4) and has 2 parts [verified by run] |
| `Brace(m, DOWN).get_tex(R"\text{한글} x", **KW)` | Works [verified by run] |
| `BraceText(m, "한글", **KW)`, `BraceLabel(...)` | `TypeError: Mobject.__init__() got an unexpected keyword argument 'template'` [verified by run] |

- Why `BraceText`/`BraceLabel` fail: they pass kwargs to `VMobject.__init__`, `Brace`, and the label constructor alike (F:manimlib/mobject/svg/brace.py:122,129,131).
  - Use `Brace` + `get_tex(..., **KW)` or `get_text("한글")` instead.
- To make English sans-serif too, you would probably need to add `\setmainfont{...}` to the preamble. Not checked.

### B4. Selecting Korean parts in kotex Tex [verified by run]

With `KWX = dict(template="empty_ctex", additional_preamble=KO + R"\usepackage{xcolor}")`:

| Code | Result |
|---|---|
| `Tex(R"\text{손실} = ...", t2c={"손실": YELLOW, R"\ell_i": RED}, **KWX)` | The 2 glyphs of 손실 and the 2 glyphs of ℓᵢ are colored |
| `eq = Tex(R"\text{손실} = ...", **KW)`, `eq["손실"].set_color(GREEN)`, `eq["N"].set_color(BLUE)` | Colored exactly. xcolor is not needed (no color command is inserted) |
| `TexText("한글 문장 with English", t2c={"문장": YELLOW, "English": RED}, **KWX)` | Works |
| `tt["문장"]`, `tt["with"]` | Works |

- In short, `t2c`, `isolate`, multiple string arguments, and `BulletedList` need xcolor. Selecting with `eq["..."]` after rendering does not.

### B5. Classes that need LaTeX [verified by run]

How I checked: removed TeX from PATH, pointed `directories.cache` in `custom_config.yml` at an empty cache, and tried to create each. Without TeX you get `FileNotFoundError: [WinError 2] 지정된 파일을 찾을 수 없습니다` (Korean Windows message; English: "The system cannot find the file specified"), not `LatexError` (`subprocess.run`, F:manimlib/utils/tex_file_writing.py:108).

| Needs it | Where the inner Tex is created |
|---|---|
| `Tex`, `TexText` | - |
| `Brace`, `BraceLabel`, `BraceText` | `Brace` is a `Tex` subclass (F:manimlib/mobject/svg/brace.py:32). Label constructors F:manimlib/mobject/svg/brace.py:111,176 |
| `Matrix`, `IntegerMatrix`, `DecimalMatrix` (even if the entries are floats) | The brackets are always Tex (F:manimlib/mobject/matrix.py:120). String entries F:manimlib/mobject/matrix.py:117. `\vdots`/`\hdots` F:manimlib/mobject/matrix.py:189,195 |
| `Axes.get_axis_labels`, `get_x_axis_label`, `get_y_axis_label` | F:manimlib/mobject/coordinate_systems.py:143 |
| `get_graph_label` (string label) | F:manimlib/mobject/coordinate_systems.py:294 |
| `ThreeDAxes.add_axis_labels` | F:manimlib/mobject/coordinate_systems.py:576 |
| `Title`, `BulletedList` | F:manimlib/mobject/svg/special_tex.py:34,61 |
| `BarChart` | F:manimlib/mobject/probability.py:270,293 |
| `Slider` | F:manimlib/mobject/number_line.py:297 |
| `DecimalNumber` with a character containing `\` such as `unit=R"^\circ"`, complex numbers (`i`) | F:manimlib/mobject/numbers.py:24-31 |
| `SampleSpace` title/labels | F:manimlib/mobject/probability.py:56,136. Source evidence |

| Does not need it |
|---|
| `Text`, `MarkupText`, `Code`, `DecimalNumber(3.14)`, `Integer`, `NumberLine.add_numbers`, `Axes.add_coordinate_labels`, `SurroundingRectangle`, `Arrow` |

- **If it is in the disk cache, it is created even without TeX.** Tex rendered earlier was created even with no TeX on PATH, and only new strings failed [verified by run].
- So a scene that worked on one machine may fail on a new environment only at the first Tex it has not seen.

### B6. cm-super, empty SVG, cache

- The default template uses `\usepackage[T1]{fontenc}` (F:manimlib/tex_templates.yml:9). The T1 font outlines come from cm-super.
  - This environment: `kpsewhich sfrm1000.pfb` → `.../fonts/type1/public/cm-super/` [verified by run].
- Without cm-super, dvisvgm produces an empty SVG and ends with exit 0 (SKILL.md §8).
  - The calibration `"0"` also becomes an empty SVG and fails with `ValueError: SVG has no content to measure` (F:manimlib/mobject/svg/tex_mobject.py:31, F:manimlib/mobject/svg/svg_mobject.py:45). I reproduced the message itself with an empty SVG [verified by run].
- Separately, the fork does not check the dvisvgm exit code (F:manimlib/utils/tex_file_writing.py:133-151). Upstream raises `LatexError` if it is nonzero (U:manimlib/utils/tex_file_writing.py:150-152).
  - But the cm-super case above is exit 0, so even the upstream check does not catch it.
- For LaTeX errors, only the two lines after `! ` in `working.log` are cut out and shown (F:manimlib/utils/tex_file_writing.py:121-130). For the full text, look at the log below.

There are two caches.

| Location | Contents | Evidence |
|---|---|---|
| `<cwd>/latex_cache/` | `working.tex`, `.log`, `.aux`, `.dvi` or `.xdv`. Overwritten every time. Open it when looking at errors | F:manimlib/default_config.yml:35, F:manimlib/config.py:240-244, F:manimlib/utils/tex_file_writing.py:97-105 [verified by run] |
| diskcache. Default `%LOCALAPPDATA%\manim\manim\Cache` | `full_tex_to_svg`, `markup_to_svg` results | F:manimlib/utils/cache.py:17-30, F:manimlib/utils/directories.py:17-18 [verified by run: `get_cache_dir()`] |

- `--clear-cache` empties the diskcache before rendering (F:manimlib/__main__.py:58-59, F:manimlib/utils/cache.py:33-34).
  - [verified by run] 17 entries → cleared → compiled again with `Writing a^2...`.
  - It does not touch the `latex_cache/` folder. Source evidence.
- You can change the diskcache location with `directories: {cache: "path"}` in `custom_config.yml` (F:manimlib/default_config.yml:40) [verified by run].

---

## C. 3D

### C1. `Scene` and `ThreeDScene`

| | `Scene` | `ThreeDScene` |
|---|---|---|
| `samples` (MSAA) | 0 (F:manimlib/scene/scene.py:60) | 4 (F:manimlib/scene/scene.py:947) |
| `default_frame_orientation` (θ, φ, degrees) | (0, 0) (F:manimlib/scene/scene.py:62) | (-30, 70) (F:manimlib/scene/scene.py:948) [verified by run: `get_euler_angles` → (-30, 70, 0)] |
| depth test on `add` | None. Draws in add order (F:manimlib/scene/scene.py:328) | `apply_depth_test()` on mobs that are not `fix_in_frame` (F:manimlib/scene/scene.py:949-954) [verified by run] |
| stroke | Unchanged | `set_flat_stroke(False)` on VMobjects that have a stroke (F:manimlib/scene/scene.py:955-956) |

- A mob that first appears through `self.play` also goes through `self.add` (F:manimlib/scene/scene.py:551-552). So the depth test is applied there too.
- To skip the depth test, add with `self.add(mob, set_depth_test=False)` [verified by run].
- Starting orientation:
  - On creation it calls `frame.reorient(*default_frame_orientation)` and then `make_orientation_default()` (F:manimlib/scene/scene.py:113-114).
  - So setting `default_frame_orientation = (θ, φ)` on a Scene subclass starts a tilted 2D scene. Source evidence.
- A plain `Scene` tilted with `reorient` is not a substitute for ThreeDScene once surfaces and lines mix [verified by run].
  - Surfaces still depth-test among themselves, because `Surface` sets `depth_test=True` in its constructor (F:manimlib/mobject/types/surface.py:48).
  - Axes, Text, and other VMobjects get no depth test and draw in add order.
  - With `reorient(20, 70)`, a `Sphere` added after a `ThreeDAxes` covered the y-axis segment that is in front of it. ThreeDScene drew that segment over the sphere.
  - Tilting a flat 2D scene in `Scene` is fine.
- VMobject's `apply_depth_test` sets `anti_alias_width` to 0 (F:manimlib/mobject/types/vectorized_mobject.py:423-430). In ThreeDScene, samples=4 compensates for this. Source evidence.
- `ThreeDScene.add` only checks `is_fixed_in_frame()` of the top-level mob (F:manimlib/scene/scene.py:953).
  - Upstream changed this to check per family (U:manimlib/scene/scene.py:934-943). The reason given in the comment is "fixed text disappears from the depth test during FadeTransform".
  - It did not reproduce in the fork with `self.add(VGroup(fixed_text))` (`depth_test` False), because `VGroup(fixed_text).is_fixed_in_frame()` was True. It was also False with `self.play(FadeIn(fixed_label))` [verified by run]. The case during FadeTransform was not checked.

### C2. `CameraFrame` API

`self.frame` is the CameraFrame. Signatures were checked with `inspect.signature` [verified by run].

| Method | Signature | Notes | Evidence (F:manimlib/camera/camera_frame.py) |
|---|---|---|---|
| `reorient` | `(theta_degrees=None, phi_degrees=None, gamma_degrees=None, center=None, height=None)` | In **degrees**. None keeps the value | :211-228 |
| `set_euler_angles` | `(theta=None, phi=None, gamma=None, units=RADIANS)` | Radians | :138-154 |
| `set_theta` / `set_phi` / `set_gamma` | `(theta)` / `(phi)` / `(gamma)` | Radians | :230-237 |
| `increment_euler_angles` | `(dtheta=0, dphi=0, dgamma=0, units=RADIANS)` | With zxz, φ is clipped to [0, π]. At φ=0, -20° → 0 [verified by run] | :156-174 |
| `increment_theta` / `_phi` / `_gamma` | `(dtheta, units=RADIANS)` / `(dphi, ...)` / `(dgamma, ...)` | | :239-249 |
| `increment_mirrored_euler_angles` (**fork only**) | `(dtheta=0, dphi=0, units=RADIANS)` | Lets φ go down to -π. When raising, the upper limit is max(current φ, 0). At (0, 30°) with dphi=-60°, `get_euler_angles` returns (180, 30, -180) (same direction as φ=-30) [verified by run] | :176-206 |
| `add_ambient_rotation` | `(angular_speed=1*DEG)` | **rad/s**. Increases θ with an updater. `10*DEG`, dt=1 → θ +10° [verified by run]. To stop, use `self.frame.clear_updaters()` | :251-253 |
| `get_euler_angles` | `() -> [θ, φ, γ]` (rad) | Folds into θ on gimbal lock | :68-83 |
| `get_theta` / `get_phi` / `get_gamma` | `()` | | :85-92 |
| `set_field_of_view` / `get_field_of_view` | `(rad)` | Default fovy is 45° [verified by run] | :261-263, :287-288, :29 |
| `set_focal_distance` / `get_focal_distance` | `(d)` | Recomputes fovy. The default (height 8, 45°) is 9.657 [verified by run] | :256-259, :284-285 |
| `get_implied_camera_location` | `()` | (-4.537, -7.859, 3.303) at (-30, 70) [verified by run] | :290-295 |
| `to_fixed_frame_point` / `from_fixed_frame_point` | `(point, relative=False)` | Applies only the view matrix. Perspective is left out | :297-305 |
| `make_orientation_default` / `to_default_state` | `()` | Restores the default orientation, shape, and center | :58-66 |
| `set_euler_axes` | `(seq)` | Default `"zxz"` | :208-209, :30 |

- The rotation is `Rotation.from_euler("zxz", [γ, φ, θ])`, that is, R = Rz(θ)·Rx(φ)·Rz(γ) (:152).
- Animate with `self.play(self.frame.animate.reorient(...))`, but only for turns under 180°. Interpolation takes the short path of the quaternion (fork only, :121-130), so larger turns go wrong (§C8).
- `set_camera_orientation`, `move_camera`, `begin_ambient_camera_rotation`, and `frame.set_center` do not exist [verified by run]. Move the frame with `move_to` or `reorient(center=...)`.
- `self.frame.copy()` is not a second camera. A fixed-in-frame copy meant as picture-in-picture drew nothing, and the main frame was unchanged [verified by run].

Reading θ, φ under the default `zxz` axes [verified by run: `get_implied_camera_location`, columns of `get_orientation().as_matrix()`]:

| `reorient(θ, φ)` | Implied camera position | Screen right / up | What you see |
|---|---|---|---|
| (0, 0) | (0, 0, 9.66) | +x / +y | XY plane from above. The 2D default |
| (0, 90) | (0, -9.66, 0) | +x / +z | XZ plane from the front (-y side), z up |
| (90, 90) | (9.66, 0, 0) | +y / +z | YZ plane from +x |
| (-90, 90) | (-9.66, 0, 0) | -y / +z | YZ plane from -x |
| (-30, 70) | (-4.54, -7.86, 3.30) | | ThreeDScene default |

- φ is measured from straight above (0) to level (90). θ turns the camera about world z.
- Negative φ does not mean "looking from below". `reorient(45, -30)` puts the camera where `reorient(225, 30)` does, but rolled 180°, so z points down on screen. `get_euler_angles` reads it back as (-135, 30, 180) [verified by run].
- Omitted angles keep the current value, roll included. `reorient` passes None through (:223), and `set_euler_angles` fills None from `get_euler_angles()` (:145-148).
  - After `reorient(45, -30)`, `reorient(30)` gives (30, 30, 180), which is upside down [verified by run].
  - Write all three angles, `reorient(θ, φ, 0)`, whenever a roll may be present: after a negative φ, `set_floor_plane("xz")`, or `increment_gamma`.

`self.set_floor_plane("xz")` (y up):
- It only switches the frame's Euler axes to `"zxy"` (F:manimlib/scene/scene.py:728-734). Upstream is the same (U:manimlib/scene/scene.py:725).
- θ then turns about world y. `add_ambient_rotation(90 * DEG)` moved the camera from (-4.54, 3.30, 7.86) to (7.86, 3.30, 4.54) in 1 s [verified by run].
- **Negative φ looks down on the floor.** `reorient(30, -20)` puts the camera at y = +3.30. `reorient(30, 20)` puts it at y = -3.30, under the floor [verified by run].
- Under `zxy`, φ is minus the elevation above the floor (φ = -elevation): 0 = level, -90 = straight down from above. That is the reverse of `zxz`, where 0 is straight down. The ThreeDScene default view (-30, 70) becomes `reorient(-30, -20, 0)` here (camera at 20° elevation, as under `zxz`), not (-30, -70, 0), which is at 70° elevation and looks almost straight down [verified by run].
- `increment_phi` clips φ to [-90°, 90°] under `zxy` (:169-170).
- In ThreeDScene, give γ. The starting (-30, 70) was built under `zxz`, and read back under `zxy` it is (-53.9, 54.5, -59.4).
  - `reorient(-30, -20)` kept that γ and turned the floor into a slanted wall. `reorient(-30, -20, 0)` gave a level floor [verified by run].
- So call `self.set_floor_plane("xz")` first, then `self.frame.reorient(θ, φ, 0)`. Code that uses negative φ for a downward view expects this floor plane. Under the default axes it comes out rolled (above).

### C3. 3D objects

Shape confirmed by rendering [verified by run]: `Sphere`, `Torus`, `Cylinder`, `Cone`, `Line3D`, `Disk3D`, `Square3D`, `Cube`, `Prism`, `VCube`, `Dodecahedron`, `SurfaceMesh`, `ThreeDAxes.get_graph`. The remaining rows are source evidence.

| Class | Main arguments (defaults) | Evidence |
|---|---|---|
| `Surface` | `color=GREY, shading=(0.3,0.2,0.4), depth_test=True, u_range=(0,1), v_range=(0,1), resolution=(101,101)` | F:manimlib/mobject/types/surface.py:44-75 |
| `ParametricSurface` | `(uv_func, u_range=(0,1), v_range=(0,1), **kw)` | F:manimlib/mobject/types/surface.py:268-280 |
| `SGroup` | `(*surfaces)` | F:manimlib/mobject/types/surface.py:283 |
| `TexturedSurface` | `(uv_surface, image_file, dark_image_file=None)` | F:manimlib/mobject/types/surface.py:296-311 |
| `TexturedGeometry`, `ThreeDModel` | `(geometry: trimesh.Trimesh, texture_file)`, `(obj_file, height=3)`. surface.py imports trimesh and pywavefront at the top level, so both packages are needed for `import manimlib` itself, not only for these classes (SKILL.md §0) | F:manimlib/mobject/types/surface.py:5-6,407-408,435-436 |
| `Sphere` | `radius=1, resolution=(101,51)` | F:manimlib/mobject/three_dimensions.py:93 |
| `Torus` | `r1=3, r2=1` | F:manimlib/mobject/three_dimensions.py:125 |
| `Cylinder` | `height=2, radius=1, axis=OUT, resolution=(101,11)` | F:manimlib/mobject/three_dimensions.py:147 |
| `Cone` | Cylinder arguments | F:manimlib/mobject/three_dimensions.py:178 |
| `Line3D` | `(start, end, width=0.05)` | F:manimlib/mobject/three_dimensions.py:192 |
| `Disk3D` | `radius=1` | F:manimlib/mobject/three_dimensions.py:212 |
| `Square3D` | `side_length=2` | F:manimlib/mobject/three_dimensions.py:237 |
| `Cube` | `color=BLUE, opacity=1, shading=(0.1,0.5,0.1), side_length=2` | F:manimlib/mobject/three_dimensions.py:270 |
| `Prism` | `(width=3, height=2, depth=1)` | F:manimlib/mobject/three_dimensions.py:290 |
| `VGroup3D`, `VCube`, `VPrism`, `Dodecahedron`, `Prismify` | VMobject-based. depth_test=True | F:manimlib/mobject/three_dimensions.py:303-399 |
| `SurfaceMesh` | `(uv_surface, resolution=(21,11), stroke_width=1, stroke_color=GREY_A)` | F:manimlib/mobject/three_dimensions.py:31 |
| `ThreeDAxes` | `x_range=(-6,6,1), y_range=(-5,5,1), z_range=(-4,4,1)` | F:manimlib/mobject/coordinate_systems.py:539 |
| `ThreeDAxes.get_graph` | `(func(x, y), color=BLUE_E, opacity=0.9, u_range=None, v_range=None)` → ParametricSurface. Reflects the axis units | F:manimlib/mobject/coordinate_systems.py:585-607 |
| `ThreeDAxes.get_parametric_surface` | `(func(u, v), color=BLUE_E, opacity=0.9)` | F:manimlib/mobject/coordinate_systems.py:609-621 |

- Missing [verified by run]: `Dot3D`, `Arrow3D`, `Cuboid`, `Polyhedron`, `Tetrahedron`, `Octahedron`, `Icosahedron`.
- For points, use `GlowDot`, `TrueDot`, `DotCloud`.
- Group surfaces, `GlowDot`/`TrueDot`/`DotCloud` and images with `Group(...)`. `VGroup` raises `Exception: Only VMobjects can be passed into VGroup` for them (F:manimlib/mobject/types/vectorized_mobject.py:1312-1316) [verified by run].
- Sort the faces of a translucent surface with `surface.always_sort_to_camera(self.camera)` (F:manimlib/mobject/types/surface.py:249-254). It removed the dark crescent on a translucent sphere, but objects added after the surface stay hidden [verified by run, §C7].
  - Upstream's `set_sort_to_camera` does not exist in the fork.

Constructor pitfalls [verified by run]:

| Code | Result | Use instead |
|---|---|---|
| `Surface(lambda u, v: ...)` | `Exception: Invalid color type`. The first parameter is `color`; the shape comes from the overridable `uv_func` method (F:manimlib/mobject/types/surface.py:44-46,78-80) | `ParametricSurface(func, u_range=..., v_range=..., resolution=...)` or `ThreeDAxes.get_graph` |
| `Cube(color=GREEN, fill_opacity=0.8)` | `TypeError: Mobject.__init__() got an unexpected keyword argument 'fill_opacity'`. Surfaces are not VMobjects, and `Cube` passes `**kwargs` to `SGroup` (F:manimlib/mobject/three_dimensions.py:270-287) | `Cube(color=GREEN, opacity=0.8)` |
| `Line3D(start=[-2, -2, -2], end=[2, 2, 2])` | `TypeError: unsupported operand type(s) for -: 'list' and 'list'` from `end - start` (F:manimlib/mobject/three_dimensions.py:201). Upstream is the same (U:manimlib/mobject/three_dimensions.py:195) | `np.array([...])`, or constants such as `2 * OUT` |
| `TexturedSurface(surface=s, image_file=f)` | `TypeError: ... missing 1 required positional argument: 'uv_surface'` (F:manimlib/mobject/types/surface.py:305-311) | `TexturedSurface(s, f)` |

- Unlike several 2D classes (SKILL.md §6), the constructor `color=` is applied on `Sphere`, `Torus`, `Cylinder`, `Disk3D`, `Square3D`, and `Cube`, and `opacity=` on `Sphere` and `Cube` [verified by run].

`TexturedSurface`:
- `TexturedSurface(Sphere(radius=2), "file.png")` rendered with `FadeIn`, `ShowCreation`, and ambient rotation [verified by run].
- `get_opacity()` raises `ValueError: no field of name rgba` [verified by run]. Its data has an `opacity` field instead of `rgba` (F:manimlib/mobject/types/surface.py:298-303, F:manimlib/mobject/mobject.py:1409-1410).
- `set_opacity`, `set_color`, `set_shading`, `copy()`, and `SurfaceMesh(textured)` work [verified by run]. `set_opacity`/`set_color` are overridden (F:manimlib/mobject/types/surface.py:370-380).
- A URL `image_file` is downloaded with `urlretrieve` on every construction, with no existence check (F:manimlib/mobject/types/surface.py:322, F:manimlib/utils/file_ops.py:33-42). Every render then needs the network. Download once and pass the local path. Source evidence.

### C4. Shading [verified by run]

- `set_shading(reflectiveness=None, gloss=None, shadow=None, recurse=True)` (F:manimlib/mobject/mobject.py:1442-1460).
- Compared by applying it to a sphere.
  - `(0, 0, 0)` gives a flat color.
  - The default `(0.3, 0.2, 0.4)` gives gentle shading.
  - `(0.8, 0.8, 0.8)` gives a strong highlight.
- The default shading of Text is (0, 0, 0).
- `set_reflectiveness(x)`, `set_gloss(x)`, `set_shadow(x)` each set one component of `set_shading` (F:manimlib/mobject/mobject.py:1471-1481). `Sphere().set_gloss(0.8).set_shadow(0.5).get_shading()` → (0.3, 0.8, 0.5).

Light source:
- The light is `self.camera.light_source`, a `Point` at world (-10, 10, 10) (F:manimlib/camera/camera.py:42,97-98). Its position is read every frame (F:manimlib/camera/camera.py:241).
- Each of these moved a sphere's highlight from the upper left to the lower right:
  - `self.camera.light_source.move_to([10, -10, -10])`
  - `self.play(self.camera.light_source.animate.move_to([10, -10, -10]))`. The play adds the Point to the scene; it draws nothing.
  - The class attribute `default_camera_config = dict(light_source_position=[10, -10, -10])`
- The light does not follow the camera. At `reorient(150, 70)` the highlight sat at the upper right, so a camera orbit sweeps the highlight across the object.

### C5. `fix_in_frame`

- `fix_in_frame(recurse=True)`, `unfix_from_frame()`, `is_fixed_in_frame()` (F:manimlib/mobject/mobject.py:1924-1934).
- A fixed mob does not get a depth test in ThreeDScene.add (`depth_test` False) [verified by run].
- To place a fixed label near a 3D point, use `label.fix_in_frame().move_to(self.frame.to_fixed_frame_point(p))`.
  - It is an approximation without perspective. At φ=60 it was correct near the screen center [verified by run].

### C6. Keeping text readable in 3D and tilted 2D [verified by run]

Text laid flat on a plane is squashed by perspective. I compared the on-screen aspect ratio of a 3:1 box (measured with `to_fixed_frame_point`).

| Camera (θ, φ) | As is | `rotate(φ, RIGHT)` only | `rotate(φ, RIGHT).rotate(θ, OUT)` |
|---|---|---|---|
| (0, 50) | 4.67 | 3.0 | 3.0 |
| (-30, 70) | 3.83 | 1.85 | 3.0 |
| (20, 50) | 2.50 | 1.86 | 3.0 |

To billboard (make it face the camera), do the following. This assumes γ=0.

```python
theta, phi = self.frame.get_euler_angles()[:2]   # radians
label.rotate(phi, RIGHT).rotate(theta, OUT).move_to(p)
```

- Using only `rotate(φ, RIGHT)` is correct **only when θ=0**.
- The same applies to a 2D scene tilted with `frame.reorient` in a Scene, because it is the same CameraFrame.
- Tex is the same. I checked by billboarding `Tex(R"z = f(x, y)")` in a ThreeDScene.
- The calculation is done once, so you must rotate again if the camera moves. For text that must read regardless of the camera, use `fix_in_frame`.
- In `ThreeDAxes.add_axis_labels`, the x and y labels lie in the xy plane, and only the z label is stood up by 90° around the RIGHT axis (F:manimlib/mobject/coordinate_systems.py:574-583). Source evidence.
- `ThreeDAxes.add_coordinate_labels()` numbers only the x and y axes, flat in the xy plane. It zips the axes with `[x_values, y_values]` (F:manimlib/mobject/coordinate_systems.py:529). It returned 2 groups of 6 numbers for x(-3, 3), y(-3, 3), z(-2, 2).
  - Add z numbers yourself, stood up like the z label. They read upright at (-30, 70):

```python
z_nums = VGroup(*(
    Integer(n, font_size=24).rotate(90 * DEG, RIGHT).next_to(axes.c2p(0, 0, n), LEFT, buff=0.15)
    for n in (-2, -1, 1, 2)
))
```

### C7. depth test pitfalls [verified by run]

Setup: ThreeDScene, camera (0, 45), a `Square3D` with opacity 0.5 at z=1. Text is placed below it (z=0) or above it (z=1.5), overlapping the surface on screen.

| Case | Result |
|---|---|
| A: added **before** the surface (z=0 or z=1.5) | Visible through the surface. A black-edge artifact appears around the glyph edges |
| B: added **after** the surface (z=0) | Almost invisible; only a faint outline remains |
| C: `self.add(t, set_depth_test=False)` after the surface | Drawn on top of the surface regardless of depth |
| D: placed **above** the surface (z=1.5) and added after the surface | **Hidden, as in B.** Being closer to the camera than the surface does not help. Tex is the same |
| `fix_in_frame()` label | Normal |
| Billboard Tex added after a `ThreeDAxes.get_graph` surface | The part overlapping the surface on screen is clipped |

- It is not only a surface problem. Text at z=0 above an opaque `Square3D` (z=-2) and a filled `Square` without stroke were hidden too. Text at z=0 above a filled `Rectangle` (z=-2) that received the depth test was hidden as well. Changing to `samples = 0` made no difference.
  - That is, the fill of a VMobject that gets the depth test is discarded when it overlaps an earlier-drawn object on screen, regardless of front-to-back order. The cause was not checked.
  - A filled `Square` with a stroke showed its fill under the same conditions. The reason was not checked.

Workarounds:
- Add with `self.add(label, set_depth_test=False)`. If it appeared through `play`, call `label.deactivate_depth_test()`.
- Or use `fix_in_frame()`.
- Or add it before the surface. With a translucent surface, both the text above and below the surface are visible. The edge artifact remains.
- Moving the label closer to the camera than the surface does not fix it.

Translucent surfaces. Setup: ThreeDScene (-30, 70), `Sphere(radius=1.4, color=BLUE, opacity=0.4)` with a red `Cube(side_length=0.8)` inside.

| Case | Result |
|---|---|
| A: cube added after the sphere | Cube invisible. A dark crescent shows at the sphere's edge |
| B: cube added before | Cube visible, tinted by the sphere. Crescent remains |
| C: `always_sort_to_camera` + cube after | Cube invisible. No crescent |
| D: `self.add(sphere, set_depth_test=False)` + cube after | Same as A. `sphere.depth_test` stayed True |
| E: `sphere.deactivate_depth_test()` + cube after | Cube visible but drawn over the sphere, untinted |
| F: `always_sort_to_camera` + cube before | Cube visible and tinted, no crescent. **Use this** |

- A translucent surface still writes depth. `opacity < 1` alone does not reveal objects added after it.
- D fails because `Surface` sets `depth_test=True` in its constructor (F:manimlib/mobject/types/surface.py:48), and `set_depth_test=False` only skips turning it on (F:manimlib/scene/scene.py:951-954).
- The crescent is probably the draw order of front and back faces. That is inference; the shader was not checked.
- Only this one sphere-and-cube setup at (-30, 70) was rendered.
- An object that must be added later can take `set_z_index(-1)` instead. `Scene.add` sorts `self.mobjects` by z_index on every add (F:manimlib/scene/scene.py:336-338), so it is drawn before the surface. A ball added after a translucent bowl stayed visible and tinted; without it the ball vanished [verified by run, gallery/gradient_descent.py]. Set it before the add: `self.add(cube); cube.set_z_index(-1)` left the cube hidden, because nothing re-sorts until the next `add` [verified by run].

### C8. Animating the camera [verified by run]

Setup: ThreeDScene, start θ = -30, `run_time=2`, `rate_func=linear`, θ logged on every rendered frame of a `-w -l` render. All exited 0.

| Code | θ over the play |
|---|---|
| `frame.animate.increment_theta(360 * DEG)` | -30 throughout. **No motion**; frames at 0, 0.7, 1.3 s identical |
| `frame.animate.increment_theta(270 * DEG)` | -30 → -120. Turns **-90°**, the other way |
| `frame.animate.reorient(200, 70)` | -30 → -160 (= 200). Turns -130° instead of +230° |
| `frame.animate.increment_theta(180 * DEG)` | -30 → 150, positive this time. 180° sits on the flip boundary (quaternion dot product 0), so do not rely on the direction |
| `frame.animate.increment_theta(170 * DEG)` | -30 → 140, at uneven speed: about 15° per 1/8 of the run at the ends, 27.5° in the middle |
| `Rotate(frame, TAU, axis=OUT)` | -30, 138, -30, 48, -120, 96, 60, -84, 150. Erratic |
| 4 × `frame.animate.increment_theta(90 * DEG)` | Full turn, back to -30 |
| `UpdateFromAlphaFunc(frame, lambda m, a: m.set_theta(t0 + a * TAU))` | Even steps, full turn |
| `add_ambient_rotation(180 * DEG)` + `wait(2)` | Even steps, full turn |

Why:
- `.animate` on the frame blends the orientation quaternion component by component (F:manimlib/mobject/mobject.py:1836). The fork then flips the target quaternion to the side nearer the start (F:manimlib/camera/camera_frame.py:121-130).
  - A +360° target is the same orientation as the start, so nothing moves. Above 180°, the other way round is shorter.
  - With φ and γ fixed, the turn between the two orientations is exactly Δθ about z, so the limit is 180° of θ.
- Component-wise blending is a lerp, not a slerp, so `linear` still gives uneven angular speed. 90° legs varied by about ±8% (examples/camera_orbit.py).
- `Rotate` restores only point data each frame and then calls `rotate` (F:manimlib/animation/rotation.py:42-55). `CameraFrame.rotate` composes onto the current orientation (F:manimlib/camera/camera_frame.py:132-136), which is not restored, so the turn piles up.
- Upstream has no `CameraFrame.interpolate` override (no `def interpolate` in U:manimlib/camera/camera_frame.py; the only match is the comment at :27). Upstream was not run, so its behavior is not claimed here.

Recipes (all in [examples/camera_orbit.py](../examples/camera_orbit.py)):
- Under 180°: `self.play(self.frame.animate.reorient(θ, φ, 0))`.
- Changing θ and φ a lot in one `.animate` also rolls the view mid-move, though both ends have γ = 0: (-30, 70, 0) → (140, 10, 0) peaked at γ = 47° [verified by run]. Split it into a θ leg and a φ leg (each stayed at γ = 0), or drive both angles: `self.play(UpdateFromAlphaFunc(self.frame, lambda m, a: m.set_euler_angles(theta=t0 + a * dt, phi=p0 + a * dp, gamma=0)), rate_func=linear)`, with `t0, p0 = self.frame.get_euler_angles()[:2]` (radians).
- Full or long turn in one play, at constant speed:

```python
t0 = self.frame.get_theta()
self.play(UpdateFromAlphaFunc(self.frame, lambda m, a: m.set_theta(t0 + a * TAU)), run_time=8, rate_func=linear)
```

- Long turn with `.animate`: chain legs under 180°, with `rate_func=linear` so it does not pause between legs.
- Open-ended: `self.frame.add_ambient_rotation(45 * DEG)` (rad/s), `self.wait(t)`, `self.frame.clear_updaters()`. Then settle on an exact view with `.animate.reorient(θ, φ, 0)`.
  - The `-sw` PNG matched the last mp4 frame, because the final view is absolute. Time updaters alone can end differently under `-sw` (SKILL.md §10).
- `frame.add_updater(lambda m, dt: m.increment_theta(20 * dt))` is 20 **rad**/s, about 3 turns per second. `increment_theta` takes radians (F:manimlib/camera/camera_frame.py:239-240). Write `20 * DEG * dt`, or use `add_ambient_rotation(20 * DEG)`. Source evidence.

Follow-cam (probed in a 2D `Scene`):
- `self.frame.add_updater(lambda m: m.move_to(dot))` keeps the frame on a moving object. Stop it with `self.frame.clear_updaters()`.
  - The frame is in `self.mobjects` (F:manimlib/scene/scene.py:117), and animations do not suspend its updaters by default (`suspend_mobject_updating=False`, F:manimlib/animation/animation.py:43).
- It kept following during `self.play(dot.animate.shift(UP * 3), self.frame.animate.set_height(4))`: frame center (5, 3, 0) = dot, height 4.0.
- `Scene.clear()` removes the frame and stops its updaters (SKILL.md §9).
