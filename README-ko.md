# manimgl-skill

[English](README.md) | **한국어**

**CodingVillainKor/manimgl 포크에서 Claude Code로 3Blue1Brown 스타일 영상을 기획하고, 렌더하고, 다듬는다**

[CodingVillainKor/manimgl](https://github.com/CodingVillainKor/manimgl) 포크 **하나만** 대상으로 하는 Claude Code 플러그인이다. 이 포크는 3b1b/manim을 바탕으로 기본값을 한국어 환경에 맞췄다. 규칙은 포크 소스(커밋 `455a4201`, 2026-10-11), manimgl-imcommit의 사용 패턴, 실제 렌더 결과에서 나왔고, 근거는 `file:line`으로 적었다. PyPI `manimgl`이나 ManimCE(`manim`)용이 아니다.

![데모](docs/demo.gif)

## 설치

```
/plugin marketplace add getCurrentThread/manimgl-skill
/plugin install manimgl-skill@manimgl-skill
```

- 셸에서는 `claude plugin marketplace add getCurrentThread/manimgl-skill`, `claude plugin install manimgl-skill@manimgl-skill`이다.
- 로컬 클론을 쓰려면 `git clone https://github.com/getCurrentThread/manimgl-skill.git`으로 받은 뒤 `/plugin marketplace add <클론 경로>`를 실행한다. `./manimgl-skill` 같은 상대 경로는 Claude Code를 시작한 폴더 기준으로 해석되어 고정 디렉터리로 등록되므로, 클론을 옮기거나 지우면 `Marketplace file not found at ...\.claude-plugin\marketplace.json` 오류가 난다. 이때는 `/plugin marketplace remove manimgl-skill` 후 다시 추가한다.
- 플러그인 명령에는 네임스페이스가 붙으므로 명령은 **`/manimgl-skill:scene`** 형태가 된다.
- 마켓플레이스와 플러그인 이름은 둘 다 `manimgl-skill`이다. `.claude-plugin/*.json`의 `owner`/`author`는 자리표시자(`manimgl-skill maintainers`)이며 공개할 때 바꾼다.

영상은 포크를 `455a4201`에 고정한 uv 프로젝트의 `src/<video>/` 아래에 만든다 (프로젝트당 한 번 준비). 프로젝트에 포크가 없으면 `/manimgl-skill:scene`이 설치 스크립트를 직접 돌린다. 프로젝트를 손으로 준비하려면 다음을 실행한다.

```bash
bash path/to/manimgl-skill/scripts/setup.sh [PROJECT_DIR] [--with-raenimgl] [--smoke]
```

- 필수: `uv`, `ffmpeg`, `git`. 그 밖에 `ffprobe`(뷰어가 쓴다), OpenGL 컨텍스트, Noto Sans KR 글꼴(포크 `Text`의 기본 글꼴)이 있어야 한다. `dvisvgm`과 cm-super를 갖춘 LaTeX는 선택 사항이며 `Tex`, `TexText` 같은 LaTeX 기반 클래스에만 필요하다.
- PROJECT_DIR를 생략하면 현재 폴더를 쓴다. 거기에 `pyproject.toml`이 없으면 Python 3.10 uv 프로젝트를 만든다. 포크와 함께 `trimesh`, `pywavefront`(포크가 import하지만 선언하지 않는다)를 추가하고, `manimlib`이 정말 포크인지 확인한다. 다른 커밋의 포크가 이미 있으면 커밋은 바꾸지 않고 경고만 한다. `--smoke`는 테스트 씬을 렌더하고, `--with-raenimgl`은 raenimgl도 추가한다.
- 프로젝트가 이미 PyPI `manimgl`에 의존하면 해결 명령을 출력하고, 아무것도 바꾸지 않은 채 exit 2로 끝난다.
- Windows 11(Git Bash)과 MiKTeX에서만 확인했다. 모든 분기, 경고, MiKTeX 참고 사항은 [docs/details-ko.md](docs/details-ko.md#환경-준비-scriptssetupsh)에 있다.

## 동작 방식

빈 폴더에서 `/manimgl-skill:scene <topic>`을 실행한다. 예: `/manimgl-skill:scene 이진 탐색을 설명하는 30초 영상`.

1. **Plan** - Claude가 지정한 자료(논문, 문서, 코드)를 읽는다. 대상, 길이, 깊이가 불분명하면 한 메시지에 질문을 최대 3개까지 한다. 그다음 `src/<video>/scenes.md`를 쓴다. 대상 시청자, 핵심 아이디어, 훅, 아하 모먼트, 흔한 오해, 색 역할, 15-30초짜리 씬 1-8개가 들어간다. 계획을 승인하기 전에는 코드를 쓰지 않는다.
2. **Code & Render** - 씬 하나에 클래스 하나씩 `src/<video>/main.py`에 쓴다. 씬마다 마지막 프레임(`-sw`)을 확인한 다음, 480p 초안(`-w -l`)으로 렌더해 0.5초 간격 프레임 시트로 읽는다. 마지막 프레임만으로는 애니메이션 도중의 겹침이 보이지 않기 때문이다. 읽기 전용 `scene-reviewer` 에이전트가 한 번 더 검토할 수 있다. 최종 렌더는 씬마다 `-w`(1920x1080, 30 fps)다.
3. **Iterate** - Claude가 씬들을 `full.mp4`로 이어 붙이고 로컬 뷰어(Python 표준 라이브러리와 ffprobe)를 띄운다. 뷰어에는 씬마다 챕터가 하나씩 있고, `main.py`를 보여 주는 Code 탭이 있다.

   ![로컬 뷰어: 씬별 챕터, 플레이어 바의 Capture, Copy가 있는 Notes 패널](docs/viewer.png)

   문제가 있는 곳에서 멈추고 **t**를 누르거나 **Capture**를 클릭한다. 시각과 씬 이름이 `[M:SS] <Scene>: ` 형식으로 **Notes**에 들어간다. 그 줄을 마저 써서 `[0:07] Quantize: 라벨이 축과 겹친다`처럼 만든다. **Copy**를 클릭하고 메모를 Claude Code에 붙여 넣는다.

   Claude는 줄마다 `full.mp4`에서 그 시각의 프레임을 뽑아 보고, 지목된 씬만 고쳐 다시 렌더한다. 이어서 `full.mp4`를 다시 만들고 같은 포트로 뷰어를 재시작한다. 고치기 전과 후의 프레임을 비교한 뒤 결과를 알린다. 탭을 새로 고치면 새 버전을 볼 수 있다.

## 포크에서 검증한 규칙

`skills/manimgl-best-practices`는 `/manimgl-skill:scene` 안팎을 가리지 않고 모든 `from manimlib import *` 코드에 적용된다. 포크에서 실패하거나 다르게 동작하는 ManimCE·upstream 습관(`Create`, `MathTex`, `-ql`/`-p`, `Succession` 등), 여러 클래스가 조용히 무시하는 생성자 `color=`, 포크에 없는 색 이름, `Scene.__init__`이 덮어쓰는 모듈 수준 시드, `Text`와 `Tex` 안의 한글, 카메라 궤도, CLI를 다룬다.

- `references/`: 근거 문서 9개. `F:`/`U:`/`R:`/`I:` `file:line` 인용(포크, upstream, raenimgl, imcommit)을 달았다.
- `examples/`: 렌더로 확인한 씬 파일 10개. `gallery/`: ML·수학 주제용으로 옮겨 온 씬 파일 9개(씬 17개), CC BY-NC-SA 4.0.
- 스킬 문서(`SKILL.md`, `references/`, 템플릿)는 영어로 썼다. 그 안의 한국어 예시 문자열은 의도한 것이다.

전체 파일 구성: [docs/details-ko.md](docs/details-ko.md#구성).

## 한국어 내레이션 (선택)

내레이션을 요청하지 않으면 영상에는 소리가 없다 (scenes.md의 `Narration: voiceover`).

- `tools/tts.py`는 `narration.txt`의 줄마다 클립 하나와 `narration/timestamps.json`을 만들고, 해시로 캐시한다. 기본 엔진은 Windows SAPI이고, 로컬 한국어 음성 Microsoft Heami Desktop을 쓴다.
- `--engine edge`는 edge-tts를 쓰며 모든 줄을 Microsoft 온라인 서비스로 보낸다. Claude는 사용자가 이 엔진을 고른 경우에만 쓴다.
- `tools/voiceover.py`는 `Narrated` 믹스인을 더한다. `with self.voice(k):`가 k번째 줄을 재생하고, `-w` 렌더마다 오디오 트랙과 씬별 `.srt`가 생긴다. 뷰어는 이 `.srt`들을 이어 자막으로 보여 준다.
- macOS나 Linux용 엔진은 제공하지 않는다. 자세한 내용: [references/voiceover.md](skills/manimgl-workflow/references/voiceover.md).

## 린트 훅과 점검

플러그인이 켜져 있는 동안 PostToolUse 훅이 Write/Edit/MultiEdit 뒤마다 `scripts/lint_manimgl.py`를 돌린다. manimlib이나 raenimgl을 import하는 `.py` 파일(또는 pyproject에 manimgl이 적힌 프로젝트 안에서 `manim`을 import하는 파일)에만 동작한다. 작업을 막지 않으며, 지적은 추가 컨텍스트로 Claude에게 넘긴다. PATH에 `python3`나 `python`이 있어야 한다.

같은 린트는 포크나 GPU 없이 손으로도 돌릴 수 있다: `python scripts/lint_manimgl.py <file>`. `scripts/check_docs.py`, `check_citations.py`, `check_inventory.py`, `check_examples.sh`는 문서의 코드, API 목록, 모든 예제 렌더를 포크에 대고 시험하고, `file:line` 인용은 고정 커밋의 참조 저장소와 대조한다. 명령, 필요한 것, 종료 코드: [docs/details-ko.md](docs/details-ko.md#점검).

## 파일 위치

모든 파일은 uv 프로젝트 안에 쓰인다.

```
<uv project>/
  pyproject.toml           # fork pinned by setup.sh
  src/<video>/             # every command runs from here
    scenes.md              # the approved plan
    main.py                # one class per scene
    videos/<Scene>.png     # last frame (-sw)
    videos/<Scene>.mp4     # scene render (-w -l draft, then -w)
    concat.txt             # scene order for ffmpeg and the viewer
    full.mp4               # joined video
    narration.txt, narration/, voiceover.py, videos/<Scene>.srt, full.srt   # only with narration
```

manimgl은 현재 폴더의 `videos/` 아래에 결과를 쓴다. 그래서 Claude는 `src/<video>`에서 작업한다.

## 라이선스

최상위 LICENSE는 아직 없다. 저작권자를 정한 뒤 추가한다. 그때까지 제3자 부분은 각자의 라이선스를 따른다.

| 부분 | 출처 | 라이선스 |
|---|---|---|
| 뷰어(`skills/manimgl-workflow/tools/video_viewer.py`, `ui.html`)와 `tts.py` 일부(캐시 키, ffprobe 길이 측정, `timestamps.json`) | [Yusuke710/manim-skill](https://github.com/Yusuke710/manim-skill) | MIT, [tools/LICENSE-manim-skill](skills/manimgl-workflow/tools/LICENSE-manim-skill) |
| 기획 참고 문서(`skills/manimgl-workflow/references/narrative-patterns.md`, `visual-techniques.md`, `templates/scenes-example.md`) | [adithya-s-k/manim_skill](https://github.com/adithya-s-k/manim_skill) `skills/manim-composer/` | MIT, [references/LICENSE-manim_skill](skills/manimgl-workflow/references/LICENSE-manim_skill) |
| `skills/manimgl-best-practices/gallery/`와 그 씬의 렌더 화면(`docs/demo.gif`, `docs/viewer.png`) | adithya-s-k/manim_skill, 예제 코드 원저작자 Grant Sanderson / 3Blue1Brown | CC BY-NC-SA 4.0, [gallery/LICENSE.txt](skills/manimgl-best-practices/gallery/LICENSE.txt) |

**`gallery/`는 비영리(NonCommercial)·동일조건 변경허락(ShareAlike) 조건이다.** 플러그인의 나머지가 어떤 라이선스를 받든 이 폴더에는 적용되지 않는다. `gallery/`나 이 두 이미지를 포함한 사본은 상업적으로 쓸 수 없고, 고친 갤러리 파일도 CC BY-NC-SA 4.0을 유지해야 한다.

포크, 3b1b/manim, manimgl-imcommit, raenimgl, 3b1b/videos는 읽고 비교했다. manimgl-imcommit과 raenimgl에는 LICENSE 파일이 없어 코드를 옮기지 않았다. 고정 커밋까지 적은 전체 표: [docs/details-ko.md](docs/details-ko.md#출처와-라이선스).
