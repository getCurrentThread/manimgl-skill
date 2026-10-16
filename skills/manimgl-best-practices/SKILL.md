---
name: manimgl-best-practices
description: Rules for writing manimgl scenes against the CodingVillainKor/manimgl fork (a 3b1b/manim fork with Korean defaults). Use whenever writing, editing, reviewing or debugging `from manimlib import *` code or `manimgl` commands, and whenever ManimCE habits (Create, MathTex, `manim` command, MovingCameraScene, -ql/-p) might leak in. Covers fork defaults, APIs the fork lacks, CLI/output paths, color pitfalls, Korean text, Tex, camera/3D and the imcommit project conventions.
---

# manimgl (CodingVillainKor 포크) 작성 규칙

대상: `CodingVillainKor/manimgl` @ `455a4201` (2026-10-11). 3b1b/manim 포크이며 PyPI `manimgl`, ManimCE(`manim`)와 다르다.

근거 표기:
- `F:` 포크 @455a420
- `U:` 3b1b/manim @fafa083
- `I:` manimgl-imcommit @a2fe49f
- `R:` raenimgl @177affc
- `[실행확인]`: 이 플러그인의 `examples/`나 프로브를 Windows에서 렌더해 확인한 것

## 0. 환경

- 설치와 검증은 `bash ${CLAUDE_PLUGIN_ROOT}/scripts/setup.sh <프로젝트 폴더>`로 한다. uv 프로젝트에 포크를 커밋 고정으로 설치한다.
- 포크인지 확인할 때 버전 문자열은 쓸 수 없다. PyPI와 같은 1.7.2다.
  - 대신 `manim_config.key_bindings.yaw == "e"`를 본다 (F:manimlib/default_config.yml:121).
  - 또는 `direct_url.json`의 URL과 커밋을 본다. setup.sh가 둘 다 검사한다.
- `surface.py`가 `trimesh`와 `pywavefront`를 import하지만 `setup.cfg` install_requires에는 없다 (F:manimlib/mobject/types/surface.py:5-6, F:setup.cfg:31). 두 패키지를 직접 추가한다 (I:pyproject.toml).
- 실행은 항상 `uv run manimgl ...`로 한다. 전역 `manimgl`은 다른 설치일 수 있다.

## 1. import

- `from manimlib import *`만 쓴다. `from manim import *`(ManimCE)는 쓰지 않는다.
- raenimgl은 선택 의존성이다. 쓸 때는 [references/raenimgl.md](references/raenimgl.md)를 먼저 읽는다.

## 2. ManimCE 습관 → 포크 대체

| 쓰지 말 것 (CE) | 포크에서 | 근거 |
|---|---|---|
| `Create` | `ShowCreation` | F:manimlib/animation/creation.py:48. 포크에는 `Create`가 없다. raenimgl만 별칭을 준다 (R:raenimgl/animation.py:310) |
| `MathTex` | `Tex` (수식 모드) | 포크에 `MathTex` 0건 |
| CE `Tex` (본문 텍스트) | `TexText` 또는 `Text` | §8 |
| `manim f.py S -ql` | `manimgl f.py S -w -l` | F:manimlib/config.py:69,79. `-ql`은 `-q`(quiet) + `-l`로 파싱된다 |
| `-p` (CE: 미리보기) | 쓰지 않는다 | 포크의 `-p`는 presenter mode다. wait마다 키 입력을 기다려 `-w`와 함께 쓰면 멈춘다 (F:manimlib/config.py:109, F:manimlib/scene/scene.py:607,624) |
| `MovingCameraScene`, `ZoomedScene` | `Scene` + `self.frame` | F:manimlib/scene/scene.py:112 |
| `self.camera.frame` | `self.frame` | `self.camera.frame`도 동작은 한다 (같은 객체, F:manimlib/scene/scene.py:112). 다만 imcommit 스타일인 `self.frame`으로 통일한다 |
| `set_camera_orientation`, `move_camera` | `self.frame.reorient(θ, φ, γ, center, height)`, `.animate.reorient(...)` (각도는 degree) | F:manimlib/camera/camera_frame.py:211 |
| `begin_ambient_camera_rotation` | `self.frame.add_ambient_rotation(10 * DEG)` 후 `self.frame.clear_updaters()` | F:manimlib/camera/camera_frame.py:251 |
| `add_fixed_in_frame_mobjects` | `mob.fix_in_frame()` | F:manimlib/mobject/mobject.py:1924 |
| `config.frame_width` | `FRAME_WIDTH` (≈14.22), `FRAME_HEIGHT` (8) | F:manimlib/constants.py:19-20 |
| `Axes.plot`, `get_area`, `add_coordinates` | `get_graph`, `get_area_under_graph`, `add_coordinate_labels` | F:manimlib/mobject/coordinate_systems.py:184,417,520 |
| `ParametricFunction` | `ParametricCurve(f, t_range=(a, b, step))` | F:manimlib/mobject/functions.py:17 |
| `Circumscribe` | `FlashAround` | F:manimlib/animation/indication.py:255 |
| `Wiggle` | `WiggleOutThenIn` | F:manimlib/animation/indication.py:355 |
| `Table`, `Paragraph`, `Unwrite`, `DoubleArrow`, `Dot3D`, `add_subcaption` | 포크에 없다 | grep 0건 (`CurvedDoubleArrow`만 있음) |

포크에 무엇이 있는지는 [references/api-inventory.md](references/api-inventory.md)에서 확인한다. 설치된 포크에서 생성한 목록이다.

## 3. 포크에 없는 것 (upstream 3b1b/manim이나 3b1b/videos에는 있음)

포크는 upstream보다 112커밋 뒤다. 다음은 쓰지 않는다. 상세 내용은 [references/fork-diff.md](references/fork-diff.md)에 있다.

- `VideoMobject`, `Sprite` (U:manimlib/mobject/types/video_mobject.py:258,398)
- `MandelbrotFractal`, `NewtonFractal` 등 fractals (U:manimlib/mobject/fractals.py)
- `vmobject_to_svg` (U:manimlib/utils/svg_export.py:8)
- `Surface.set_sort_to_camera` (U:manimlib/mobject/types/surface.py:267)
- `VMobject.set_joint_roundness`, `set_fill(gradient_direction=)` (U:manimlib/mobject/types/vectorized_mobject.py:271,591)
- `Updater` 클래스 (U:manimlib/mobject/mobject.py:2247)
- 설정 키 `scene.invert_zoom_scroll`, `camera.bundle_draws`
  - 포크의 `Scene`은 모르는 키를 받으면 TypeError로 실패한다. `TypeError: Scene.__init__() got an unexpected keyword argument 'invert_zoom_scroll'` [실행확인]
  - 그래서 3b1b/videos의 `custom_config.yml`은 그대로 쓸 수 없다.

## 4. 렌더 CLI와 출력

- 씬 이름은 항상 준다. 씬이 여럿인데 이름이 없으면 `input()` 프롬프트에서 멈춘다 (F:manimlib/extract_scene.py:48,95).
- 마지막 프레임 확인은 `uv run manimgl main.py S -sw`이고, 결과는 `videos/S.png`다 [실행확인].
  - `-s`만 쓰면 아무것도 저장하지 않고 창을 띄운 채 멈춘다.
  - 이유: `save_last_frame = skip_animations and write_file` (F:manimlib/config.py:278-280).
- 영상은 `-w`로 만들며 결과는 `videos/S.mp4`, 기본 1920x1080 30fps다 (F:manimlib/default_config.yml:55,57).
  - 초안은 `-w -l`(854x480)로 만든다 (F:manimlib/default_config.yml:101).
- 출력은 **실행한 cwd 기준 `videos/` 바로 아래**에 평면으로 쌓인다 (F:manimlib/default_config.yml:23, F:manimlib/config.py:391-393). 그래서 `src/<영상>/` 안에서 실행한다.
- 설정 병합 순서 (F:manimlib/config.py:37-38):
  1. 기본 yml
  2. cwd의 `custom_config.yml`
  3. `--config_file`
  4. CLI 인자
- `self.embed()`는 창이 없으면 아무 일도 하지 않는다 (F:manimlib/scene/scene.py:208). 그래서 `-w` 렌더에 남아 있어도 된다.
- Tex 결과가 이상하면 `--clear-cache`로 다시 렌더한다 (F:manimlib/config.py:222).

## 5. 포크 기본값 (upstream과 다름)

- 배경 `#000000` (yml:56)
- `default_stroke_width` 2.0 (yml:78)
- `text.font` "Noto Sans KR" (yml:91)

upstream 기본값은 차례로 `#333333`, 4.0, Consolas다.

## 6. 색 지정 함정 [실행확인]

- **`Text`, `Tex`, `TexText`, `Dot`는 생성자의 `color=`를 무시하고 흰색이 된다.** `.set_color(X)`나 `fill_color=X`를 쓴다.
  - StringMobject는 `super().__init__` 뒤에 `set_fill(fill_color=흰색 기본값)`을 다시 호출한다 (F:manimlib/mobject/svg/string_mobject.py:49,72).
  - `Dot`은 `fill_color=DEFAULT_MOBJECT_COLOR`를 명시하고, VMobject는 `fill_color or color` 순서로 고른다 (F:manimlib/mobject/geometry.py:446, F:manimlib/mobject/types/vectorized_mobject.py:100). upstream도 같다.
  - imcommit은 `.set_color(`를 150회, 생성자 `color=`는 6회 쓴다.
- `Square`, `Circle`, `Rectangle`, `SurroundingRectangle`, `Arrow`의 `color=`는 정상이다.
- 부분 색은 `t2c={"loss": RED}`나 `t["정밀도"].set_color(YELLOW)`로 칠한다 (F:manimlib/mobject/svg/string_mobject.py:549,575).

## 7. 한글 [실행확인]

- 한글은 `Text`로 쓴다. 포크 기본 폰트가 Noto Sans KR이라 `font=`가 필요 없다 (yml:91). imcommit도 한글 `Text`에 `font=`를 0회 쓴다. 폰트가 없으면 setup.sh가 경고한다.
- 한글과 수식은 따로 만들어 붙인다: `VGroup(Text("손실"), Tex(R"= \sum_i ...")).arrange(RIGHT, buff=0.15)` (I:src/floatingpoint/main.py:1501). imcommit은 Tex 안에 한글을 넣은 적이 없다 (0건).
- Tex 안에 꼭 한글이 필요할 때:
  - 기본 템플릿은 LaTeX 오류, `template="ctex"`는 fontspec 오류가 난다.
  - 동작이 확인된 방법은 `Tex(R"\text{손실} = ...", template="empty_ctex", additional_preamble=R"\usepackage{amsmath}\usepackage{kotex}\setmainhangulfont{Noto Sans KR}")`다. xelatex과 kotex가 필요하다. 예제는 [examples/korean.py](examples/korean.py).
- `Brace.get_text("한글")`은 `Text`를 만들기 때문에 한글이 된다 (F:manimlib/mobject/svg/brace.py:87).
- 이 문서의 한글 결과는 시스템 UTF-8 로캘(Windows ACP 65001)에서만 확인했다.

## 8. Tex

- 문자열은 raw string `R"..."`로 쓴다. 수식은 `Tex`, 문장은 `TexText`다.
- 부분은 문자열로 고른다: `eq["m"]`, `eq["(p c)^2"]`, `t2c={"m": BLUE}`.
  - 같은 기호를 이어 가는 변형은 `TransformMatchingTex`로 한다 (F:manimlib/animation/transform_matching_parts.py:189). 예제는 [examples/tex.py](examples/tex.py).
- LaTeX가 필요한 것: Tex/TexText, `Brace`(Tex 하위 클래스, F:manimlib/mobject/svg/brace.py:32), Matrix 괄호, `get_graph_label`, `get_axis_labels`.
- LaTeX가 필요 없는 것: 눈금 숫자 `add_coordinate_labels`, `add_numbers`, `DecimalNumber`. 숫자는 `Text`로 만든다 (F:manimlib/mobject/numbers.py:24-30).
- MiKTeX를 새로 설치하면 cm-super가 없다.
  - 그러면 dvisvgm이 빈 SVG를 만들고 exit 0으로 끝나며, manimgl은 `SVG has no content to measure`로 실패한다.
  - `miktex packages install cm-super`로 설치한 뒤 `--clear-cache`로 다시 렌더한다. 빈 SVG가 캐시에 남기 때문이다 [실행확인].

## 9. 카메라와 3D

- 2D 카메라 이동 [실행확인, examples/camera.py]:
  1. `self.frame.save_state()`
  2. `self.play(self.frame.animate.move_to(x).set_height(h))`
  3. `self.play(Restore(self.frame))`
- 2D 씬을 기울이는 imcommit 방식 (I:src/bondinterest/main.py:129-150):
  - `self.frame.animate.reorient(θ, φ, γ, center, height)`로 기울인다.
  - 읽어야 할 라벨은 같은 φ만큼 `rotate(φ * DEG, axis=RIGHT)`해서 카메라를 보게 한다.
- 진짜 3D는 `ThreeDScene`으로 한다 [실행확인, examples/three_d.py].
  - 기본 방향은 (-30, 70)이고, add할 때 depth test가 켜진다 (F:manimlib/scene/scene.py:946-953).
  - 화면에 고정할 제목은 `fix_in_frame()`.
  - 곡면은 `ThreeDAxes.get_graph(lambda x, y: ...)`로 만든다.
- `Scene.clear()`는 `self.mobjects`를 비우므로 `self.frame`도 빠진다 (F:manimlib/scene/scene.py:117,400). 지울 때는 대상을 명시해 `FadeOut`이나 `remove`를 쓴다.

## 10. 업데이터

- `dt`는 **파라미터 이름**으로 판별한다: `lambda m, dt: m.rotate(dt)` (F:manimlib/mobject/mobject.py:834).
- `add_updater`는 붙이는 즉시 한 번 실행된다. `call=True`가 기본값이다 (F:manimlib/mobject/mobject.py:843).
- `number.f_always.set_value(tracker.get_value)` (F:manimlib/mobject/mobject.py:186).
- `always_redraw`는 매 프레임 객체를 새로 만든다.
- 애니메이션이 끝나면 `clear_updaters()`를 호출한다. 예제는 [examples/updaters.py](examples/updaters.py).

## 11. 구성, 레이아웃, 색, 타이밍 (imcommit 관례 요약)

상세 내용과 근거는 [references/imcommit-patterns.md](references/imcommit-patterns.md)에 있다.

- **구성**
  - 영상 하나는 `src/<영상>/main.py` 하나다.
  - 서사 순서대로 씬 클래스 3~8개를 두고, 각 씬은 15~30초다.
  - 각 클래스는 앞 씬의 끝 상태를 스스로 다시 만든다.
  - `construct` 안은 `## <내레이션 한 줄>` 주석으로 블록을 나눈다.
- 파일 머리에서 시드를 고정한다: `seed(41)`, `np.random.seed(41)` (I:init_project.py:7-10). 예제는 [examples/structure.py](examples/structure.py).
- **레이아웃**
  - `next_to`와 `arrange`를 쓰고, buff는 0.1, 0.2, 0.5가 대부분이다.
  - 넓은 캔버스에 영역을 나누고 카메라를 옮긴다.
- **색**
  - 이름 있는 상수만 쓴다. imcommit에 hex 리터럴은 0건이다.
  - 쓰임: `GREY_B`는 보조, `GREEN`은 정답, `RED`는 오답, `YELLOW`는 강조.
  - 흐리게 할 때는 `set_opacity(0.2)`를 쓰거나, 반투명 오버레이를 깔고 남길 것을 `set_z_index`로 올린 뒤 다시 `add`한다.
- **타이밍**
  - 짧은 동작은 `run_time=0.5`로 한다 (imcommit 최다, 185회).
  - `lag_ratio`는 0.3~0.5, rate_func는 기본값을 쓴다.

## 12. 예제 (전부 `-sw`와 `-w -l`로 렌더 확인)

`bash ${CLAUDE_PLUGIN_ROOT}/scripts/check_examples.sh <uv 프로젝트>`로 다시 확인할 수 있다.

| 파일 | 보여 주는 것 |
|---|---|
| [examples/structure.py](examples/structure.py) | 한 파일에 여러 씬, `##` 블록, 시드, 강조와 흐림, 오버레이 + z_index, `set_color` |
| [examples/korean.py](examples/korean.py) | 한글 Text, 부분 색, Text+Tex 나란히, kotex로 Tex 안 한글 |
| [examples/tex.py](examples/tex.py) | t2c, 문자열 선택, TransformMatchingTex, Brace+한글 |
| [examples/camera.py](examples/camera.py) | `self.frame` 이동/복원, 2D 씬 기울이기 + 라벨 회전 |
| [examples/three_d.py](examples/three_d.py) | ThreeDScene, 곡면, `fix_in_frame`, ambient rotation |
| [examples/updaters.py](examples/updaters.py) | ValueTracker, `dt` 업데이터, `f_always`, `always_redraw`, `Dot(fill_color=)` |
| [examples/graphs.py](examples/graphs.py) | Axes, `get_graph`, 그래프 라벨, 넓이, ParametricCurve |
| [examples/raenimgl_optional.py](examples/raenimgl_optional.py) | raenimgl을 쓸 때: `(InteractiveScene, Scene2D)`, `playw` |
