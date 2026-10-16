# 포크와 upstream 차이

| 항목 | 값 |
|---|---|
| 포크 HEAD | `455a4201669cd68ff5e522c7fcd1a7ac31aadff0` (2026-10-11) |
| merge-base | `2e31f79a` (2026-03-14) |
| 비교한 upstream/master | `fafa083a` (2026-09-09) |
| 포크 전용 커밋 | 9개. 파일 9개, +107/−11 |
| upstream 전용 커밋 | 112개. 포크가 그만큼 뒤처져 있다 |

명령: `git log upstream/master..HEAD`, `git rev-list --count HEAD..upstream/master`, `git diff --stat <merge-base> HEAD`

## 포크 전용 변경 (전체)

경로는 포크 저장소 루트 기준이다.

| 커밋 | 변경 | 위치 |
|---|---|---|
| 355b1ea5 | 기본값 변경. 배경 `#333333→#000000`, `default_stroke_width 4.0→2.0`, `text.font Consolas→"Noto Sans KR"` | manimlib/default_config.yml:56,78,91 |
| 2dae42f1 | dvisvgm에 `--fontmap=ps2pk.map` 추가 (MiKTeX용) | manimlib/utils/tex_file_writing.py:138 |
| f4c60267 | reload 경로 비교에 `os.path.normcase` 적용 (Windows) | manimlib/module_loader.py:125,132 |
| 3c7d4789 | SVG를 utf-8로 읽음 | manimlib/mobject/svg/svg_mobject.py:159 |
| 268f44c0 | 미리보기 창 폭을 모니터의 1/3로 (원래 1/2) | manimlib/window.py:108 |
| bde8ddca | `e` 키 = yaw (`key_bindings.yaw`) | manimlib/scene/scene.py:767-771, manimlib/default_config.yml:121 |
| 993b64b2 | `c` 키 = `pan_3d_mirror`. `CameraFrame.increment_mirrored_euler_angles(dtheta=0, dphi=0, units=RADIANS)` 추가 | manimlib/camera/camera_frame.py:176, manimlib/default_config.yml:120 |
| df31da90 | `CameraFrame.interpolate`가 쿼터니언의 짧은 경로를 택함 | manimlib/camera/camera_frame.py:122-130 |
| 455a4201 | CLI `--always_on_top`, yml `window.always_on_top`, `Window(always_on_top=)` (Windows 전용) | manimlib/config.py:103-107, manimlib/window.py:40,82 |

부작용이 하나 있다.
- `c` 키가 `pan_3d_mirror`(yml:120)와 `color`(yml:132) 두 곳에 묶여 있다.
- 이 충돌은 InteractiveScene 미리보기 창에서만 의미가 있다.

## upstream/master에만 있는 것 (포크에서 쓰면 안 됨)

경로는 upstream@fafa083 기준이며, 포크에는 해당 정의가 없다. `Updater`는 포크 `manimlib/mobject/mobject.py:61`에 TYPE_CHECKING용 타입 별칭으로만 있고 클래스는 없다. 그래서 `grep Updater`는 포크에서도 결과가 나온다.

| API | upstream 위치 |
|---|---|
| `VideoMobject`, `Sprite`, `VideoSource` | manimlib/mobject/types/video_mobject.py:258,398,31 |
| `PlaneFractal`, `MandelbrotFractal`, `JuliaFractal`, `NewtonFractal`, `MetaNewtonFractal` | manimlib/mobject/fractals.py:64,116,164,185,284 |
| `vmobject_to_svg` | manimlib/utils/svg_export.py:8 |
| `COMMON_UNIFORMS`, `uniform_block_dtype` (포크에는 `manimlib/renderer/` 자체가 없음) | manimlib/renderer/uniform_block.py:21,37 |
| `Keys`, `Mods` (모듈 `manimlib.event_keys`) | manimlib/event_keys.py:17,38 |
| `Surface.set_sort_to_camera`, `Surface(sort_to_camera=)`, `Surface.get_resolution` | manimlib/mobject/types/surface.py:267,73,98 |
| `VMobject.set_joint_roundness`, `VMobject(joint_roundness=, stroke_width_in_scene_units=)` | manimlib/mobject/types/vectorized_mobject.py:591,107,112 |
| `set_fill(..., gradient_direction=)` | manimlib/mobject/types/vectorized_mobject.py:271 |
| `Mobject(textures=, texture_filter=)` | manimlib/mobject/mobject.py:103,104 |
| `Mobject.update(..., frame_rate=)` | manimlib/mobject/mobject.py:799 |
| `AnimationGroup(time_span=)`, `LaggedStartMap(time_span=)`의 그룹 단위 적용 | manimlib/animation/composition.py:35-47,113,174-186 |
| `set_color_by_code`에 WGSL 코드, `VMobject.set_color_by_code(code_target=)` | manimlib/mobject/mobject.py:1956, manimlib/mobject/types/vectorized_mobject.py:468 |
| `Updater` 클래스 | manimlib/mobject/mobject.py:2247 |
| 설정 `scene.invert_zoom_scroll` | manimlib/default_config.yml:87 |
| `Camera(bundle_draws=, draw_together=)`, 설정 `camera.bundle_draws`, `camera.draw_together` | manimlib/camera/camera.py:119-120, manimlib/default_config.yml:56,59 |
| `SceneFileWriter(crf=)`, 설정 `file_writer.crf` | manimlib/scene/scene_file_writer.py:52 |

- 포크에서 쓰면 이렇게 된다 [실행확인: 포크 환경에서 생성·호출만, 렌더 없음].
  - 위 클래스·함수 이름은 `from manimlib import *`에 없다. 그래서 NameError다. `manimlib.event_keys`, `manimlib.renderer`를 직접 import하면 ModuleNotFoundError다.
  - `set_sort_to_camera`, `get_resolution`, `set_joint_roundness`는 AttributeError다.
  - `sort_to_camera=`, `joint_roundness=`, `stroke_width_in_scene_units=`, `textures=`, `texture_filter=`는 `TypeError: Mobject.__init__() got an unexpected keyword argument ...`다. `set_fill(gradient_direction=)`, `update(frame_rate=)`, `set_color_by_code(code_target=)`도 TypeError다.
- `time_span=` 키워드 자체는 포크의 모든 Animation이 받는다 (F:manimlib/animation/animation.py:29). 차이는 그룹 단위 적용이다 [실행확인: 포크 scene.py:494,562의 진행을 그대로 따라 불투명도 측정].
  - 포크 `AnimationGroup(FadeIn(sq), time_span=(1, 2))`는 오류가 없다. 재생 길이만 2초가 된다. `AnimationGroup.interpolate`가 time_span을 보지 않아서 (F:manimlib/animation/composition.py:114) 내용은 0초부터 원래 길이 1초로 끝난다. t=0.5에서 불투명도 0.5다.
  - upstream은 내용을 [1, 2]초에 맞춘다 (U:composition.py:43-47,113) [소스만].
  - 포크 `LaggedStartMap`은 `time_span`을 그룹이 아니라 각 멤버 생성에 넘긴다 (F:composition.py:175-178). 그룹의 `time_span`은 None이다. `anim_func`가 이 키워드를 받지 않으면 (예: `lambda m: FadeIn(m)`) TypeError다. upstream은 그룹에 준다 (U:composition.py:174-186) [소스만].
  - 포크에서는 각 애니메이션에 직접 준다. `FadeIn(sq, time_span=(1, 2))`는 t=1에서 0, t=1.5에서 0.5다 [실행확인].
- `set_color_by_code`는 이름만 같다. 포크는 GLSL 코드를 받고 (F:manimlib/mobject/mobject.py:1989 `glsl_code`), upstream은 WGSL을 받는다. 포크는 호출 시점에 코드를 검사하지 않는다 [실행확인]. WGSL 코드가 렌더에서 어떻게 실패하는지는 렌더하지 않아 확인하지 않았다.

- 포크는 모르는 설정 키를 받으면 그 섹션의 생성자에서 TypeError를 낸다 [실행확인]. 그래서 upstream용 `custom_config.yml`을 그대로 가져오면 렌더가 시작되지 않는다.
  ```
  TypeError: Scene.__init__() got an unexpected keyword argument 'invert_zoom_scroll'
  TypeError: Camera.__init__() got an unexpected keyword argument 'bundle_draws'
  ```
  - `camera.draw_together`, `file_writer.crf`도 같은 식으로 실패한다. 상세 내용은 [cli-and-output.md](cli-and-output.md) §5에 있다.
- 3b1b/videos의 `custom_config.yml`이 `invert_zoom_scroll`을 쓴다.

## 포크와 PyPI `manimgl` 1.7.2 비교

아래는 PyPI 1.7.2와 포크를 각각 깨끗한 venv에 설치해 비교한 결과다 [실행확인, Windows].

- PyPI 1.7.2의 `manimlib/`은 포크 저장소의 태그 v1.7.2(f427fc67)와 파일 단위로 같다 (`diff -rq`).
- 버전 문자열이 둘 다 `1.7.2`라 구분할 수 없다. `importlib.metadata.version`과 `manimlib.__version__` 모두 같다.
- 판별 방법은 둘이다.
  - fork 마커 `manim_config.key_bindings.yaw == "e"` 확인. 1.7.2에는 `yaw` 키가 없다.
  - `site-packages/manimgl-*.dist-info/direct_url.json`의 `url`과 `vcs_info.commit_id` 확인. PyPI 설치에는 이 파일이 없다.
- `scripts/setup.sh`가 두 가지를 모두 검사한다. 1.7.2 환경에서는 둘 다 `[fail]`로 나온다.
- 포크는 태그 v1.7.2(f427fc67)에 upstream 커밋 51개와 포크 커밋 9개를 더한 상태다 (`git rev-list --count v1.7.2..2e31f79a`).
  - 51개에는 버전 번호를 1.7.2로 올린 0c69ab6a(setup.cfg만 변경)와 머지 커밋 c48c4b6a가 들어 있다. 나머지 49개 중 `manimlib/`을 바꾸는 커밋은 39개다 (`git rev-list --no-merges --count v1.7.2..2e31f79a -- manimlib`). 나머지 10개는 README, example_scenes.py, 의존성 파일(requirements.txt/setup.cfg), CI 워크플로(.github/workflows/publish.yml)만 바꾸거나 빈 커밋(14f5f8ea)이다.
- 1.7.2 이후 포크에 들어온 API (두 환경에서 `hasattr`로 확인):
  - `Scene.remove_all_except`, `Scene.set_background_color`
  - `set_clip_planes`, `clip_to_box`, `put_start_on`/`put_end_on`
  - `LineBrace`, `Slider`, `ThreeDModel`, `TexturedGeometry`
- `set_z_index`는 1.7.2에도 있었다.
  - 1.7.2는 그 객체에만 적용한다.
  - 포크는 `recurse=True` 인자가 추가되어 기본으로 하위 객체 전체에 적용한다 (F:manimlib/mobject/mobject.py:1238). `VGroup(Square(), Circle()).set_z_index(3)`의 자식 값은 1.7.2에서 [0, 0], 포크에서 [3, 3]이다.
- 글자 크기 기준:
  - 포크의 `Tex`는 `font_size=144`일 때 "0"의 높이가 약 1 unit이다 (F:manimlib/default_config.yml:88 `tex.font_size_for_unit_height`, 실측 0.997).
  - `Text`도 같은 설정이 있지만 (yml:94) 실측 높이는 폰트에 따라 다르다. 포크 기본 Noto Sans KR에서는 약 1.37 unit이고, Consolas는 약 1.18이다. 비율은 font_size와 무관하게 일정하다.
  - 그래서 같은 font_size에서 `Text`가 `Tex`보다 약 1.37배 크다. Text 크기를 정확히 맞추려면 `height=`나 `set_height`를 쓴다.
  - 1.7.2에는 이 설정이 없고 고정 상수를 쓴다 (`TEXT_MOB_SCALE_FACTOR=0.0076`, `SCALE_FACTOR_PER_FONT_POINT=0.001`). 그래서 두 버전의 글자 크기가 다르다.
- `Surface`의 생성 축 인자는 포크에서 `preferred_creation_axis`, 1.7.2에서 `prefered_creation_axis`(오타)다 (F:manimlib/mobject/types/surface.py:55). 한쪽용 코드는 다른 쪽에서 동작하지 않는다.
- CLI:
  - `--help`의 차이는 `--always_on_top` 하나뿐이다.
  - `--fps 30`은 포크에서 int 30, 1.7.2에서 문자열 `'30'`으로 파싱된다. help 문구는 같아서 help로는 드러나지 않는다.
- 1.7.2 자체의 문제 (포크에서는 해결됨):
  - `manimlib/__init__.py:1`이 `import pkg_resources`를 하는데 setuptools가 의존성에 없다. 그래서 깨끗한 venv에서 `import manimlib`가 실패한다. `setuptools<81`을 설치하면 된다.
  - `Tex`가 MiKTeX에서 항상 `LaTeX compilation failed`로 실패한다. 1.7.2는 `latex`에 `-no-pdf`를 무조건 넘기는데 MiKTeX의 latex는 이 옵션을 모른다. 포크는 xelatex일 때만 넘긴다.

## 패키징 공백

- `manimlib/mobject/types/surface.py:5-6`이 `trimesh`와 `pywavefront`를 최상위에서 import한다.
- `manimlib/__init__.py:62`가 이 모듈을 star-import한다.
- 그런데 `setup.cfg` install_requires에는 둘 다 없고, 두 패키지를 끌어오는 다른 의존성도 없다 (`uv tree --invert --package trimesh` 결과 프로젝트 직접 의존뿐).
- 그래서 포크만 설치하면 `import manimlib`가 `ModuleNotFoundError: No module named 'trimesh'`로 실패한다 [실행확인: 새 venv에 포크만 설치].
- 1.7.2도 이 두 패키지를 의존성에 두지 않지만, 1.7.2 소스는 둘을 import하지 않으므로 문제가 없다. 이 공백은 1.7.2 이후의 일이다.
- 해결: 두 패키지를 함께 설치한다. imcommit pyproject와 setup.sh가 이렇게 한다.
- `python_requires`가 없다. imcommit은 3.10.18, setup.sh는 3.10을 쓴다. 이 플러그인은 3.10에서만 확인했다.
