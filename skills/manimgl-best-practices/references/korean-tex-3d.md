# 한글 텍스트, Tex, 3D 상세 참조

대상: 포크 @455a420. 근거 표기는 SKILL.md와 같다 (`F:` 포크, `U:` upstream @fafa083, `[실행확인]`).

확인 환경:
- Windows 11, Python 3.10, 시스템 UTF-8 로캘 (`locale.getpreferredencoding()` = cp65001)
  - `working.tex`는 인코딩을 지정하지 않고 쓴다 (F:manimlib/utils/tex_file_writing.py:105). 그래서 로캘이 cp949인 Windows에서는 한글 Tex가 cp949로 써질 수 있다. 소스 근거.
- pango 1.58.2, manimpango 0.7.0
- MiKTeX: cm-super, kotex(`cjk-ko` 패키지 경로) 설치

`[실행확인]`은 이 문서를 쓰며 `-sw` 렌더 PNG를 보거나 Python 프로브로 값을 찍어 본 것이다. 숫자는 이 환경 기준이다.

`text_mobject.py`, `tex_mobject.py`, `brace.py`, `tex_templates.yml`은 upstream과 같다. 이 문서의 Text/Tex 동작은 포크만의 것이 아니다. 예외는 따로 표시한다.

---

## A. 한글 `Text`

### A1. 기본값

| 항목 | 값 | 근거 |
|---|---|---|
| 기본 폰트 | `"Noto Sans KR"` | F:manimlib/default_config.yml:91 [실행확인: `manim_config.text.font`] |
| 여러 줄 정렬 기본값 | `"LEFT"` | F:manimlib/default_config.yml:92 |
| `font_size` 기본값 | 48 | F:manimlib/mobject/svg/text_mobject.py:139 |
| 경로 | Pango 마크업 → SVG → 디스크 캐시 | F:manimlib/mobject/svg/text_mobject.py:53-100 |

- 폰트가 깔려 있는지는 `"Noto Sans KR" in manimpango.list_fonts()`로 확인한다. 이 환경에서는 True였다 [실행확인].

### A2. 글리프 수와 부분 선택 [실행확인]

글리프 수:

| 식 | 결과 |
|---|---|
| `len(Text("가나다 라"))` | 4. 음절 하나가 서브모브젝트 하나이고, 공백은 0개다 |
| `len(Text("한글 abc 123"))` | 8 |
| `len(Text("첫 줄\n둘째 줄 길다"))` | 7. 줄바꿈도 0개다 |

선택:

| 식 | 결과 |
|---|---|
| `t = Text("가나 가나 다가나")`, `t["가나"]` | 3개 부분의 VGroup. 첫 번째만이 아니라 전부 고르고, 단어 경계도 보지 않는다 (`다가나` 안의 것도 포함) |
| `t.select_part("가나", 1)` | 두 번째 출현만 고른다 (0부터 센다) |
| `t[re.compile(r"값\d")]` (`Text("값1 값2 값3")`) | 3개 |

- 근거: `__getitem__` → `select_parts` → `select_unisolated_substring` (F:manimlib/mobject/svg/string_mobject.py:542-573), `select_part` (F:manimlib/mobject/svg/string_mobject.py:554).
- 인덱스는 문자열에서 공백이 아닌 문자 수로 계산한다 (F:manimlib/mobject/svg/string_mobject.py:557-571).
  - 그래서 자모가 분해된(NFD) 한글은 어긋난다.
  - NFD `"가나다 라"`는 코드포인트 8개, 글리프 4개다. NFC `"다"`로 고르면 일치가 없어 빈 VGroup이 나온다. NFD `"다"`로 고르면 글리프 0개인 부분 하나가 나오고, NFD `"가"`로 고르면 `가나` 두 글리프가 잡힌다 [실행확인].
  - macOS 파일명 등 밖에서 읽은 문자열은 `unicodedata.normalize("NFC", s)`로 바꾼 뒤 넘긴다.

### A3. 부분 스타일 인자

| 인자 (긴 이름) | 예 | 결과 |
|---|---|---|
| `t2c` (`text2color`) | `t2c={"loss": RED, "평균": BLUE}` | 동작 [실행확인] |
| `t2w` (`text2weight`) | `t2w={"굵게": BOLD}` | 한글 굵게 동작 [실행확인] |
| `t2s` (`text2slant`) | `t2s={"기울임": ITALIC}` | 한글 기울임 동작 [실행확인] |
| `t2f` (`text2font`) | `t2f={"맑은고딕": "Malgun Gothic"}` | 동작 [실행확인] |
| `t2g` (`text2gradient`) | - | 경고만 낸다. 그라데이션은 `set_color_by_gradient`로 한다 (F:manimlib/mobject/svg/text_mobject.py:193-197) |
| `lsh` (`line_spacing_height`) | - | 줄 간격. Pango 1.50 미만이면 무시된다 (F:manimlib/mobject/svg/text_mobject.py:353-366) |

- 인자 목록: F:manimlib/mobject/svg/text_mobject.py:150-161.
- `BOLD`, `ITALIC`, `NORMAL`은 manimlib 상수(문자열)다 [실행확인].
- 생성자 `color=`는 무시된다. 색은 `set_color`나 `t2c`로 준다 (SKILL.md §6).

### A4. `MarkupText` [실행확인]

- 한글에 `<b>`, `<i>`, `<u>`가 동작한다.
- **`<span foreground="#FF0000">` 같은 마크업 색은 무시되고 흰색이 된다.**
  - SVG를 읽은 뒤 `StringMobject.__init__`이 `set_fill(fill_color)`로 전체를 다시 칠하기 때문이다 (F:manimlib/mobject/svg/string_mobject.py:72).
  - 색은 `MarkupText(..., t2c={"빨강": RED})`나 `set_color`로 준다. 둘 다 동작한다.
- `Text`는 `< > & " '`를 자동으로 escape한다 (F:manimlib/mobject/svg/text_mobject.py:420-431). `MarkupText`에서는 직접 `&lt;` 등으로 쓴다.

### A5. 여러 줄과 정렬 [실행확인]

- `"\n"`으로 줄을 바꾼다.
- `alignment="LEFT" | "CENTER" | "RIGHT"`에 따라 짧은 첫 줄이 왼쪽, 가운데, 오른쪽에 붙었다. 기본값은 LEFT다.
- 자동 줄바꿈은 `line_width=`(manim 단위)로 하며 Pango 폭으로 바뀐다 (F:manimlib/mobject/svg/text_mobject.py:72-75). 소스 근거.

### A6. `font_size`와 실제 높이 [실행확인]

| 객체 (`font_size=144`) | 높이 |
|---|---|
| `Tex("0")` | 0.997 |
| `Text("0")`, Noto Sans KR | 1.367 |
| `Text("가")`, Noto Sans KR | 1.628 |
| `Text("0")`, Malgun Gothic | 1.338 |
| `Text("0")`, Arial | 1.317 |
| `Text("0")`, Consolas | 1.181 |

- "`font_size_for_unit_height=144`이면 `0`의 높이가 1 unit"(F:manimlib/default_config.yml:88,94)이라는 기준은 **Tex에서만 맞았다.**
- 같은 `font_size`라도 Text가 약 1.37배 크다. 빈 캐시 디렉터리에서 다시 재도 같았다.
  - 보정은 `font_family` 없이 `<span font_size="49152">0</span>`을 렌더해서 한다 (F:manimlib/mobject/svg/text_mobject.py:103-112). Text 본문에는 항상 `font_family`가 들어간다 (F:manimlib/mobject/svg/text_mobject.py:346-352).
  - 원인은 이 글꼴 차이다 [실행확인]. 48pt `"0"`의 SVG 높이는 `font_family`가 없을 때 35.53이고, 이는 `serif`와 같다. Sans는 48.44, Noto Sans KR 48.57, Arial 46.78, Times New Roman 44.00이다.
  - 그래서 비율은 글꼴마다 다르다. `font="Sans"`도 serif가 아니라서 1.363이 나온다.
- 실무 기준: Noto Sans KR Text와 Tex를 한 줄에 놓고 숫자 높이를 맞추려면 Text의 `font_size`를 Tex의 약 0.73배로 준다 (예: Tex 40 ↔ Text 29). 다른 글꼴은 다시 잰다.

### A7. 없는 폰트 [실행확인]

`Text("가나다 abc", font="Some Missing Font")`는 예외 없이 아래 경고만 낸다.

```
couldn't load font "Some Missing Font Not-Rotated 48", falling back to "Sans Not-Rotated 48", expect ugly output.
```

- 한글은 대체 폰트로 그려진다. 다만 글자 모양과 자간이 달라지고 폭도 바뀐다 (2.954, 기본 폰트는 2.759).
- `markup_to_svg`는 디스크 캐시를 쓴다. 키는 함수 이름과 인자(마크업 문자열, 정렬, `line_width` 등)의 해시다 (F:manimlib/mobject/svg/text_mobject.py:53-54, F:manimlib/utils/cache.py:21-30). 마크업에 글꼴 이름이 들어 있으므로, 글꼴을 설치하기 전과 후의 키가 같다.
  - 그래서 폰트를 나중에 설치해도 같은 문자열은 캐시된 대체 결과가 계속 나올 수 있다. 이때는 `--clear-cache`를 쓴다. 소스 근거.

### A8. 한글이 들어가는 보조 객체

- `Brace(...).get_text("한글")`은 `Text`를 만든다 (F:manimlib/mobject/svg/brace.py:87-91) [실행확인].
- 다만 `Brace` 자체는 Tex 하위 클래스라 LaTeX가 필요하다 (B5).
- `Code`의 기본 폰트는 Consolas다 (F:manimlib/mobject/svg/text_mobject.py:442).

---

## B. `Tex` / `TexText`

### B1. 렌더 경로

- `Tex(..., template="", additional_preamble="")`는 `latex_to_svg(content, template, additional_preamble)`를 부른다 (F:manimlib/mobject/svg/tex_mobject.py:43-44,81-82).
- 템플릿 결정 (F:manimlib/utils/tex_file_writing.py:19-37):
  - `template=""`이면 설정 `tex.template`을 쓴다. 기본값은 `"default"`다 (F:manimlib/default_config.yml:86).
  - 이름은 소문자로 바꾸고 공백을 `_`로 바꿔서 찾는다.
  - 없는 이름이면 경고 후 default로 간다: `Cannot recognize template no_such_template, falling back to 'default'.` [실행확인]
- 프리앰블은 `템플릿 preamble + "\n" + additional_preamble` 순서다 (F:manimlib/utils/tex_file_writing.py:79).
  - 문서는 `\documentclass[preview]{standalone}`로 만든다 (F:manimlib/utils/tex_file_writing.py:40-47).
- 컴파일러 (F:manimlib/utils/tex_file_writing.py:89-94):
  - `latex`이면 .dvi, `xelatex`이면 `-no-pdf`로 .xdv를 만든다.
  - 그 밖의 컴파일러는 `NotImplementedError: Compiler 'lualatex' is not implemented`로 실패한다 [실행확인, `template="chalkduster"`].
- dvisvgm에는 `--fontmap=ps2pk.map`이 붙는다. 포크 전용이다 (F:manimlib/utils/tex_file_writing.py:138).
- 환경:
  - `Tex`는 `align*` 안에 넣는다 (F:manimlib/mobject/svg/tex_mobject.py:36). `TexText`는 환경이 없다 (F:manimlib/mobject/svg/tex_mobject.py:276-277).
  - 그래서 `empty`나 `empty_ctex` 템플릿에 amsmath 없이 `Tex`를 쓰면 `LaTeX Error: Environment align* undefined.`로 실패한다 [실행확인]. `TexText`는 된다.
- 색 명령:
  - `t2c`, 여러 문자열 인자, `isolate`가 있으면 `{{\color[RGB]{r, g, b} ...}}`가 들어간다 (F:manimlib/mobject/svg/tex_mobject.py:163-178). `BulletedList`는 내부에서 항상 `isolate`를 쓴다 (F:manimlib/mobject/svg/special_tex.py:34).
  - 그래서 xcolor가 없는 프리앰블에서 `t2c`를 쓰면 `LatexError: Undefined control sequence. <argument> {{\color`로 실패한다 [실행확인].
  - 이때는 `\usepackage{xcolor}`를 추가한다.
- 크기 보정은 템플릿 인자 없이 `"0"`을 컴파일해서 한다. 즉 설정 `tex.template`(기본 `default`)을 쓴다 (F:manimlib/mobject/svg/tex_mobject.py:25-32, F:manimlib/utils/tex_file_writing.py:35).
  - 그래서 xelatex 템플릿만 쓰더라도, 설정을 바꾸지 않았다면 default 템플릿(latex와 그 패키지들)이 컴파일되어야 한다. 소스 근거.

### B2. `tex_templates.yml` 전체 (F:manimlib/tex_templates.yml)

기본 템플릿:

| 이름 (줄) | 컴파일러 | 내용 | 이 환경 결과 |
|---|---|---|---|
| `default` (3) | latex | babel, inputenc, `[T1]{fontenc}`, amsmath, amssymb, physics, xcolor 등 | 영문/수식 동작. 한글은 오류 (B3) |
| `ctex` (29) | xelatex | ctex, xeCJK, `\setmainfont{Microsoft YaHei}` | 한글은 `fontspec` 오류 (B3) |
| `basic` (56) | latex | babel, amsmath, amssymb, xcolor | `Tex(R"x^2 + \alpha")` 동작 [실행확인] |
| `basic_ctex` (65) | xelatex | ctex, amsmath, amssymb, xcolor | ctex와 같은 오류 [실행확인] |
| `empty` (74) | latex | 비어 있음 | `TexText` 동작, `Tex`는 `align*` 오류 [실행확인] |
| `empty_ctex` (79) | xelatex | 비어 있음 | kotex 조합의 바탕 (B3) |

글꼴 템플릿 (줄 87-736):

- xelatex:
  - `american_typewriter`, `apple_chancery`, `baskerville_it`, `brushscriptx`, `chalkboard_se`, `comic_sans`, `ecf_webster`
  - `gnu_freesans_tx`, `gnu_freeserif_freesans`, `minion_pro_myriad_pro`, `minion_pro_tx`, `papyrus`, `verdana_it`
- lualatex: `chalkduster`. 포크에서는 NotImplementedError로 쓸 수 없다 [실행확인].
- latex:
  - `antykwa`, `auriocus_kalligraphicus`, `baskervald_adf_fourier`, `biolinum`, `comfortaa`
  - `droid_sans`, `droid_sans_it`, `droid_serif`, `droid_serif_px_it`
  - `ecf_augie`, `ecf_jd`, `ecf_skeetch`, `ecf_tall_paul`, `electrum_adf`, `epigrafica`, `fourier_utopia`, `french_cursive`
  - `gfs_bodoni`, `gfs_didot`, `gfs_neohellenic`, `helvetica_fourier_it`, `latin_modern_tw`, `latin_modern_tw_it`
  - `libertine`, `libris_adf_fourier`, `new_century_schoolbook`, `new_century_schoolbook_px`, `noteworthy_light`, `palatino`
  - `romande_adf_fourier_it`, `slitex`, `times_fourier_it`, `urw_avant_garde`, `urw_zapf_chancery`
  - `venturis_adf_fourier_it`, `vollkorn`, `vollkorn_fourier_it`, `zapf_chancery`

이 환경에서 확인한 것 [실행확인]:
- `verdana_it`, `comic_sans`는 Windows 글꼴이라 동작한다.
- `biolinum`, `noteworthy_light`는 컴파일러가 latex인데 fontspec을 써서 `Fatal Package fontspec Error: The fontspec package requires either XeTeX or LuaTeX.`로 실패한다. 템플릿 정의 오류이며 upstream도 같다.
- 나머지 글꼴 템플릿은 확인하지 않았다. 다수가 macOS 글꼴이나 추가 TeX 패키지를 전제한다.

### B3. Tex 안의 한글

`KO = R"\usepackage{amsmath}\usepackage{kotex}\setmainhangulfont{Noto Sans KR}"`, `KW = dict(template="empty_ctex", additional_preamble=KO)`일 때:

| 코드 | 결과 |
|---|---|
| `Tex(R"\text{손실} = x")` (기본 템플릿) | `LaTeX Error: Unicode character 손 (U+C190) not set up for use with LaTeX.` [실행확인] |
| 같은 식, `template="ctex"` | `Package fontspec Error: The font "SimHei" cannot be found` [실행확인]. 템플릿의 YaHei가 아니라 SimHei를 찾다 실패한다 |
| 같은 식, `template="basic_ctex"` | 위와 같은 SimHei 오류 [실행확인] |
| `Tex(R"\text{손실} = \frac{1}{N} \sum_i \ell_i", **KW)` | 동작, `len` 10 [실행확인] |
| `TexText("한글 문장 with English", **KW)` | 동작, `len` 15 (공백 뺀 글자 수와 같다). 한글은 Noto Sans KR, 영문은 xelatex 기본 Latin Modern(세리프)이다 [실행확인] |
| `TexText(R"넓이는 $\pi r^2$ 이다", **KW)` | 동작 [실행확인] |
| `TexText(R"첫 줄\\둘째 줄", **KW)` | 두 줄, 가운데 정렬 [실행확인]. 기본 `alignment=R"\centering"`이다 (F:manimlib/mobject/svg/tex_mobject.py:42) |
| `Tex(R"손실 = x^2", **KW)` (`\text` 없음) | **오류 없이 한글만 사라지고** `= x²`만 남는다 (`len` 3) [실행확인]. 수식 모드 한글은 반드시 `\text{}`로 감싼다 |
| `Title("한글 제목 Title", **KW)` | 동작 [실행확인] |
| `BulletedList("첫째 항목", "둘째 항목 item", **KW)` | `LatexError: Undefined control sequence. ... {{\color` [실행확인]. 항목마다 `isolate`를 넘기므로 xcolor가 필요하다 (F:manimlib/mobject/svg/special_tex.py:34). `KWX`(B4)로는 동작하고 2부분이다 [실행확인] |
| `Brace(m, DOWN).get_tex(R"\text{한글} x", **KW)` | 동작 [실행확인] |
| `BraceText(m, "한글", **KW)`, `BraceLabel(...)` | `TypeError: Mobject.__init__() got an unexpected keyword argument 'template'` [실행확인] |

- `BraceText`/`BraceLabel`이 실패하는 이유: kwargs를 `VMobject.__init__`, `Brace`, 라벨 생성자에 모두 넘긴다 (F:manimlib/mobject/svg/brace.py:122,129,131).
  - 대신 `Brace` + `get_tex(..., **KW)`나 `get_text("한글")`을 쓴다.
- 영문도 산세리프로 맞추려면 프리앰블에 `\setmainfont{...}`를 추가해야 할 것이다. 확인하지 않았다.

### B4. kotex Tex에서 한글 부분 선택 [실행확인]

`KWX = dict(template="empty_ctex", additional_preamble=KO + R"\usepackage{xcolor}")`일 때:

| 코드 | 결과 |
|---|---|
| `Tex(R"\text{손실} = ...", t2c={"손실": YELLOW, R"\ell_i": RED}, **KWX)` | 손실 글리프 2개와 ℓᵢ 글리프 2개가 칠해진다 |
| `eq = Tex(R"\text{손실} = ...", **KW)`, `eq["손실"].set_color(GREEN)`, `eq["N"].set_color(BLUE)` | 정확히 칠해진다. xcolor가 필요 없다 (색 명령을 넣지 않음) |
| `TexText("한글 문장 with English", t2c={"문장": YELLOW, "English": RED}, **KWX)` | 동작 |
| `tt["문장"]`, `tt["with"]` | 동작 |

- 정리하면, `t2c`, `isolate`, 여러 문자열 인자, `BulletedList`에는 xcolor가 필요하다. 렌더 후 `eq["..."]`로 고르는 것에는 필요 없다.

### B5. LaTeX가 필요한 클래스 [실행확인]

확인 방법: PATH에서 TeX를 빼고, `custom_config.yml`의 `directories.cache`로 빈 캐시를 지정한 뒤 생성해 보았다. TeX가 없으면 `LatexError`가 아니라 `FileNotFoundError: [WinError 2] 지정된 파일을 찾을 수 없습니다`가 난다 (`subprocess.run`, F:manimlib/utils/tex_file_writing.py:108).

| 필요함 | 내부 Tex 생성 위치 |
|---|---|
| `Tex`, `TexText` | - |
| `Brace`, `BraceLabel`, `BraceText` | `Brace(Tex)` F:manimlib/mobject/svg/brace.py:32. 라벨 생성자 F:manimlib/mobject/svg/brace.py:111,176 |
| `Matrix`, `IntegerMatrix`, `DecimalMatrix` (요소가 float여도) | 괄호가 항상 Tex다 (F:manimlib/mobject/matrix.py:120). 문자열 요소 F:manimlib/mobject/matrix.py:117. `\vdots`/`\hdots` F:manimlib/mobject/matrix.py:189,195 |
| `Axes.get_axis_labels`, `get_x_axis_label`, `get_y_axis_label` | F:manimlib/mobject/coordinate_systems.py:143 |
| `get_graph_label`(문자열 라벨) | F:manimlib/mobject/coordinate_systems.py:294 |
| `ThreeDAxes.add_axis_labels` | F:manimlib/mobject/coordinate_systems.py:576 |
| `Title`, `BulletedList` | F:manimlib/mobject/svg/special_tex.py:34,61 |
| `BarChart` | F:manimlib/mobject/probability.py:270,293 |
| `Slider` | F:manimlib/mobject/number_line.py:297 |
| `DecimalNumber`의 `unit=R"^\circ"`처럼 `\`가 든 문자, 복소수(`i`) | F:manimlib/mobject/numbers.py:24-31 |
| `SampleSpace` 제목/라벨 | F:manimlib/mobject/probability.py:56,136. 소스 근거 |

| 필요 없음 |
|---|
| `Text`, `MarkupText`, `Code`, `DecimalNumber(3.14)`, `Integer`, `NumberLine.add_numbers`, `Axes.add_coordinate_labels`, `SurroundingRectangle`, `Arrow` |

- **디스크 캐시에 있으면 TeX 없이도 생성된다.** 전에 렌더한 Tex는 PATH에 TeX가 없어도 만들어지고, 새 문자열만 실패했다 [실행확인].
- 그래서 한 기계에서 되던 씬이 새 환경에서 처음 보는 Tex에서만 실패할 수 있다.

### B6. cm-super, 빈 SVG, 캐시

- default 템플릿은 `\usepackage[T1]{fontenc}`를 쓴다 (F:manimlib/tex_templates.yml:9). T1 글꼴 윤곽은 cm-super가 준다.
  - 이 환경: `kpsewhich sfrm1000.pfb` → `.../fonts/type1/public/cm-super/` [실행확인].
- cm-super가 없으면 dvisvgm은 빈 SVG를 내고 exit 0으로 끝난다 (SKILL.md §8).
  - 보정용 `"0"`도 빈 SVG가 되어 `ValueError: SVG has no content to measure`로 실패한다 (F:manimlib/mobject/svg/tex_mobject.py:31, F:manimlib/mobject/svg/svg_mobject.py:45). 메시지 자체는 빈 SVG로 재현했다 [실행확인].
- 이와 별개로 포크는 dvisvgm 종료 코드를 보지 않는다 (F:manimlib/utils/tex_file_writing.py:133-151). upstream은 0이 아니면 `LatexError`를 낸다 (U:manimlib/utils/tex_file_writing.py:150-152).
  - 다만 위 cm-super 경우는 exit 0이라 upstream 검사로도 잡히지 않는다.
- LaTeX 오류는 `working.log`에서 `! ` 뒤 두 줄만 잘라 보여준다 (F:manimlib/utils/tex_file_writing.py:121-130). 전체는 아래 log를 본다.

캐시는 두 곳이다.

| 위치 | 내용 | 근거 |
|---|---|---|
| `<cwd>/latex_cache/` | `working.tex`, `.log`, `.aux`, `.dvi` 또는 `.xdv`. 매번 덮어쓴다. 오류를 볼 때 연다 | F:manimlib/default_config.yml:35, F:manimlib/config.py:240-244, F:manimlib/utils/tex_file_writing.py:97-105 [실행확인] |
| diskcache. 기본 `%LOCALAPPDATA%\manim\manim\Cache` | `full_tex_to_svg`, `markup_to_svg` 결과 | F:manimlib/utils/cache.py:17-30, F:manimlib/utils/directories.py:17-18 [실행확인: `get_cache_dir()`] |

- `--clear-cache`는 렌더 전에 diskcache를 비운다 (F:manimlib/__main__.py:58-59, F:manimlib/utils/cache.py:33-34).
  - [실행확인] 항목 17개 → 비움 → `Writing a^2...`로 다시 컴파일했다.
  - `latex_cache/` 폴더는 건드리지 않는다. 소스 근거.
- `custom_config.yml`의 `directories: {cache: "경로"}`로 diskcache 위치를 바꿀 수 있다 (F:manimlib/default_config.yml:40) [실행확인].

---

## C. 3D

### C1. `Scene`과 `ThreeDScene`

| | `Scene` | `ThreeDScene` |
|---|---|---|
| `samples` (MSAA) | 0 (F:manimlib/scene/scene.py:60) | 4 (F:manimlib/scene/scene.py:947) |
| `default_frame_orientation` (θ, φ, 도) | (0, 0) (F:manimlib/scene/scene.py:62) | (-30, 70) (F:manimlib/scene/scene.py:948) [실행확인: `get_euler_angles` → (-30, 70, 0)] |
| `add` 시 depth test | 없음. add 순서대로 그린다 (F:manimlib/scene/scene.py:328) | `fix_in_frame`이 아닌 mob에 `apply_depth_test()` (F:manimlib/scene/scene.py:949-954) [실행확인] |
| stroke | 그대로 | stroke 있는 VMobject는 `set_flat_stroke(False)` (F:manimlib/scene/scene.py:955-956) |

- `self.play`로 처음 등장하는 mob도 `self.add`를 거친다 (F:manimlib/scene/scene.py:551-552). 그래서 depth test가 같이 걸린다.
- depth test를 빼려면 `self.add(mob, set_depth_test=False)`로 add한다 [실행확인].
- 시작 방향:
  - 생성 시 `frame.reorient(*default_frame_orientation)` 후 `make_orientation_default()`를 부른다 (F:manimlib/scene/scene.py:113-114).
  - 그래서 Scene 서브클래스에 `default_frame_orientation = (θ, φ)`를 두면 기울어진 2D 씬으로 시작한다. 소스 근거.
- VMobject의 `apply_depth_test`는 `anti_alias_width`를 0으로 만든다 (F:manimlib/mobject/types/vectorized_mobject.py:423-430). ThreeDScene에서는 samples=4가 이를 메운다. 소스 근거.
- `ThreeDScene.add`는 최상위 mob의 `is_fixed_in_frame()`만 본다 (F:manimlib/scene/scene.py:953).
  - upstream은 family 단위로 검사하도록 고쳤다 (U:manimlib/scene/scene.py:934-943). 주석상 이유는 "FadeTransform 중 고정 글씨가 depth test에 걸려 사라짐"이다.
  - 포크에서 `self.add(VGroup(고정_Text))`로는 재현되지 않았다 (`depth_test` False). `VGroup(고정_Text).is_fixed_in_frame()`이 True였기 때문이다. `self.play(FadeIn(고정_라벨))`에서도 False였다 [실행확인]. FadeTransform 중의 경우는 확인하지 않았다.

### C2. `CameraFrame` API

`self.frame`이 CameraFrame이다. 시그니처는 `inspect.signature`로 확인했다 [실행확인].

| 메서드 | 시그니처 | 비고 | 근거 (F:manimlib/camera/camera_frame.py) |
|---|---|---|---|
| `reorient` | `(theta_degrees=None, phi_degrees=None, gamma_degrees=None, center=None, height=None)` | **도** 단위. None이면 유지 | :211-228 |
| `set_euler_angles` | `(theta=None, phi=None, gamma=None, units=RADIANS)` | 라디안 | :138-154 |
| `set_theta` / `set_phi` / `set_gamma` | `(theta)` / `(phi)` / `(gamma)` | 라디안 | :230-237 |
| `increment_euler_angles` | `(dtheta=0, dphi=0, dgamma=0, units=RADIANS)` | zxz면 φ를 [0, π]로 자른다. φ=0에서 -20° → 0 [실행확인] | :156-174 |
| `increment_theta` / `_phi` / `_gamma` | `(dtheta, units=RADIANS)` / `(dphi, ...)` / `(dgamma, ...)` | | :239-249 |
| `increment_mirrored_euler_angles` (**포크 전용**) | `(dtheta=0, dphi=0, units=RADIANS)` | φ를 -π까지 내린다. 올릴 때 상한은 max(현재 φ, 0). (0, 30°)에서 dphi=-60° → `get_euler_angles`가 (180, 30, -180)을 돌려준다 (φ=-30과 같은 방향) [실행확인] | :176-206 |
| `add_ambient_rotation` | `(angular_speed=1*DEG)` | **rad/s**. updater로 θ를 늘린다. `10*DEG`, dt=1 → θ +10° [실행확인]. 멈추려면 `self.frame.clear_updaters()` | :251-253 |
| `get_euler_angles` | `() -> [θ, φ, γ]` (rad) | 짐벌락이면 θ에 합친다 | :68-83 |
| `get_theta` / `get_phi` / `get_gamma` | `()` | | :85-92 |
| `set_field_of_view` / `get_field_of_view` | `(rad)` | 기본 fovy는 45° [실행확인] | :261-263, :287-288, :29 |
| `set_focal_distance` / `get_focal_distance` | `(d)` | fovy를 다시 계산한다. 기본(높이 8, 45°)은 9.657 [실행확인] | :256-259, :284-285 |
| `get_implied_camera_location` | `()` | (-30, 70)에서 (-4.537, -7.859, 3.303) [실행확인] | :290-295 |
| `to_fixed_frame_point` / `from_fixed_frame_point` | `(point, relative=False)` | 뷰 행렬만 적용한다. 원근은 빠진다 | :297-305 |
| `make_orientation_default` / `to_default_state` | `()` | 기본 방향, 모양, 중심으로 되돌린다 | :58-66 |
| `set_euler_axes` | `(seq)` | 기본 `"zxz"` | :208-209, :30 |

- 회전은 `Rotation.from_euler("zxz", [γ, φ, θ])`, 즉 R = Rz(θ)·Rx(φ)·Rz(γ)다 (:152).
- 애니메이션은 `self.play(self.frame.animate.reorient(...))`로 한다. 보간은 쿼터니언의 짧은 경로를 택한다. 포크 전용이다 (:121-130).
- `set_camera_orientation`, `move_camera`, `begin_ambient_camera_rotation`은 없다 [실행확인].

### C3. 3D 객체

렌더해서 형태를 확인한 것 [실행확인]: `Sphere`, `Torus`, `Cylinder`, `Cone`, `Line3D`, `Disk3D`, `Square3D`, `Cube`, `Prism`, `VCube`, `Dodecahedron`, `SurfaceMesh`, `ThreeDAxes.get_graph`. 나머지 행은 소스 근거다.

| 클래스 | 주요 인자 (기본값) | 근거 |
|---|---|---|
| `Surface` | `color=GREY, shading=(0.3,0.2,0.4), depth_test=True, u_range=(0,1), v_range=(0,1), resolution=(101,101)` | F:manimlib/mobject/types/surface.py:44-75 |
| `ParametricSurface` | `(uv_func, u_range=(0,1), v_range=(0,1), **kw)` | F:manimlib/mobject/types/surface.py:268-280 |
| `SGroup` | `(*surfaces)` | F:manimlib/mobject/types/surface.py:283 |
| `TexturedSurface` | `(uv_surface, image_file, dark_image_file=None)` | F:manimlib/mobject/types/surface.py:296-311 |
| `TexturedGeometry`, `ThreeDModel` | `(geometry: trimesh.Trimesh, texture_file)`, `(obj_file, height=3)`. surface.py가 trimesh와 pywavefront를 최상위에서 import하므로, 두 패키지는 이 클래스뿐 아니라 `import manimlib` 자체에 필요하다 (SKILL.md §0) | F:manimlib/mobject/types/surface.py:5-6,407-408,435-436 |
| `Sphere` | `radius=1, resolution=(101,51)` | F:manimlib/mobject/three_dimensions.py:93 |
| `Torus` | `r1=3, r2=1` | F:manimlib/mobject/three_dimensions.py:125 |
| `Cylinder` | `height=2, radius=1, axis=OUT, resolution=(101,11)` | F:manimlib/mobject/three_dimensions.py:147 |
| `Cone` | Cylinder 인자 | F:manimlib/mobject/three_dimensions.py:178 |
| `Line3D` | `(start, end, width=0.05)` | F:manimlib/mobject/three_dimensions.py:192 |
| `Disk3D` | `radius=1` | F:manimlib/mobject/three_dimensions.py:212 |
| `Square3D` | `side_length=2` | F:manimlib/mobject/three_dimensions.py:237 |
| `Cube` | `color=BLUE, opacity=1, shading=(0.1,0.5,0.1), side_length=2` | F:manimlib/mobject/three_dimensions.py:270 |
| `Prism` | `(width=3, height=2, depth=1)` | F:manimlib/mobject/three_dimensions.py:290 |
| `VGroup3D`, `VCube`, `VPrism`, `Dodecahedron`, `Prismify` | VMobject 기반. depth_test=True | F:manimlib/mobject/three_dimensions.py:303-399 |
| `SurfaceMesh` | `(uv_surface, resolution=(21,11), stroke_width=1, stroke_color=GREY_A)` | F:manimlib/mobject/three_dimensions.py:31 |
| `ThreeDAxes` | `x_range=(-6,6,1), y_range=(-5,5,1), z_range=(-4,4,1)` | F:manimlib/mobject/coordinate_systems.py:539 |
| `ThreeDAxes.get_graph` | `(func(x, y), color=BLUE_E, opacity=0.9, u_range=None, v_range=None)` → ParametricSurface. 축 단위를 반영한다 | F:manimlib/mobject/coordinate_systems.py:585-607 |
| `ThreeDAxes.get_parametric_surface` | `(func(u, v), color=BLUE_E, opacity=0.9)` | F:manimlib/mobject/coordinate_systems.py:609-621 |

- 없는 것 [실행확인]: `Dot3D`, `Arrow3D`, `Cuboid`, `Polyhedron`, `Tetrahedron`, `Octahedron`, `Icosahedron`.
- 점은 `GlowDot`, `TrueDot`, `DotCloud`를 쓴다.
- 반투명 곡면의 면 정렬은 `surface.always_sort_to_camera(self.camera)`로 한다 (F:manimlib/mobject/types/surface.py:249-254). 소스 근거.
  - upstream의 `set_sort_to_camera`는 포크에 없다.

### C4. 셰이딩 [실행확인]

- `set_shading(reflectiveness=None, gloss=None, shadow=None, recurse=True)` (F:manimlib/mobject/mobject.py:1442-1460).
- 구에 적용해 비교했다.
  - `(0, 0, 0)`이면 평면색이 된다.
  - 기본값 `(0.3, 0.2, 0.4)`이면 완만한 음영이 생긴다.
  - `(0.8, 0.8, 0.8)`이면 강한 하이라이트가 생긴다.
- Text의 shading 기본값은 (0, 0, 0)이다.

### C5. `fix_in_frame`

- `fix_in_frame(recurse=True)`, `unfix_from_frame()`, `is_fixed_in_frame()` (F:manimlib/mobject/mobject.py:1924-1934).
- 고정된 mob은 ThreeDScene.add에서 depth test를 받지 않는다 (`depth_test` False) [실행확인].
- 3D 점 근처에 고정 라벨을 놓을 때는 `label.fix_in_frame().move_to(self.frame.to_fixed_frame_point(p))`로 한다.
  - 원근이 빠진 근사다. φ=60에서 화면 중앙 부근은 맞았다 [실행확인].

### C6. 3D와 기울인 2D에서 글자 읽히게 하기 [실행확인]

평면에 눕힌 글자는 원근으로 눌린다. 3:1 상자의 화면 가로세로비를 비교했다 (`to_fixed_frame_point`로 측정).

| 카메라 (θ, φ) | 그대로 | `rotate(φ, RIGHT)`만 | `rotate(φ, RIGHT).rotate(θ, OUT)` |
|---|---|---|---|
| (0, 50) | 4.67 | 3.0 | 3.0 |
| (-30, 70) | 3.83 | 1.85 | 3.0 |
| (20, 50) | 2.50 | 1.86 | 3.0 |

빌보드(카메라를 보게 하기)는 다음처럼 한다. γ=0이라고 가정한다.

```python
theta, phi = self.frame.get_euler_angles()[:2]   # 라디안
label.rotate(phi, RIGHT).rotate(theta, OUT).move_to(p)
```

- `rotate(φ, RIGHT)`만 쓰는 방식은 **θ=0일 때만** 맞다.
- Scene에서 `frame.reorient`로 기울인 2D 씬에도 똑같이 적용된다. 같은 CameraFrame이기 때문이다.
- Tex도 같다. ThreeDScene에서 `Tex(R"z = f(x, y)")`를 빌보드해 확인했다.
- 계산은 한 번만 하므로 카메라를 돌리면 다시 회전해야 한다. 카메라와 무관하게 읽혀야 하는 글자는 `fix_in_frame`을 쓴다.
- `ThreeDAxes.add_axis_labels`의 x, y 라벨은 xy 평면에 눕고, z 라벨만 RIGHT 축으로 90° 세운다 (F:manimlib/mobject/coordinate_systems.py:574-583). 소스 근거.

### C7. depth test 함정 [실행확인]

설정: ThreeDScene, 카메라 (0, 45), z=1에 opacity 0.5인 `Square3D`. Text는 그 아래(z=0)나 위(z=1.5)에 두고, 화면에서 곡면과 겹치게 했다.

| 경우 | 결과 |
|---|---|
| A: 곡면보다 **먼저** add (z=0이나 z=1.5) | 곡면을 통해 보인다. 글자 가장자리에 검은 테두리 artifact가 생긴다 |
| B: 곡면 **다음에** add (z=0) | 거의 보이지 않고 윤곽만 희미하게 남는다 |
| C: 곡면 다음에 `self.add(t, set_depth_test=False)` | 깊이와 상관없이 곡면 위에 그려진다 |
| D: 곡면 **위**(z=1.5)에 두고 곡면 다음에 add | **B처럼 가려진다.** 곡면보다 카메라에 가까워도 소용없다. Tex도 같다 |
| `fix_in_frame()` 라벨 | 정상 |
| `ThreeDAxes.get_graph` 곡면 다음에 add한 빌보드 Tex | 화면에서 곡면과 겹친 부분이 잘린다 |

- 곡면만의 문제가 아니다. 불투명 `Square3D`(z=-2) 위 z=0에 둔 Text와 stroke 없는 채운 `Square`도 가려졌다. depth test를 받은 채운 `Rectangle`(z=-2) 위 z=0에 둔 Text도 가려졌다. `samples = 0`으로 바꿔도 같았다.
  - 즉 depth test를 받는 VMobject의 채움은, 먼저 그려진 물체와 화면에서 겹치면 앞뒤 순서와 상관없이 버려진다. 원인은 확인하지 않았다.
  - stroke를 준 채운 `Square`는 같은 조건에서 채움이 보였다. 이유는 확인하지 않았다.

대응:
- `self.add(label, set_depth_test=False)`로 add한다. `play`로 등장시킨 뒤라면 `label.deactivate_depth_test()`를 부른다.
- 또는 `fix_in_frame()`을 쓴다.
- 또는 곡면보다 먼저 add한다. 반투명 곡면이면 곡면 위 글자와 아래 글자가 모두 보인다. 가장자리 artifact는 남는다.
- 라벨을 곡면보다 카메라 쪽으로 옮겨도 해결되지 않는다.
