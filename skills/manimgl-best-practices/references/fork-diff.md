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

경로는 포크 기준이다.

| 커밋 | 변경 | 위치 |
|---|---|---|
| 355b1ea5 | 기본값 변경. 배경 `#333333→#000000`, `default_stroke_width 4.0→2.0`, `text.font Consolas→"Noto Sans KR"` | manimlib/default_config.yml:56,78,91 |
| 2dae42f1 | dvisvgm에 `--fontmap=ps2pk.map` 추가 (MiKTeX용) | manimlib/utils/tex_file_writing.py:138 |
| f4c60267 | reload 경로 비교에 `os.path.normcase` 적용 (Windows) | manimlib/module_loader.py:125 |
| 3c7d4789 | SVG를 utf-8로 읽음 | manimlib/mobject/svg/svg_mobject.py:159 |
| 268f44c0 | 미리보기 창 폭을 모니터의 1/3로 (원래 1/2) | manimlib/window.py:108 |
| bde8ddca | `e` 키 = yaw (`key_bindings.yaw`) | manimlib/scene/scene.py:767, default_config.yml:121 |
| 993b64b2 | `c` 키 = `pan_3d_mirror`. `CameraFrame.increment_mirrored_euler_angles(dtheta=0, dphi=0, units=RADIANS)` 추가 | manimlib/camera/camera_frame.py:176, default_config.yml:120 |
| df31da90 | `CameraFrame.interpolate`가 쿼터니언의 짧은 경로를 택함 | manimlib/camera/camera_frame.py:122 |
| 455a4201 | CLI `--always_on_top`, yml `window.always_on_top`, `Window(always_on_top=)` (Windows 전용) | manimlib/config.py:104, manimlib/window.py:40,82 |

부작용이 하나 있다.
- `c` 키가 `pan_3d_mirror`(yml:120)와 `color`(yml:132) 두 곳에 묶여 있다.
- 이 충돌은 InteractiveScene 미리보기 창에서만 의미가 있다.

## upstream/master에만 있는 것 (포크에서 쓰면 안 됨)

경로는 upstream@fafa083 기준이며, 포크에서는 grep 결과가 0건이다.

| API | upstream 위치 |
|---|---|
| `VideoMobject`, `Sprite` | manimlib/mobject/types/video_mobject.py:258,398 |
| `PlaneFractal`, `MandelbrotFractal`, `JuliaFractal`, `NewtonFractal` | manimlib/mobject/fractals.py |
| `vmobject_to_svg` | manimlib/utils/svg_export.py:8 |
| `Surface.set_sort_to_camera` | manimlib/mobject/types/surface.py:267 |
| `VMobject.set_joint_roundness` | manimlib/mobject/types/vectorized_mobject.py:591 |
| `set_fill(..., gradient_direction=)` | manimlib/mobject/types/vectorized_mobject.py:271 |
| `Updater` 클래스 | manimlib/mobject/mobject.py:2247 |
| 설정 `scene.invert_zoom_scroll` | manimlib/default_config.yml:87 |
| `Camera(bundle_draws=)` | manimlib/camera/camera.py:119 |

- 포크의 `Scene`은 생성자에 모르는 설정 키가 들어오면 TypeError를 낸다 [실행확인]. 그래서 upstream용 `custom_config.yml`을 그대로 가져오면 렌더가 시작되지 않는다.
  ```
  TypeError: Scene.__init__() got an unexpected keyword argument 'invert_zoom_scroll'
  ```
- 3b1b/videos의 `custom_config.yml`이 이 키를 쓴다.

## 포크와 PyPI `manimgl` 1.7.2 비교

- 버전 문자열이 둘 다 `1.7.2`라 구분할 수 없다.
- 판별 방법은 둘이다.
  - fork 마커 `manim_config.key_bindings.yaw == "e"` 확인
  - `site-packages/manimgl-*.dist-info/direct_url.json`의 `url`과 `vcs_info.commit_id` 확인
- `scripts/setup.sh`가 두 가지를 모두 검사한다.
- 포크는 1.7.2에 upstream 커밋 51개와 포크 커밋 9개를 더한 상태다.
- 1.7.2 이후 포크에 들어온 API:
  - `Scene.remove_all_except`, `Scene.set_background_color`
  - `set_clip_planes`, `clip_to_box`, `put_start_on`/`put_end_on`, `set_z_index`
  - `LineBrace`, `Slider`, `ThreeDModel`, `TexturedGeometry`
- `Text`/`Tex` 크기 기준이 `font_size=144`일 때 "0"의 높이가 1 unit이다 (default_config.yml `font_size_for_unit_height`).

## 패키징 공백

- `manimlib/mobject/types/surface.py:5-6`이 `trimesh`와 `pywavefront`를 최상위에서 import한다.
- `manimlib/__init__.py:62`가 이 모듈을 star-import한다.
- 그런데 `setup.cfg` install_requires에는 둘 다 없고, 두 패키지를 끌어오는 다른 의존성도 없다 (`uv tree --invert --package trimesh` 결과 프로젝트 직접 의존뿐).
- 그래서 `pip install git+…`만 하면 `import manimlib`가 ModuleNotFoundError로 실패한다. 소스로 추론한 것이며 별도 환경에서 재현하지는 않았다.
- 해결: 두 패키지를 함께 설치한다. imcommit pyproject와 setup.sh가 이렇게 한다.
- `python_requires`가 없지만 `float | int` 같은 문법을 쓰므로 실제로는 3.10 이상이 필요하다. imcommit은 3.10.18, setup.sh는 3.10을 쓴다.
