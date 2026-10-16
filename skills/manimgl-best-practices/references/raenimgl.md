# raenimgl (선택 의존성)

## 개요

- 출처: `CodingVillainKor/raenimgl` @ `177affc69311d13fcad3404b2599a7714de1d4f2` (2026-09-25)
- imcommit이 실제로 import하는 유틸 라이브러리다.
- `raenim`과는 다른 저장소다. `raenim`은 ManimCE용이다.
- **LICENSE 파일이 없다.** 이 문서는 API와 동작만 설명하고 코드는 옮기지 않는다.
- 경로는 raenimgl 저장소 루트 기준이다.

## 설치

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/setup.sh <프로젝트> --with-raenimgl
```

- pyproject는 `manimgl>=1.7.2`만 선언하고 git 소스는 없다 (pyproject.toml).
  - 그래서 raenimgl을 단독으로 설치하면 PyPI manimgl이 깔린다.
  - **포크를 git 소스로 고정한 같은 uv 프로젝트에 추가해야** 포크가 유지된다.
  - setup.sh는 추가한 뒤 `direct_url.json`이 여전히 포크 @455a4201을 가리키는지 확인한다 [실행확인].
- `setuptools<71`도 같이 고정된다.

## import 부작용 (몽키패치)

`from raenimgl import *` 한 줄로 다음이 바뀐다.

| 대상 | 내용 | 위치 |
|---|---|---|
| `manimlib.utils.tex_file_writing.full_tex_to_svg` | 교체된다. 포크가 추가한 dvisvgm `--fontmap=ps2pk.map`이 빠진다 | raenimgl/__init__.py:15-68 |
| `_AnimationBuilder.__init__` / `__getattr__` | 메서드 호출을 기록했다가 다시 재생하도록 바뀐다 | raenimgl/animation.py:6-30 |
| `InteractiveSceneEmbed.launch` | 패치된다 | raenimgl/scene.py:199-204 |
| `StringMobject.mobjects_from_svg_string` | 해당 메서드가 없을 때만 패치된다 | raenimgl/script.py:13-37 |

- Tex 호환성: MiKTeX + cm-super 환경에서 `from raenimgl import *` 상태로 `Tex(R"\frac{a}{b} = c")`가 정상 렌더된다 (examples/raenimgl_optional.py) [실행확인].
- 단, cm-super가 없는 MiKTeX와 TeX Live는 확인하지 않았다.

## 제공 API (자주 쓰는 것)

| 이름 | 내용 | 위치 |
|---|---|---|
| `Scene2D(Scene, …)`, `Scene3D(ThreeDScene, …)` | imcommit은 `class S(InteractiveScene, Scene2D)`로 쓴다 | raenimgl/scene.py:120,150 |
| `self.playw(*anims, wait=1, **kw)` | play 다음에 wait | raenimgl/scene.py:40 |
| `self.addw(*mobs, wait=1)` | add 다음에 wait | raenimgl/scene.py:50 |
| `self.playwl(*anims, lag_ratio=0.05, wait=1)` | LaggedStart로 play 다음에 wait | raenimgl/scene.py:68 |
| `self.cf` | `self.frame` | raenimgl/scene.py:146 |
| `self.overlay` | 오버레이 객체 | raenimgl/scene.py:101 |
| `Create` | `ShowCreation`의 별칭 | raenimgl/animation.py:310 |
| `Circumscribe` | `FlashAround`의 별칭 | raenimgl/animation.py:314 |
| `PythonCode` | 코드 표시 | raenimgl/script.py:175 |

- `Create`와 `Circumscribe`는 raenimgl이 있어야만 존재한다. 포크만 쓰는 코드에서는 `ShowCreation`과 `FlashAround`를 쓴다.
- `PythonCode`는 파일을 encoding 지정 없이 연다 (raenimgl/script.py:192). Windows 비UTF-8 로캘에서 한글 주석이 있으면 깨질 수 있다. 확인하지 않았다.

## 빨리감기

- `Scene2D.play`와 `playw`는 `_fast_forward()`가 참일 때 `run_time=0.1`로 줄인다 (raenimgl/scene.py:24-38,128-131).
- 이 값은 `interactive()`이고 아직 `self.embed()`에 도달하지 않았을 때만 참이다. 즉 미리보기 창에서 embed 지점까지 빨리 가기 위한 기능이다.
- `-w` 렌더에서는 적용되지 않는다. examples/raenimgl_optional.py의 mp4 길이가 3.5초로 정상 길이였다 [실행확인].
