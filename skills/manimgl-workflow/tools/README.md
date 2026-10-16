# tools: local video viewer

`video_viewer.py` and `ui.html` are taken from `skills/manim-skill/tools/` in [Yusuke710/manim-skill](https://github.com/Yusuke710/manim-skill) and modified.
- Base commit: `a0048d9e265499038f34a9aa58ff16d306b5034c`
- License: MIT, Copyright (c) 2025 Yusuke Miyashita. The original text is in [LICENSE-manim-skill](LICENSE-manim-skill).

## Usage

```bash
# Run from src/<video>. full.mp4 and concat.txt are there.
uv run python <tools folder>/video_viewer.py full.mp4 --order concat.txt [--script main.py] [--port N] [--host HOST] [--srt file.srt]
```

- **Requirements**: Python standard library, `ffprobe` (must be on PATH). No external packages.
- **`--order`**: an ffmpeg concat list made of `file '<path>'` lines. Paths are relative to the folder containing concat.txt. Chapters are built from each file's duration and file name (stem).
- **Run behavior**:
  - Without `--port`, it finds a free port in 8000-8999. With `--port N`, it uses only that port.
  - The default `--host` is `127.0.0.1`.
  - It prints `VIDEO_READY http://localhost:<port>` and opens the browser. To avoid opening it, prefix the command with `BROWSER=true`. Python `webbrowser` honors this environment variable [verified by run, Windows].
  - There is no stop command. Kill the process holding the port. If it was started with `uv run`, that process is the child python.
- **Routes**:
  - `/`: UI
  - `/video.mp4`: supports Range requests and returns 206
  - `/chapters.json`
  - `/subtitles.srt`
  - `/download`
  - `/cscript.py`: contents of the file given with `--script`
- **Feedback**: the `t` key inserts a `[M:SS] <chapter name>: ` line, and **Copy** copies it. There is no feature to send it to the server (POST).
- **Restart needed**: chapters and script contents are read only once, at startup. After re-rendering a scene, start the viewer again.
  - If the previous process is not killed, the new viewer uses the next free port.
  - If you kill the previous process and pass the same port with `--port`, the URL stays the same (workflow SKILL.md step 3, item 4.5).

## Differences from the original

1. Added `encoding="utf-8"` to every `read_text()`, so that main.py with Korean comments does not break under the default Windows locale.
2. Removed the third-party brand link in the original UI, along with the related CSS and comments.
3. The code tab label `script.py` is replaced with the file name given with `--script`. The `/cscript.py` route is unchanged.
4. The order file is checked at startup. On a missing entry, a file whose duration cannot be read (ffprobe failure or 0 s), or a difference of more than 0.1 s between the sum of scene durations and the video duration, it exits with an error without starting the server. Previously, missing entries were dropped, which pulled later chapter timestamps earlier.
5. The Range end position of `/video.mp4` is clamped to the file size. If the start position is past the end of the file, it returns 416 and `Content-Range: bytes */<size>`. Ranges whose end is before the start, and `bytes=-N` (last N bytes) ranges, are ignored and the whole file is sent with 200. Previously, when the end was past the file, only a larger Content-Length was sent, so curl exited with 18.
6. All other logic (port, chapters, SRT concatenation) is the same as the original.
