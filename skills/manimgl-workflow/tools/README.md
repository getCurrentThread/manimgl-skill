# tools: 로컬 영상 뷰어

`video_viewer.py`와 `ui.html`은 [Yusuke710/manim-skill](https://github.com/Yusuke710/manim-skill)의 `skills/manim-skill/tools/`를 가져와 고친 것이다.
- 기준 커밋: `a0048d9e265499038f34a9aa58ff16d306b5034c`
- 라이선스: MIT, Copyright (c) 2025 Yusuke Miyashita. 원문은 [LICENSE-manim-skill](LICENSE-manim-skill)에 있다.

## 사용

```bash
# src/<영상>에서 실행한다. full.mp4와 concat.txt가 거기 있다.
uv run python <tools 폴더>/video_viewer.py full.mp4 --order concat.txt [--script main.py] [--port N] [--host HOST] [--srt file.srt]
```

- **필요한 것**: Python 표준 라이브러리, `ffprobe`(PATH에 있어야 함). 외부 패키지는 없다.
- **`--order`**: `file '<경로>'` 줄로 된 ffmpeg concat 목록이다. 경로는 concat.txt가 있는 폴더 기준이다. 각 파일의 길이와 파일명(stem)으로 챕터를 만든다.
- **실행 동작**:
  - `--port`가 없으면 8000~8999에서 빈 포트를 찾는다. `--port N`을 주면 그 포트만 쓴다.
  - `--host` 기본값은 `127.0.0.1`이다.
  - `VIDEO_READY http://localhost:<port>`를 출력하고 브라우저를 연다. 열지 않으려면 명령 앞에 `BROWSER=true`를 붙인다. Python `webbrowser`가 이 환경 변수를 따른다 [실행확인, Windows].
  - 종료 명령은 없다. 포트를 잡은 프로세스를 끈다. `uv run`으로 띄웠으면 그 프로세스는 자식 python이다.
- **경로**:
  - `/`: UI
  - `/video.mp4`: Range 요청을 지원하며 206을 돌려준다
  - `/chapters.json`
  - `/subtitles.srt`
  - `/download`
  - `/cscript.py`: `--script`로 준 파일 내용
- **피드백**: `t` 키로 `[M:SS] <챕터명>: ` 줄을 넣고, **Copy**로 복사한다. 서버로 보내는 기능(POST)은 없다.
- **재시작 필요**: 챕터와 스크립트 내용은 시작할 때 한 번만 읽는다. 씬을 다시 렌더한 뒤에는 뷰어를 다시 띄운다.
  - 이전 프로세스를 끄지 않으면 새 뷰어는 다음 빈 포트를 쓴다.
  - 이전 프로세스를 끄고 `--port`로 같은 포트를 주면 URL이 그대로다 (workflow SKILL.md 3단계 4.5).

## 원본과 다른 점

1. 모든 `read_text()`에 `encoding="utf-8"`을 넣었다. Windows 기본 로캘에서 한글 주석이 있는 main.py가 깨지지 않게 하기 위해서다.
2. 원본 UI의 제3자 브랜드 링크와 관련 CSS, 주석을 지웠다.
3. 코드 탭 라벨 `script.py`를 `--script`로 준 파일 이름으로 바꿔 보여 준다. `/cscript.py` 경로는 그대로다.
4. 그 외 로직(포트, 챕터, Range, SRT 이어 붙이기)은 원본과 같다.
