---
name: manimgl-workflow
description: End-to-end workflow for making an explainer video with the CodingVillainKor/manimgl fork - Plan (scenes.md, user approval) → Code & Render (src/<video>/main.py, last-frame check with -sw, mid-animation frame sheets, then -w per scene) → Iterate (concat, local viewer, timestamped feedback, re-render only the affected scenes). Use when the user asks to make or animate a video/scene with manimgl, or runs /manimgl-skill:scene.
---

# manimgl 영상 워크플로: Plan → Code & Render → Iterate

코드를 쓰기 전에 **manimgl-best-practices** 스킬을 따른다. 포크 API, 색 함정, 한글, CLI 규칙이 거기 있다.

## 계약

- **결과물**: `src/<영상>/main.py`, 씬별 `videos/<Scene>.mp4`, `full.mp4`, 뷰어 URL을 넘긴다.
- **막혔을 때**: 실패한 명령과 에러의 마지막 줄을 그대로 보고한다.
- **승인 전 코딩 금지**: 사용자가 Plan을 승인하기 전에는 `main.py`를 쓰지 않는다.
- **커밋 기준**: 이 워크플로가 맞춘 것은 포크 @455a4201 하나다. setup.sh는 포크를 새로 추가할 때 이 커밋으로 고정하고, 이미 다른 커밋이면 경고만 한다.

## 0. 준비 (프로젝트당 한 번)

- 프로젝트는 `pyproject.toml`이 있는 uv 프로젝트 루트다. 포크가 아직 없으면 설치한다.
  ```bash
  bash ${CLAUDE_PLUGIN_ROOT}/scripts/setup.sh <프로젝트 루트>                  # raenimgl도 쓰려면 --with-raenimgl
  ```
- setup.sh 결과별 처리:
  - **exit 2 (PyPI `manimgl`과 충돌)**: 출력된 해결 명령을 사용자에게 보여 주고, 승인을 받은 뒤 실행한다.
  - **exit 1 (`[fail]`)**: 렌더할 수 없다. 출력된 `[fail]` 줄을 그대로 보고한다.
  - **LaTeX / cm-super 경고**: Tex 없이 계획하거나(Text, 도형, 숫자만 사용) 사용자에게 설치를 요청한다.
  - **ffprobe 경고**: 3단계 뷰어가 시작하지 못한다. ffmpeg와 함께 ffprobe를 설치해 달라고 요청한다.
  - **Noto Sans KR 경고**: 한글 Text가 □로 나올 수 있다. 폰트 설치를 요청하거나 `font=`를 지정한다.
  - **OpenGL 경고**: `-w` 렌더가 실패할 수 있다. 경고 줄을 그대로 보고한다.
- 영상 폴더는 `<프로젝트>/src/<영상명>/`이다. 영상명은 짧은 영문으로 짓는다. **이후 명령은 모두 이 폴더에서 실행한다.** 출력이 cwd 아래 `videos/`에 쌓이기 때문이다.

## 1. Plan

1. `${CLAUDE_SKILL_DIR}/templates/scenes.md` 형식으로 scenes.md 내용을 채운다.
   - **청중**: 누가 보는지, 무엇을 이미 아는지
   - **핵심 개념**: 영상이 끝나면 남을 한 문장
   - **씬 목록**: 서사 순서. 씬마다 클래스명(PascalCase), 15~30초, `##` 블록이 될 내레이션/의도 줄, 화면 요소, 끝 상태, 다음 씬으로의 연결
2. scenes.md 내용을 보여 주고 **명시적 승인**을 받는다. 수정 요청이 오면 반영하고 다시 승인을 받는다.
   - plan mode에서는 파일을 쓸 수 없다. scenes.md 내용 전체를 계획으로 제시하고, 승인되어 plan mode를 나온 뒤에 `src/<영상>/scenes.md`로 쓴다.
   - plan mode가 아니면 `src/<영상>/scenes.md`를 먼저 쓰고 보여 준다.
   - 승인되면 scenes.md의 `## 승인` 칸에 표시한다.

## 2. Code & Render

1. `main.py` 하나에 scenes.md 순서대로 클래스를 쓴다. 형태는 `${CLAUDE_PLUGIN_ROOT}/skills/manimgl-best-practices/examples/structure.py`를 따른다.
   - 각 클래스는 **혼자 렌더된다.** 앞 씬의 끝 상태가 필요하면 그 클래스 안에서 다시 만든다.
   - `construct` 안의 `## …` 블록은 scenes.md의 줄과 1:1로 맞춘다.
2. **씬 하나씩** 마지막 프레임을 확인한다.
   ```bash
   cd <프로젝트>/src/<영상>
   uv run manimgl main.py <Scene> -sw </dev/null   # -> videos/<Scene>.png  (-s 만 쓰면 창이 뜨고 멈춘다)
   ```
   - 종료 코드가 0이 아니면 실패다. 실패해도 예전 `videos/<Scene>.png`/`.mp4`가 남아 있으므로 파일만 보고 판단하지 않는다.
   - `videos/<Scene>.png`를 Read로 열어 다음을 본다.
     - 겹침
     - 화면 밖으로 잘린 부분
     - 한글 □(두부)
     - 검은 배경 대비 부족
     - 너무 작은 글자
     - 지웠어야 할 잔여 객체
     - 의도와 다른 색. 생성자 `color=`는 `Text/Tex/TexText/Dot/Brace`에서 무시되어 흰색, `Arrow/Vector/StrokeArrow`에서 회색이 되고, `Circle/Ellipse`는 테두리가 빨갛다 (best-practices §6)
   - 문제가 있으면 고치고 같은 명령을 다시 실행한다.
3. 영상으로 렌더한다.
   ```bash
   uv run manimgl main.py <Scene> -w -l </dev/null   # 초안 854x480 -> videos/<Scene>.mp4
   ```
   - 에러가 나면 Traceback 마지막 부분을 읽고 고친 뒤 **그 씬만** 다시 렌더한다.
   - 렌더가 끝나면 **중간 장면도 본다.** `-sw` PNG는 마지막 프레임뿐이다.
     - 그래서 애니메이션 도중의 문제(겹치며 바뀌는 글자, 사라지는 객체 위를 지나가는 객체, 원점에서 커지는 객체)와 카메라가 움직이는 씬의 시작 구도는 거기 보이지 않는다.
     - 0.5초 간격 프레임을 한 장(6×6칸, 18초분)에 모아 Read로 본다.
     ```bash
     ffmpeg -v error -y -i videos/<Scene>.mp4 -vf "fps=2,scale=320:-1,tile=6x6" videos/sheet_<Scene>_%02d.png
     ```
     - 시트 m의 k번째 칸(왼쪽 위부터 행 순서)은 약 18(m-1) + 0.5k - 0.25초다.
     - 2번의 목록으로 각 칸을 본다. 의심 가는 시점은 `ffmpeg -v error -y -ss <초> -i videos/<Scene>.mp4 -frames:v 1 videos/t<초>.png`로 크게 뽑아 본다.
   - 더 꼼꼼한 검토는 **scene-reviewer** 에이전트(`manimgl-skill:scene-reviewer`)에 `src/<영상>` 절대경로와 씬 이름을 주고 맡긴다.
4. 모든 씬이 에러 없이 나올 때까지 2~3을 반복한다.
5. 최종본은 `uv run manimgl main.py <Scene> -w </dev/null`(1920x1080 30fps)로 만든다. 같은 `videos/<Scene>.mp4`에 덮어쓴다.
   - **모든 씬을 같은 품질 옵션으로** 렌더해야 다음 단계의 `-c copy` 이어 붙이기가 된다.

## 3. Iterate

1. scenes.md 순서대로 `concat.txt`를 쓰고 이어 붙인다. 경로는 concat.txt 기준이다.
   ```
   file 'videos/Intro.mp4'
   file 'videos/Quantize.mp4'
   ```
   ```bash
   ffmpeg -v error -y -f concat -safe 0 -i concat.txt -c copy full.mp4
   ```
2. 뷰어를 **백그라운드**로 띄운다. 표준 라이브러리와 ffprobe만 쓴다.
   ```bash
   uv run python ${CLAUDE_SKILL_DIR}/tools/video_viewer.py full.mp4 --order concat.txt --script main.py
   ```
   - 출력의 `VIDEO_READY http://localhost:<port>` URL을 사용자에게 알린다. 포트는 8000~8999 중 빈 것을 쓴다. 4.5에서 쓰므로 **포트를 기억해 둔다.**
   - 뷰어는 브라우저를 직접 연다. 열지 않으려면 명령 앞에 `BROWSER=true`를 붙인다.
   - 뷰어에는 종료 명령이 없다. 끄는 법은 4.5에 있다.
   - 챕터 이름은 mp4 파일명, 즉 씬 클래스명이다.
3. 사용자는 뷰어에서 `t` 키(Capture)로 `[M:SS] <Scene>: <메모>` 줄을 만든다. **Copy** 버튼으로 복사해 대화에 붙여 넣는다.
4. 피드백 한 줄마다 처리한다.
   1. 그 시점을 뽑아 Read로 본다. 사용자가 본 장면을 먼저 확인한다.
      - `[M:SS]`는 full.mp4 기준 시각이고 초 아래를 버린 값이다 (`tools/ui.html` `fmt`). 프레임 한 장만 보면 그 1초 안의 문제를 놓친다.
      - `<초>` = M×60+SS부터 1초를 4장으로 뽑아 한 장에 모은다.
      ```bash
      ffmpeg -v error -y -ss <초> -t 1 -i full.mp4 -vf "fps=4,scale=854:-1,tile=2x2" -frames:v 1 fb_<초>.png
      ```
      - main.py의 어느 `##` 블록인지는 씬 안의 시각으로 찾는다. `<초>`에서 그 챕터의 `start`를 빼면 된다. `start`는 뷰어의 `/chapters.json`에 있다.
   2. **이름이 나온 씬 클래스만** 고친다.
      - 고친 결과 그 씬의 끝 상태(남은 객체, 카메라 방향)가 바뀌면, 다음 씬이 다시 만드는 시작 상태도 맞추고 그 씬도 다시 렌더한다.
      - 여러 씬이 함께 쓰는 함수를 고쳤을 때도 그 씬들을 모두 다시 렌더한다.
   3. 고친 씬을 `-sw`로 확인한 뒤, 다른 씬과 같은 품질 옵션으로 `-w`(또는 `-w -l`) 다시 렌더한다.
   4. concat을 다시 해서 `full.mp4`를 만든다.
   5. **뷰어를 재시작한다.** 챕터 길이와 main.py 탭은 시작할 때 한 번만 읽는다 (`tools/video_viewer.py` `main()`).
      - 먼저 떠 있는 뷰어를 끈다. 끄지 않으면 아래 `--port` 명령이 그 포트를 잡지 못해 `OSError`(Windows: WinError 10048)로 끝난다. `--port` 없이 띄우면 다음 빈 포트를 잡아 URL이 바뀐다.
      - `uv run` 아래에서 포트를 잡은 것은 자식 python 프로세스다. 그래서 포트로 찾아서 끈다.
        ```bash
        # Windows (Git Bash): 마지막 열이 PID
        netstat -ano | grep LISTENING | grep ":<port> "
        taskkill //F //PID <pid>
        # macOS / Linux (-sTCP:LISTEN이 없으면 브라우저 연결까지 끈다)
        kill $(lsof -ti tcp:<port> -sTCP:LISTEN)
        ```
      - 같은 포트로 다시 띄운다. 새 탭은 열지 않는다. 사용자는 열려 있는 탭을 새로고침하면 된다.
        ```bash
        BROWSER=true uv run python ${CLAUDE_SKILL_DIR}/tools/video_viewer.py full.mp4 --order concat.txt --script main.py --port <port>
        ```
   6. 고쳐졌는지 확인한다.
      - 새 full.mp4에서 1번 명령을 `fb_<초>_after.png`로 다시 실행하고 `fb_<초>.png`와 비교한다.
      - 고친 씬의 길이가 바뀌었으면 `<초>`도 새 `/chapters.json`의 `start`로 다시 계산한다.
      - 고쳐진 것을 확인한 뒤에 사용자에게 알린다. `-sw` PNG는 마지막 프레임이라서 중간 장면에 대한 피드백은 그것으로 확인되지 않는다.
5. 사용자가 만족할 때까지 4를 반복한다.

## 참고

- 뷰어 원본은 Yusuke710/manim-skill(MIT)이다. 바꾼 점은 `tools/README.md`에 있다.
- 자막, TTS, 보이스오버는 이 워크플로에 없다. 포크에 subcaption API가 없다.
