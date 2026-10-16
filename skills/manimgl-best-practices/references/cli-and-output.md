# manimgl CLI와 출력 (포크 @455a420)

- 형식: `uv run manimgl <file.py> <Scene> [<Scene> ...] [옵션]`. `manimgl`과 `manim-render`는 같은 진입점이다 (F:setup.cfg:65-66).
- [실행확인] 환경: Windows 11, Git Bash, uv Python 3.10, ffmpeg gyan.dev 2025-12-24 빌드 (PATH). 설치된 `manimlib`은 포크 @455a420 소스와 파일 단위로 같다 (`diff -rq`).
- 이 문서의 `F:` 경로는 포크 저장소 루트 기준이다. §2 표의 `:NN`은 `F:manimlib/config.py:NN`이다.

## 1. 먼저 알아야 할 것

| 규칙 | 근거 |
|---|---|
| `-w`가 없으면 창 모드다. 창을 닫을 때까지 프로세스가 끝나지 않는다 | `show_in_window = not write_file` (F:manimlib/config.py:331), `interact()` 루프 (F:manimlib/scene/scene.py:186-201). `-s`, `-ql`, `-sql`, `-a`를 단독으로 쓰면 `timeout`(20~60초)으로 강제 종료될 때까지(124) 멈추고 아무 파일도 남지 않는다 [실행확인] |
| 저장 스위치는 `-w`다. `-o`와 `--finder`도 `-w`를 켠다 | F:manimlib/config.py:233 |
| `-s -w`(`-sw`)는 PNG만 쓰고, `-w`만 쓰면 영상만 쓴다 | `write_to_movie = not s and w`, `save_last_frame = s and w` (F:manimlib/config.py:278,280) [실행확인] |
| 씬 이름을 항상 준다. 씬이 2개 이상인데 이름이 없거나 틀리면 `input()` 프롬프트에서 멈춘다 | F:manimlib/extract_scene.py:94-104,48. stdin이 `/dev/null`이면 즉시 exit 1 [실행확인] |
| `-p`는 presenter mode다 (CE의 preview가 아니다). `-w`와 함께 쓰면 첫 `play`/`wait`에서 영원히 멈춘다 | `pre_play`에서 `hold_loop()` (F:manimlib/scene/scene.py:519-521,605,623-626). 창이 없으면 space 키를 받을 수 없다. `-w -l -p`가 `timeout 40`에서 exit 124로 끝났고 `videos/`는 비어 있었다 [실행확인] |
| 출력은 **cwd** 기준 `videos/`에 쌓인다. 스크립트 위치는 상관없다 | F:manimlib/default_config.yml:20,23, F:manimlib/config.py:244,393. 다른 폴더에서 `../w/one.py`를 실행하면 `<cwd>/videos/Only.mp4`가 생긴다 [실행확인] |
| `import manimlib`만 해도 `sys.argv`를 manimgl CLI로 파싱한다 | `manim_config = initialize_manim_config()` → `parse_cli()` (F:manimlib/config.py:33,406). `python -c "import manimlib" --bogus` → `unrecognized arguments`, exit 2 [실행확인]. manimlib을 import하는 도구 스크립트는 자기 인자를 받으면 안 된다 |

## 2. 플래그 전체

`manimgl --help`의 모든 플래그를 주제별로 묶었다 (순서는 help와 다르다). "효과"는 help 문구가 아니라 구현을 읽고 쓴 것이다.

| 플래그 | 정의 | 구현된 효과 |
|---|---|---|
| `file` | F:manimlib/config.py:59 | 생략하면 `BlankScene`(InteractiveScene + `embed()`)을 창으로 연다 (F:manimlib/extract_scene.py:22-25,115). stdin이 EOF면 IPython이 바로 끝나고 exit 0 [실행확인] |
| `scene_names` | :64 | 여러 개를 주면 순서대로 렌더한다 [실행확인]. 파일에 씬이 1개뿐이면 이름이 틀려도 그 씬을 렌더한다 (F:manimlib/extract_scene.py:95) [실행확인] |
| `-w, --write_file` | :69 | 영상 파일을 쓰고 창을 띄우지 않는다 (F:manimlib/config.py:278,331) [실행확인] |
| `-s, --skip_animations` | :74 | 모든 애니메이션을 건너뛰고 마지막 상태만 만든다. `-w`가 있을 때만 PNG를 저장하고, 없으면 창을 띄운 채 멈춘다 [실행확인] |
| `-l` / `-m` / `--hd` / `--uhd` | :79,84,89,94 | 해상도를 854x480 / 1280x720 / 1920x1080 / 3840x2160으로 바꾼다 (F:manimlib/default_config.yml:101-104). fps는 그대로다 [실행확인, §3.1] |
| `-r, --resolution WxH` | :176 | 해상도를 직접 준다. `-l` 등과 같이 쓰면 `-r`이 이긴다 (F:manimlib/config.py:358-368) [실행확인] |
| `--fps N` | :180 | `camera.fps`를 바꾼다 (F:manimlib/config.py:262-263) [실행확인]. 창 모드에서는 30으로 고정된다 (F:manimlib/scene/scene.py:104, 소스 근거) |
| `-c, --color` | :185 | 배경색이다. `colour.Color`로 파싱하므로 `red`는 CSS 색 `#FF0000`이며 manim `RED`(`#FC6255`, F:manimlib/default_config.yml:163)가 아니다 [실행확인]. 잘못된 색이면 `Please use a valid color` 후 exit 2 [실행확인] |
| `-t, --transparent` | :120 | `.mov` + `prores_ks`로 쓴다 (ffprobe: `prores`, `yuva444p12le`). `background_opacity=0`이 된다 (F:manimlib/config.py:271-272,292-294). `-sw -t`면 PNG 배경 알파가 0이다 [실행확인] |
| `-i, --gif` | :115 | `.gif`로 쓴다. `video_codec=''`라 ffmpeg가 확장자로 인코더를 고른다 (F:manimlib/config.py:295-296,374-375). `-t`와 같이 쓰면 `-t`가 이겨 `.mov`가 된다 [실행확인] |
| `--vcodec` | :125 | ffmpeg `-vcodec`. `-t`/`-i`보다 우선한다 (F:manimlib/config.py:290-291). 없는 코덱이면 `BrokenPipeError`, exit 1 [실행확인] |
| `--pix_fmt` | :129 | ffmpeg `-pix_fmt` (F:manimlib/config.py:298-299). `--pix_fmt yuv444p` → yuv444p [실행확인] |
| `-q, --quiet` | :133 | 파일 쓰기 진행 바와 `File ready at` 로그를 끈다 (F:manimlib/scene/scene_file_writer.py:232,340). 배너는 그대로 나온다 [실행확인]. 창 모드 Tips 로그도 `-q`와 무관하게 나온다 (F:manimlib/scene/scene.py:194-198, 소스 근거) |
| `-a, --write_all` | :138 | 파일의 모든 씬을 렌더한다 (F:manimlib/extract_scene.py:95). `-w`를 켜지 않으므로 `-a`만 쓰면 창이 뜨고 멈춘다. `-a -w`로 쓴다 [실행확인] |
| `-o, --open` | :143 | `-w`를 켜고, 끝나면 결과 파일을 연다. Windows에서는 `os.startfile` (F:manimlib/scene/scene_file_writer.py:363-364, 소스 근거) |
| `--finder` | :148 | `-w`를 켠다. Windows에서는 `-o`와 똑같이 파일 자체를 연다 (같은 줄, 소스 근거) |
| `--subdivide` | :153 | 애니메이션마다 `videos/<Scene>/00000.mp4`, `00001.mp4` …를 쓰고 `<Scene>.mp4`는 만들지 않는다 (F:manimlib/scene/scene_file_writer.py:94-95,121-123) [실행확인] |
| `--file_name` | :159 | 씬 이름과 `-n` 접미사를 대신한다. 확장자는 `with_suffix`로 바뀐다 (F:manimlib/scene/scene_file_writer.py:88-92,104-105). 그래서 `v1.2` → `v1.mp4`, `x.mp4` → `x.mp4`가 된다 [실행확인] |
| `-n, --start_at_animation_number` | :163 | §3.2 |
| `-e, --embed LINE` | :170 | 해당 줄 뒤에 `self.embed()`를 끼워 모듈을 다시 실행한다. 씬 이름이 없으면 위쪽에서 가장 가까운 `class`를 고른다 (F:manimlib/extract_scene.py:146-178). 창이 없으면 `embed()`는 아무 일도 하지 않는다 (F:manimlib/scene/scene.py:208). 소스 근거 |
| `-f, --full_screen` | :99 | 창 모드 전용. 창 폭을 모니터 전체로 한다 (F:manimlib/window.py:108). 소스 근거 |
| `--always_on_top` | :104 | 창 모드, Windows 전용. 포크에만 있다 (F:manimlib/window.py:53-54,82-97). 소스 근거 |
| `-p, --presenter_mode` | :109 | 첫 `play`/`wait`의 `pre_play`와 매 `wait`에서 `hold_loop()`로 멈춘다. 창에서 space나 → 키를 받아야 풀린다 (F:manimlib/scene/scene.py:519-521,607-610,623-626,869-870). 창이 없는 `-w`와 같이 쓰면 끝나지 않는다 (§1) [실행확인] |
| `--leave_progress_bars` | :189 | `scene.leave_progress_bars=True` (F:manimlib/config.py:316-317). 소스 근거 |
| `--show_animation_progress` | :194 | 애니메이션별 진행 바를 stderr에 추가로 띄운다. `scene.py:129-130`은 파일 쓰기 진행 바가 있으면 끄려 하지만, 그 바는 `Scene.__init__`이 끝난 뒤 `run()`의 `file_writer.begin()`에서 만들어지므로 검사 시점에는 항상 없다 (F:manimlib/scene/scene.py:116,129-130,152, F:manimlib/scene/scene_file_writer.py:232-238). 그래서 `-w`에서도 두 진행 바가 함께 나온다 [실행확인] |
| `--prerun` | :199 | 렌더하기 전에 skip 모드로 한 번 더 실행해 총 프레임 수를 센다 (F:manimlib/extract_scene.py:63-84). 진행 바가 `46/150`처럼 표시되고, 예외는 파일을 쓰기 전에 난다 [실행확인] |
| `--video_dir DIR` | :205 | 출력 폴더를 바꾼다 (cwd 기준 상대 경로, 없으면 만든다). `directories.base`보다 우선한다 (F:manimlib/config.py:393) [실행확인] |
| `--config_file PATH` | :209 | §5. 경로가 없어도 **조용히 무시**하고 exit 0으로 끝난다 (F:manimlib/config.py:343-348) [실행확인] |
| `-v, --version` | :213 | 파일 없이 쓰면 배너만 출력하고 끝난다. 파일과 함께 쓰면 무시되고 렌더가 진행된다 (F:manimlib/__main__.py:53-57) [실행확인] |
| `--log-level` | :218 | 로거 레벨을 바꾼다 (F:manimlib/config.py:41). `WARNING`이면 `File ready` 로그가 사라진다 [실행확인] |
| `--clear-cache` | :222 | §6. 디스크 캐시 전체를 지운 뒤 평소처럼 실행한다 (F:manimlib/__main__.py:58-61) |
| `--autoreload` | :227 | `embed.autoreload=True` (F:manimlib/config.py:335-337). IPython embed 전용이다. 소스 근거 |

`-ql`은 `-q -l`로 파싱된다. `-w`가 없으므로 창이 뜨고 멈춘다. `-sql`도 같다 [실행확인]. `-w -ql`이면 854x480 영상을 조용히 쓴다 [실행확인].

## 3. 실행으로 확인한 의미

### 3.1 해상도와 fps (ffprobe, 1초 씬) [실행확인]

| 옵션 | 결과 |
|---|---|
| (없음) / `--hd` | 1920x1080, 30fps, h264, yuv420p |
| `-l` | 854x480, 30fps |
| `-m` | 1280x720 |
| `--uhd` | 3840x2160 |
| `-r 640x360` / `-r 1000x1000` | 640x360 / 1000x1000 |
| `-l -r 320x240` | 320x240 (`-r` 우선) |
| `--fps 12` / `-l --fps 60` | 1920x1080 12fps / 854x480 60fps |

- 해상도 비율을 바꾸면 `FRAME_HEIGHT`는 8로 두고 `FRAME_WIDTH`가 비율을 따른다 (F:manimlib/constants.py:13-20).
  - `-r 1080x1920`이면 4.5, `-r 1000x1000`이면 8.0이다 [실행확인].
  - 세로 영상은 `-r 1080x1920`으로 만들고, 레이아웃은 폭 4.5 기준으로 짠다.

### 3.2 `-n` (애니메이션 번호) [실행확인]

- `play`와 `wait`가 각각 번호 하나씩을 쓴다 (`play`는 F:manimlib/scene/scene.py:590,594, `wait`는 :605,621에서 `pre_play`/`post_play`를 호출한다). 번호는 0부터 센다.
- `-n a`는 a번부터 끝까지, `-n a,b`는 a번 이상 b번 미만이다. b번의 `pre_play`에서 `EndScene`이 난다 (F:manimlib/scene/scene.py:450-458).
- a번 전까지는 skip으로 실행한다 (F:manimlib/scene/scene.py:127-128). 객체 배치는 맞지만, skip된 `play`마다 `dt` 업데이터가 run_time만큼 두 번 불리므로 시간 업데이터가 있으면 a번 시점의 상태가 전체 렌더와 다르다 (§7 마지막 항목) [실행확인].
- 파일명은 `<Scene>_a.mp4`, `<Scene>_a_b.mp4`다 (F:manimlib/scene/scene_file_writer.py:109-115). 전체 렌더 결과 `<Scene>.mp4`를 덮어쓰지 않는다.
- 시험 씬은 0.5s, 1s, 1.5s 애니메이션 다음에 `wait(2)`를 둔 것이다 (전체 5s). 결과:

| 명령 | 결과 |
|---|---|
| `-n 2` | `A_2.mp4` 3.5s (2번과 3번) |
| `-n 1,3` | `A_1_3.mp4` 2.5s (1번과 2번) |
| `-n 0` | `A_0.mp4` 5s (전체지만 이름이 다르다) |
| `-n 10` (범위 밖) | exit 0인데 `A_10.mp4`가 261바이트이고 영상 스트림이 없다 |
| `-sw -n 0,2` | `A_0_2.png`, 2번 애니메이션 직전 상태 (그 뒤에 나오는 원이 없다) |

### 3.3 씬 선택 (`timeout 20`, stdin `</dev/null`) [실행확인]

| 상황 | 결과 |
|---|---|
| 씬 1개, 이름 없음 | 그 씬을 렌더, exit 0 |
| 씬 1개, 틀린 이름 | 그래도 그 씬을 렌더, exit 0 |
| 씬 2개, 이름 없음 | `1: A / 2: B` 목록과 `Select which scene to render` 프롬프트가 나온다. EOF면 exit 1 |
| 씬 2개, 틀린 이름 | `ERROR No scene named Nope found` 뒤에 같은 프롬프트, exit 1 |
| 씬 2개, stdin으로 `2` | B를 렌더 |
| 모듈에 `SCENES_IN_ORDER = [Q]` | 후보가 그 목록으로 바뀐다 (F:manimlib/extract_scene.py:116-117). 항목이 하나뿐이면 `P`를 지정해도 `Q`를 렌더한다 |

- 후보는 `__module__`이 그 파일의 모듈 이름으로 **시작하는** `Scene` 하위 클래스다 (F:manimlib/extract_scene.py:35, 접두사 비교). 그래서 `main.py`가 import한 `other.py`의 씬은 빠지지만 `main_parts.py`의 씬은 후보에 들어간다 [실행확인].
- `manimgl`은 스크립트 폴더도 cwd도 `sys.path`에 넣지 않는다 (F:manimlib/module_loader.py:40-49). 옆 파일을 import하려면 `PYTHONPATH=.`를 준다. 주지 않으면 `ModuleNotFoundError`로 exit 1이다 [실행확인].

### 3.4 종료 코드 [실행확인]

| 상황 | exit | 남는 파일 |
|---|---|---|
| 정상 | 0 | 결과 파일 |
| `construct()` 안 예외 (`-w`, `-sw`, `--prerun` 모두) | 1, traceback | `-w`면 `videos/<Scene>_temp.mp4`가 남는다 (`--prerun`이면 prerun 단계에서 실패하므로 남지 않는다). **이전 `<Scene>.mp4`는 지워지지 않고 그대로 남는다** |
| 모듈 import 오류 (`ModuleNotFoundError`) | 1 | 없음 |
| 씬 여러 개 중 뒤 씬이 실패 | 1 | 앞 씬 결과와 실패한 씬의 `_temp.mp4`. `--prerun`이면 모든 씬의 prerun이 렌더보다 먼저 돌므로 (F:manimlib/extract_scene.py:81-85,106-109) 앞 씬 결과도 생기지 않는다 [실행확인] |
| 설정에 모르는 키 (§5) | 1, `TypeError` | 없음 |
| `-c` 잘못된 색, 모르는 플래그 | 2 | 없음 |
| 씬 선택 프롬프트 + EOF | 1 | 없음 |
| `--config_file` 경로 없음, `-n` 범위 밖 | **0** | 설정은 무시된다 / 빈 mp4가 생긴다 |

- 예외는 `Scene.run`에서 `EndScene`과 `KeyboardInterrupt`만 잡는다 (F:manimlib/scene/scene.py:155-164). 나머지는 그대로 올라가 프로세스가 실패한다.
- Ctrl-C로 끊으면 `_temp` 파일을 최종 이름으로 옮기지 않고 정상 종료 경로를 탄다 (F:manimlib/scene/scene.py:160-164, F:manimlib/scene/scene_file_writer.py:298-301). 소스 근거이며 종료 코드는 확인하지 않았다.
- 스크립트에서는 **결과 파일이 있는지가 아니라 종료 코드로** 성공을 판정한다. 실패해도 예전 결과 파일이 남아 있기 때문이다.

### 3.5 출력 스트림 [실행확인]

- 배너 `ManimGL v1.7.2`와 rich 로그(`File ready at …`)는 stdout으로, tqdm 진행 바는 stderr로 나온다 (F:manimlib/logger.py:10).
- 진행 바는 `\r`로 줄을 갱신한다. grep하기 전에 `tr '\r' '\n'`을 거친다.
- rich가 터미널 폭에 맞춰 경로를 여러 줄로 자른다. `COLUMNS=400`을 주면 한 줄로 나온다.
  - 그래도 경로는 파싱하지 말고 §4의 규칙으로 계산하는 편이 낫다.
- `--prerun`이 없으면 총 프레임 수를 모르므로 진행 바가 `15it`처럼 개수로만 나온다.

## 4. 출력 레이아웃

| 항목 | 규칙 | 근거 |
|---|---|---|
| 폴더 | `--video_dir` > `<directories.base>/videos`. 기본 base는 `""`라 cwd 기준 `videos/`다. 없으면 만든다 | F:manimlib/config.py:240-244,393, F:manimlib/utils/file_ops.py:20-23 [실행확인] |
| 영상 | `<Scene>.mp4` (기본), `.mov` (`-t`), `.gif` (`-i`) | F:manimlib/config.py:371-378 [실행확인] |
| 마지막 프레임 | `<Scene>.png` (`-sw`). `-t`가 없어도 RGBA PNG이고 알파는 255다 | `png_mode`는 저장만 하고 읽지 않는다 (F:manimlib/config.py:281, F:manimlib/scene/scene_file_writer.py:55). `Camera.get_image`가 RGBA를 쓴다 (F:manimlib/camera/camera.py:149-154) [실행확인] |
| `-n` | `<Scene>_a[_b].<ext>` | §3.2 |
| `--file_name X` | `X.<ext>`. 마지막 `.` 뒤를 확장자로 바꾼다 | §2 |
| `--subdivide` | `<Scene>/00000.mp4` … (애니메이션 번호) | §2 |
| 쓰는 중 | `<이름>_temp.<ext>`에 쓰고, 끝나면 `shutil.move`로 최종 이름으로 옮긴다 | F:manimlib/scene/scene_file_writer.py:205,299 |
| 덮어쓰기 | 묻지 않고 덮어쓴다. ffmpeg에 `-y`를 주고 `move`로 교체한다. 다시 렌더하면 mtime과 길이가 바뀐다 | F:manimlib/scene/scene_file_writer.py:215,299 [실행확인] |
| `-a --file_name X` | 모든 씬이 같은 `X.<ext>`를 써서 서로 덮어쓴다 | F:manimlib/scene/scene_file_writer.py:104-105, 소스 근거 |

`directories.mirror_module_path: True` (기본 False, F:manimlib/default_config.yml:15) [실행확인]
- `removed_mirror_prefix`가 없으면 `TypeError: startswith first arg must be str or a tuple of str, not Dict`로 실패한다 (F:manimlib/config.py:396). 기본 yml에 그 키가 없기 때문이다.
- 스크립트 절대경로가 prefix로 시작하면 `videos/<나머지 경로에서 .py 뺀 것>/<Scene>.png`가 된다. 예: `videos/w/one/Only.png`.
- prefix와 맞지 않으면 `videos/<파일 stem>/<Scene>.png`가 된다 (F:manimlib/config.py:394-401).

`directories.base: outbase`면 `outbase/videos/`에 쓴다 [실행확인]. 이미지·소리 검색 폴더(`raster_images`, `vector_images`, `sounds`)도 base 기준이다 (F:manimlib/default_config.yml:24-29, F:manimlib/utils/images.py:20,28, F:manimlib/utils/sounds.py:14).

## 5. 설정 병합

순서 (뒤가 이긴다):

1. 패키지의 `manimlib/default_config.yml` (F:manimlib/config.py:34)
2. `custom_config.yml`. **cwd에서만** 찾는다. 상대 경로 `open("custom_config.yml")`이기 때문이다 (F:manimlib/config.py:37). 스크립트 옆에 두고 다른 폴더에서 실행하면 무시된다 [실행확인]
3. `--config_file` (F:manimlib/config.py:38). custom_config보다 우선한다 [실행확인]
4. CLI 플래그. `update_*_config`가 덮어쓴다 (F:manimlib/config.py:43-49). custom_config의 해상도 640x360보다 `-l`이 이긴다 [실행확인]
5. 씬 클래스 속성 `default_camera_config` / `default_file_writer_config`. **CLI보다 우선한다** (F:manimlib/scene/scene.py:58-59,89-98). `default_camera_config = dict(background_color="#00FF00", fps=10)`인 씬은 `-c "#0000FF" --fps 24`를 줘도 초록 배경 10fps로 나온다 [실행확인]

병합은 키 단위 재귀 병합이다 (F:manimlib/utils/dict_ops.py:5).

모르는 키 [실행확인]:

| 위치 | 결과 |
|---|---|
| 최상위 (`foo: 1`), `directories` 아래 새 키 | 무시 |
| `scene:` 아래 (예: upstream `invert_zoom_scroll`) | `TypeError: Scene.__init__() got an unexpected keyword argument`, exit 1 |
| `camera:` 아래 (upstream `bundle_draws`, `draw_together`) | `TypeError: Camera.__init__() …`, exit 1 |
| `file_writer:` 아래 (upstream `crf`) | `TypeError: SceneFileWriter.__init__() …`, exit 1 |
| `tex.template: nosuch` | `WARNING Cannot recognize template nosuch, falling back to 'default'.` 후 정상 렌더 (F:manimlib/utils/tex_file_writing.py:24-26) |
| `window:` 아래 | 창 모드에서 `Window(**manim_config.window)`로 전달된다 (F:manimlib/__main__.py:31). 소스 근거로는 같은 TypeError가 날 것이다 |

`crf`, `bundle_draws`, `draw_together`, `invert_zoom_scroll`은 upstream에만 있다 (U:manimlib/scene/scene_file_writer.py:52, U:manimlib/default_config.yml:56,59,87). upstream용 설정 파일을 그대로 쓰면 렌더가 시작되지 않는다.

## 6. 캐시

| 무엇 | 어디 | 근거 |
|---|---|---|
| Tex→SVG, Text(markup)→SVG 결과 | `diskcache`이고, `directories.cache`가 비어 있으면 `appdirs.user_cache_dir("manim")`을 쓴다. Windows에서는 `%LOCALAPPDATA%\manim\manim\Cache\cache.db`다. 모든 프로젝트가 같은 캐시를 쓴다. 크기 한도 1GB | F:manimlib/utils/cache.py:17-18, F:manimlib/utils/directories.py:17-18, F:manimlib/utils/tex_file_writing.py:84, F:manimlib/mobject/svg/text_mobject.py:53-54 [실행확인 경로] |
| 캐시 키 | 함수 이름 + 인자 전체의 문자열 해시. Tex는 preamble을 포함한 전체 문서, compiler, 진행 메시지(`Writing …`)가 인자다 | F:manimlib/utils/cache.py:24, F:manimlib/utils/tex_file_writing.py:81,85 |
| LaTeX 작업 폴더 | `<base>/latex_cache/` = **cwd의 `latex_cache/`** (`working.tex/.dvi/.log/.aux`). 캐시에 없을 때만 만든다 | F:manimlib/default_config.yml:35, F:manimlib/utils/tex_file_writing.py:97-101. 처음 렌더할 때 생겼고, 지운 뒤 다시 렌더할 때는 생기지 않았다 [실행확인] |
| Text SVG 임시 파일 | `%TEMP%/<hash>.svg` | F:manimlib/mobject/svg/text_mobject.py:78 |

`--clear-cache` [실행확인]
- `diskcache`만 비운다 (F:manimlib/utils/cache.py:33-34). `latex_cache/` 폴더는 건드리지 않는다.
- 렌더 명령에 붙여 쓴다: `manimgl main.py S -sw --clear-cache`. 그러면 Tex를 다시 컴파일해서 `latex_cache/`가 다시 생긴다.
- `--clear-cache`만 단독으로 쓰면 지운 뒤 `BlankScene` 창과 IPython을 띄운다.
- 캐시가 전역이라 다른 프로젝트의 캐시도 함께 사라진다. 그 프로젝트들은 다음 렌더 때 다시 컴파일한다.
- 쓸 때: 빈 SVG처럼 잘못된 결과가 캐시에 남은 경우 (SKILL.md §8 cm-super).

## 7. 레시피 (플러그인 워크플로)

모두 `cd <프로젝트>/src/<영상>`에서 실행한다. 출력이 cwd의 `videos/`로 가기 때문이다. 자동화할 때는 `</dev/null`을 붙인다. 씬이 여러 개인 파일에서 씬 이름을 빠뜨리거나 틀려도 프롬프트에서 멈추지 않고 exit 1로 끝난다 (씬이 1개면 그 씬을 렌더한다, §3.3).

```bash
# 마지막 프레임 확인 -> videos/<Scene>.png
uv run manimgl main.py <Scene> -sw </dev/null

# 중간 상태 확인: k번 애니메이션 직전 -> videos/<Scene>_0_k.png
uv run manimgl main.py <Scene> -sw -n 0,k </dev/null

# 초안 854x480 30fps -> videos/<Scene>.mp4
uv run manimgl main.py <Scene> -w -l </dev/null

# 최종 1920x1080 30fps -> 같은 videos/<Scene>.mp4를 덮어쓴다
uv run manimgl main.py <Scene> -w </dev/null

# 한 씬만 다시 렌더: 다른 씬과 같은 품질 옵션으로, 그 씬 이름만 준다
uv run manimgl main.py <Scene> -w -l </dev/null || echo "FAILED: videos/<Scene>.mp4는 예전 것"

# 구간만 반복 확인 (전체 결과를 덮어쓰지 않는다) -> videos/<Scene>_3_6.mp4
uv run manimgl main.py <Scene> -w -l -n 3,6 </dev/null

# 여러 씬 한 번에 (반드시 -w 포함)
uv run manimgl main.py Intro Body Outro -w -l </dev/null
```

- 성공 판정은 종료 코드로 한다. 실패하면 `<Scene>_temp.mp4`와 예전 `<Scene>.mp4`가 남는다 (§3.4).
- `ffmpeg -f concat … -c copy`로 이어 붙일 씬들은 해상도, fps, 코덱이 같아야 한다. 모두 같은 옵션(`-w -l` 또는 `-w`)으로 렌더한다.
- 쓰지 않을 것: `-p`(멈춤), `-s` 단독, `-ql`/`-sql`(`-w` 없음), `-a` 단독, `-o`/`--finder`(외부 플레이어가 열린다).
- 투명 배경 소스가 필요하면 `-w -t` → `.mov` (ProRes, `yuva444p12le`)다. 이 파일은 mp4 concat에 섞을 수 없다.
- `-s`에서는 `play` 하나마다 `dt` 업데이터가 dt=run_time으로 **두 번** 불린다. 진행 루프의 `update_frame`에서 한 번(F:manimlib/scene/scene.py:474-475,557-564), `finish_animations`에서 한 번이다(F:manimlib/scene/scene.py:571-572). `wait`는 한 번이다. 그래서 시간 업데이터는 `-sw`에서 영상보다 더 많이 진행되고, 마지막 프레임이 영상의 마지막 프레임과 다를 수 있다 [실행확인: `play(run_time=1)` 동안 `increment_value(dt)` 누적이 `-sw` 2.0, `-w` 1.0].
