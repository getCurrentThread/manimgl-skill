# manimgl-skill 세부 사항

[English](details.md) | **한국어**

[README](../README-ko.md)에서 옮긴 내용이다: 플러그인 구성, `setup.sh` 내부 동작, 점검, 출처와 라이선스, 검증 기록. 아래 경로는 플러그인 루트 기준이다.

## 구성

| 경로 | 내용 |
|---|---|
| `skills/manimgl-best-practices/` | 작성 규칙(SKILL.md), 렌더 확인된 예제(`examples/*.py`) |
| `skills/manimgl-best-practices/references/` | 근거 문서: CLI와 출력, 포크와 upstream 차이(다른 manim 버전 코드가 깨지는 경우 포함), imcommit 패턴, 한글/Tex/3D(카메라 궤도 §C8 포함), 애니메이션 의미, 스타일과 색, 대화형 셸, raenimgl, API 목록 |
| `skills/manimgl-best-practices/gallery/` | ML·수학 주제용으로 옮겨 온 씬 파일 9개(씬 17개)와 자체 `README.md`, `LICENSE.txt`. **CC BY-NC-SA 4.0**이다 (출처와 라이선스 참고) |
| `skills/manimgl-workflow/` | Plan → Code & Render → Iterate 워크플로, `templates/scenes.md`(작성 예시 `templates/scenes-example.md`), 기획 참고 문서 `references/`(내러티브 패턴, 포크 검증 시각 기법, 내레이션, 선택 기능인 팀 모드 `team-production.md`) |
| `skills/manimgl-workflow/tools/` | 로컬 뷰어(`video_viewer.py`, `ui.html`). 선택 기능인 내레이션: `tts.py`(narration.txt → 음성 클립 + `timestamps.json`, 엔진 sapi·edge·gemini), `voiceover.py`(`Narrated` 믹스인: 오디오와 씬별 SRT) |
| `commands/scene.md` | `/manimgl-skill:scene <topic>`로 워크플로를 시작한다 |
| `agents/scene-reviewer.md` | 렌더된 프레임을 읽기 전용으로 검토하는 에이전트 |
| `hooks/hooks.json` | Claude가 manimgl `.py` 파일을 쓰거나 고치면 린트를 돌려 결과를 Claude에게 전한다 (경고만) |
| `scripts/setup.sh` | uv 프로젝트에 포크를 커밋 고정으로 설치하고 검증한다. 이미 다른 커밋의 포크가 있으면 커밋은 바꾸지 않고 경고한다 (빠진 `trimesh`/`pywavefront`만 추가) |
| `scripts/check_examples.sh` | `examples/`와 `gallery/`의 모든 Scene을 `-sw`와 `-w -l`로 렌더해 확인한다 (stdin 닫음, 렌더별 타임아웃) |
| `scripts/lint_manimgl.py` | 정적 린트 (표준 라이브러리만, GPU 불필요): CE 전용·upstream 전용 API, CLI 습관, 무시되는 생성자 `color=`, 포크에 없는 색 이름, `Scene.__init__`이 덮어쓰는 시드, `Succession`, `.copy()` 유도 체인 |
| `scripts/check_docs.py` | SKILL.md와 `references/`의 Python 코드를 한 번의 `-sw` 렌더 안에서 포크로 실행하고 문서에 적힌 결과를 확인한다 |
| `scripts/check_citations.py` | 모든 `F:`/`U:`/`R:`/`I:` `file:line` 인용을 고정 커밋의 참조 저장소와 대조한다 |
| `scripts/check_inventory.py` | `references/api-inventory.md`를 설치된 포크가 내보내는 클래스와 비교한다 |

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
   - pyproject가 이미 포크를 가리키면 manimgl 선언은 바꾸지 않는다. `trimesh`, `pywavefront` 중 선언되지 않은 것만 추가한다. 둘 다 있으면 pyproject를 건드리지 않는다.
   - 그 포크가 다른 커밋이면 경고하고, 설치된 커밋도 다르면 경고를 하나 더 낸다. exit 0이다.
   - `--with-raenimgl`인데 raenimgl이 이미 다른 rev로 있으면 바꾸지 않고 경고한다.
3. **PyPI `manimgl` 충돌**: 해결 명령을 출력하고 **exit 2**로 끝낸다. 아무것도 바꾸지 않는다. 큰따옴표와 작은따옴표, 한 줄 배열과 여러 줄 배열, 대소문자(`'ManimGL'`)를 가리지 않고 잡는다 (예: `dependencies = ['manimgl>=1.7.2']`). TOML 파서가 아니라 정규식 검사다.
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
5. **`--smoke`**: 임시 폴더에서 스모크 렌더를 하고 ffprobe로 길이가 0초보다 긴지 확인한다 (아니거나 못 읽으면 실패). ffprobe가 없으면 길이 확인만 건너뛴다.
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

## 점검

플러그인 폴더에서 실행한다. `<uv project>`는 `scripts/setup.sh`로 준비한 폴더다.

| 명령 | 점검 내용 | 필요한 것 |
|---|---|---|
| `python scripts/lint_manimgl.py skills agents commands README.md README-ko.md` | `.py` 파일과 `.md` 안의 python/bash 코드 블록: §2/§3 API, CLI 습관(`-ql`, `-qh`, `-p`, `-w`/`-o`/`--finder` 없는 `manimgl` 실행, 맨 `manimgl`), §6 클래스의 생성자 `color=`, 포크에 없는 색 이름(`GRAY*`, `CYAN`, `MAGENTA`, `BROWN`, `DARK_BLUE` 등), 모듈 수준 시드와 여러 씬 파일의 `random_seed`, `Succession`, 그룹 수준 `time_span=`, `TransformMatching*(x.copy(), y)` 체인. 먼저 자체 테스트를 돈다 | Python 3만 (포크, GPU 불필요) |
| `python scripts/check_citations.py <ref dir> [--fetch]` | `.md`와 `.py`의 모든 `F:`/`U:`/`R:`/`I:` `file:line` 인용: 파일이 있는지, 그 줄이 있는지, 한 줄짜리 인용이 빈 줄이 아닌지. 인용한 줄 근처에 문서 줄의 식별자가 없으면 WEAK로 출력해 검토 목록으로 쓴다 | 고정 커밋의 `fork/ upstream/ raenimgl/ imcommit/`가 든 `<ref dir>`. `--fetch`는 없는 저장소를 거기에 클론한다 (git, 네트워크, 약 22 MB) |
| `uv run --project <uv project> python scripts/check_inventory.py` | `references/api-inventory.md`와 `from manimlib import *`가 내보내는 클래스 비교 | 포크 환경 (GPU 불필요) |
| `python scripts/check_docs.py <uv project> [OUT_DIR] [-v]` | `skills/*/SKILL.md`와 `skills/*/references/*.md`의 인라인 코드와 python 코드 블록을 생성한 씬 하나에서 `-sw`로 실행한다. 결과 칸이 오류나 숫자인 표 행은 그 결과를 확인한다. `-v`는 건너뛴 항목과 이유를 모두 출력한다. raenimgl이 설치돼 있으면 `raenimgl.md`는 두 번째 씬에서 돈다 | OpenGL, LaTeX |
| `bash scripts/check_examples.sh <uv project> [OUT_DIR]` | `examples/`와 `gallery/`의 모든 Scene을 `-sw`와 `-w -l`로 렌더 | OpenGL, LaTeX, ffmpeg |
| `claude plugin validate --strict .` | 매니페스트, 프런트매터, `hooks/hooks.json` 문법 | Claude Code CLI |

- 종료 코드: 0 = 문제 없음.
  - `lint_manimgl.py`, `check_docs.py`, `check_citations.py`, `check_inventory.py`: 1 = 지적 있음, 2 = 사용법이나 준비 오류 (다른 커밋의 참조 저장소, 렌더 크래시).
  - `check_examples.sh`: 실패한 렌더 수(최대 63), 64 = 사용법 오류 또는 씬 목록을 만들 수 없음 (uv 없음, 파싱되지 않는 예제), 65 = 두 파일에 대소문자를 무시하고 같은 Scene 클래스 이름이나 같은 파일 이름이 있음 (출력이 모두 한 OUT_DIR와 그 `videos/`에 쌓이고, NTFS는 대소문자를 구분하지 않는다).
- 린트 예외: 줄 끝에 `# lint: ok`를 붙인다.
- 문서 코드 주석은 그 코드가 있는 줄이나 바로 앞 줄(또는 코드 블록 앞)에 단독으로 쓴다: `<!-- snippet: skip <이유> -->`, 또는 그 코드에만 대체 값을 묶는 `<!-- snippet: name=expr -->`.
- `check_examples.sh`는 렌더마다 stdin을 `/dev/null`로 준다 (씬 이름 프롬프트가 막지 않고 exit 1로 끝난다). `timeout`/`gtimeout`이 있으면 `CHECK_TIMEOUT`초(기본 600) 뒤에 멈춘다.
- 훅은 플러그인이 켜져 있는 동안 모든 프로젝트에서 Write/Edit/MultiEdit 뒤마다 린트를 돈다.
  - manimlib이나 raenimgl을 import하는 `.py`, 또는 가장 가까운 pyproject.toml에 manimgl이 적힌 프로젝트 안에서 `manim`(CE)을 import하는 `.py`가 아니면 바로(약 0.2초) 끝난다 (ManimCE 프로젝트는 건드리지 않는다).
  - 작업을 막지 않는다. 지적은 추가 컨텍스트로 Claude에게 간다.
  - PATH에 `python3`나 `python`이 있어야 하고, 없으면 아무것도 하지 않는다.

## 출처와 라이선스

| 출처 | 커밋 | 쓴 방식 |
|---|---|---|
| [CodingVillainKor/manimgl](https://github.com/CodingVillainKor/manimgl) | `455a4201669cd68ff5e522c7fcd1a7ac31aadff0` | 대상. 소스를 읽어 규칙과 근거를 만들었다. 코드는 setup.sh가 git에서 설치한다 |
| [3b1b/manim](https://github.com/3b1b/manim) upstream | `fafa083a` | 포크와 차이를 비교했다 |
| [CodingVillainKor/manimgl-imcommit](https://github.com/CodingVillainKor/manimgl-imcommit) | `a2fe49f4284082ce6c3627cd26e5952cd1d01bb6` | LICENSE 파일이 없어 **코드는 옮기지 않았다.** 패턴과 사용 빈도만 요약했다 (`references/imcommit-patterns.md`) |
| [CodingVillainKor/raenimgl](https://github.com/CodingVillainKor/raenimgl) | `177affc69311d13fcad3404b2599a7714de1d4f2` | LICENSE 파일이 없어 API와 동작만 설명했다. 선택 의존성으로 원 저장소에서 설치한다 |
| [3b1b/videos](https://github.com/3b1b/videos) | `306a1346a356c7a7b097875ceb51c5cd67d0a56c` | `custom_config.yml`과 사용 예를 포크와 비교만 했다. 코드는 옮기지 않았다 |
| [Yusuke710/manim-skill](https://github.com/Yusuke710/manim-skill) | `a0048d9e265499038f34a9aa58ff16d306b5034c` | **MIT**, Copyright (c) 2025 Yusuke Miyashita. 참고한 것은 다음과 같다 |
| [adithya-s-k/manim_skill](https://github.com/adithya-s-k/manim_skill) | `cef045011722d285692e3381d12d4d637da56e18` | 라이선스가 두 가지이고 따로 다뤘다. 각각에서 쓴 것은 다음과 같다 |

Yusuke710/manim-skill에서 참고한 것:
- 플러그인 구조 (`.claude-plugin`에 marketplace와 plugin을 한 저장소로)
- 워크플로 구성과 문구 (단계별 진행, `[M:SS] Scene: note` 피드백 형식, 해당 씬만 재렌더)
- 뷰어 `skills/manimgl-workflow/tools/video_viewer.py`, `ui.html`
  - 원본을 가져와 고쳤다. 바꾼 점은 `tools/README.md`에 있다.
  - 라이선스 원문은 `tools/LICENSE-manim-skill`에 있다.
- `skills/manimgl-workflow/tools/tts.py`는 그 `tts-generate.py`의 일부(sha256 캐시 키, ffprobe 길이 측정, 캐시 적중 루프, `timestamps.json` 아이디어)를 고쳐 썼다. Kokoro 파이프라인과 단일 voiceover.mp3는 가져오지 않았다. `tools/README.md`에 적었다. `voiceover.py`는 새로 쓴 코드다.

adithya-s-k/manim_skill에서 쓴 것:
- **MIT** 부분 (최상위 LICENSE, Copyright (c) 2026 Adithya S Kolavi):
  - `skills/manim-composer/`를 포크에 맞게 고쳐 `skills/manimgl-workflow/references/narrative-patterns.md`, `visual-techniques.md`, `templates/scenes-example.md`에 옮겼다. 바꾼 점은 각 파일 맨 위에 있다. 라이선스 원문: `skills/manimgl-workflow/references/LICENSE-manim_skill`.
  - `scripts/check_docs.py`는 문서 코드 블록을 생성한 Scene으로 감싸는 아이디어를 `tests/manimgl/test_utils.py`에서 얻었다. 코드는 옮기지 않았다.
- **CC BY-NC-SA 4.0** 부분 (`skills/manimgl-best-practices/`, 예제 코드 원저작자 Grant Sanderson / 3Blue1Brown, 각색 Adithya S Kolavi):
  - 예제 파일 9개를 고쳐 `skills/manimgl-best-practices/gallery/`에 옮겼다. 각 파일의 docstring에 출처와 바꾼 점을 적었다. 라이선스는 `gallery/LICENSE.txt`, 목록은 `gallery/README.md`에 있다.
  - `rules/*.md`와 나머지 예제는 포크에서 시험만 했다. 짧은 주장 구절은 출처를 밝혀 `references/animation-semantics.md` §6과 `references/style-and-color.md`에 인용했다. 예제 씬 183개는 시험용으로 렌더했다 (`references/fork-diff.md`). 3줄짜리 `create_label` 패턴 하나는 다시 썼다.
  - 이 부분에서 가져온 것은 `skills/manimgl-workflow/`에 없다.

이 플러그인의 라이선스:
- 최상위 LICENSE는 아직 없다. 저작권자를 정한 뒤 추가한다. 그때까지 제3자 부분은 위에 적은 각자의 라이선스를 따른다.
- **`skills/manimgl-best-practices/gallery/`는 CC BY-NC-SA 4.0(저작자 표시, 비영리, 동일조건 변경허락)이다.** 플러그인의 나머지가 어떤 라이선스를 받든 이 폴더에는 적용되지 않는다. `gallery/`를 포함한 사본은 상업적으로 쓸 수 없고, 고친 갤러리 파일도 CC BY-NC-SA 4.0을 유지해야 한다.
- `docs/demo.gif`와 `docs/viewer.png`는 `gallery/` 씬의 렌더 화면이므로 gallery/와 같이 CC BY-NC-SA 4.0이다 (원저작자 Grant Sanderson / 3Blue1Brown, 각색 Adithya S Kolavi).

## 요청과 사실이 달라 조정한 점

| 요청/통념 | 확인한 사실 | 반영 |
|---|---|---|
| `-s`로 마지막 프레임 확인 | 포크의 `-s`만으로는 저장이 안 되고 창이 뜬다 (`config.py:278-280`, 창은 `config.py:331`) | 워크플로는 `-sw` → `videos/<Scene>.png` |
| `self.camera.frame`은 CE API라 금지 | 포크에서도 유효하다. `self.frame`과 같은 객체다 (`scene.py:112`) | "스타일상 `self.frame` 사용"으로 표기 |
| `Create` 금지 | 포크에는 없지만 raenimgl이 별칭을 제공한다 | 포크 단독이면 `ShowCreation`. raenimgl 문서에 별칭을 명시 |
| imcommit 패턴: Scene3D, PythonCode, MINT | imcommit 실제 사용은 0, 1, 0개 파일이다 | 실제로 쓰는 `(InteractiveScene, Scene2D)`와 2D 씬 카메라 기울이기를 기준으로 삼았다 |
| `/scene` | 플러그인 명령은 `/manimgl-skill:scene`이다 | README와 명령 파일에 반영 |
| `/plugin install manimgl-skill/manimgl-skill` | 문서 형식은 `<plugin>@<marketplace>`다 | `/plugin install manimgl-skill@manimgl-skill` |
| 모듈 수준 `seed(41)`, `np.random.seed(41)`(imcommit 템플릿)이나 클래스 속성 `random_seed`로 시드 고정 | `Scene.__init__`이 `random_seed`(기본 0)로 두 난수 생성기를 다시 시드하므로 모듈 시드는 효과가 없다 (F:manimlib/scene/scene.py:53,139-141). 여러 씬을 한 명령으로 렌더하면 모든 씬을 먼저 만들기 때문에 (F:manimlib/extract_scene.py:106-109) 클래스 속성은 단독 렌더에서만 유지된다 | `construct` 첫 줄에서 시드: `examples/structure.py`, `gallery/token_sampling.py`, `gallery/matrix_vector_product.py` |
| adithya-s-k/manim_skill 예제를 플러그인에 옮기기 | 그 폴더는 MIT가 아니라 CC BY-NC-SA 4.0이다 | 별도 `gallery/`에 자체 LICENSE.txt와 파일별 출처 표기를 두었다 |

## 검증한 것

검증 환경:

| 항목 | 값 |
|---|---|
| OS / 셸 | Windows 11 Pro, Git Bash |
| uv / Python | uv 0.13.0, Python 3.10.18 |
| ffmpeg | 2025-12-24 gyan build |
| LaTeX | MiKTeX 25.12 (XeTeX 4.16, dvisvgm 3.4.3) |
| GPU | NVIDIA RTX 4070 Ti (OpenGL 3.3) |
| Claude Code | 2.1.301 (0.1.0 점검), 2.1.302 (0.2.0 점검) |
| 로캘 | 시스템 UTF-8 (ACP 65001) |

- **`setup.sh --smoke` (새 폴더, 새 venv)**
  - 확인한 항목: 경고 0개, `manimlib.__file__`이 `.venv` 안, `direct_url.json` 커밋 `455a4201`, 포크 마커, OpenGL 3.3, Noto Sans KR, cm-super
  - `OpeningManimExample.mp4`: 22.0초
  - 마지막 안내 줄의 경로가 `C:/...` 형식으로, 따옴표 안에 나온다.
  - 단, uv 캐시와 MiKTeX는 같은 머신의 것을 썼다. MiKTeX는 이 셸의 PATH 앞에 직접 넣어 실행했다 (사용자 PATH에는 설치 때 들어가 있다).
- **setup.sh 분기**
  - PyPI 충돌 (여러 줄 배열): `uv add manimgl`(PyPI) 프로젝트에서 경고, 해결 명령 출력, exit 2. 출력된 명령을 실행한 뒤 다시 돌리면 경고 0개로 통과한다.
  - PyPI 충돌 (한 줄 배열 `dependencies = ["manimgl>=1.7.2"]`): exit 2이고 pyproject.toml은 그대로다.
  - PyPI 충돌 (작은따옴표 한 줄 `['manimgl>=1.7.2']`, 작은따옴표 여러 줄 `'ManimGL==1.7.2'`): 둘 다 exit 2, 경고 1개, pyproject.toml sha256이 그대로다.
  - 고정 커밋 포크만 선언한 프로젝트(`uv add`로 포크만 추가): `trimesh`, `pywavefront`를 추가하고 경고 0개, exit 0, `import manimlib` 성공. 다시 돌리면 아무것도 추가하지 않고 sha256이 그대로다.
  - 포크와 `trimesh`만 있는 프로젝트: `pywavefront`만 추가하고 경고 0개, exit 0.
  - 다른 커밋의 포크(`df31da90`)와 `trimesh`, `pywavefront`가 이미 있는 프로젝트: 바꾸지 않고 경고 2개(pyproject, 설치 커밋), exit 0.
  - 한글 폴더 이름(`uv init`이 거부): `[fail]` 줄과 `--name` 안내를 내고 exit 1.
  - `bash -n` 통과. 감지 정규식은 큰따옴표와 작은따옴표 모두에서 `manimgl-extra`, `manimgl_x`, `manimpango`를 잡지 않는다. 포크 줄(`"manimgl @ git+…CodingVillainKor/manimgl…"`)은 포크 분기로 먼저 간다.
- **예제 렌더**
  - 결과: 파일 19개(`examples/`, `gallery/`)의 씬 32개 × (`-sw`, `-w -l`) = 64/64 성공 (`check_examples.sh`, raenimgl 포함 환경, 2026-10-17). 마지막 실행은 이 커밋의 파일 그대로다.
  - PNG는 전부 눈으로 확인했다. 겹침, 잘림, 두부(□), 색을 봤다. `camera.py`의 원은 초록, `korean.py` KoreanInTex의 "손실"은 노랑(kotex + xcolor + `t2c`)으로 나왔다. 새 예제와 갤러리 파일은 작성자가 mp4마다 2 fps 프레임 시트도 확인했다.
  - 시드: `construct` 안에서 시드하면 `examples/structure.py`의 `Intro`와 `gallery/token_sampling.py`의 `TokenSamplingAnimation`이 단독 렌더와 다음 씬과 함께 렌더한 경우에 바이트 단위로 같은 PNG를 냈다. 클래스 속성 `random_seed = 41`일 때는 `Intro`의 단독과 함께 렌더 결과가 달랐다.
  - `check_examples.sh`에 pyproject.toml이 없는 폴더를 주면 exit 64로 바로 끝난다. 두 파일에 같은 Scene 클래스 이름이 있으면 렌더 전에 exit 65로 끝난다.
- **색 함정 (프로브)**
  - 생성자 `color=`가 무시됨: `Text`, `Tex`, `TexText`, `Dot`, `Brace`(흰색), `Arrow`, `Vector`, `StrokeArrow`, `Annulus`, `Sector`, `AnnularSector`(회색 #BBBBBB), `Circle`, `Ellipse`(빨간 테두리), `Cross`(빨강)
  - 그대로 먹음: `Square`, `Rectangle`, `SurroundingRectangle`, `Line`, `DashedLine`, `Arc`, `Polygon`, `Triangle`, `RegularPolygon`, `CurvedArrow`, `NumberLine`
  - `.set_color()`는 위 전부에서 동작한다.
- **그 밖의 함정 (프로브)**
  - 포크만 설치하면 `import manimlib`가 `No module named 'trimesh'`로 실패한다.
  - `Scene.clear()` 뒤에는 `self.frame`이 빠져 ambient rotation이 멈추고, `self.add(self.frame)`로 되살아난다.
  - `TransformMatchingStrings`/`Tex`의 기본 run_time 2, `Square().set_opacity(0.2)`의 회색 바탕, 비대칭 `ThreeDAxes`의 원점 위치, `Arrow.set_perpendicular_to_camera`
  - 모르는 설정 키: `scene.invert_zoom_scroll`, `camera.bundle_draws`, `camera.draw_together`, `file_writer.crf`가 각 섹션 생성자에서 TypeError로 실패한다.
- **CLI (`references/cli-and-output.md`)**: 플래그별 출력 파일과 해상도/fps(ffprobe), `-s`/`-ql`/`-a` 단독의 멈춤, `-p -w`의 멈춤(`timeout`으로 확인), 씬 선택 프롬프트와 stdin EOF의 exit 1, 실패한 렌더가 이전 mp4를 남기는 것, 설정 병합 순서, 캐시 위치를 실행해 확인했다. 표에 `source evidence`로 적은 것은 실행하지 않았다.
- **대화형 셸과 CLI 함정 (`references/interactive.md`, `references/cli-and-output.md` §2.1, §5.1, §7)**: 실행해서 확인했다. `self.embed()` 뒤 코드(창 모드와 `-w`의 차이), `close_scene_on_exit=False`, 셸 네임스페이스, `checkpoint_paste`의 되돌리기/건너뛰기/녹화(`pyperclip.paste`를 바꿔 끼워 실제 클립보드는 건드리지 않음), `-e`/`-se`와 실패 경우, `reload(N)`이 유지되는 것, Shift+D/Shift+C 출력과 Ctrl+Shift+Z(창 없이 호출), 다른 문서의 플래그(`-h`와 `-w -qh`는 렌더 없이 exit 0, `--config`는 `--config_file`로 읽혀 무시됨, `--resolution 1920,1080`은 exit 1, 없는 플래그 10개는 exit 2), `custom_config.yml` 키와 튜플 문자열(가이드식 yml은 exit 0으로 1920x1080 30 fps를 렌더), `sizes.frame_height`를 쓴 세로 영상, 한 명령으로 렌더한 씬들이 난수 흐름을 공유하는 것. 셸은 stdin 파이프로 조작했고, 창 모드 실행은 실제 미리보기 창을 띄웠다.
- **한글, Tex, 3D (`references/korean-tex-3d.md`)**: 한글 글리프 수와 부분 선택, `MarkupText` 색이 무시되는 것, Text와 Tex의 크기 차(1.37배)와 원인(보정 글꼴), kotex 조합의 `Tex`/`TexText`/`Title`/`BulletedList`, xcolor가 필요한 경우, LaTeX가 필요한 클래스 목록(TeX를 PATH에서 빼고 확인), depth test 함정, 빌보드 공식, 반투명 곡면이 나중에 추가한 객체를 가리는 것, `set_z_index(-1)`은 추가하기 전에 걸어야만 듣는 것, 음수 φ와 남은 γ를 포함한 (θ, φ) 시점 표, `set_floor_plane("xz")`, 광원, 3D 생성자 오류, 카메라 궤도(프레임마다 θ 기록: `animate` +360°는 움직이지 않음, +270°는 -90°, `Rotate(frame)`은 불규칙, θ와 φ를 한 `.animate`로 바꾸면 도중에 γ = 47.3°까지 기울어짐)를 렌더나 프로브로 확인했다. `examples/camera_orbit.py`는 `-sw`와 `-w -l` 모두 exit 0이고 프레임마다 θ를 기록해 확인했다.
- **애니메이션 의미 (`references/animation-semantics.md`, `examples/compositions.py`)**: `compositions.py`(씬 4개)는 `TransformMatchingTex`, `Transform`, `ReplacementTransform`과 프레임을 남기는 화면 비우기 뒤의 씬 구성원을 assert하므로 exit 0이면 그 규칙들이 확인된다. 프로브로 `.animate.rotate(PI)`가 한 점으로 줄어드는 것(점 퍼짐 1.586/0.0/1.586), play보다 짧은 `Rotate`가 자기 run_time이 끝난 뒤에도 약 4바퀴 더 돌아 mp4는 회전 전 모습으로 끝나는데 `-sw` PNG는 정상으로 보이는 것, `Succession`과 `LaggedStart(lag_ratio=1)`의 시작 상태(b 불투명도 1.0과 0.0), 뒤 구성원이 같은 객체를 움직이면 `LaggedStart(lag_ratio=1)`가 첫 단계를 감추는 것(t=0.5와 t=0.97에서 불투명도 0.0), 기본 run_time(`ApplyWave(m, run_time=1)`도 3초), `LaggedStartMap`/`TransformMatching*`는 `rate_func=`를 구성원에 넘기고 다른 그룹은 무시하는 것, 회전축과 다른 `path_arc_axis`(회전 중간에 반지름 1.414 대신 2.0), play 수준과 생성자의 `lag_ratio=0` 차이, `time_span`과 `squish_rate_func`의 불투명도, `f_always`와 `always`, 타깃 없는 `MoveToTarget`, TypeError/NameError를 내는 CE 인자를 측정했다. 모듈 시드 41과 99는 같은 결과를 냈다.
- **스타일, 색, Tex 선택 (`references/style-and-color.md`)**: 프로브나 렌더로 확인했다. `set_backstroke`와 `set_color` 순서, VMobject당 획 하나, `opacity=`/`background=` TypeError, `add_background_rectangle`이 문자열 선택을 한 칸 밀어내는 것, `BackgroundRectangle` 기본색, `VHighlight`, 없는 색 이름(`GRAY*`, `CYAN`, `MAGENTA`, `BROWN`), hex 문자열, 그라디언트, `set_background_color`와 `default_camera_config`로 배경 바꾸기, 없는 스타일 메서드, GLSL `set_color_by_code`/`set_color_by_xyz_func` 실패(exit 1), 사후 선택과 `isolate=` 선택의 차이(수식 8개), 연산자나 `\cos`에 걸친 키가 간격을 잃는 것(`a + b = c`의 폭 1.886, `isolate=["="]`이면 1.617), 여러 줄 `&`/`\\`와 중첩 `align*`의 LatexError.
- **다른 manim 버전의 코드 (`references/fork-diff.md`)**: adithya-s-k/manim_skill @cef0450 `skills/manimgl-best-practices/{examples,templates}`의 Scene 클래스 183개를 포크에서 `-sw`로 렌더했다. 155개 통과, 28개 실패. 실패 26개는 API·사용법 원인 15가지에서 나왔고, 원인마다 최소 실패 씬(exit 1, 같은 메시지)과 고친 씬(exit 0, PNG 확인)을 만들어 재현했다. 나머지 2개는 예제 자체의 버그다. 조용한 색 변화: 통과한 155개 중 49개가 무시되는 생성자 `color=`를 쓴다(호출 131개). 마지막 프레임 8개를 표본으로 봤더니 그런 객체 31개 중 29개의 색이 틀렸다.
- **기획 참고 문서 (`skills/manimgl-workflow/references/`)**: `visual-techniques.md`의 `[verified by run]` 레시피는 모두 프로브로 렌더했거나(`-sw` 또는 `-w -l`, exit 0, PNG나 프레임 시트 확인) 프로브 스크립트로 값을 출력해 확인했다. 작성 예시 `templates/scenes-example.md`는 씬 3개를 실제로 구현해 `-sw`와 `-w -l`로 렌더했고(exit 0, 내레이션 없이 14초, 16.5초, 14.5초), 씬 사이 컷을 프레임으로 비교했다. imcommit 휴리스틱은 AST로 다시 셌다.
- **내레이션 (`tools/tts.py`, `tools/voiceover.py`, `references/voiceover.md`)**: Windows 11에서 E2E로 확인했다. `tts.py`(SAPI, Microsoft Heami Desktop)가 한국어 문장 3개를 합성했고(2.629/3.794/4.209초), 다시 돌리면 3개 모두 캐시를 썼다. 씬 2개를 `-sw`와 `-w -l`로 렌더했고, mp4마다 영상과 길이가 같은 48 kHz 모노 AAC 트랙이 있으며 씬별 SRT 큐는 프레임에 맞는다. `+faststart`로 이어 붙인 `full.mp4`는 영상 10.667초, 오디오 10.688초이고 moov가 mdat 앞에 온다. 뷰어는 VIDEO_READY를 출력하고 오프셋이 맞는 `/subtitles.srt`를 냈다. 소프트 자막과 번인도 확인했다. 씬 7개를 이었을 때 `-c copy`는 말소리 시작 시점이 21 ms에서 225 ms로 밀렸고, 오디오만 다시 인코딩하는 방식(`references/voiceover.md` §2 6단계)은 21.3 ms를 유지했으며 뷰어도 받아들였다. 경계 경우: 초과·미사용 줄 경고, 오래된 `narration.txt` 경고, `-w -n`에서 예외, 0.5초 씬의 오디오가 0.5초로 잘리는 것, 스트림 구성이 다른 씬이면 뷰어가 거부하는 것(exit 1). `edge-tts`는 고정 예문 한 문장으로만 돌렸다.
- **갤러리 (`skills/manimgl-best-practices/gallery/`)**: 파일 9개를 옮겼다. 모든 씬을 `-sw`와 `-w -l`로 렌더했고(exit 0), PNG와 mp4별 프레임 시트를 눈으로 확인했으며, `lint_manimgl.py` 지적은 0개다. 옮기면서 찾은 함정은 `gallery/README.md`에 있고, 각각 프로브로 출력했거나 렌더에서 봤다.
- **점검** (Claude Code 2.1.302, 이 트리, 2026-10-17):
  - `lint_manimgl.py skills agents commands README.md README-ko.md`: 자체 테스트 통과, 파일 44개에서 지적 0개. adithya-s-k/manim_skill `skills/manimgl-best-practices` @cef0450에서는 파일 106개에서 지적 397개.
  - `check_docs.py`: 문서 14개, 코드 797개: 통과 329, 이유를 달고 건너뜀 366, 실행하지 않은 `kwarg=value` 언급 102, 실패 0.
  - `check_citations.py`: 인용 656개 통과(그중 63개는 문서 줄에 기준이 될 식별자가 없어 파일과 줄만 확인), WEAK 126개(추가할 때 손으로 읽음), 갤러리 docstring의 태그 없는 출처 경로 1개, 오류 0.
  - `check_inventory.py`: Scene 3, Animation 80, Mobject 149, 차이 없음.
  - 훅: `claude -p --plugin-dir . --model haiku`로 `Text("hi", color=RED)`와 `Create(t)`가 든 파일을 쓰게 했더니, 모델이 훅의 추가 컨텍스트에서 두 지적을 그대로 인용했다. `.py`가 아닌 파일, manimlib이 없는 `.py`, 깨진 stdin, Python이 없는 PATH는 모두 출력 없이 exit 0이다. Windows에서 호출당 약 0.2초.
  - `check_examples.sh`: `input()`을 부르는 씬은 멈추지 않고 exit 1로 끝난다. `CHECK_TIMEOUT=8`이면 100초 sleep이 `timeout 8s`로 끝났고, 그 뒤 uv 자식 프로세스도 없었다.
  - `claude plugin validate --strict`는 `hooks/hooks.json`이 있어도 통과한다. 깨진 hooks.json은 실패하고, 모르는 키는 통과한다.
- **PyPI 1.7.2 비교**: PyPI 1.7.2와 포크를 각각 새 venv에 설치해 `hasattr`, `--help`, 크기, `--fps` 파싱을 비교했다. PyPI 1.7.2의 `manimlib/`은 태그 v1.7.2와 파일 단위로 같다.
- **포크에 없는 upstream API (`references/fork-diff.md`)**: 포크 환경에서 생성·호출만 해서 확인했다 (렌더 없음).
  - `VideoSource`, `Keys`/`Mods`, `COMMON_UNIFORMS`, `uniform_block_dtype`는 이름이 없다. `get_resolution`, `set_sort_to_camera`, `set_joint_roundness`는 AttributeError다.
  - `sort_to_camera=`, `joint_roundness=`, `stroke_width_in_scene_units=`, `textures=`, `texture_filter=`, `gradient_direction=`, `update(frame_rate=)`, `code_target=`는 TypeError다.
  - 포크 `AnimationGroup(time_span=(1, 2))`는 오류 없이 span을 무시하고 0초부터 재생한다 (t=0.5에서 불투명도 0.5). 포크 scene의 진행 계산을 그대로 따라 측정했다.
- **한글 렌더**
  - `Text` 한글과 부분 선택(`t["정밀도"]`), `t2c`
  - Tex 안 한글: 기본 템플릿 실패, `ctex`/`basic_ctex`는 SimHei 글꼴이 없어 실패, `empty_ctex` + kotex 성공
- **raenimgl**
  - `from raenimgl import *` 상태로 Tex를 MiKTeX에서 렌더했다 (포크의 `--fontmap`이 빠진 상태).
  - `-w`에서는 빨리감기가 적용되지 않았다 (mp4 3.5초).
  - `StringMobject` 패치는 포크에서 항상 적용된다.
- **뷰어**
  - `/` 200, `/chapters.json`의 챕터 4개, `/video.mp4` Range 요청 → 206
  - Range 경계(curl, 바이트 비교): 끝이 파일을 넘으면 끝을 잘라 206, 시작이 파일 끝 이상이면 416(`bytes */<크기>`), 끝 < 시작과 `bytes=-N`은 200 전체. 수정 전에는 끝이 넘는 요청에서 curl이 exit 18로 끝났다. 여러 범위는 첫 범위만 보낸다.
  - 실제 브라우저(Chrome)에서 9.4초에 `t`를 누르면 메모 칸에 `[0:09] Quantize: `가 들어갔다. 컨트롤 바의 챕터 이름과 진행 바 4칸도 확인했다.
  - 코드 탭 라벨이 `main.py`이고 한글 주석이 깨지지 않는다.
  - `BROWSER=true`면 브라우저를 열지 않는다.
  - 브랜드 문자열 0건
  - 시작 검사: order 항목이 없거나, mp4 길이를 못 읽거나(0바이트, 잘린 파일), full.mp4가 다른 목록으로 만들어졌으면 서버를 띄우지 않고 exit 1로 끝난다. 메시지에 없는 경로, 그 파일, 다시 만드는 ffmpeg 명령이 나온다.
  - 4·10·50개 항목을 `-c copy`로 이은 full.mp4는 그대로 뜨고 챕터 시각도 맞다. 씬 길이 합과의 차이는 최대 0.00065초(AAC 오디오가 있는 합성 클립 10개는 0.024초)여서 허용 오차를 0.1초로 정했다.
- **워크플로 전체 (에이전트 E2E)**: 새 에이전트 둘이 문서만 보고 주제 2개(이진 탐색, 3D 내적)를 Plan부터 Iterate까지 진행했다.
  - 둘 다 setup.sh 경고 0개, 씬 2개씩(34.3초, 29.5초) 렌더, 뷰어 기동과 종료, 피드백 한 줄을 받아 그 씬만 고치고 다시 렌더했다.
  - 이때 나온 문서 문제(색 목록, 중간 장면 확인, 뷰어 재시작, plan mode 순서 등)는 이 커밋에서 고쳤다.
- **문서 감사**: 에이전트가 문서 주장 약 450개를 소스와 대조했고, 다른 에이전트가 반박을 시도해 살아남은 지적만 반영했다.
  - 고친 뒤 같은 방식으로 약 430개를 다시 확인했다. 확인된 지적 8개(`-sw`에서 dt 업데이터가 두 번 불리는 것, setup.sh의 uv 오류 처리, 뷰어 재시작 문구 등)를 고쳤다.
- **플러그인**
  - `claude plugin validate ./manimgl-skill --strict`가 exit 0이다 (0.1.0에서 Claude Code 2.1.301, 0.2.0에서 `hooks/hooks.json`을 포함해 2.1.302). 통과하면 marketplace.json 줄만 나오지만 plugin.json과 skills/, agents/, commands/의 프런트매터도 검사하고, 문제가 있는 파일만 출력한다.
  - 사본을 하나씩 망가뜨려 확인했다. plugin.json JSON 오류와 SKILL.md `description` 삭제는 exit 1이다. 에이전트 `name` 삭제와 marketplace.json `source`가 없는 폴더를 가리키는 경우는 exit 0이라 이 명령으로 잡지 못한다.
  - 프런트매터 YAML 오류는 일부만 잡는다. 파싱이 실패하면 특수 문자(`>`, `#`, 콜론+공백 등)가 든 값을 따옴표로 감싸 한 번 더 파싱하고, 그래도 실패할 때만 exit 1이다. 그래서 LF 파일의 닫지 않은 따옴표(`argument-hint: "<topic>`)는 exit 0이고, 값에 특수 문자가 없거나 CRLF 파일이면 exit 1이다.
  - 설치(0.1.0에서): `claude plugin marketplace add ./manimgl-skill`과 `claude plugin install manimgl-skill@manimgl-skill`이 성공했고, `claude plugin list`에 0.1.0 enabled로 나왔다. 0.2.0 설치는 다시 하지 않았고, 훅은 `--plugin-dir`로 불러 확인했다.
  - 새 세션(`claude -p`, 0.1.0에서)에서 다음이 인식됐다.
    - 명령 `manimgl-skill:scene`
    - 스킬 `manimgl-skill:manimgl-best-practices`, `manimgl-skill:manimgl-workflow`
    - 에이전트 `manimgl-skill:scene-reviewer`

## 검증하지 못한 것

- macOS와 Linux에서 setup.sh 실행. Linux Pango 검사 경로도 실행하지 않았다. 이 OS에서는 setup.sh가 `[info]` 줄로 알린다.
- TeX Live 환경. MiKTeX만 확인했다.
- cm-super가 없는 상태에서 raenimgl의 Tex 패치가 어떻게 동작하는지.
- 비UTF-8 Windows 로캘(cp949)에서의 한글 Text, Tex(`working.tex` 인코딩), 뷰어, raenimgl `PythonCode`.
- 뷰어의 **Copy** 버튼. 사용자 클립보드를 덮어쓰므로 누르지 않았다.
- GitHub에서 `/plugin marketplace add getCurrentThread/manimgl-skill`. 로컬 폴더 설치만 해 봤다.
- 사람이 직접 하는 Plan 승인과 피드백. E2E에서는 에이전트가 피드백 줄을 만들어 넣었다.
- plan mode에서 scenes.md를 계획으로 내고, 나온 뒤에 파일로 쓰는 순서. 실제 plan mode 세션으로 해 보지 않았다.
- 최종 1920x1080 `-w` 렌더로 영상 전체를 만드는 것. E2E는 `-w -l`까지만 했다. 예제, 갤러리, 스모크 렌더는 1080p PNG와 480p mp4다.
- 새 Plan 항목(Hook, Aha moment, Next, Assumptions)과 질문 3개 제한 단계는 에이전트 E2E로 돌려 보지 않았다.
- `--autoreload`, `embed.exception_mode` 값, InteractiveScene 선택/잡기 키(Ctrl+C/V/X, `g`/`h`/`v`/`z`), Esc, cp949에서 `custom_config.yml` 읽기(`encoding=` 없이 연다).
- 내레이션: macOS/Linux의 로컬 TTS 엔진(제공하지 않음, 네트워크 엔진 `edge`와 `gemini`도 거기서는 돌려 보지 않았다), 팀 모드(`references/team-production.md`는 멀티 에이전트로 영상 하나를 만든 과정을 옮긴 것이고 처음부터 다시 돌려 보지는 않았다), 한국어 음성이 없는 Windows에 음성 설치, 귀로 들은 음성 품질, 한 문장을 넘는 `edge-tts`, cp949 로캘의 내레이션, 내레이션과 `--subdivide`.
- adithya-s-k/manim_skill 예제를 upstream에서 렌더하는 것. 각 행이 upstream에서도 똑같이 실패하는지는 소스로만 판단했고, 인용한 줄 일부는 upstream과 다르다 (fork-diff.md, "Upstream/PyPI-era code that breaks on the fork").
- macOS와 Linux에서의 점검. `check_examples.sh`, `check_docs.py`, 훅 명령은 Windows Git Bash에서만 돌렸다.
- PowerShell에서의 훅(Git Bash 없는 Windows의 Claude Code)과 Windows 스토어 `python3` 별칭 스텁. 이 머신에는 실제 `python3`가 있다. 명령은 `python`으로 넘어가게 돼 있다.
- CI. 없다. 모든 점검은 한 머신에서 손으로 돌렸다.

## 미확인 (소스로만 판단했고 실행하지 않음)

- raenimgl `PythonCode.exec()`의 동작.
- `-o`, `--finder`가 결과 파일을 여는 동작, `-f`, `--always_on_top` (창 전용).
- 렌더 중 Ctrl-C의 종료 코드.
- 창 모드(`-w` 없음)에서 `--fps`가 30으로 고정되는 것.
- `references/` 문서에서 `source evidence`라고 표시한 나머지 항목.
