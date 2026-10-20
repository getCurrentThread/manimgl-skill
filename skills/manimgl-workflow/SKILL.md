---
name: manimgl-workflow
description: End-to-end workflow for making an explainer video with the CodingVillainKor/manimgl fork - Plan (research the topic, hook/aha/misconception, narrative pattern and fork-verified visual techniques, scenes.md, user approval) → optional Korean narration (local TTS, per-scene audio and SRT) → Code & Render (src/<video>/main.py, last-frame check with -sw, mid-animation frame sheets, then -w per scene) → Iterate (concat, local viewer, timestamped feedback, re-render only the affected scenes). Use when the user asks to make or animate a video/scene with manimgl, or runs /manimgl-skill:scene.
---

# manimgl video workflow: Plan → Code & Render → Iterate

Before writing code, follow the **manimgl-best-practices** skill. Fork API, color pitfalls, Korean text, and CLI rules are there.

## Contract

- **Deliverables**: hand over `src/<video>/main.py`, per-scene `videos/<Scene>.mp4`, `full.mp4`, and the viewer URL. With narration, also `full.srt`.
- **When blocked**: report the failed command and the last line of the error as-is.
- **No coding before approval**: do not write `main.py` until the user approves the Plan.
- **Commit baseline**: this workflow was tuned against exactly one fork commit, @455a4201. When setup.sh adds the fork fresh, it pins to this commit. If the fork is already on another commit, it does not change the commit and only warns (it only adds the missing `trimesh`/`pywavefront`).

## Team mode (optional)

- Only when the user asks for subagents or team mode; it spawns many agents and costs many tokens. Otherwise ignore this section.
- The main session leads: it plans, writes briefs and `handoff.md`, and judges every report by Reading the frame itself. Sub-agents (non-fork, explicit model override) write and render one act file each. Reviewers are `manimgl-skill:scene-reviewer`.
- Roles, file ownership, phase gates, the viewer feedback loop, brief checklist and `handoff.md`: `${CLAUDE_SKILL_DIR}/references/team-production.md`.

## 0. Setup (once per project)

- The project is a uv project root containing `pyproject.toml`. If the fork is not there yet, install it.
  ```bash
  bash ${CLAUDE_PLUGIN_ROOT}/scripts/setup.sh <project root>                  # add --with-raenimgl to use raenimgl too
  ```
- Handling setup.sh results:
  - **exit 2 (conflict with PyPI `manimgl`)**: show the printed fix command to the user, get approval, then run it.
  - **exit 1 (`[fail]`)**: rendering is impossible. Report the printed `[fail]` line as-is.
  - **LaTeX / cm-super warning**: plan without Tex (use only Text, shapes, numbers) or ask the user to install it.
  - **ffprobe warning**: the §3 viewer cannot start. Ask the user to install ffprobe along with ffmpeg.
  - **Noto Sans KR warning**: Korean Text may render as □. Ask the user to install the font or set `font=`.
  - **OpenGL warning**: `-w` rendering may fail. Report the warning line as-is.
- The video folder is `<project>/src/<video name>/`. Give the video a short English name. **Run all later commands from this folder.** Output piles up under `videos/` in the cwd.

## 1. Plan

1. **Understand the topic.**
   - For a paper, algorithm, formula or library, read the source the user gave (paper, docs, code). If there is none and a web tool is available, look it up. Do not plan from memory alone.
   - Write down the insight that makes it click (→ **Aha moment**), 1–2 misconceptions the audience probably holds (→ **Misconception**), and the concrete example to animate.
   - Every number, formula, date and name on screen comes from that source or from your own calculation, recorded in **Facts and numbers on screen**. Do not invent values. A made-up example value is labeled "illustrative" there and on screen.
2. **Ask only what blocks the plan.** If the topic leaves the audience, length, depth or series context unclear, ask at most 3 short questions, once, in one message: the audience's background; the number of scenes; intuition only or with formulas (Tex); standalone or part of a series (if a series, what the previous video covered). Skip anything the topic already answers.
   - If no answer can come (a non-interactive run) or the user leaves it to you, choose defaults and list them under `## Assumptions and open decisions`. Approval confirms them.
3. **Choose the story and the visuals.** One narrative pattern from [references/narrative-patterns.md](references/narrative-patterns.md); one technique per idea from [references/visual-techniques.md](references/visual-techniques.md) or best-practices. For an API covered by neither, check that the fork has it (`${CLAUDE_PLUGIN_ROOT}/skills/manimgl-best-practices/references/api-inventory.md`) and list it under Assumptions as "to probe".
4. **Fill in scenes.md** following `${CLAUDE_SKILL_DIR}/templates/scenes.md`. A filled example: `${CLAUDE_SKILL_DIR}/templates/scenes-example.md`.
   - **Audience**: who watches, and what they already know
   - **Core idea**: the one sentence that remains when the video ends
   - **Hook**: scene 1 reaches the question, surprise or wrong answer within its first ~10 s. Explain only after it
   - **Aha moment**: the scene and `##` block where the core idea lands. Give it the slowest beat (`self.wait(1~2)` after it) and one emphasis (`Indicate`/`FlashAround`)
   - **Misconception**: the scene that shows the wrong intuition failing before the right idea, or "none"
   - **Color roles**: one meaning per named constant, fixed for the whole video. No hex colors (best-practices §11)
   - **Narration**: `none` unless the user asks for spoken narration. With `voiceover`, each spoken block line also carries its sentence; a silent block carries none (Korean budget: about 4 syllables per second, references/voiceover.md), and the plan names the TTS engine (§1b)
   - **Tex strings**: when Uses Tex is yes, every formula with its scenes; mark the ones containing Korean (best-practices §7)
   - **Scene list**: in narrative order, 1–8 scenes (the imcommit range). For each scene: class name (PascalCase), 15~30 seconds, the narration/intent lines that become `##` blocks, on-screen elements, technique (optional), end state, and **Next** (what the next scene rebuilds and how the cut looks)
5. Show the scenes.md content and get **explicit approval**. If changes are requested, apply them and get approval again.
   - In plan mode you cannot write files. Present the whole scenes.md content as the plan, and write it to `src/<video>/scenes.md` after approval, once plan mode is exited.
   - Outside plan mode, write `src/<video>/scenes.md` first and then show it.
   - Once approved, mark it in the `## Approval` field of scenes.md.

## 1b. Narration (only when scenes.md says `Narration: voiceover`)

Silent videos are the default. Details, evidence and pitfalls: `${CLAUDE_SKILL_DIR}/references/voiceover.md`.

1. Write `src/<video>/narration.txt` from the approved blocks: a `[SceneClass]` header per scene, then one `- <spoken line>` per `##` block, in order; a silent `##` block gets no line and no `with self.voice`.
2. Synthesize, then read each line's seconds before writing `construct`.
   ```bash
   uv run python ${CLAUDE_SKILL_DIR}/tools/tts.py     # sapi: local, Windows only
   ```
   - `--engine edge` sends every line to Microsoft's online TTS service. Use it only if the user chose it, and run `uv add edge-tts` only with their consent.
   - `uv run python ${CLAUDE_SKILL_DIR}/tools/tts.py --engine gemini [--voice Charon] [--model gemini-3.8-flash-tts] [--key-env GEMINI_API_KEY] [--batch K] [--say FROM=TO ...]` is a network engine: it sends every new line to Google. Use it only if the user chose it, and run `uv add google-genai` only with their consent. The key is read only from the env var named by `--key-env`, only when an uncached line exists, and is never printed. `--batch K` (gemini only; K>1 with another engine exits 2) sends K uncached lines per request, split at silences (saves free-tier daily request limits); on `[SPLIT-FAIL]` rerun with a smaller K. `--say FROM=TO` (any engine) fixes a pronunciation in the TTS input only; subtitles keep the original text, e.g. `--say RAG=래그`.
   - No local macOS/Linux engine is shipped (not verified); `edge` and `gemini` are network engines that do not need Windows (not run elsewhere). If tts.py exits listing voices without a Korean one, report that list.
3. `cp ${CLAUDE_SKILL_DIR}/tools/voiceover.py .`, then in `main.py`:
   - First line: `import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # manimgl does not put the script folder on sys.path`, then `from voiceover import Narrated`. <!-- snippet: skip needs voiceover.py next to main.py -->
   - **Every** scene is `class X(Narrated, Scene)`, silent ones too, so all mp4s share one audio layout for concat.
   - Wrap each voiced `##` block in `with self.voice(k):` (k is the line's index under its `[SceneClass]` header, from 0). Leaving the block waits out the rest of the clip.
4. In §2 step 2, `-sw` also prints `[voice] ...` lines (overruns, unvoiced lines, stale `timestamps.json`). Fix them like any other problem.
5. Render narrated scenes whole with `-w -l` / `-w`, **never `-n`** (`voice()` raises). Each mp4 gets audio and `videos/<Scene>.srt`; the viewer joins them into subtitles. In §3 step 1, join narrated scenes with the `references/voiceover.md` §2 step 6 command (`-c:v copy -af aresample=async=1:min_hard_comp=0.001:first_pts=0 -c:a aac -b:a 320k`), not `-c copy`: `-c copy` adds 21-43 ms of decoded audio per join (AAC priming plus the previous scene's end padding), so anything that follows samples (an audio re-encode, a wav export) puts later narration late.
6. After the viewer starts (§3 step 2), save the subtitles: `curl -s http://localhost:<port>/subtitles.srt -o full.srt`. Redo this after each re-render.

## 2. Code & Render

1. Write the classes in one `main.py` in scenes.md order. Follow the shape of `${CLAUDE_PLUGIN_ROOT}/skills/manimgl-best-practices/examples/structure.py`.
   - Each class **renders on its own.** If it needs the previous scene's end state, rebuild it inside that class.
   - If a class uses `random_color()`, `random` or `np.random`, make `random.seed(41); np.random.seed(41)` the first line of its `construct`. Scenes listed in one command share one random stream, so without this, re-rendering only that scene in §3 (Iterate) changes its colors or positions (best-practices §11) [verified by run].
   - Match the `## …` blocks inside `construct` 1:1 with the lines in scenes.md.
2. Check the last frame **one scene at a time**.
   ```bash
   cd <project>/src/<video>
   uv run manimgl main.py <Scene> -sw </dev/null   # -> videos/<Scene>.png  (with -s alone, a window opens and hangs)
   ```
   - A nonzero exit code means failure. Even on failure, an old `videos/<Scene>.png`/`.mp4` may remain, so do not judge by the files alone.
   - Open `videos/<Scene>.png` with Read and look for the following.
     - Overlaps
     - Parts cut off the screen
     - Korean □ (tofu)
     - Low contrast on the black background
     - Text that is too small
     - Leftover objects that should have been removed
     - Colors that differ from intent. The constructor `color=` is ignored for `Text/Tex/TexText/Dot/Brace` (they come out white), makes `Arrow/Vector/StrokeArrow` gray and `Annulus/Sector` gray-filled, `Circle/Ellipse` have a red outline and `Cross` is red (best-practices §6)
   - If there is a problem, fix it and rerun the same command.
3. Render to video.
   ```bash
   uv run manimgl main.py <Scene> -w -l </dev/null   # draft 854x480 -> videos/<Scene>.mp4
   ```
   - On an error, read the end of the Traceback, fix it, and re-render **only that scene**.
   - After rendering, **also look at the mid-animation frames.** The `-sw` PNG is only the last frame.
     - So problems during the animation (text that overlaps while changing, an object passing over a disappearing object, an object growing from the origin) and the starting composition of scenes where the camera moves are not visible there.
     - Gather frames at 0.5-second intervals into one sheet (6×6 cells, 18 seconds' worth) and view it with Read.
     ```bash
     ffmpeg -v error -y -i videos/<Scene>.mp4 -vf "fps=2,scale=320:-1,tile=6x6" videos/sheet_<Scene>_%02d.png
     ```
     - The k-th cell of sheet m (row order from the top left) is at about 18(m-1) + 0.5k - 0.25 seconds.
     - Look at each cell using the list in item 2. For a suspicious moment, extract it large with `ffmpeg -v error -y -ss <sec> -i videos/<Scene>.mp4 -frames:v 1 videos/t<sec>.png`.
   - For a more careful review, hand it to the **scene-reviewer** agent (`manimgl-skill:scene-reviewer`) with the absolute path of `src/<video>` and the scene name.
4. Repeat 2~3 until every scene comes out without errors.
5. Make the final version with `uv run manimgl main.py <Scene> -w </dev/null` (1920x1080 30fps). It overwrites the same `videos/<Scene>.mp4`.
   - Render **all scenes with the same quality options** so the `-c copy` concatenation in the next step works.

## 3. Iterate

1. Write `concat.txt` in scenes.md order and concatenate. Paths are relative to concat.txt.
   ```
   file 'videos/Intro.mp4'
   file 'videos/Quantize.mp4'
   ```
   ```bash
   ffmpeg -v error -y -f concat -safe 0 -i concat.txt -c copy -movflags +faststart full.mp4
   ```
   - With narration, use the audio re-encoding command from §1b item 5 instead, here and in step 4.4.
2. Start the viewer **in the background**. It uses only the standard library and ffprobe.
   ```bash
   uv run python ${CLAUDE_SKILL_DIR}/tools/video_viewer.py full.mp4 --order concat.txt --script main.py
   ```
   - Tell the user the `VIDEO_READY http://localhost:<port>` URL from the output. Use a free port in 8000~8999. It is needed in 4.5, so **remember the port.**
   - If it ends with `Error:` instead of `VIDEO_READY`, a concat.txt entry is missing, a duration could not be read, the scenes differ in resolution/fps/audio (re-render them with the same flags), or full.mp4 does not match concat.txt. Fix it as the message says and redo from step 1, concat.
   - The viewer opens the browser itself. To keep it from opening, put `BROWSER=true` in front of the command.
   - The viewer has no quit command. How to stop it is in 4.5.
   - Chapter names are the mp4 file names, that is, the scene class names.
3. In the viewer, the user presses the `t` key (Capture) to make a `[M:SS] <Scene>: <note>` line. They copy it with the **Copy** button and paste it into the conversation.
4. Handle each feedback line.
   1. Extract that moment and view it with Read. First check the scene the user saw.
      - `[M:SS]` is the time in full.mp4, with the fraction of a second dropped (`tools/ui.html` `fmt`). Looking at a single frame misses problems within that one second.
      - From `<sec>` = M×60+SS, extract 1 second as 4 frames and gather them into one image.
      ```bash
      ffmpeg -v error -y -ss <sec> -t 1 -i full.mp4 -vf "fps=4,scale=854:-1,tile=2x2" -frames:v 1 fb_<sec>.png
      ```
      - Find which `##` block in main.py by the time within the scene. Subtract that chapter's `start` from `<sec>`. `start` is in the viewer's `/chapters.json`.
   2. Fix **only the scene class that was named.**
      - If the fix changes that scene's end state (leftover objects, camera orientation), also match the starting state that the next scene rebuilds, and re-render that scene too.
      - If you fixed a function shared by several scenes, re-render all of those scenes too.
      - If a re-rendered scene's random colors or positions changed although you did not touch them, its `construct` is not seeded (§2 step 1). Seed it, then re-render it.
   3. Check the fixed scene with `-sw`, then re-render it with `-w` (or `-w -l`) using the same quality options as the other scenes.
   4. Redo the concat to make `full.mp4`.
   5. **Restart the viewer.** Chapter durations and the main.py tab are read only once at startup (`tools/video_viewer.py` `main()`).
      - First stop the running viewer. If you do not, the `--port` command below cannot take that port and ends with `OSError` (Windows: WinError 10048). If you start it without `--port`, it takes the next free port and the URL changes.
      - Under `uv run`, the process holding the port is the child python process. So find it by port and stop it.
        ```bash
        # Windows (Git Bash): the last column is the PID
        netstat -ano | grep LISTENING | grep ":<port> "
        taskkill //F //PID <pid>
        # macOS / Linux (without -sTCP:LISTEN, browser connections are killed too)
        kill $(lsof -ti tcp:<port> -sTCP:LISTEN)
        ```
      - Start it again on the same port. Do not open a new tab. The user just refreshes the open tab.
        ```bash
        BROWSER=true uv run python ${CLAUDE_SKILL_DIR}/tools/video_viewer.py full.mp4 --order concat.txt --script main.py --port <port>
        ```
   6. Verify the fix.
      - Rerun the command from item 1 on the new full.mp4 as `fb_<sec>_after.png` and compare it with `fb_<sec>.png`.
      - If the fixed scene's duration changed, recompute `<sec>` from the new `/chapters.json` `start` too.
      - Tell the user only after confirming the fix. The `-sw` PNG is the last frame, so it does not verify feedback about a mid-animation moment.
5. Repeat 4 until the user is satisfied.

## Notes

- The viewer and the cache idea of `tools/tts.py` originate from Yusuke710/manim-skill (MIT). The changes are in `tools/README.md`.
- `references/narrative-patterns.md`, `references/visual-techniques.md` and `templates/scenes-example.md` adapt adithya-s-k/manim_skill `skills/manim-composer/` (MIT). The changes are listed at the top of each file; the license text is in `references/LICENSE-manim_skill`.
- Narration is opt-in (§1b). The fork has no subcaption API; `tools/voiceover.py` adds clips with `Scene.add_sound` and writes `videos/<Scene>.srt` itself. There is no separate timing linter: `-sw` runs `construct()` and prints overruns.
