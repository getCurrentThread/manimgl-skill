---
name: manimgl-workflow
description: End-to-end workflow for making an explainer video with the CodingVillainKor/manimgl fork - Plan (scenes.md, user approval) → Code & Render (src/<video>/main.py, last-frame check with -sw, mid-animation frame sheets, then -w per scene) → Iterate (concat, local viewer, timestamped feedback, re-render only the affected scenes). Use when the user asks to make or animate a video/scene with manimgl, or runs /manimgl-skill:scene.
---

# manimgl video workflow: Plan → Code & Render → Iterate

Before writing code, follow the **manimgl-best-practices** skill. Fork API, color pitfalls, Korean text, and CLI rules are there.

## Contract

- **Deliverables**: hand over `src/<video>/main.py`, per-scene `videos/<Scene>.mp4`, `full.mp4`, and the viewer URL.
- **When blocked**: report the failed command and the last line of the error as-is.
- **No coding before approval**: do not write `main.py` until the user approves the Plan.
- **Commit baseline**: this workflow was tuned against exactly one fork commit, @455a4201. When setup.sh adds the fork fresh, it pins to this commit. If the fork is already on another commit, it does not change the commit and only warns (it only adds the missing `trimesh`/`pywavefront`).

## 0. Setup (once per project)

- The project is a uv project root containing `pyproject.toml`. If the fork is not there yet, install it.
  ```bash
  bash ${CLAUDE_PLUGIN_ROOT}/scripts/setup.sh <project root>                  # add --with-raenimgl to use raenimgl too
  ```
- Handling setup.sh results:
  - **exit 2 (conflict with PyPI `manimgl`)**: show the printed fix command to the user, get approval, then run it.
  - **exit 1 (`[fail]`)**: rendering is impossible. Report the printed `[fail]` line as-is.
  - **LaTeX / cm-super warning**: plan without Tex (use only Text, shapes, numbers) or ask the user to install it.
  - **ffprobe warning**: the step 3 viewer cannot start. Ask the user to install ffprobe along with ffmpeg.
  - **Noto Sans KR warning**: Korean Text may render as □. Ask the user to install the font or set `font=`.
  - **OpenGL warning**: `-w` rendering may fail. Report the warning line as-is.
- The video folder is `<project>/src/<video name>/`. Give the video a short English name. **Run all later commands from this folder.** Output piles up under `videos/` in the cwd.

## 1. Plan

1. Fill in the scenes.md content following the `${CLAUDE_SKILL_DIR}/templates/scenes.md` format.
   - **Audience**: who watches, and what they already know
   - **Core idea**: the one sentence that remains when the video ends
   - **Scene list**: in narrative order. For each scene: class name (PascalCase), 15~30 seconds, the narration/intent lines that become `##` blocks, on-screen elements, end state, and the link to the next scene
2. Show the scenes.md content and get **explicit approval**. If changes are requested, apply them and get approval again.
   - In plan mode you cannot write files. Present the whole scenes.md content as the plan, and write it to `src/<video>/scenes.md` after approval, once plan mode is exited.
   - Outside plan mode, write `src/<video>/scenes.md` first and then show it.
   - Once approved, mark it in the `## Approval` field of scenes.md.

## 2. Code & Render

1. Write the classes in one `main.py` in scenes.md order. Follow the shape of `${CLAUDE_PLUGIN_ROOT}/skills/manimgl-best-practices/examples/structure.py`.
   - Each class **renders on its own.** If it needs the previous scene's end state, rebuild it inside that class.
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
     - Colors that differ from intent. The constructor `color=` is ignored for `Text/Tex/TexText/Dot/Brace` (they come out white), makes `Arrow/Vector/StrokeArrow` gray, and `Circle/Ellipse` have a red outline (best-practices §6)
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
   ffmpeg -v error -y -f concat -safe 0 -i concat.txt -c copy full.mp4
   ```
2. Start the viewer **in the background**. It uses only the standard library and ffprobe.
   ```bash
   uv run python ${CLAUDE_SKILL_DIR}/tools/video_viewer.py full.mp4 --order concat.txt --script main.py
   ```
   - Tell the user the `VIDEO_READY http://localhost:<port>` URL from the output. Use a free port in 8000~8999. It is needed in 4.5, so **remember the port.**
   - If it ends with `Error:` instead of `VIDEO_READY`, a concat.txt entry is missing, a duration could not be read, or full.mp4 does not match concat.txt. Fix it as the message says and redo from step 1, concat.
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

- The viewer originates from Yusuke710/manim-skill (MIT). The changes are in `tools/README.md`.
- Subtitles, TTS, and voiceover are not part of this workflow. The fork has no subcaption API.
