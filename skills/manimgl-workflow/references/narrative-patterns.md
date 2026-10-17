# Narrative patterns (Plan reference)

Adapted from adithya-s-k/manim_skill @cef0450 `skills/manim-composer/references/narrative-patterns.md` and the "3b1b Style Principles" in its `SKILL.md` (MIT, Copyright (c) 2026 Adithya S Kolavi; license text in [LICENSE-manim_skill](LICENSE-manim_skill)). Changed: steps mapped to this plugin's 15–30 s scenes and 1–8 scenes per video; the 5–30 min pacing table replaced; Korean hooks and narration notes added; imcommit counts added; style principles annotated with fork limits.

- Patterns, example topics, English hooks, combining, emotional arc and style principles are the composer's text, shortened.
- `I:` = manimgl-imcommit @a2fe49f. The imcommit counts come from scene class names and `##` text only (AST over `src/*/main.py`: 30 videos, 125 classes). A class name hints at a role; it does not prove it. Treat the counts as heuristics, not measured story structure.
- "best-practices §N" is a section of [../../manimgl-best-practices/SKILL.md](../../manimgl-best-practices/SKILL.md). `imcommit-patterns.md` is in [../../manimgl-best-practices/references/](../../manimgl-best-practices/references/).

## How to use

- Pick one main pattern. Optionally open with a second one (see Combining).
- Map each step to one 15–30 s scene. A step that needs a second visual takes a second scene.
- Scene 1 reaches the **Hook** within its first ~10 s. The **Aha moment** gets the slowest beat.
- Write the choice in the scenes.md **Narrative pattern** line.

## What imcommit does (heuristic)

- 18 of 30 videos open with a class named `intro`.
- 10 of 30 have a scene named for a wrong idea, a failure or a problem. In 8 a later scene follows, which fits Pattern 4; justgrpo `GRPOfail` (I:src/justgrpo/main.py:785) and CFMvsDiffusion `whydiffusion_notoptimal` (I:src/CFMvsDiffusion/main.py:1278) are the last scenes of their videos:
  - CLIP `naiveApproach` → `naiveBad` → … → `contrastiveLearning` (I:src/CLIP/main.py:85,145,523)
  - bondinterest `misunderstanding` → `realCredit` (I:src/bondinterest/main.py:250,422)
  - floatingpoint `floatFault` → `actualFloat` (I:src/floatingpoint/main.py:388,736)
  - MLA `problem1`, `problem2` → `solvedByRoPENoPE` (I:src/MLA/main.py:418,668,787)
  - The other four: linearAttn `softmaxNotAssociative`, turboquant2 `turboquant_key_problem`, pagedAttn `redundantGPU`, siglip `collapse`.
- Comparison classes (`vs`, `compare`): 4 videos (justgrpo, justgrpo2, linearAttn2, lora1), plus mdlm's paired `ARModel`/`MDLModel`.
- Quiz or question scene: 3 videos (RvsBquiz; CLIP `question` I:src/CLIP/main.py:394; turboquant2 `question`).
- Recap-like last scene: 4 videos (gen_model `conclusion`, floatingpoint `reflectIntro` I:src/floatingpoint/main.py:1202, curseofknowledge `results`, mdlm `MeaningOfT`).
- Numbered series parts: 11 of 30 folders (lora1–2, turboquant1–3, linearAttn/linearAttn2, justgrpo/justgrpo2, clco2–3). turboquant3's first block refers back to the previous video (I:src/turboquant3/main.py:12). For a series part, the hook can start from the previous video.

## Pattern 1: Mystery → Investigation → Resolution

- Steps: puzzling result or paradox → investigate visually → reveal the principle → show how it generalizes.
- Scenes: hook (the puzzle) → 1–2 investigation scenes → principle → generalization (optional).
- Example topics: Euler's identity, Bayes theorem, infinite series paradoxes.
- Hooks: "This equation looks wrong, but it's actually true..." / "Most people get this probability question wrong..."
- Korean hooks: "이 식, 틀려 보이지만 사실 맞습니다." / "대부분 이 문제를 틀립니다. 한번 맞혀 보세요."

## Pattern 2: Build Up → Payoff

- Steps: simple building blocks → combine them → the surprising result → why it works.
- Scenes: one scene per building block → combination → payoff.
- Example topics: Fourier series, neural networks, linear algebra.
- Hooks: "Let's start with something simple..." / "Each piece here is easy, but together they do something remarkable..."
- Korean hooks: "아주 간단한 것부터 시작해 볼게요." / "하나하나는 쉬운데, 합치면 놀라운 일이 생깁니다."

## Pattern 3: Two Perspectives → Unity

- Steps: perspective A (e.g. algebraic) → perspective B (e.g. geometric) → they are the same thing → implications.
- Scenes: A → B → unity, often in one scene with both side by side.
- Example topics: dot product, determinants, complex multiplication.
- Hooks: "There are two ways to think about this..." / "These seem like completely different ideas, but..."
- Korean hooks: "이걸 보는 방법은 두 가지가 있습니다." / "전혀 달라 보이는 두 생각이 사실 같은 겁니다."
- Layout: side by side with `VGroup(left, right).arrange(RIGHT, buff=1)`, or the imcommit wide canvas with `self.frame` moving between regions ([visual-techniques.md](visual-techniques.md) Scene composition).

## Pattern 4: Wrong → Less Wrong → Right

- Steps: common misconception or naive approach → why it fails → refine → correct understanding.
- Scenes: wrong attempt → failure shown → fix. Fill the scenes.md **Misconception** line with the first two.
- Example topics: limits, probability distributions, definitions.
- Hooks: "Your first instinct here is probably wrong..." / "The obvious approach doesn't quite work..."
- Korean hooks: "가장 먼저 떠오르는 방법은… 사실 잘 안 됩니다." / "직관대로 하면 틀립니다."
- Color the wrong attempt RED and the fix GREEN (imcommit roles, best-practices §11).

## Pattern 5: Specific → General

- Steps: solve one concrete example → notice the pattern → abstract the principle → apply it to a new case.
- Scenes: concrete example (real numbers) → pattern → general form.
- Example topics: derivatives, group theory, algorithm analysis.
- Hooks: "Let's work through a specific example..." / "Once you see the pattern here, it shows up everywhere..."
- Korean hooks: "구체적인 숫자로 먼저 해 볼게요." / "이 패턴이 보이면, 어디서나 보입니다."
- Numbers on screen must be correct. Compute them before planning (workflow §1, step 1).

## Pattern 6: History as Narrative

- Steps: the problem as it was first met → the path of discovery → the key insights → the modern view.
- Example topics: calculus, cryptography, quantum mechanics.
- Hooks: "Imagine you're a mathematician in the 1600s..." / "This problem stumped the greatest minds for centuries..."
- Korean hooks: "1600년대의 수학자라고 상상해 보세요." / "이 문제는 수백 년 동안 최고의 수학자들을 괴롭혔습니다."
- Dates, names and quotes are facts on screen. Take them from a source, not from memory.

## Combining patterns

- Mystery hook + Build Up explanation
- Two Perspectives + Specific → General examples
- Wrong → Right + History narrative

## Pacing (replaces the composer's 5–30 min table)

| Video | Hook | Main | Recap |
|---|---|---|---|
| 1–4 scenes | the first ≤ 10 s of scene 1 | the rest | last block of the last scene (optional) |
| 5–8 scenes | scene 1 | scenes 2 … n-1 | last scene (4 of 30 imcommit videos have a recap-like one) |

- imcommit has 1–8 scene classes per video, median 4 (best-practices §11). 15–30 s per scene is this plugin's recommendation, not an imcommit measurement.

## Emotional arc

| Beat | Viewer feels | Where it goes in scenes.md |
|---|---|---|
| Curiosity (opening) | Why should I care? | **Hook** block |
| Confusion (early) | This is harder than it looks | **Misconception** scene, if any |
| Partial clarity (middle) | I'm starting to see... | investigation / build-up scenes |
| Aha moment (climax) | Oh! That's beautiful! | **Aha moment** block |
| Satisfaction (end) | Now I truly understand | recap block or the last End state |

## Style principles (composer, with fork notes)

- **Show, don't just tell**: every concept needs a visual.
- **Progressive revelation**: build complexity gradually; never show everything at once.
- **Visual continuity**: transform objects rather than replacing them.
  - Fork: transforms work only inside one scene (`TransformMatchingTex`/`TransformMatchingStrings`, [visual-techniques.md](visual-techniques.md)). Each class renders on its own, so at a scene boundary the next class rebuilds the previous End state (workflow §2.1). The scenes.md **Next** line plans that cut.
- **Pause for insight**: `self.wait(1~2)` after the aha block. imcommit's `playw` waits 1 s after every play (imcommit-patterns.md).
- **Vary the pace**: fast-fast-SLOW ([visual-techniques.md](visual-techniques.md) Timing).
- **End scenes with resolution**: each scene's End state should look complete.
- **Emphasize elegance**; **connect representations** (algebraic, geometric, intuitive); **embrace abstraction gradually** (concrete first).
- **Pose questions** before revealing answers; **acknowledge difficulty** ("처음엔 헷갈릴 수 있어요"); **celebrate insight**: the aha must feel earned.

## Korean narration

- `##` lines are narration or intent, one sentence per block.
- imcommit: 180 of 1111 `##` lines contain Hangul (19 videos). 74 of the 180 end in `~니다` (polite formal); 15 end in `?`, e.g. "원래 key는 뭐하는 용도였죠?" (I:src/turboquant3/main.py:343); 3 more ask mid-line, as in "이게 무슨 말일까요? 한 번 볼게요" (I:src/turboquant2/main.py:112). Use a rhetorical question at the hook and right before the aha.
- On screen, keep Korean short: nouns and short phrases in `Text`, formulas in `Tex`, joined with `VGroup(...).arrange(RIGHT)` (best-practices §7). The full sentence stays in the `##` line or the voiceover.
- Reuse the same on-screen words across steps. `TransformMatchingStrings` then keeps them in place and morphs only the changed word ([visual-techniques.md](visual-techniques.md) Core principles).
- Voiceover budget: with the Windows SAPI Korean voice, lines of 10, 16 and 17 syllables took 2.63, 3.79 and 4.21 s, about 0.9 s of each clip silence (voiceover.md, engine table). Plan about 4 syllables per second: a 20 s scene holds about 80 spoken syllables. Count digits as the syllables spoken (32 = 삼십이). Other engines differ.
