#!/usr/bin/env python3
"""Video Viewer - Local viewer for manimgl videos with chapter navigation.

Ported from Yusuke710/manim-skill tools/video_viewer.py
(MIT, Copyright (c) 2025 Yusuke Miyashita; see LICENSE-manim-skill).
Changes: utf-8 file reads (Windows/Korean), Code-tab label shows the --script file name,
startup fails on missing/unreadable order entries, scenes with different stream layouts,
or a video/order duration mismatch, Range end is clamped to the file size and a start past
the end gets 416, --srt is read as text so CRLF files parse.
"""

import argparse, http.server, json, os, re, shutil, socketserver, subprocess, sys, threading, webbrowser
from pathlib import Path
from urllib.parse import unquote, urlparse, parse_qs

def get_duration(path):
    result = subprocess.run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path], capture_output=True, text=True)
    return float(json.loads(result.stdout).get("format", {}).get("duration", 0)) if result.returncode == 0 else 0.0

def stream_layout(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    return " | ".join(r.stdout.split())

def scene_name(path):
    return re.sub(r"_\d{4}x\d{4}$", "", Path(path).stem)

def build_chapters(scenes):
    chapters, t = [], 0.0
    for i, path in enumerate(scenes):
        dur = get_duration(path)
        chapters.append({"index": i, "name": scene_name(path), "start": t, "duration": dur})
        t += dur
    return chapters

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, ctx=None, **kw):
        self.ctx = ctx
        super().__init__(*a, **kw)

    def do_GET(self):
        parsed = urlparse(unquote(self.path))
        path, query = parsed.path, parse_qs(parsed.query)

        routes = {
            "/": lambda: self.send_bytes(self.ctx["ui_html"], "text/html"),
            "/index.html": lambda: self.send_bytes(self.ctx["ui_html"], "text/html"),
            "/video.mp4": lambda: self.send_file(self.ctx["video"], "video/mp4"),
            "/chapters.json": lambda: self.send_bytes(json.dumps(self.ctx["chapters"]).encode(), "application/json"),
            "/subtitles.srt": lambda: self.send_bytes(self.ctx.get("srt"), "text/plain"),
            "/download": lambda: self.handle_download(),
            "/cscript.py": lambda: self.send_bytes(self.ctx.get("script_content"), "text/x-python"),
        }

        if path in routes:
            routes[path]()
        else:
            self.send_error(404)

    def send_bytes(self, data, ctype):
        if data is None:
            self.send_error(404)
            return
        body = data.encode() if isinstance(data, str) else data
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path, ctype):
        try:
            size = os.path.getsize(path)
            range_hdr = self.headers.get("Range")

            # RFC 9110: end < start is invalid and ignored; suffix ranges (bytes=-N) don't match either; both get a full 200
            if range_hdr and (m := re.match(r"bytes=(\d+)-(\d*)", range_hdr)) and not (m[2] and int(m[2]) < int(m[1])):
                start, end = int(m[1]), min(int(m[2]), size - 1) if m[2] else size - 1
                if start >= size:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.send_header("Content-Length", 0)
                    self.end_headers()
                    return
                self.send_response(206)
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                self.send_header("Content-Length", end - start + 1)
            else:
                start, end = 0, size - 1
                self.send_response(200)
                self.send_header("Content-Length", size)

            self.send_header("Content-Type", ctype)
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()

            with open(path, "rb") as f:
                f.seek(start)
                self.wfile.write(f.read(end - start + 1))
        except (BrokenPipeError, ConnectionResetError):
            pass

    def handle_download(self):
        video = self.ctx["video"]
        name = Path(video).stem
        try:
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Disposition", f'attachment; filename="{name}.mp4"')
            self.send_header("X-Filename", f"{name}.mp4")
            self.send_header("Content-Length", os.path.getsize(video))
            self.end_headers()
            with open(video, "rb") as f:
                shutil.copyfileobj(f, self.wfile)
        except Exception as e:
            print(f"Download error: {e}")
            self.send_error(500, str(e))

    def log_message(self, *_): pass

def find_port(start=8000, end=9000):
    import socket
    for p in range(start, end):
        try:
            with socket.socket() as s:
                s.bind(("127.0.0.1", p))
                return p
        except OSError:
            pass
    return None

def parse_order_file(path):
    base_dir = Path(path).parent
    videos = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if m := re.match(r"file '(.+)'", line.strip()):
            videos.append(str(base_dir / m[1]))
    return videos

def srt_time(s):
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{int(h):02}:{int(m):02}:{int(sec):02},{int((sec % 1) * 1000):03}"

def concatenate_srts(scenes):
    """Concatenate SRT files from scene videos with time offset adjustments."""
    entries, offset = [], 0.0
    for video in scenes:
        srt_path = Path(video).with_suffix(".srt")
        if srt_path.exists():
            for block in srt_path.read_text(encoding="utf-8").strip().split("\n\n"):
                lines = block.split("\n")
                if len(lines) < 3: continue
                m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", lines[1])
                if not m: continue
                start = int(m[1])*3600 + int(m[2])*60 + int(m[3]) + int(m[4])/1000 + offset
                end = int(m[5])*3600 + int(m[6])*60 + int(m[7]) + int(m[8])/1000 + offset
                text = "\n".join(lines[2:])
                entries.append(f"{len(entries)+1}\n{srt_time(start)} --> {srt_time(end)}\n{text}")
        offset += get_duration(video)
    return "\n\n".join(entries) + "\n" if entries else ""

def main():
    p = argparse.ArgumentParser()
    p.add_argument("video")
    p.add_argument("--order", required=True, help="concat.txt with video file list")
    p.add_argument("--port", type=int, default=0)
    p.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    p.add_argument("--srt")
    p.add_argument("--script")
    args = p.parse_args()

    if not os.path.exists(args.video):
        sys.exit(f"Error: {args.video} not found")
    if not os.path.exists(args.order):
        sys.exit(f"Error: {args.order} not found")

    scenes = parse_order_file(args.order)
    if not scenes:
        sys.exit("Error: No videos found in order file")
    if missing := [os.path.abspath(s) for s in scenes if not os.path.exists(s)]:
        sys.exit("Error: order file entries not found:\n  " + "\n  ".join(missing))

    port = args.port or find_port()
    if not port:
        sys.exit("Error: No port available")

    print("Building chapters...")
    chapters = build_chapters(scenes)
    if bad := [os.path.abspath(s) for s, c in zip(scenes, chapters) if not c["duration"] > 0]:
        sys.exit("Error: no duration (ffprobe failed or 0):\n  " + "\n  ".join(bad))
    # error, not warning: concat -c copy keeps the first file's layout, so another resolution/fps plays at the wrong
    # size and a missing or different audio track drops or garbles the sound, with ffmpeg exiting 0
    layouts = {os.path.abspath(s): stream_layout(s) for s in scenes}
    if len(set(layouts.values())) > 1:
        sys.exit("Error: scenes differ in resolution/fps/audio, so full.mp4 would be broken. Re-render them with the same flags "
                 "(narrated videos: every scene inherits Narrated):\n  " + "\n  ".join(f"{k}: {v}" for k, v in layouts.items()))
    total, full = sum(c["duration"] for c in chapters), get_duration(args.video)
    # measured |full - total| with ffmpeg concat -c copy: <=0.00065s (2/4/10/50 sample mp4s), 0.024s (10 clips with AAC audio)
    if abs(full - total) > 0.1:
        sys.exit(f"Error: {args.video} is {full:.3f}s but order file scenes sum to {total:.3f}s. "
                 f"Rebuild it from the same order file: ffmpeg -v error -y -f concat -safe 0 -i {args.order} -c copy -movflags +faststart {args.video} "
                 "(narrated video: use the audio re-encoding join in references/voiceover.md §2 step 6 instead)")
    print(f"Found {len(chapters)} chapters")

    script_name = Path(args.script).name if args.script else "script.py"
    ctx = {
        "video": os.path.abspath(args.video),
        "chapters": chapters,
        "ui_html": Path(__file__).with_name("ui.html").read_text(encoding="utf-8").replace(">script.py<", f">{script_name}<").replace("No script.py", f"No {script_name}").encode(),
        # read_text: universal newlines turn CRLF into LF; ui.html parseSRT splits cues on \n\n only
        "srt": (Path(args.srt).read_text(encoding="utf-8-sig") if args.srt else concatenate_srts(scenes)).encode() or None,
        "script_content": Path(args.script).read_text(encoding="utf-8").encode() if args.script and os.path.exists(args.script) else None,
    }

    handler = lambda *a, **kw: Handler(*a, ctx=ctx, **kw)

    try:
        with socketserver.TCPServer((args.host, port), handler) as srv:
            url = f"http://localhost:{port}"
            print(f"Viewer: {url}")
            threading.Timer(0.5, lambda: webbrowser.open(url)).start()
            print(f"VIDEO_READY http://localhost:{port}", flush=True)
            srv.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped")

if __name__ == "__main__":
    main()
