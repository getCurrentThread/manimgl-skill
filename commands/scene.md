---
description: Start a manimgl (CodingVillainKor fork) video - plan scenes.md, get approval, then code, render and iterate
argument-hint: <topic or video description>
---

Topic: $ARGUMENTS

1. Follow the **manimgl-workflow** skill. When writing code, also follow the **manimgl-best-practices** skill.
2. Start at step 0 (setup). Check whether this repository has a uv project with the fork installed; if not, run setup.sh.
3. Then go to step 1 (Plan) and create `src/<video>/scenes.md` for the topic above.
4. If the topic is empty, ask what the video explains in the same single message as the manimgl-workflow §1 step 2 questions (the topic plus at most 3). Otherwise, if the audience, length, depth or series context is unclear, follow §1 step 2: at most 3 questions in one message, or, when nobody can answer, defaults listed under `## Assumptions and open decisions`.
5. Do not write main.py until the user approves scenes.md.
