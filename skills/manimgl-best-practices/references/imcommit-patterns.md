# imcommit 관례 (패턴 요약)

## 출처와 범위

- 출처: `CodingVillainKor/manimgl-imcommit` @ `a2fe49f4284082ce6c3627cd26e5952cd1d01bb6`
- 범위: 영상 폴더 30개, 씬 클래스 127개. `src/curseofknowledge/main copy.py` 사본을 포함해 .py 파일 31개다
- 이 저장소에는 LICENSE 파일이 없다. 그래서 코드는 옮기지 않고 패턴과 수치만 적는다.
- 수치는 `src/**/*.py`를 grep으로 센 값이다. 경로는 저장소 루트 기준이다.

## 프로젝트 구조

- **루트 `pyproject.toml`**
  - `requires-python ==3.10.18`
  - 의존성: `manimgl`(포크 git, rev 고정 없음), `raenimgl`(git), `trimesh`, `pywavefront` 등. 위치는 `[tool.uv.sources]`.
  - 이 플러그인의 setup.sh는 같은 구성에 **커밋을 고정**한다.
- **`init_project.py --name <영상>`**: `src/<영상>/main.py`를 만든다.
  - 템플릿 내용은 import 두 줄, 시드 고정, `self.embed()` 다음에 `##` 블록 하나가 있는 씬 하나다 (init_project.py:4-17).
  - README의 `uv init_project.py`는 오타이고, 실제로 동작하는 것은 `uv run init_project.py --name <영상>`이다.
- **실행**: `cd src/<영상>; uv run manimgl main.py [씬]` (README.md). 결과는 `src/<영상>/videos/`에 쌓인다.
- **`_mhelper.py` (20줄)**: IPython embed 안에서 실행하는 도구다.
  - 파일의 마지막 `##` 줄부터 끝까지를 클립보드에 복사한다 (pyperclip).
  - 그다음 `checkpoint_paste()`를 호출한다 (_mhelper.py:16-20).
- **`_mupdater.py` (79줄)**: `construct` 안의 `self.embed()`를 마지막 `##` 블록 바로 앞으로 옮긴다 (_mupdater.py:58-70). 에디터 작업(task)으로 돌리는 용도다.
- 이 대화형 흐름(embed, checkpoint)은 창이 있는 미리보기 전용이다.
  - `-w` 렌더에서는 `self.embed()`가 아무 일도 하지 않는다 (포크 manimlib/scene/scene.py:208).
  - 이 플러그인의 워크플로는 대화형 흐름 대신 `-sw` 마지막 프레임 확인을 쓴다.

## 씬 나누기

- 영상 하나는 `main.py` 하나다. 클래스 수는 파일당 1~8개이고 중앙값은 4다. 클래스는 서사 순서대로 위에서 아래로 놓는다.
- **127개 클래스 전부 `(InteractiveScene, Scene2D)`** (raenimgl)를 상속한다.
  - `Scene3D`, `ThreeDScene`, `MINT` 사용: 0개 파일
  - `PythonCode` 사용: 1개 파일
- 각 클래스는 독립적으로 렌더된다. 이전 클래스의 마지막 상태가 필요하면 그 클래스 안에서 다시 만든다.
- `construct` 안은 `## <내레이션/의도 한 줄>` 주석으로 블록을 나눈다 (예: src/bondinterest/main.py:12,31,45). 한 블록은 내레이션 한 문장에 대응한다.
- 파일 머리: `from manimlib import *`, `from raenimgl import *`, `seed(41)`, `np.random.seed(41)` (init_project.py:5-10).

## 재생 래퍼 (raenimgl)

- `playw`: play 다음에 wait(1)
- `playwl`: LaggedStart 버전
- `addw`: add 다음에 wait
- `self.cf`는 `self.frame`이다.
- 사용 예: src/bondinterest/main.py:91 (`playwl`), :308 (`addw`), :127 (`self.cf.save_state`)
- 래퍼 없이 같은 효과를 내려면 `self.play(...)` 다음에 `self.wait()`를 쓰면 된다.

## 레이아웃

- 배치는 `next_to`, `arrange`, `align_to`로 한다.
- `buff=` 사용 빈도:
  - 0.1: 409회
  - 0.2: 235회
  - 0.5: 222회
  - 0.3: 105회
- 화면 하나에 다 넣지 않는다. 넓은 캔버스에 영역을 두고 카메라(`self.cf`/`self.frame`)를 옮긴다.
- 2D 씬에서 카메라를 기울이는 경우는 18개 파일에서 `reorient(`로 나온다 (예: src/bondinterest/main.py:129, src/CFMvsDiffusion/main.py:323).
  - 읽어야 하는 텍스트는 카메라 φ와 비슷한 각도만큼 `axis=RIGHT`로 돌려 카메라를 보게 한다 (src/bondinterest/main.py:132,140,150).

## 색

- 이름 있는 상수만 쓴다. hex 리터럴은 0회다.
- 빈도와 쓰임:

| 상수 | 횟수 | 쓰임 |
|---|---|---|
| `GREY_B` | 274 | 보조 설명 |
| `RED` | 262 | 오답, 문제 |
| `GREEN` | 229 | 정답, 결과 |
| `BLUE` | 159 | |
| `GREY_C` | 88 | |
| `YELLOW` | 77 | 강조 |
| `PURE_RED` | 45 | |

- `Text`/`Tex` 색은 생성 뒤 `.set_color(…)`로 준다 (150회). 생성자 `color=`는 6회뿐이다.
  - 포크에서는 `color=`가 무시된다 (SKILL.md §6).
- 흐리게 하는 방법은 둘이다.
  - `set_opacity(0.2)` (예: src/bondinterest/main.py:500)
  - 반투명 오버레이(raenimgl `self.overlay`)를 깔고, 남길 것을 `set_z_index(오버레이 + 1)`로 올려 다시 `add`한다 (src/bondinterest/main.py:122-150)

## 타이밍

- `run_time`:
  - 0.5: 185회 (최다)
  - 0.7: 58회
  - 0.75: 41회
  - 3: 29회
- `lag_ratio`:
  - 0.5: 58회
  - 0.3: 24회
  - 0.2: 17회
- `rate_func`는 대부분 기본값(smooth)이다.
- 대기는 주로 `playw`의 기본 wait(1)이다.

## 한글

- 한글 `Text`는 90회 나오고, 그중 `font=`를 지정한 것은 0회다. 포크 기본 폰트 Noto Sans KR을 그대로 쓴다.
- Tex/TexText 안의 한글: 0회. `TexText`는 아예 쓰지 않는다 (0개 파일).
- 한글과 수식을 같이 쓸 때는 `VGroup(Text(…), Tex(…)).arrange(RIGHT)`로 나란히 붙인다 (src/floatingpoint/main.py:1501,1603).
- Tex 일부를 고를 때는 글리프 인덱스 슬라이스를 쓴다.
  - 포크의 문자열 선택자(`tex["..."]`, `t2c`)도 동작한다 [실행확인, examples/tex.py].
