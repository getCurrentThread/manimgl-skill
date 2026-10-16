# raenimgl (선택 의존성)

## 개요

- 출처: `CodingVillainKor/raenimgl` @ `177affc69311d13fcad3404b2599a7714de1d4f2` (2026-09-25)
- imcommit이 실제로 import하는 유틸 라이브러리다.
- `raenim`과는 다른 저장소다. `raenim`은 ManimCE용이다.
- **LICENSE 파일이 없다.** 이 문서는 API와 동작만 설명하고 코드는 옮기지 않는다.
- 경로는 raenimgl 저장소 루트 기준이다. imcommit 사용 횟수는 [imcommit-patterns.md](imcommit-patterns.md)와 같은 범위(사본 제외 34개 파일)에서 AST로 센 이름 출현 수다.

## 설치

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/setup.sh <프로젝트> --with-raenimgl
```

- pyproject는 `manimgl>=1.7.2`만 선언하고 git 소스는 없다 (pyproject.toml).
  - 그래서 raenimgl을 단독으로 설치하면 PyPI manimgl이 깔린다.
  - **포크를 git 소스로 고정한 같은 uv 프로젝트에 추가해야** 포크가 유지된다.
  - setup.sh는 추가한 뒤 `direct_url.json`이 여전히 포크 @455a4201을 가리키는지 확인한다 [실행확인].
- `setuptools<71`도 같이 고정된다.
- setup.sh는 raenimgl이 이미 pyproject에 있으면 다시 고정하지 않는다. 그 경우 rev는 기존 pyproject를 따른다.

## import 부작용 (몽키패치)

`from raenimgl import *` 한 줄로 다음이 바뀐다.

| 대상 | 내용 | 위치 |
|---|---|---|
| `manimlib.utils.tex_file_writing.full_tex_to_svg` | 교체된다. 포크가 추가한 dvisvgm `--fontmap=ps2pk.map`이 빠진다 | raenimgl/__init__.py:15-68 |
| `_AnimationBuilder.__init__` / `__getattr__` | `.animate` 동작은 그대로다. 메서드 호출을 `_recorded_calls`에 추가로 기록하고, raenimgl `SkewedAnimations`만 이 기록을 다시 재생한다 | raenimgl/animation.py:6-30 |
| `InteractiveSceneEmbed.launch` | embed 셸을 띄우기 전에 `scene._reached_embed = True`로 표시한다. 그 뒤로 빨리감기가 꺼진다 | raenimgl/scene.py:204-215 |
| `InteractiveSceneEmbed.get_shortcuts` | embed 셸에 `request_normal_speed_reload` 함수를 추가한다 | raenimgl/scene.py:233-242 |
| `StringMobject.mobjects_from_svg_string` | `StringMobject`에 `get_file_path_by_content`가 없으면 교체된다. 포크에는 그 메서드가 없으므로 **항상 교체된다** [실행확인]. 동작은 포크와 같지만, 라벨 정렬에 실패할 때 내던 `Cannot align submobjects` 경고가 사라진다. 그래서 `tex["..."]`/`t2c` 부분 선택이 경고 없이 틀릴 수 있다 | raenimgl/script.py:13-37 |
| `Code.validate_markup_string` | 없으면 아무 일도 하지 않는 메서드로 추가된다. 포크에는 없어서 항상 추가된다 | raenimgl/script.py:6-8 |
| `Mobject.align` | 포크에 없는 `align(target, direction, buff)` 메서드가 모든 Mobject에 추가된다 | raenimgl/functions.py:11-31 |

- Tex 호환성: MiKTeX + cm-super 환경에서 `from raenimgl import *` 상태로 `Tex(R"\frac{a}{b} = c")`가 정상 렌더된다 (examples/raenimgl_optional.py) [실행확인].
- 단, cm-super가 없는 MiKTeX와 TeX Live는 확인하지 않았다.

## 제공 API

imcommit에서 자주 나오는 순서다.

| 이름 | 내용 | imcommit | 위치 |
|---|---|---|---|
| `self.playw(*anims, wait=1, **kw)` | play 다음에 wait | 1197회 | raenimgl/scene.py:40 |
| `self.cf` | `self.frame` | 178회 | raenimgl/scene.py:146 |
| `self.playwl(*anims, lag_ratio=0.05, wait=1)` | LaggedStart로 play 다음에 wait | 144회 | raenimgl/scene.py:68 |
| `Transformr` | `ReplacementTransform`과 같다 (`replace_mobject_with_target_in_scene=True`) | 138회 | raenimgl/animation.py:284 |
| `Words` | `Text` 하위 클래스. `.words`로 공백 기준 단어 단위 부분을 준다 | 122회 | raenimgl/text.py:74-80 |
| `MONO_FONT` | OS별 고정폭 폰트 이름 | 117회 | raenimgl/utils.py:26-37 |
| `Tensor` | 색칠한 칸을 늘어놓은 벡터 VGroup | 79회 | raenimgl/nn.py:67 |
| `Circumscribe` | `FlashAround`의 별칭 | 60회 | raenimgl/animation.py:314 |
| `mob.align(target, ...)` | 대상 안쪽 가장자리에 붙인다 (import 부작용 표 참고) | 59회 | raenimgl/functions.py:11-31 |
| `Create` | `ShowCreation`의 별칭 | 46회 | raenimgl/animation.py:310 |
| `self.addw(*mobs, wait=1)` | add 다음에 wait | 44회 | raenimgl/scene.py:50 |
| `Scene2D(Scene, …)`, `Scene3D(ThreeDScene, …)` | imcommit은 `class S(InteractiveScene, Scene2D)`로 쓴다 (125개 클래스 전부) | | raenimgl/scene.py:120,150 |
| `self.overlay` | 오버레이 객체 | | raenimgl/scene.py:101 |
| `PythonCode` | 코드 표시 | 2회 | raenimgl/script.py:175 |

- `Create`와 `Circumscribe`는 raenimgl이 있어야만 존재한다. 포크만 쓰는 코드에서는 `ShowCreation`과 `FlashAround`를 쓴다.
- 포크만 쓰는 코드의 다른 대체: `Transformr` → `ReplacementTransform`, `Words` → `Text` + 글리프 슬라이스, `playw` → `self.play(...)` + `self.wait()`.
- `PythonCode`는 파일을 encoding 지정 없이 연다 (raenimgl/script.py:192). Windows 비UTF-8 로캘에서 한글 주석이 있으면 깨질 수 있다. 확인하지 않았다.

## 빨리감기

- `Scene2D.play`와 `playw`는 `_fast_forward()`가 참일 때 `run_time=0.1`로 줄이고, `playw`/`addw`는 wait도 건너뛴다 (raenimgl/scene.py:24-55,128-131).
- 이 값은 세 조건이 모두 맞을 때만 참이다.
  1. `interactive()`(창 미리보기)이다.
  2. 아직 embed 셸에 도달하지 않았다.
  3. `request_normal_speed_reload()`로 정상 속도를 요청하지 않았다.
- 즉 미리보기 창에서 embed 지점까지 빨리 가기 위한 기능이다.
- 주의: `self.embed()`가 없는 씬을 `-w` 없이 미리보기하면 끝까지 모든 play가 0.1초로 줄고 playw/addw의 wait가 빠진다 (직접 쓴 `self.wait()`는 그대로다). 소스 근거.
- `-w` 렌더에서는 적용되지 않는다. examples/raenimgl_optional.py의 mp4 길이가 3.5초로 정상 길이였다 [실행확인].
