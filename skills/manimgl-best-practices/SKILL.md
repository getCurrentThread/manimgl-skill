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
- `surface.py`가 `trimesh`와 `pywavefront`를 import하지만 `setup.cfg` install_requires에는 없다 (F:manimlib/mobject/types/surface.py:5-6, F:setup.cfg:31).
  - 그래서 포크만 설치하면 `import manimlib`가 `ModuleNotFoundError: No module named 'trimesh'`로 실패한다 [실행확인].
  - 두 패키지를 직접 추가한다 (I:pyproject.toml).
- 실행은 항상 `uv run manimgl ...`로 한다. 전역 `manimgl`은 다른 설치일 수 있다.
- CLI 플래그와 출력 경로의 상세 내용은 [references/cli-and-output.md](references/cli-and-output.md)에 있다.

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
| `-p` (CE: 미리보기) | 쓰지 않는다 | 포크의 `-p`는 presenter mode다. wait마다 키 입력을 기다린다 (F:manimlib/config.py:109, F:manimlib/scene/scene.py:607,624) |
| `MovingCameraScene`, `ZoomedScene` | `Scene` + `self.frame` | F:manimlib/scene/scene.py:112 |
| `self.camera.frame` | `self.frame` | `self.camera.frame`도 동작은 한다 (같은 객체, F:manimlib/scene/scene.py:112). 다만 `self.frame`으로 통일한다. imcommit은 raenimgl 별칭 `self.cf`를 쓰는데, 이것도 `self.frame`과 같은 객체다 (R:raenimgl/scene.py:146-147) |
| `set_camera_orientation`, `move_camera` | `self.frame.reorient(θ, φ, γ, center, height)`, `.animate.reorient(...)` (각도는 degree) | F:manimlib/camera/camera_frame.py:211 |
| `begin_ambient_camera_rotation` | `self.frame.add_ambient_rotation(10 * DEG)` (초당 각도) 후 `self.frame.clear_updaters()`. 다음 씬이 끝 방향을 이어받아야 하면 `self.play(self.frame.animate.reorient(θ, φ), run_time=t)`로 정확히 맞춘다 | F:manimlib/camera/camera_frame.py:251 |
| `add_fixed_in_frame_mobjects` | `mob.fix_in_frame()` | F:manimlib/mobject/mobject.py:1924 |
| `config.frame_width` | `FRAME_WIDTH` (≈14.22), `FRAME_HEIGHT` (8) | F:manimlib/constants.py:19-20 |
| `Axes.plot`, `get_area`, `add_coordinates` | `get_graph`, `get_area_under_graph`, `add_coordinate_labels` | F:manimlib/mobject/coordinate_systems.py:184,417,520 |
| `ParametricFunction` | `ParametricCurve(f, t_range=(a, b, step))` | F:manimlib/mobject/functions.py:17 |
| `Circumscribe` | `FlashAround` | F:manimlib/animation/indication.py:255 |
| `Wiggle` | `WiggleOutThenIn` | F:manimlib/animation/indication.py:355 |
| `Table`, `Paragraph`, `Unwrite`, `DoubleArrow`, `Dot3D`, `add_subcaption` | 포크에 없다 | grep 0건 (`CurvedDoubleArrow`만 있음) |

포크에 어떤 Scene/Animation/Mobject 클래스가 있는지는 [references/api-inventory.md](references/api-inventory.md)에서 확인한다. 설치된 포크에서 생성한 목록이다.

## 3. 포크에 없는 것 (upstream 3b1b/manim이나 3b1b/videos에는 있음)

포크는 upstream보다 112커밋 뒤다. 다음은 쓰지 않는다. 상세 내용은 [references/fork-diff.md](references/fork-diff.md)에 있다.

- `VideoMobject`, `Sprite` (U:manimlib/mobject/types/video_mobject.py:258,398)
- `MandelbrotFractal`, `NewtonFractal` 등 fractals (U:manimlib/mobject/fractals.py:64-284)
- `vmobject_to_svg` (U:manimlib/utils/svg_export.py:8)
- `Surface.set_sort_to_camera` (U:manimlib/mobject/types/surface.py:267)
- `VMobject.set_joint_roundness`, `set_fill(gradient_direction=)` (U:manimlib/mobject/types/vectorized_mobject.py:591,271)
- `Updater` 클래스 (U:manimlib/mobject/mobject.py:2247)
- 설정 키 `scene.invert_zoom_scroll`, `camera.bundle_draws`, `camera.draw_together`, `file_writer.crf`
  - 포크는 모르는 설정 키를 받으면 그 섹션의 생성자에서 TypeError로 실패한다 [실행확인]. 예: `TypeError: Scene.__init__() got an unexpected keyword argument 'invert_zoom_scroll'`, `Camera.__init__() got an unexpected keyword argument 'bundle_draws'`
  - 그래서 3b1b/videos의 `custom_config.yml`은 그대로 쓸 수 없다.

## 4. 렌더 CLI와 출력

- 씬 이름은 항상 정확히 준다.
  - 씬이 여럿인데 이름이 없거나 틀리면 `input()` 프롬프트가 뜬다 (F:manimlib/extract_scene.py:48,103-104).
  - 대화형 터미널에서는 그 자리에서 멈춘다. stdin이 없는 셸(에이전트)에서는 아무것도 렌더하지 않고 exit 1로 끝난다 [실행확인].
- 마지막 프레임 확인은 `uv run manimgl main.py S -sw`이고, 결과는 `videos/S.png`(1920x1080)다 [실행확인].
  - `-s`만 쓰면 아무것도 저장하지 않고 창을 띄운다.
  - 이유: `save_last_frame = skip_animations and write_file`이고 (F:manimlib/config.py:278-280), 창은 `-w`가 없을 때 뜬다 (F:manimlib/config.py:331).
  - PNG는 **마지막 프레임뿐**이다. 애니메이션 도중의 문제와 카메라가 움직이는 씬의 시작 구도는 mp4에서 프레임을 뽑아 본다 (manimgl-workflow 2단계).
- 영상은 `-w`로 만들며 결과는 `videos/S.mp4`, 기본 1920x1080 30fps다 (F:manimlib/default_config.yml:55,57).
  - 초안은 `-w -l`(854x480)로 만든다 (F:manimlib/default_config.yml:101).
- 출력은 **실행한 cwd 기준 `videos/` 바로 아래**에 평면으로 쌓인다 (F:manimlib/default_config.yml:23, F:manimlib/config.py:391-393). 그래서 `src/<영상>/` 안에서 실행한다.
- 성공 여부는 **종료 코드**로 판정한다. `construct()`에서 예외가 나면 exit 1이고 `<Scene>_temp.mp4`가 남지만, 이전 `<Scene>.mp4`는 그대로 남는다 [실행확인]. 파일이 있다고 성공한 것이 아니다.
- `-a`는 `-w`를 켜지 않는다. 여러 씬은 `manimgl main.py A B C -w`처럼 이름을 나열한다 [실행확인].
- 설정 병합 순서 (F:manimlib/config.py:37-38):
  1. 기본 yml
  2. cwd의 `custom_config.yml`
  3. `--config_file` (경로가 없으면 조용히 무시된다)
  4. CLI 인자
  5. 씬 클래스 속성 `default_camera_config`. CLI의 `-c`, `--fps`보다 우선한다 [실행확인]
  - 상세 내용은 [references/cli-and-output.md](references/cli-and-output.md) §5에 있다.
- `self.embed()`는 창이 없으면 아무 일도 하지 않는다 (F:manimlib/scene/scene.py:208). 그래서 `-w` 렌더에 남아 있어도 된다.
- Tex 결과가 이상하면 `--clear-cache`로 다시 렌더한다 (F:manimlib/config.py:222).

## 5. 포크 기본값 (upstream과 다름)

- 배경 `#000000` (yml:56)
- `default_stroke_width` 2.0 (yml:78)
- `text.font` "Noto Sans KR" (yml:91)

upstream 기본값은 차례로 `#333333`, 4.0, Consolas다.

## 6. 색 지정 함정 [실행확인]

**규칙: 색은 생성한 뒤 `.set_color(X)`로 준다.** 생성자 `color=`는 클래스에 따라 무시된다. `.set_color()`는 아래 모든 클래스에서 동작하고, imcommit 방식과도 같다.

생성자 `color=`가 무시되는 클래스. 생성자가 fill/stroke 색을 직접 지정하고, VMobject는 `fill_color or color`, `stroke_color or color` 순서로 고르기 때문이다 (F:manimlib/mobject/types/vectorized_mobject.py:100-102).

| 클래스 | `color=BLUE`의 결과 | 근거 |
|---|---|---|
| `Text`, `Tex`, `TexText`, `Brace` | 흰색 | StringMobject가 생성 끝에 `set_fill(흰색 기본값)`을 다시 호출한다 (F:manimlib/mobject/svg/string_mobject.py:49,72) |
| `Dot` | 흰색 | F:manimlib/mobject/geometry.py:446 |
| `Arrow`, `Vector` | 회색 #BBBBBB | F:manimlib/mobject/geometry.py:1083,1085 |
| `StrokeArrow` | 회색 #BBBBBB | F:manimlib/mobject/geometry.py:945 |
| `Circle`, `Ellipse` | **빨간** 테두리 | `stroke_color=RED` (F:manimlib/mobject/geometry.py:392) |
| `Annulus` | 회색 채움 #BBBBBB | F:manimlib/mobject/geometry.py:636 |

- `color=`가 그대로 먹는 것: `Square`, `Rectangle`, `SurroundingRectangle`, `Line`, `DashedLine`, `Arc`, `Polygon`, `Triangle`, `RegularPolygon`, `CurvedArrow`, `NumberLine`, `axes.get_graph(color=)`, `ParametricCurve(color=)`.
- `fill_color=X`도 `Text`, `Tex`, `Dot`, `Arrow`에서는 동작한다. 하지만 `Circle` 테두리는 바꾸지 못하므로 `.set_color()`가 안전하다.
- upstream도 같은 코드다.
- imcommit 사용 빈도 (AST, `main copy.py` 제외):
  - `Text(...)`/`Tex(...)` 뒤에 체인으로 붙인 `.set_color(`: 376회 / 152회
  - 생성자 `color=`: `Text`에서 10회뿐이다. 이 10회는 포크에서 모두 무시된다.
- 부분 색은 `t2c={"loss": RED}`나 `t["정밀도"].set_color(YELLOW)`로 칠한다 (F:manimlib/mobject/svg/string_mobject.py:549,575).

## 7. 한글 [실행확인]

- 한글은 `Text`로 쓴다. 포크 기본 폰트가 Noto Sans KR이라 `font=`가 필요 없다 (yml:91).
  - imcommit의 한글 `Text` 90회 중 `font=`를 준 것은 1회뿐이고, 그것도 기본값과 같은 `"Noto Sans KR"`이다 (I:src/gen_model/main.py:30-32).
  - 세리프체가 필요할 때만 `font="Noto Serif KR"`을 준다 (imcommit에서는 raenimgl `Words`로 13회).
  - 폰트가 없으면 setup.sh가 경고한다.
- 한글과 수식은 따로 만들어 붙인다: `VGroup(Text("손실"), Tex(R"= \sum_i ...")).arrange(RIGHT, buff=0.15)` (I:src/floatingpoint/main.py:1501). imcommit은 Tex 안에 한글을 넣은 적이 없다 (0건).
  - 같은 `font_size`면 Noto Sans KR `Text`가 `Tex`보다 약 1.37배 크다 [실행확인]. 높이를 맞추려면 Text의 `font_size`를 Tex의 약 0.73배로 준다 (Tex 40 ↔ Text 29).
- Tex 안에 꼭 한글이 필요할 때:
  - 기본 템플릿은 LaTeX 오류가 난다. 이 머신에서는 `template="ctex"`도 fontspec 오류가 났다.
  - 동작이 확인된 방법은 `Tex(R"\text{손실} = ...", template="empty_ctex", additional_preamble=R"\usepackage{amsmath}\usepackage{xcolor}\usepackage{kotex}\setmainhangulfont{Noto Sans KR}")`다. xelatex과 kotex가 필요하다. 예제는 [examples/korean.py](examples/korean.py).
  - `xcolor`가 없으면 `t2c`, `isolate`, `BulletedList`가 `Undefined control sequence ... {{\color`로 실패한다 [실행확인].
  - 수식 모드의 한글은 반드시 `\text{}`로 감싼다. 감싸지 않으면 오류 없이 한글만 사라진다 [실행확인].
  - `BraceText`/`BraceLabel`에는 `template=`를 줄 수 없다 (TypeError). `Brace(...).get_tex(..., template=...)`를 쓴다 [실행확인].
- `Brace.get_text("한글")`은 `Text`를 만들기 때문에 한글이 된다 (F:manimlib/mobject/svg/brace.py:87).
- 이 문서의 한글 결과는 시스템 UTF-8 로캘(Windows ACP 65001)에서만 확인했다.
- 한글, Tex 템플릿, 3D의 상세 내용은 [references/korean-tex-3d.md](references/korean-tex-3d.md)에 있다.

## 8. Tex

- 문자열은 raw string `R"..."`로 쓴다. 수식은 `Tex`, 문장은 `TexText`다.
- 부분은 문자열로 고른다: `eq["m"]`, `eq["(p c)^2"]`, `t2c={"m": BLUE}`.
  - 같은 기호를 이어 가는 변형은 `TransformMatchingTex`로 한다 (F:manimlib/animation/transform_matching_parts.py:189). 예제는 [examples/tex.py](examples/tex.py).
  - `TransformMatchingTex`/`TransformMatchingStrings`의 기본 `run_time`은 **2**다 (F:manimlib/animation/transform_matching_parts.py:29). 다른 1초짜리 애니메이션과 같은 play에 넣으면 play 전체가 2초가 되므로 `run_time`을 적는다 [실행확인].
- 글자가 바뀌는 라벨과 카운터:
  - 폭이 다른 두 문자열을 `FadeTransform`으로 바꾸면 줄 전체가 늘어나며 약 1초 동안 두 겹으로 보인다.
  - 일부만 바뀌면 `TransformMatchingStrings(a, b, key_map={"16": "8"}, run_time=1)`처럼 바뀌는 부분을 짝지어 준다.
    - key_map이 없으면 남은 글자를 모양이 같은 것끼리 짝지어서, 같은 숫자가 다른 자리로 날아갈 수 있다 (F:manimlib/animation/transform_matching_parts.py:101).
  - 관계없는 문장으로 바꿀 때는 `LaggedStart(FadeOut(a), FadeIn(b), lag_ratio=0.6)`처럼 나갔다가 들어오게 한다.
  - 이 항목들은 E2E 테스트 렌더에서 확인했다.
- LaTeX가 필요한 것: Tex/TexText, `Brace`(Tex 하위 클래스, F:manimlib/mobject/svg/brace.py:32), Matrix 괄호, `get_graph_label`, `get_axis_labels`.
- LaTeX가 필요 없는 것: 눈금 숫자 `add_coordinate_labels`, `add_numbers`, 실수 `DecimalNumber`/`Integer`.
  - 숫자 글자는 `Text`로 만든다 (F:manimlib/mobject/numbers.py:24-30).
  - 단 `unit=R"^\circ"`처럼 백슬래시가 든 글자와 복소수(`i`)는 `Tex`로 만들어지므로 LaTeX가 필요하다 (같은 줄).
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
  - 기울인 영역의 라벨과 평면 요소는 같은 φ만큼 `rotate(φ * DEG, axis=RIGHT)`해서 카메라를 보게 한다.
  - 이 회전은 θ = 0일 때만 정확하다. θ가 0이 아니면 원점에서 `label.rotate(φ, RIGHT).rotate(θ, OUT)`(γ = 0일 때) 또는 `label.apply_matrix(self.frame.get_orientation().as_matrix())`로 돌린 뒤 `move_to`한다 [실행확인].
- 진짜 3D는 `ThreeDScene`으로 한다 [실행확인, examples/three_d.py].
  - 기본 방향은 (-30, 70)이고, add할 때 depth test가 켜진다 (F:manimlib/scene/scene.py:946-953).
  - 화면에 고정할 제목은 `fix_in_frame()`.
  - 곡면은 `ThreeDAxes.get_graph(lambda x, y: ...)`로 만든다.
  - **depth test는 add할 때마다 다시 켜진다.** `play`가 객체를 넣을 때도 마찬가지다.
    - depth test를 받은 글자는 먼저 그려진 곡면이나 채운 도형과 화면에서 겹치면, 그보다 카메라에 가까워도 가려진다 [실행확인].
    - 같은 평면에서 겹쳐 깜빡이는 객체나 늘 보여야 하는 객체(라벨)는, 그것을 넣는 애니메이션이 끝난 **뒤에** `mob.deactivate_depth_test()`를 부른다.
    - 또는 `self.add(mob, set_depth_test=False)`로 넣는다 (F:manimlib/scene/scene.py:951-953).
    - `become()`도 depth test 설정을 복사한다 (F:manimlib/mobject/mobject.py:735).
  - `ThreeDAxes`는 범위의 가운데에 놓인다. 범위가 비대칭이면 축 원점이 ORIGIN이 아니다 [실행확인].
    - 예: x(-1,4), y(-2,3)이면 `c2p(0,0,0)`은 (-1.5, -0.5, 0)이다.
    - 좌표는 모두 `axes.c2p`로 쓰거나, `axes.shift(-axes.c2p(0, 0, 0))`로 원점을 맞춘다.
  - `Arrow`는 평평한 도형이라 카메라가 돌면 옆으로 누워 얇아진다. `arrow.set_perpendicular_to_camera(self.frame)`를 쓴다 (`Arrow`는 `Line` 하위 클래스, F:manimlib/mobject/geometry.py:798). 카메라가 움직이는 동안은 업데이터로 붙인다.
  - `ThreeDAxes.add_axis_labels()`의 x, y 라벨은 xy 평면에 눕고 z 라벨만 선다 (F:manimlib/mobject/coordinate_systems.py:574-583). 읽어야 할 라벨은 위 2D 기울이기의 빌보드 방식으로 돌린다.
  - 카메라가 움직이는 씬의 `-sw` PNG는 이동이 끝난 뒤의 구도다.
- `Scene.clear()`는 `self.mobjects`를 비우므로 `self.frame`도 빠진다 (F:manimlib/scene/scene.py:117,400).
  - 그 뒤로는 `add_ambient_rotation` 같은 frame 업데이터가 멈춘다 [실행확인].
  - `clear()` 다음에 `self.add(self.frame)`를 하면 다시 돈다 [실행확인].
  - `remove_all_except(...)`도 내부에서 `clear()`를 부르므로 같은 문제가 있다 (F:manimlib/scene/scene.py:385-387).
  - 지울 때는 대상을 명시해 `FadeOut`이나 `remove`를 쓴다.

## 10. 업데이터

- `dt`는 **이름**으로 판별한다 (F:manimlib/mobject/mobject.py:834).
  - 함수의 파라미터나 지역 변수에 `dt`가 있으면 `dt=`를 키워드로 넘긴다.
  - 시간 업데이터의 두 번째 파라미터는 반드시 `dt`로 쓰고 (`lambda m, dt: m.rotate(dt)`), 다른 업데이터에는 `dt`라는 지역 변수를 두지 않는다.
- `add_updater`는 붙이는 즉시 실행된다. `call=False`를 줘도 한 번은 실행된다 (F:manimlib/mobject/mobject.py:848).
  - 이미 업데이터가 있는 객체에서 `call=True`(기본값)를 쓰면 새 업데이터가 두 번 실행되고 기존 업데이터도 다시 돈다 (같은 파일 :845-848).
  - 그래서 업데이터는 여러 번 불려도 결과가 같게 쓴다.
- `-sw`(skip)에서는 `play`마다 `dt` 업데이터가 dt=run_time으로 두 번 불린다. 시간 업데이터가 있는 씬의 PNG는 영상 끝 상태와 다를 수 있으니 mp4로 확인한다 [실행확인, references/cli-and-output.md §7].
- `number.f_always.set_value(tracker.get_value)` (F:manimlib/mobject/mobject.py:186).
- `always_redraw`는 매 프레임 객체를 새로 만든다.
- 애니메이션이 끝나면 `clear_updaters()`를 호출한다. 예제는 [examples/updaters.py](examples/updaters.py).

## 11. 구성, 레이아웃, 색, 타이밍

imcommit 관례 요약이다. 상세 내용과 근거는 [references/imcommit-patterns.md](references/imcommit-patterns.md)에 있다.

- **구성**
  - 영상 하나는 `src/<영상>/main.py` 하나다.
  - 서사 순서대로 씬 클래스를 여러 개 둔다 (imcommit은 파일당 1~8개, 중앙값 4).
  - 각 클래스는 앞 씬의 끝 상태를 스스로 다시 만든다.
  - `construct` 안은 `## <짧은 라벨 또는 내레이션 한 줄>` 주석으로 블록을 나눈다.
  - 씬당 15~30초는 이 플러그인의 권장값이다. imcommit에서 잰 값은 아니다.
- 파일 머리에서 시드를 고정한다: `from random import seed`, `seed(41)`, `np.random.seed(41)` (I:init_project.py:5-10). 예제는 [examples/structure.py](examples/structure.py).
- **레이아웃**
  - `next_to`와 `arrange`를 쓰고, buff는 0.1, 0.2, 0.5가 대부분이다.
  - 넓은 캔버스에 영역을 나누고 카메라를 옮긴다.
- **색**
  - 거의 이름 있는 상수만 쓴다. imcommit에 hex 리터럴은 0건이고, 그 밖에는 `interpolate_color`/`random_color`로 계산한 색뿐이다.
  - 쓰임: `GREY_B`는 보조, `GREEN`은 정답, `RED`는 오답, `YELLOW`는 강조.
  - 흐리게 할 때는 `set_opacity(0.2~0.3)`를 쓰거나, 반투명 오버레이를 깔고 남길 것을 `set_z_index`로 올린 뒤 다시 `add`한다.
    - `set_opacity`는 fill opacity도 바꾼다. 테두리만 있는 도형(`Square()` 등, fill opacity 0)에 쓰면 fill 0.2의 회색(#888888) 바탕이 생긴다 [실행확인].
    - 테두리만 흐리게 하려면 `set_stroke(opacity=0.2)`를 쓴다.
- **타이밍**
  - 짧은 동작은 `run_time=0.5`로 한다 (imcommit 최다).
  - `lag_ratio`는 0.3~0.5, rate_func는 기본값을 쓴다.
  - 한 `self.play` 안에서 한 객체에는 `.animate`를 하나만 준다.
    - 부모 VGroup과 그 자식에 `.animate`를 따로 주면, 둘 다 play 전 상태로 목표를 만들고 나중 것이 앞의 변경을 덮어쓴다 (E2E 테스트에서 재현).
    - 메서드를 한 `.animate`에 이어 쓰거나(`mob.animate.set_stroke(...).set_opacity(...)`) play를 나눈다.

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
