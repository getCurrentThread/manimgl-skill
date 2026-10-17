# 내적은 왜 cos θ를 품고 있을까 (`dot_product`)

> Worked example of `templates/scenes.md`. Every block was implemented in the fork and rendered with `-sw` and `-w -l` (exit 0; without narration the scenes ran 14 s, 16.5 s, 14.5 s). Story beats adapted from the dot-product example in adithya-s-k/manim_skill @cef0450 `skills/manim-composer/references/scene-examples.md` (MIT, [LICENSE-manim_skill](../references/LICENSE-manim_skill)), rewritten for this template and the fork.

- **Audience**: high-school vectors. Can compute a₁b₁ + a₂b₂, has not linked it to the angle
- **Core idea (one sentence)**: 내적은 b를 a 위로 내린 그림자의 길이에 |a|를 곱한 값이다
- **Hook**: 곱하고 더했을 뿐인데, 왜 각도(cos θ)가 나올까?
- **Aha moment**: `Projection` → `## 그림자 길이 × |a|, 이것이 내적입니다`
- **Misconception**: none. The last `Projection` block (same lengths, θ → 90°, shadow and dot product → 0) is a check after the aha
- **Narrative pattern**: Mystery → Investigation → Resolution; `Components` is Two Perspectives
- **Color roles** (named constants, fixed for the whole video, black background): BLUE a, GREEN b, YELLOW emphasis (cos θ, shadow, results), GREY_B helper lines, GREY_D grid
- **Facts and numbers on screen**: a = (3, 1), b = (1, 2). a·b = 3·1 + 1·2 = 5; |a| = √10, |b| = √5; cos θ = 5/√50 = 1/√2, so θ = 45°; shadow |b| cos θ = √2.5 ≈ 1.58 (computed by hand)
- **Length target**: 3 scenes × 15–20 s
- **Narration**: none
- **Uses Tex**: yes (formulas and vector labels; Korean stays in Text)
- **Tex strings**: R"\vec a \cdot \vec b = a_1 b_1 + a_2 b_2 = |\vec a|\,|\vec b|\,\cos\theta" (1–3), R"\vec a", R"\vec b" (1), R"|\vec b|\,\cos\theta" (2), R"(3, 1)", R"(1, 2)", R"= 3 \cdot 1 + 1 \cdot 2 = 5", R"= \sqrt{10}\,\sqrt{5}\cos 45^\circ = 5" (3). No Korean in Tex

## Scene list (narrative order = main.py class order = concat.txt order)

### 1. `Question` (~15 s)
- **Purpose**: pose the question: why does an angle appear?
- **Blocks** (1:1 with `## …` comments):
  - `## 두 벡터 a와 b가 있습니다`: a (BLUE) and b (GREEN) grow from one origin; labels \vec a, \vec b
  - `## 내적은 성분끼리 곱해서 더하죠`: Write the left half of the formula at the top
  - `## 그런데 이 값은 |a||b|cos θ와 같습니다`: Write the right half; Indicate cos θ (YELLOW)
  - `## 곱하고 더했을 뿐인데, 왜 각도가 나올까요?`: Text "왜 각도가 나올까?" (YELLOW) under the formula, then fade it out with the labels
- **On-screen elements**: 2 `Arrow(buff=0)` placed with a hidden NumberPlane's `c2p`, Tex labels, Tex formula, Text question
- **Technique**: Highlight (Indicate)
- **End state**: a, b, the full formula at the top
- **Next**: `Projection` rebuilds a, b and the formula at the same place (same plane coordinates); nothing moves at the cut

### 2. `Projection` (~20 s)
- **Purpose**: 내적 = 그림자 길이 × |a| (the aha)
- **Blocks**:
  - `## b를 a 위로 수직으로 내려 봅니다`: GREY_B DashedLine from b's tip to its foot on a, plus an Elbow mark
  - `## 이 그림자의 길이가 |b| cos θ입니다`: YELLOW shadow on a; Brace along it with Tex |\vec b|\,\cos\theta
  - `## 그림자 길이 × |a|, 이것이 내적입니다`: FlashAround on |\vec a|\,|\vec b|\,\cos\theta, then wait 1.5 s (slow beat)
  - `## 길이가 같아도 각도가 90°면 내적은 0입니다`: Brace fades; a ValueTracker turns θ 45° → 90° → 45°; b, dashed line, Elbow and shadow follow; the shadow shrinks to a point; helper lines fade out
- **On-screen elements**: a, b, dashed line, Elbow, shadow, Brace + Tex label, formula
- **Technique**: Projection + Elbow (moving version); Brace along a slanted segment; Highlight (FlashAround)
- **End state**: a, b at θ = 45° (b = (1, 2)), formula
- **Next**: `Components` rebuilds a, b and the formula; nothing moves at the cut

### 3. `Components` (~15 s)
- **Purpose**: the component formula gives the same number (two perspectives)
- **Blocks**:
  - `## 좌표 위에 놓아 봅시다`: the NumberPlane (grid restyled with `background_line_style=dict(stroke_color=GREY_D, stroke_width=1)`, since its default BLUE_D grid would hide the BLUE a, F:manimlib/mobject/coordinate_systems.py:641-642) fades in under the vectors; Tex (3, 1), (1, 2) at the tips
  - `## 성분끼리 곱해서 더하면 5`: numbers fly from a_1, b_1, a_2, b_2 in the formula into `= 3 \cdot 1 + 1 \cdot 2 = 5` right of the plane
  - `## 그림자로 계산해도 5, 같은 값입니다`: Write `= \sqrt{10}\,\sqrt{5}\cos 45^\circ = 5` under it; both final 5s turn YELLOW with FlashAround
- **On-screen elements**: NumberPlane, a, b, coordinate labels, formula, two result lines
- **Technique**: Numbers dropping into a formula (`select_part`; the last 5 is index -1); Highlight (FlashAround)
- **End state**: last frame of the video
- **Next**: —

## Assumptions and open decisions (confirm at approval)

- Narration none: the user did not ask for spoken narration (opt-in), so `##` lines are on-screen intent only.
- Standalone video, 3 scenes: the topic is one identity.
- Open: show θ as a number while b turns? Not planned (a `DecimalNumber` needs no LaTeX, but adds clutter).

## Approval

- [ ] User approval (date):
