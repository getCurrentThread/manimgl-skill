# Narration (voiceover) for fork scenes (fork @455a420)

- **Opt-in.** Silent videos stay the default. Add narration only when the user asks for it (scenes.md `Narration: voiceover`).
- Pipeline: `narration.txt` → `tools/tts.py` → `narration/*.wav` + `narration/timestamps.json` → scenes inherit `Narrated` (`tools/voiceover.py`) → `-sw` prints overruns → `-w` muxes audio and writes `videos/<Scene>.srt` per scene → concat → the viewer joins the SRTs.
- The fork has no subcaption API (`grep -rn subcaption manimlib` is empty in the fork and upstream; `hasattr(Scene, "add_subcaption")` is False [verified by run]). `voiceover.py` builds narration on `Scene.add_sound` and writes the SRT itself.
- `F:` paths are relative to the fork root. [verified by run] = the E2E below (Windows 11, uv Python 3.10, ffmpeg 2025-12-24 gyan build): 2 scenes, 3 Korean SAPI lines, `-w -l`, concat, viewer.

## 1. Three rules

| Rule | Why | Evidence |
|---|---|---|
| Every scene of a narrated video inherits `Narrated`, silent ones too: `class Intro(Narrated, Scene)` | Each `-w` mp4 then has one 48 kHz mono AAC track exactly as long as its video. `concat -c copy` needs identical streams in every input | First scene without audio → `full.mp4` has no audio stream at all; a scene whose audio outlasts its video → a 3.2 s timestamp gap in the joined video [verified by run]. The viewer refuses to start when scene stream layouts differ (§4) |
| Never `-n` for narrated `-w` renders. Render the whole scene | `add_sound` returns early while skipping (F:manimlib/scene/scene.py:652-653), so clips before animation n are dropped, and later clips land at absolute scene time in a shorter video | [verified by run]: a `-n 6` render without the helper had 15.7 s of video and 28.77 s of audio (a 4 s clip placed at 24.77 s). `voice()` raises `RuntimeError` under `-w -n` [verified by run]. `-sw -n` still works (no audio) |
| Copy `voiceover.py` next to `main.py`, and make the first line of `main.py` put its own folder on `sys.path` | manimgl puts neither the script folder nor the cwd on `sys.path`; it loads `main.py` with `spec_from_file_location` (F:manimlib/module_loader.py:40-49) | Without the line: `ModuleNotFoundError`, exit 1 (best-practices `references/cli-and-output.md` §3.3) [verified by run]. With it, both E2E scenes import `voiceover` [verified by run] |

## 2. Steps (run from `src/<video>`)

1. Write `narration.txt` from the approved scenes.md: one `[SceneClass]` header per scene, one `- <spoken line>` per `##` block (its `Narration: "…"` text); a silent `##` block gets no line and no `with self.voice`. `k` counts from 0 within each scene. Blank lines and `#` comments are allowed; any other line is an error with its line number.
   ```
   [Halve]
   - 정렬된 배열의 가운데 값을 먼저 봅니다.
   - 찾는 값이 더 크면 오른쪽 절반만 남깁니다.
   ```
2. Synthesize. It prints each line's length; read these budgets before writing `construct`.
   ```bash
   uv run python ${CLAUDE_SKILL_DIR}/tools/tts.py             # sapi, local
   ```
3. Copy the helper and write the header.
   ```bash
   cp ${CLAUDE_SKILL_DIR}/tools/voiceover.py .
   ```
   ```python
   import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # manimgl does not put the script folder on sys.path
   from manimlib import *
   from voiceover import Narrated

   class Halve(Narrated, Scene):
       def construct(self):
           ## 정렬된 배열의 가운데 값을 먼저 봅니다.
           with self.voice(0) as dur:   # dur = clip length in seconds
               self.play(ShowCreation(mid))
   ```
   - `with self.voice(k)` adds clip `k` at the current scene time. Leaving the block waits out the rest of the clip.
   - That wait is one more animation number when time is left (relevant only to `-sw -n`).
   - Scenes that override `setup()` need nothing extra: the narration loads on first use.
4. Check with `-sw` as usual. It has no audio, but it runs `construct()` and prints:
   - `[voice] <Scene> #k: animations overran the clip by Xs`: shorten the animations or split the line. Printed above 0.05 s.
   - `[voice] <Scene>: narration lines [..] are never voiced`: a `##` block lacks its `with self.voice(k)`.
   - `[voice] narration.txt is newer than narration/timestamps.json: rerun tts.py`
   - A `k` with no line in `timestamps.json` raises `IndexError` naming the scene and `k`. A missing `narration/timestamps.json` (tts.py not run, or manimgl started outside `src/<video>`) raises `FileNotFoundError` with the full path [verified by run].
5. Render every scene with `-w -l` (draft) or `-w` (final), the same flags for all. Each gets audio and `videos/<Scene>.srt`.
6. Concatenate, re-encoding only the audio (`-c copy` drifts the decoded audio, §4), then start the viewer as usual. Its `/subtitles.srt` serves the joined cues, and the UI shows the CC button when there are any (`tools/ui.html` `parseSRT`, `ccBtn`).
   ```bash
   ffmpeg -v error -y -f concat -safe 0 -i concat.txt -c:v copy -af aresample=async=1:min_hard_comp=0.001:first_pts=0 -c:a aac -b:a 320k -movflags +faststart full.mp4
   ```
7. Deliver `full.srt` (§5).

## 3. TTS engines (`tools/tts.py`)

| Engine | Where the text goes | Default voice | Output | Status |
|---|---|---|---|---|
| `sapi` (default) | Local. Windows `System.Speech` through PowerShell. Text passes in a UTF-8 JSON file, not the command line | `Microsoft Heami Desktop` (ko-KR) | wav, 22050 Hz mono | [verified by run]. 10, 16 and 17 syllables = 2.629, 3.794, 4.209 s: about 5-6 syllables/s of speech plus about 0.13 s of leading and 0.74 s of trailing silence per clip, so about 4 syllables/s overall |
| `edge` | **Network.** `edge-tts` sends every new or changed line to Microsoft's online TTS service. Only with `--engine edge`, and installed only when the user agrees: `uv add edge-tts` | `ko-KR-SunHiNeural` | mp3, 24 kHz mono | [verified by run] with one fixed sample sentence only (4.104 s; ffprobe length = decoded length). Korean voices listed: `ko-KR-HyunsuMultilingualNeural`, `ko-KR-InJoonNeural`, `ko-KR-SunHiNeural` |

- Missing voice: `sapi` exits listing the installed voices (`--voice "<name>"` picks one). Without a Korean voice, the Korean text-to-speech feature of Windows must be added (that install path was not run). An unknown or malformed `edge` voice exits listing the ko-KR voices [verified by run with `ko-KR-NopeNeural`; malformed names such as `SunHi` raise `ValueError` in edge-tts 7.3.1, verified offline with the voice list stubbed].
- Cache: `narration/<sha256(engine, voice, text)[:16]>.<ext>`. A rerun synthesizes only new or changed lines. Clips are written as `.part` and renamed on success, so a failed run leaves no half clip [verified by run]. A line of only punctuation (`- …`, `- ...`, `- ?`) gives a SAPI clip with no samples: the run stops naming that line and does not cache it [verified by run]. Old clips are not deleted.
- `timestamps.json`: `{Scene: [{k, text, file, duration_s}]}`, durations from ffprobe.
- Not shipped, because they were not verified: macOS `say`, any Linux engine, Kokoro (no Korean language code; an unknown voice prefix falls back to American English), MeloTTS/XTTS (torch-pinned or non-commercial weights). Voice quality was not judged by ear.

## 4. Fork sound facts and concat pitfalls

| Fact | Evidence |
|---|---|
| `add_sound(file, time_offset=0, gain=None, gain_to_background=None)` places the clip at `get_time() + time_offset` and does nothing while skipping (`-s`, `-sw`, the part before `-n`) | F:manimlib/scene/scene.py:645-655 |
| The file is used as given if it exists, else looked up in the `sounds` folder with `.wav`/`.mp3` | F:manimlib/utils/sounds.py:11-16, F:manimlib/utils/file_ops.py:44-46 |
| Audio is muxed only by `-w` without `--subdivide`: pydub exports the track in its default format, MP3 (`bitrate='312k'`; 320 kbps), into a file named `<Scene>.wav`, then `ffmpeg -c:v copy -c:a aac -b:a 320k` re-encodes it to AAC (two lossy encodes). `-shortest` is commented out, so nothing trims it | F:manimlib/scene/scene_file_writer.py:190-194,303-332 [verified by run] |
| The track starts as `AudioSegment.silent()` = 1 s and only grows to the end of the last clip. A 0.5 s scene with a 0.1 s sound → 1.0 s audio; with `Narrated` → 0.5 s | F:manimlib/scene/scene_file_writer.py:132-133,145-157 [verified by run] |
| `pydub` is a fork dependency; mp3 decoding needs ffmpeg | F:setup.cfg:47 |
| Under `-w` each `play`/`wait` emits `len(np.arange(0, rt, 1/fps))` frames, so it can run up to one frame long. A 3.794 s clip block ended at 3.800 s | F:manimlib/scene/scene.py:477 [verified by run] |
| So use one track per scene, placed at `get_time()`. One global track for the whole video (the Yusuke710 design) drifts by those frame remainders | gap probe: a 4.444 s budget consumed 4.4667 s [verified by run] |
| `-sw` advances time by the exact `run_time` (no frame rounding), so its overrun numbers can differ from `-w` by up to one frame per `play` | F:manimlib/scene/scene.py:474-475 |
| After `concat -c copy` the timestamps stay aligned (video starts at 0.021 s, audio at 0; by timestamp, speech onsets = cue start + clip lead + 21 ms in every scene). But each joined file keeps its 1024 AAC priming samples and its end padding, so the decoded audio grows by 21-43 ms per join: the next file's 1024 priming samples plus the previous scene's end padding, which depends on its length (40.0 ms after a 3.800 s scene; 32-36 ms per join in the 7-scene probe, 41.17 s of PCM for 40.93 s of video). Consumers that follow samples (`ffmpeg -i full.mp4 x.wav`, an audio re-encode) put each later scene's narration that much later. The §2 step 6 command re-encodes only the audio while joining: decoded onsets stay at +21 ms over 6 joins, and `full.mp4` (40.97 s) passes the viewer's 0.1 s duration check | [verified by run] (7-scene `-w -l` join, decoded onsets and ffprobe; 2-scene join: the second scene's audio, cross-correlated, starts at 3.8613 s with `-c copy` and 3.8213 s with §2 step 6). Browser playback not measured |
| Scenes with another resolution, fps or audio layout join with ffmpeg exit 0 into a broken `full.mp4` (container keeps the first file's size). `video_viewer.py` compares the scene stream layouts and exits 1 listing them | [verified by run]: 480p + 1080p, and audio + no audio |
| `-movflags +faststart` moves `moov` before `mdat` (`ftyp, moov, free, mdat`). Fork mp4s and plain concat end with `moov` (`ftyp, free, mdat, moov`) | [verified by run]. Benefit (reasoning, not measured): the browser need not fetch the file's tail first, and the viewer server is single-threaded |

## 5. SRT

- Under `-w`, `voiceover.py` writes `videos/<Scene>.srt` (UTF-8, LF). A cue runs from the clip start for the clip length, trailing silence included. A scene without lines writes an empty file, replacing a stale one.
- Without `--srt`, the viewer joins the per-scene files with chapter offsets into `/subtitles.srt`. E2E cues: 0.000-2.629, 2.633-6.427, 6.433-10.642 [verified by run].
- `--srt <file>` is read as text, so CRLF files work (before the fix, a CRLF file became one cue holding the whole file) [verified by run].
- Save it while the viewer runs. Offsets match `full.mp4`, because the viewer has already checked the durations.
  ```bash
  curl -s http://localhost:<port>/subtitles.srt -o full.srt
  ```
- Optional, from `src/<video>` with relative paths (an absolute `C:/` path inside the `subtitles` filter needs escaping; not tried):
  ```bash
  # soft subtitles (a track the player can switch off)
  ffmpeg -v error -y -i full.mp4 -i full.srt -map 0 -map 1 -c copy -c:s mov_text -metadata:s:s:0 language=kor -movflags +faststart full_sub.mp4
  # burned in
  ffmpeg -v error -y -i full.mp4 -vf "subtitles=full.srt:force_style='FontName=Noto Sans KR,FontSize=20'" -c:a copy full_burned.mp4
  ```
  - Both [verified by run]: the `mov_text` track is tagged `kor` and extracts back to the same cues; the burned frame shows Korean correctly.
  - To preview one burned frame, put `-ss` after `-i`. Before `-i`, timestamps restart at 0 and the filter draws the cue for 0 s [verified by run].

## 6. Limits

- Removing `Narrated` from a scene leaves its old `videos/<Scene>.srt`, and the viewer still shows those cues. Delete the file.
- `tts.py` prints with `errors="replace"`, so a stdout code page without Hangul (cp1252 pipe) shows `?` instead of crashing before `timestamps.json` is written [verified by run, `PYTHONIOENCODING=cp1252`].
- Not verified: engines on macOS/Linux, a cp949 Windows locale end to end, `--subdivide`, `gain`/`gain_to_background`, `edge` beyond one sample sentence.
