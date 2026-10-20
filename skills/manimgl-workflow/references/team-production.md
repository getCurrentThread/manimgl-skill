# Team production (optional)

Several agents build one video in parallel. The main session leads and judges; sub-agents execute. Steps, files and commands come from SKILL.md §1-§3; this file adds only who does what and how the work is split.

## 1. When

- **Opt-in only.** Use it when the user asks for subagents or team mode. It spawns many agents and costs many tokens. Otherwise follow SKILL.md alone.
- It fits videos with several scenes that can live in separate files. For 1-2 scenes, do the work yourself.

## 2. Roles

| Role | Who | Does | Does not |
|---|---|---|---|
| Lead | The main session | Plans (§1 as usual, scenes.md approval); writes agent briefs and `handoff.md`; judges every report by extracting and Reading the frame at the reported moment itself; decides which reviewer findings to adopt; dispatches | Write scene code or render. Exception: the user tells the lead to fix something directly |
| Executor | Non-fork `general-purpose` agent with an explicit model override (used: `model: "sonnet", effort: "high"`) | Writes and renders the files it owns | Edit files it does not own; commit |
| Reviewer | `manimgl-skill:scene-reviewer` per scene file (read-only, same model override); a `general-purpose` code reviewer for tools (tts, join script) | Reports findings with scene-local timestamps | Edit code |
| Image maker (optional) | Whatever image tool the user names | Generative images, only if review says shapes are not enough | |

- Do not fork executors: a fork inherits the parent model, so the override is ignored.
- One executor per owned file set.
- Never accept a report on the agent's word. Reading the frame is the check.

## 3. File ownership

- This replaces SKILL.md §2 step 1 ("classes in one `main.py`"): in team mode the classes live in the act files, and `main.py` holds only the imports and `SCENES_IN_ORDER`.
- With narration, every act file needs `from voiceover import Narrated` <!-- snippet: skip needs voiceover.py in the project folder --> (SKILL.md §1b step 3), and `voiceover.py` sits in the project folder. manimgl puts neither the script folder nor the cwd on `sys.path`, so the import resolves one of two ways: `PYTHONPATH=.` when rendering an act file directly, or the `sys.path.insert` first line of `main.py` when rendering through `main.py` (the same line also lets `main.py` import the act files). Both rest on the `sys.path` fact in `references/voiceover.md` §1; `PYTHONPATH=.` with `voiceover.py` was not verified. Run from the project folder: `voiceover.py` reads `narration/timestamps.json` relative to the cwd.
- Split scenes into act files `act_a.py`, `act_b.py`, ... with 1-3 scene classes each. One agent owns each act file.
- `main.py` imports the act files and lists `SCENES_IN_ORDER`. manimgl does not discover scene classes in other modules, so the list is needed. Only the integrator creates or edits `main.py`.
- Shared `components.py` is append-only. Re-read it before every edit; another agent may have appended since.
- While agents work, each renders its own act file, so one broken file does not stop the others. Put the folder on the path, for example:
  ```bash
  PYTHONPATH=. uv run manimgl act_a.py <Scene> -w -l --fps 15
  ```
- Each class still renders on its own (SKILL.md §2 step 1). Final renders use the same flags for every scene (SKILL.md §2 step 5).

## 4. Phases and gates

The lead judges each gate and updates `handoff.md` before the next phase.

1. **Plan and approval.** The plan names the agents, their owned files and the user checkpoints (voice choice, viewer feedback).
2. **Scaffold.** One agent creates the project folder, runs `setup.sh`, saves `scenes.md`, and writes the `components.py` skeleton. It does not create `main.py`: the integrator writes it in phase 6, and until then each act agent renders its own act file directly (§3).
3. **In parallel:**
   - Narration agent (only with voiceover, §1b): writes `narration.txt`, synthesizes 1-2 sample lines, the user listens and picks the voice, then all lines.
   - Components agent: fills `components.py`.
4. **In parallel, one act agent per act file.** Each runs `-sw`, then `-w -l --fps 15`, and reports overruns 0 and the frame sheet. It fixes its own problems up to 3 times, else reports `BLOCKED` with the command and the last error line.
5. **Review.** One scene-reviewer per act file, in parallel. The lead adopts or rejects each finding, then sends the adopted fixes to the **owning agent** with SendMessage, which keeps its context. Do not spawn a new agent for a fix.
6. **Integrate.** The integrator writes `main.py`, renders all scenes, and joins them (SKILL.md §3 step 1). A scene-reviewer then checks the cuts between scenes: black gaps, leftover objects.
7. **Viewer loop** (§5).
8. **Final.** Render all scenes with `-w`, join, commit.

## 5. Viewer feedback loop

1. The integrator starts the viewer (SKILL.md §3 step 2). The lead gives the user the URL.
2. For each `[M:SS] Scene: note` line, the lead converts to scene-local time: M x 60 + SS minus that scene's `start` in `/chapters.json`. It finds the `##` block and sends the note and block to the owning agent.
3. The owner re-renders only that scene.
4. The lead Reads the frame at that moment.
5. The integrator re-joins and restarts the viewer on the same port (SKILL.md §3 step 4.5).
6. The lead tells the user to hard-refresh (Ctrl+F5, or Cmd+Shift+R): a browser can keep serving the old video.

## 6. Agent brief checklist

Every brief states:

- Path of the approved plan (`scenes.md`) and `handoff.md`.
- Owned files, and the rules for shared files (`components.py` append-only, `main.py` integrator only).
- The exact commands to run, from the project folder.
- Done criteria: overruns 0, the project's pixel and lint checks, the frame sheet read.
- "Do not commit."
- Report format: files changed / checks run and results / frame PNG paths / blockers.

## 7. `handoff.md`

Lead-owned, committed, never secrets. Update it after every phase, verdict and user decision, so a new session can resume from it plus `scenes.md`.

- Current step and next action.
- Phase checklist.
- Decisions with dates (voice, colors, wording).
- Agent table: name, owned files, status, last report summary, `BLOCKED`.
- Open review findings and the lead's verdicts.
- Resume commands: render, tts, join, viewer port and PID. Last commit hash.

## 8. Pitfalls

- An agent can send a duplicate idle report after a later instruction. Check file contents and mtimes before acting on it.
- A fix to a shared helper requires re-rendering every scene that uses it. List them in the brief.
- When the plan says a scene's end state equals the next scene's start, keep it so after every fix. Verify with a pixel diff of the last frame against the next scene's first frame.
