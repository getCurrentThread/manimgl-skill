# imcommit 관례 (패턴 요약)

## 출처와 범위

- 출처: `CodingVillainKor/manimgl-imcommit` @ `a2fe49f4284082ce6c3627cd26e5952cd1d01bb6`
- 이 저장소에는 LICENSE 파일이 없다. 그래서 코드는 옮기지 않고 패턴과 수치만 적는다.
- 범위: 영상 폴더 30개. `src/` 아래 `.py` 파일은 35개다.
  - 영상별 `main.py` 30개, 사본 `src/curseofknowledge/main copy.py` 1개, 보조 스크립트 4개 (`src/CLIP/prepare_images.py`, `src/dunder_all/import.py`, `src/dunder_all/piui.py`, `src/turboquant2/example.py`).
  - 수치는 사본을 뺀 34개 파일에서 셌다. 씬 클래스는 125개다.
- 방법: Python `ast`로 셌다. 여러 줄에 걸친 호출도 센다.
  - `buff=`, `run_time=`, `lag_ratio=`는 그 이름의 키워드 인자에 숫자 리터럴을 준 경우만 센다 (`h_buff` 등 제외).
  - 체인 `.set_color`는 `Text(...).next_to(...).set_color(...)`처럼 호출 체인의 뿌리가 그 생성자인 경우다.
  - 경로는 저장소 루트 기준이다.

## 프로젝트 구조

- **루트 `pyproject.toml`**
  - `requires-python ==3.10.18`
  - 의존성: `manimgl`(포크 git, rev 고정 없음), `raenimgl`(git), `trimesh`, `pywavefront` 등. 위치는 `[tool.uv.sources]`.
  - 이 플러그인의 setup.sh는 manimgl 포크(+ trimesh, pywavefront, `--with-raenimgl`이면 raenimgl)를 **커밋 고정**으로 설치한다. imcommit 구성을 그대로 복제하지는 않는다.
    - Python은 3.10이고, matplotlib·torchvision은 넣지 않는다.
    - 이미 포크를 rev 없이 가리키는 pyproject는 고치지 않고 경고만 한다.
- **`init_project.py --name <영상>`**: `src/<영상>/main.py`를 만든다.
  - 템플릿 내용은 import 세 줄(`manimlib`, `raenimgl`, `random.seed`), 시드 고정, `self.embed()` 다음에 `##` 블록 하나가 있는 씬 하나다 (init_project.py:4-17).
  - README의 `uv init_project.py`는 오타이고, 실제로 동작하는 것은 `uv run init_project.py --name <영상>`이다.
- **실행**: `cd src/<영상>; uv run manimgl main.py [씬]` (README.md). 결과는 `src/<영상>/videos/`에 쌓인다.
- **`_mhelper.py` (20줄)**: IPython embed 안에서 실행하는 도구다.
  - 파일의 마지막 `##` 줄부터 끝까지를 클립보드에 복사한다 (pyperclip).
  - 그다음 `checkpoint_paste()`를 호출한다 (_mhelper.py:16-20).
- **`_mupdater.py` (79줄)**:
  - 파일 안 모든 `construct`의 `self.embed()`를 지우고, 파일 전체의 마지막 `##` 줄 바로 앞에 `self.embed()` 하나를 넣는다 (_mupdater.py:55-70).
  - 대상 파일은 명령행 인자로 받는다 (:77-79).
  - VS Code 작업(task)으로 현재 파일에 돌리는 용도다 (src/floatingpoint/.vscode/tasks.json의 `mupdate`).
- 이 대화형 흐름(embed, checkpoint)은 창이 있는 미리보기 전용이다.
  - `-w` 렌더에서는 `self.embed()`가 아무 일도 하지 않는다 (포크 manimlib/scene/scene.py:208).
  - 이 플러그인의 워크플로는 대화형 흐름 대신 `-sw` 마지막 프레임 확인을 쓴다.

## 씬 나누기

- 영상 하나는 `main.py` 하나다.
  - 클래스 수는 파일당 1~8개이고 중앙값은 4다. 분포: 1개 4파일, 2개 4, 3개 5, 4개 4, 5개 3, 6개 5, 7개 3, 8개 2.
  - 클래스는 서사 순서대로 위에서 아래로 놓는다.
- **125개 클래스 전부 `(InteractiveScene, Scene2D)`** (raenimgl)를 상속한다.
  - `Scene3D`, `ThreeDScene`, `MINT` 사용: 0개 파일
  - `PythonCode` 사용: 1개 파일
- 각 클래스는 독립적으로 렌더된다. 이전 클래스의 마지막 상태가 필요하면 그 클래스 안에서 다시 만든다.
- `construct` 안은 `## <짧은 라벨 또는 내레이션 한 줄>` 주석으로 블록을 나눈다 (예: src/bondinterest/main.py:12,31,45).
  - `##` 줄은 1111개다. 대부분은 구현 메모(`## nl`, `## lines`, `## intro`)이고, 일부만 내레이션 문장이다.
- 파일 머리: `from manimlib import *`, `from raenimgl import *`, `from random import seed`, `seed(41)`, `np.random.seed(41)` (init_project.py:5-10).

## 재생 래퍼 (raenimgl)

- `playw`: play 다음에 wait(1)
- `playwl`: LaggedStart 버전
- `addw`: add 다음에 wait
- `self.cf`는 `self.frame`이다.
- 사용 예: src/bondinterest/main.py:91 (`playwl`), :308 (`addw`), :127 (`self.cf.save_state`)
- 래퍼 없이 같은 효과를 내려면 `self.play(...)` 다음에 `self.wait()`를 쓰면 된다.

## 레이아웃

- 배치는 `next_to`, `arrange`, `align_to`로 한다.
- `buff=` 사용 빈도 (상위 5):
  - 0.1: 378회
  - 0.2: 222회
  - 0.5: 206회
  - 0.05: 93회
  - 0.15: 90회
- 화면 하나에 다 넣지 않는다. 넓은 캔버스에 영역을 두고 카메라(`self.cf`/`self.frame`)를 옮긴다.
- `reorient(`는 17개 파일에 나온다.
  - 그중 16개 파일이 φ ≠ 0으로 2D 씬을 기울인다 (예: src/bondinterest/main.py:129, src/CFMvsDiffusion/main.py:341).
  - `reorient(0, 0, 0, center, height)`는 기울이지 않고 이동·확대할 때도 쓴다 (src/CFMvsDiffusion/main.py:323).
  - 기울인 영역의 텍스트와 평면 요소(수직선, 눈금)는 카메라 φ와 같은 각도만큼 `axis=RIGHT`로 돌려 카메라를 보게 한다 (텍스트 src/bondinterest/main.py:132, 수직선 :140, 눈금 :150).

## 색

- 색은 거의 이름 있는 상수로 준다. hex 리터럴은 0회다.
  - 그 밖에는 계산된 색만 있다: `interpolate_color` 52회, `random_color()` 29회.
- 빈도 (이름 있는 상수, 상위 13):

| 상수 | 횟수 | 쓰임 |
|---|---|---|
| `GREY_B` | 270 | 보조 설명 |
| `RED` | 255 | 오답, 문제 |
| `GREEN` | 227 | 정답, 결과 |
| `BLUE` | 154 | |
| `YELLOW_B` | 86 | |
| `GREY_C` | 86 | |
| `RED_B` | 78 | |
| `YELLOW` | 77 | 강조 |
| `BLACK` | 72 | |
| `GREY_A` | 69 | |
| `WHITE` | 69 | |
| `ORANGE` | 57 | |
| `PURE_RED` | 44 | |

- 쓰임 근거: src/CLIP/main.py:409-411,484 (오답 RED, 정답 GREEN), src/justgrpo/main.py:738-741.
- `Text`/`Tex` 색은 생성 뒤 체인 `.set_color(…)`로 준다: `Text` 376회, `Tex` 152회 (raenimgl `Words` 64회).
  - 생성자 `color=`는 10회뿐이고 모두 `Text`다.
  - 포크에서는 `Text`/`Tex`의 `color=`가 무시된다 (SKILL.md §6).
- 흐리게 하는 방법은 둘이다.
  - `set_opacity(0.2)` (예: src/bondinterest/main.py:500)
  - 반투명 오버레이(raenimgl `self.overlay`)를 깔고, 남길 것을 `set_z_index(오버레이 + 1)`로 올려 다시 `add`한다 (src/bondinterest/main.py:122-150)

## 타이밍

- `run_time` (상위 5):
  - 0.5: 179회 (최다)
  - 0.7: 58회
  - 0.75: 41회
  - 3: 25회
  - 1.5: 21회
- `lag_ratio` (상위 5):
  - 0.5: 57회
  - 0.3: 24회
  - 0.2: 15회
  - 0.1: 12회
  - 0.7: 10회
- `rate_func`는 대부분 기본값(smooth)이다.
- 대기는 주로 `playw`의 기본 wait(1)이다.

## 한글

- 한글 `Text`는 90회 나오고, 그중 `font=`를 지정한 것은 1회다 (src/gen_model/main.py:30-32, 기본값과 같은 `"Noto Sans KR"`). 사실상 포크 기본 폰트를 그대로 쓴다.
- 한글 내레이션은 raenimgl `Words`(Text 하위 클래스)로도 쓴다.
  - 한글 `Words` 41회 중 14회는 `font=`를 지정한다. 13회가 `"Noto Serif KR"`, 1회가 `"Noto Sans KR"`이다 (예: src/bondinterest/main.py:85-87).
- Tex/TexText 안의 한글: 0회. `TexText`는 아예 쓰지 않는다 (0개 파일).
- 한글과 수식을 같이 쓸 때는 `VGroup(Text(…), Tex(…)).arrange(RIGHT)`로 나란히 붙인다 (src/floatingpoint/main.py:1501,1603).
- Tex 일부를 고를 때는 글리프 인덱스 슬라이스를 쓴다.
  - 포크의 문자열 선택자(`tex["..."]`, `t2c`)도 동작한다 [실행확인, examples/tex.py].

## 다시 세기

수치는 아래 조건의 AST 집계와 같아야 한다. 스크립트는 플러그인에 넣지 않았다.

- 대상: `src/**/*.py` 중 `main copy.py`를 뺀 것
- 클래스: 모듈 최상위 `ClassDef`
- 한글 `Text`: 첫 위치 인자가 문자열 상수(또는 f-string의 상수 부분)이고 `[가-힣]`을 포함
- 색 상수: `ast.Name` 중 manimlib 색 이름 패턴(`GREY_B`, `RED`, `PURE_RED` 등)
