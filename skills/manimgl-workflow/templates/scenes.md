# <Video title>

- **Audience**: <who is watching, what they already know>
- **Core idea (one sentence)**: <the one thing that should remain when the video ends>
- **Hook**: <the question, surprising result or common wrong answer scene 1 opens with (first ~10 s)>
- **Aha moment**: <`<Scene>` → `## <block>` where the core idea lands>
- **Misconception**: <wrong intuition → the scene that breaks it, or "none">
- **Narrative pattern**: <entry from references/narrative-patterns.md>
- **Color roles** (named constants, fixed for the whole video, black background): <e.g. BLUE given, GREEN correct/result, RED wrong, YELLOW emphasis, GREY_B secondary>
- **Facts and numbers on screen**: <each value with its source or calculation; mark made-up values "illustrative">
- **Length target**: <number of scenes × 15–30 s>
- **Narration**: <none | voiceover (engine: sapi = local Windows voice | edge = sends the text to Microsoft)>. none: `##` lines are intent notes. voiceover: append `— Narration: "<spoken line>"` to each spoken block line; a silent block gets none (no narration.txt line, no `with self.voice`)
- **Uses Tex**: <yes/no. no if LaTeX is not installed>
- **Tex strings** (when Uses Tex is yes): <each formula as R"…" with its scene numbers; mark any containing Korean (kotex template, best-practices §7)>

## Scene list (narrative order = main.py class order = concat.txt order)

### 1. `<SceneClassName>` (~20 s)
- **Purpose**: <the one thing this scene conveys>
- **Blocks** (1:1 with `## …` comments):
  - `## <narration/intent 1>`: <what happens on screen>
  - `## <narration/intent 2>`: <…>
- **On-screen elements**: <Text/Tex/shapes/axes…, in the color roles above>
- **Technique** (optional): <entry from references/visual-techniques.md>
- **End state**: <what is on screen when the scene ends>
- **Next**: <what the next scene rebuilds and how the cut looks, or "—" for the last scene>

### 2. `<SceneClassName>` (~20 s)
- **Purpose**:
- **Blocks**:
  - `## …`:
- **On-screen elements**:
- **Technique**:
- **End state**:
- **Next**:

## Assumptions and open decisions (confirm at approval)

- <defaults chosen without the user's answer, open creative choices, or "none">

## Approval

- [ ] User approval (date):
