# manimgl-skill

[CodingVillainKor/manimgl](https://github.com/CodingVillainKor/manimgl) 포크 **하나만** 대상으로 하는 Claude Code 플러그인이다. 이 포크는 3b1b/manim을 바탕으로 기본값을 한국어 환경에 맞췄다.

- 대상 커밋: 포크 `455a4201669cd68ff5e522c7fcd1a7ac31aadff0` (2026-10-11)
- PyPI `manimgl`이나 ManimCE(`manim`)용이 아니다.
- 모든 규칙은 포크 소스, manimgl-imcommit의 실제 사용 패턴, 실제 렌더 결과에 근거한다. 근거는 `file:line`으로 적었다.

## 구성

| 경로 | 내용 |
|---|---|
| `skills/manimgl-best-practices/` | 작성 규칙(SKILL.md), 근거 문서(`references/`), 렌더 확인된 예제(`examples/*.py`) |
| `skills/manimgl-workflow/` | Plan → Code & Render → Iterate 워크플로, `templates/scenes.md`, 로컬 뷰어 `tools/` |
| `commands/scene.md` | `/manimgl-skill:scene <주제>`로 워크플로를 시작한다 |
| `agents/scene-reviewer.md` | 렌더된 프레임을 읽기 전용으로 검토하는 에이전트 |
| `scripts/setup.sh` | uv 프로젝트에 포크를 커밋 고정으로 설치하고 검증한다. 이미 다른 커밋의 포크가 있으면 바꾸지 않고 경고만 한다 |
| `scripts/check_examples.sh` | 예제 전부를 `-sw`와 `-w -l`로 렌더해 확인한다 |

## 설치

GitHub에 올린 뒤:

```
/plugin marketplace add <사용자>/manimgl-skill
/plugin install manimgl-skill@manimgl-skill
```

로컬 폴더에서 바로 쓸 때:

```
/plugin marketplace add ./manimgl-skill
/plugin install manimgl-skill@manimgl-skill
```

CLI로는 `claude plugin marketplace add ./manimgl-skill`, `claude plugin install manimgl-skill@manimgl-skill`이다.

- 플러그인 명령은 네임스페이스가 붙어 **`/manimgl-skill:scene`**이 된다.
- 마켓플레이스와 플러그인 이름은 둘 다 `manimgl-skill`이다.
- `.claude-plugin/*.json`의 `owner`/`author`는 자리표시자(`manimgl-skill maintainers`)다. 공개할 때 바꾼다.

## 환경 준비 (`scripts/setup.sh`)

```bash
bash scripts/setup.sh [PROJECT_DIR] [--with-raenimgl] [--smoke]
```

- PROJECT_DIR를 생략하면 현재 폴더(`.`)를 uv 프로젝트로 만든다. 플러그인 폴더 안에서 인자 없이 실행하지 않는다.

### 하는 일

1. **시스템 의존성 확인**
   - 필수: `uv`, `ffmpeg`, `git`(uv가 포크를 git에서 받을 때 쓴다).
   - `--smoke`는 LaTeX가 있으면 `curl`로 `example_scenes.py`를 받는다.
   - 경고만: `ffprobe`, `latex`+`dvisvgm`, cm-super(`sfrm1000.pfb`). Linux에서는 `pkg-config pango`도 본다.
2. **포크 설치**: PROJECT_DIR에 pyproject가 없으면 Python 3.10 uv 프로젝트를 만든다. 그 위에 다음을 추가한다.
   - `manimgl @ git+https://github.com/CodingVillainKor/manimgl@455a4201…`
   - `trimesh`, `pywavefront` (포크 setup.cfg에 빠져 있다)
   - pyproject가 이미 포크를 다른 커밋으로 가리키면 바꾸지 않는다. 경고하고, 설치된 커밋도 다르면 경고를 하나 더 낸다. exit 0이다.
   - `--with-raenimgl`인데 raenimgl이 이미 다른 rev로 있으면 바꾸지 않고 경고한다.
3. **PyPI `manimgl` 충돌**: 해결 명령을 출력하고 **exit 2**로 끝낸다. 아무것도 바꾸지 않는다. 여러 줄 배열과 한 줄 배열(`dependencies = ["manimgl>=1.7.2"]`) 모두 잡는다.
   ```bash
   uv remove manimgl && uv add "manimgl @ git+https://github.com/CodingVillainKor/manimgl@455a4201669cd68ff5e522c7fcd1a7ac31aadff0" trimesh pywavefront
   ```
4. **설치 검증**: `uv sync` 후 다음을 확인한다.
   - `uv run python -c "import manimlib; print(manimlib.__file__)"`가 프로젝트 `.venv`를 가리키는지
   - `direct_url.json`의 URL과 커밋
   - 포크 마커 `key_bindings.yaw == "e"`
   - OpenGL 컨텍스트
   - Pango에서 Noto Sans KR이 보이는지
   - 전역 `manimgl`이 따로 있으면 경고한다
5. **`--smoke`**: 임시 폴더에서 스모크 렌더를 하고 ffprobe로 길이를 확인한다. ffprobe가 없으면 길이 확인만 건너뛴다.
   - LaTeX가 있으면 고정 커밋의 `example_scenes.py`로 `OpeningManimExample`을 렌더한다.
   - 없으면 한글 Text 장면을 렌더한다.

### 참고 사항

- **PyPI manimgl 제거**: 프로젝트에서는 위 명령을 쓴다. 전역 설치는 `pip uninstall manimgl`, `uv tool uninstall manimgl` 등 설치한 방법에 맞춰 지운다. 포크와 PyPI판은 같은 `manimlib` 모듈을 쓰고 버전 문자열(1.7.2)도 같아서 import만으로는 구분되지 않는다.
- **MiKTeX(Windows)**:
  - 새로 설치하면 **cm-super가 없다.** 이때 Tex는 빈 SVG가 되어 `SVG has no content to measure`로 실패한다.
  - `miktex packages install cm-super`로 설치한 뒤 `manimgl ... --clear-cache`로 다시 렌더한다.
  - 렌더 중 패키지 설치 창이 막지 않게 하려면 `initexmf --set-config-value "[MPM]AutoInstall=1"`.
  - 사용자 단위로 설치하면 PATH에 안 잡힐 수 있다. 그때는 `%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64`를 PATH에 넣는다.
- **Tex 안의 한글**: xelatex과 kotex(`cjk-ko`)가 필요하다. MiKTeX에서는 자동 설치로 받아졌다. `t2c`를 쓰려면 프리앰블에 `\usepackage{xcolor}`도 넣는다 (`examples/korean.py`).

## 출처와 라이선스

| 출처 | 커밋 | 쓴 방식 |
|---|---|---|
| [CodingVillainKor/manimgl](https://github.com/CodingVillainKor/manimgl) | `455a4201669cd68ff5e522c7fcd1a7ac31aadff0` | 대상. 소스를 읽어 규칙과 근거를 만들었다. 코드는 setup.sh가 git에서 설치한다 |
| [3b1b/manim](https://github.com/3b1b/manim) upstream | `fafa083a` | 포크와 차이를 비교했다 |
| [CodingVillainKor/manimgl-imcommit](https://github.com/CodingVillainKor/manimgl-imcommit) | `a2fe49f4284082ce6c3627cd26e5952cd1d01bb6` | LICENSE 파일이 없어 **코드는 옮기지 않았다.** 패턴과 사용 빈도만 요약했다 (`references/imcommit-patterns.md`) |
| [CodingVillainKor/raenimgl](https://github.com/CodingVillainKor/raenimgl) | `177affc69311d13fcad3404b2599a7714de1d4f2` | LICENSE 파일이 없어 API와 동작만 설명했다. 선택 의존성으로 원 저장소에서 설치한다 |
| [3b1b/videos](https://github.com/3b1b/videos) | `306a1346a356c7a7b097875ceb51c5cd67d0a56c` | `custom_config.yml`과 사용 예를 포크와 비교만 했다. 코드는 옮기지 않았다 |
| [Yusuke710/manim-skill](https://github.com/Yusuke710/manim-skill) | `a0048d9e265499038f34a9aa58ff16d306b5034c` | **MIT**, Copyright (c) 2025 Yusuke Miyashita. 참고한 것은 다음과 같다 |

Yusuke710/manim-skill에서 참고한 것:
- 플러그인 구조 (`.claude-plugin`에 marketplace와 plugin을 한 저장소로)
- 워크플로 구성과 문구 (단계별 진행, `[M:SS] Scene: note` 피드백 형식, 해당 씬만 재렌더)
- 뷰어 `skills/manimgl-workflow/tools/video_viewer.py`, `ui.html`
  - 원본을 가져와 고쳤다. 바꾼 점은 `tools/README.md`에 있다.
  - 라이선스 원문은 `tools/LICENSE-manim-skill`에 있다.

이 플러그인 자체의 라이선스 파일은 아직 없다. 저작권자를 정한 뒤 추가한다.

## 요청과 사실이 달라 조정한 점

| 요청/통념 | 확인한 사실 | 반영 |
|---|---|---|
| `-s`로 마지막 프레임 확인 | 포크의 `-s`만으로는 저장이 안 되고 창이 뜬다 (`config.py:278-280`, 창은 `config.py:331`) | 워크플로는 `-sw` → `videos/<Scene>.png` |
| `self.camera.frame`은 CE API라 금지 | 포크에서도 유효하다. `self.frame`과 같은 객체다 (`scene.py:112`) | "스타일상 `self.frame` 사용"으로 표기 |
| `Create` 금지 | 포크에는 없지만 raenimgl이 별칭을 제공한다 | 포크 단독이면 `ShowCreation`. raenimgl 문서에 별칭을 명시 |
| imcommit 패턴: Scene3D, PythonCode, MINT | imcommit 실제 사용은 0, 1, 0개 파일이다 | 실제로 쓰는 `(InteractiveScene, Scene2D)`와 2D 씬 카메라 기울이기를 기준으로 삼았다 |
| `/scene` | 플러그인 명령은 `/manimgl-skill:scene`이다 | README와 명령 파일에 반영 |
| `/plugin install manimgl-skill/manimgl-skill` | 문서 형식은 `<plugin>@<marketplace>`다 | `/plugin install manimgl-skill@manimgl-skill` |

## 검증한 것

검증 환경:

| 항목 | 값 |
|---|---|
| OS / 셸 | Windows 11 Pro, Git Bash |
| uv / Python | uv 0.13.0, Python 3.10.18 |
| ffmpeg | 2025-12-24 gyan build |
| LaTeX | MiKTeX 25.12 (XeTeX 4.16, dvisvgm 3.4.3) |
| GPU | NVIDIA RTX 4070 Ti (OpenGL 3.3) |
| Claude Code | 2.1.301 |
| 로캘 | 시스템 UTF-8 (ACP 65001) |

- **`setup.sh --smoke` (새 폴더, 새 venv)**
  - 확인한 항목: 경고 0개, `manimlib.__file__`이 `.venv` 안, `direct_url.json` 커밋 `455a4201`, 포크 마커, OpenGL 3.3, Noto Sans KR, cm-super
  - `OpeningManimExample.mp4`: 22.0초
  - 마지막 안내 줄의 경로가 `C:/...` 형식으로, 따옴표 안에 나온다.
  - 단, uv 캐시와 MiKTeX는 같은 머신의 것을 썼다. MiKTeX는 이 셸의 PATH 앞에 직접 넣어 실행했다 (사용자 PATH에는 설치 때 들어가 있다).
- **setup.sh 분기**
  - PyPI 충돌 (여러 줄 배열): `uv add manimgl`(PyPI) 프로젝트에서 경고, 해결 명령 출력, exit 2. 출력된 명령을 실행한 뒤 다시 돌리면 경고 0개로 통과한다.
  - PyPI 충돌 (한 줄 배열 `dependencies = ["manimgl>=1.7.2"]`): exit 2이고 pyproject.toml은 그대로다.
  - 다른 커밋의 포크(`df31da90`)가 이미 있는 프로젝트: 바꾸지 않고 경고 2개(pyproject, 설치 커밋), exit 0.
  - 한글 폴더 이름(`uv init`이 거부): `[fail]` 줄과 `--name` 안내를 내고 exit 1.
  - `bash -n` 통과. 감지 정규식은 `manimgl-extra`, `manimgl_x`, `manimpango`를 잡지 않는다.
- **예제 렌더**
  - 결과: 10개 씬 × (`-sw`, `-w -l`) = 20/20 성공 (`check_examples.sh`, raenimgl 포함 환경). 마지막 실행은 이 커밋의 예제 그대로다.
  - PNG는 전부 눈으로 확인했다. 겹침, 잘림, 두부(□), 색을 봤다. `camera.py`의 원은 초록, `korean.py` KoreanInTex의 "손실"은 노랑(kotex + xcolor + `t2c`)으로 나왔다.
  - `check_examples.sh`에 없는 폴더를 주면 exit 2로 바로 끝난다.
- **색 함정 (프로브)**
  - 생성자 `color=`가 무시됨: `Text`, `Tex`, `TexText`, `Dot`, `Brace`(흰색), `Arrow`, `Vector`, `StrokeArrow`, `Annulus`(회색 #BBBBBB), `Circle`, `Ellipse`(빨간 테두리)
  - 그대로 먹음: `Square`, `Rectangle`, `SurroundingRectangle`, `Line`, `DashedLine`, `Arc`, `Polygon`, `Triangle`, `RegularPolygon`, `CurvedArrow`, `NumberLine`
  - `.set_color()`는 위 전부에서 동작한다.
- **그 밖의 함정 (프로브)**
  - 포크만 설치하면 `import manimlib`가 `No module named 'trimesh'`로 실패한다.
  - `Scene.clear()` 뒤에는 `self.frame`이 빠져 ambient rotation이 멈추고, `self.add(self.frame)`로 되살아난다.
  - `TransformMatchingStrings`/`Tex`의 기본 run_time 2, `Square().set_opacity(0.2)`의 회색 바탕, 비대칭 `ThreeDAxes`의 원점 위치, `Arrow.set_perpendicular_to_camera`
  - 모르는 설정 키: `scene.invert_zoom_scroll`, `camera.bundle_draws`, `camera.draw_together`, `file_writer.crf`가 각 섹션 생성자에서 TypeError로 실패한다.
- **CLI (`references/cli-and-output.md`)**: 플래그별 출력 파일과 해상도/fps(ffprobe), `-s`/`-ql`/`-a` 단독의 멈춤, `-p -w`의 멈춤(`timeout`으로 확인), 씬 선택 프롬프트와 stdin EOF의 exit 1, 실패한 렌더가 이전 mp4를 남기는 것, 설정 병합 순서, 캐시 위치를 실행해 확인했다. 표에 `소스 근거`로 적은 것은 실행하지 않았다.
- **한글, Tex, 3D (`references/korean-tex-3d.md`)**: 한글 글리프 수와 부분 선택, `MarkupText` 색이 무시되는 것, Text와 Tex의 크기 차(1.37배)와 원인(보정 글꼴), kotex 조합의 `Tex`/`TexText`/`Title`/`BulletedList`, xcolor가 필요한 경우, LaTeX가 필요한 클래스 목록(TeX를 PATH에서 빼고 확인), depth test 함정, 빌보드 공식을 렌더나 프로브로 확인했다.
- **PyPI 1.7.2 비교**: PyPI 1.7.2와 포크를 각각 새 venv에 설치해 `hasattr`, `--help`, 크기, `--fps` 파싱을 비교했다. PyPI 1.7.2의 `manimlib/`은 태그 v1.7.2와 파일 단위로 같다.
- **한글 렌더**
  - `Text` 한글과 부분 선택(`t["정밀도"]`), `t2c`
  - Tex 안 한글: 기본 템플릿 실패, `ctex`/`basic_ctex`는 SimHei 글꼴이 없어 실패, `empty_ctex` + kotex 성공
- **raenimgl**
  - `from raenimgl import *` 상태로 Tex를 MiKTeX에서 렌더했다 (포크의 `--fontmap`이 빠진 상태).
  - `-w`에서는 빨리감기가 적용되지 않았다 (mp4 3.5초).
  - `StringMobject` 패치는 포크에서 항상 적용된다.
- **뷰어**
  - `/` 200, `/chapters.json`의 챕터 4개, `/video.mp4` Range 요청 → 206
  - 실제 브라우저(Chrome)에서 9.4초에 `t`를 누르면 메모 칸에 `[0:09] Quantize: `가 들어갔다. 컨트롤 바의 챕터 이름과 진행 바 4칸도 확인했다.
  - 코드 탭 라벨이 `main.py`이고 한글 주석이 깨지지 않는다.
  - `BROWSER=true`면 브라우저를 열지 않는다.
  - 브랜드 문자열 0건
- **워크플로 전체 (에이전트 E2E)**: 새 에이전트 둘이 문서만 보고 주제 2개(이진 탐색, 3D 내적)를 Plan부터 Iterate까지 진행했다.
  - 둘 다 setup.sh 경고 0개, 씬 2개씩(34.3초, 29.5초) 렌더, 뷰어 기동과 종료, 피드백 한 줄을 받아 그 씬만 고치고 다시 렌더했다.
  - 이때 나온 문서 문제(색 목록, 중간 장면 확인, 뷰어 재시작, plan mode 순서 등)는 이 커밋에서 고쳤다.
- **문서 감사**: 에이전트가 문서 주장 약 450개를 소스와 대조했고, 다른 에이전트가 반박을 시도해 살아남은 지적만 반영했다.
  - 고친 뒤 같은 방식으로 약 430개를 다시 확인했다. 확인된 지적 8개(`-sw`에서 dt 업데이터가 두 번 불리는 것, setup.sh의 uv 오류 처리, 뷰어 재시작 문구 등)를 고쳤다.
- **플러그인**
  - `claude plugin validate --strict`: marketplace.json, plugin.json, skills/, agents/, commands/ 모두 통과
  - 설치: `claude plugin marketplace add ./manimgl-skill`과 `claude plugin install manimgl-skill@manimgl-skill`이 성공했고, `claude plugin list`에 0.1.0 enabled로 나온다.
  - 새 세션(`claude -p`)에서 다음이 인식됐다.
    - 명령 `manimgl-skill:scene`
    - 스킬 `manimgl-skill:manimgl-best-practices`, `manimgl-skill:manimgl-workflow`
    - 에이전트 `manimgl-skill:scene-reviewer`

## 검증하지 못한 것

- macOS와 Linux에서 setup.sh 실행. Linux Pango 검사 경로도 실행하지 않았다. 이 OS에서는 setup.sh가 `[info]` 줄로 알린다.
- TeX Live 환경. MiKTeX만 확인했다.
- cm-super가 없는 상태에서 raenimgl의 Tex 패치가 어떻게 동작하는지.
- 비UTF-8 Windows 로캘(cp949)에서의 한글 Text, Tex(`working.tex` 인코딩), 뷰어, raenimgl `PythonCode`.
- 뷰어의 **Copy** 버튼. 사용자 클립보드를 덮어쓰므로 누르지 않았다.
- GitHub에서 `/plugin marketplace add <사용자>/manimgl-skill`. 아직 저장소를 올리지 않았다.
- 사람이 직접 하는 Plan 승인과 피드백. E2E에서는 에이전트가 피드백 줄을 만들어 넣었다.
- plan mode에서 scenes.md를 계획으로 내고, 나온 뒤에 파일로 쓰는 순서. 실제 plan mode 세션으로 해 보지 않았다.
- 최종 1920x1080 `-w` 렌더로 영상 전체를 만드는 것. E2E는 `-w -l`까지만 했다. 예제와 스모크 렌더는 1080p PNG와 480p mp4다.

## 미확인 (소스로만 판단했고 실행하지 않음)

- raenimgl `PythonCode.exec()`의 동작.
- `-o`, `--finder`가 결과 파일을 여는 동작, `-e LINE`, `-f`, `--always_on_top` (창 전용).
- 렌더 중 Ctrl-C의 종료 코드.
- 창 모드(`-w` 없음)에서 `--fps`가 30으로 고정되는 것과 `-s`에서 `dt` 업데이터가 run_time 전체를 한 번에 받는 것.
- 반투명 곡면의 `always_sort_to_camera`.
- `references/` 문서에서 `소스 근거`라고 표시한 나머지 항목.
