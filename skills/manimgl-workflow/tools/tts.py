#!/usr/bin/env python3
"""narration.txt -> one audio clip per line + narration/timestamps.json, for tools/voiceover.py.

Run from src/<video>:
    uv run python <tools>/tts.py                  # engine sapi (Windows, local)
    uv run python <tools>/tts.py --engine edge    # edge-tts: NETWORK, sends every new line to Microsoft

narration.txt: a `[SceneClass]` header, then one `- <spoken line>` per `with self.voice(k):` block
(k counts from 0 within the scene). Blank lines and `#` comments are allowed.
Clips are cached by sha256(engine, voice, text): a rerun synthesizes only new or changed lines.

Cache-by-hash, ffprobe durations and the timestamps.json idea are adapted from
Yusuke710/manim-skill tools/tts-generate.py (MIT, Copyright (c) 2025 Yusuke Miyashita; see LICENSE-manim-skill).
"""

import argparse, asyncio, base64, hashlib, json, os, re, subprocess, sys, tempfile
from pathlib import Path

OUT = Path("narration")


def parse(path):
    scenes, scene = {}, None
    if not Path(path).exists():
        sys.exit(f"Error: {path} not found. Run tts.py from src/<video>: it reads ./narration.txt and writes ./narration/, where manimgl looks")
    for n, line in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if m := re.fullmatch(r"\s*\[(\w+)\]\s*", line):
            scene = scenes.setdefault(m[1], [])
        elif (m := re.fullmatch(r"\s*-\s+(.*\S)\s*", line)) and scene is not None:
            scene.append(m[1])
        else:
            sys.exit(f"Error: {path}:{n}: expected `[SceneClass]` or `- <line>` under a header, got: {line.strip()}")
    if not any(scenes.values()):
        sys.exit(f"Error: {path} has no `- <line>` entries")
    return scenes


def sapi(jobs, voice):
    """Windows System.Speech, local. Text goes through a UTF-8 JSON file, never the command line."""
    if os.name != "nt":
        sys.exit("Error: engine sapi needs Windows. No other local engine is verified; --engine edge uses the network.")
    ps = r"""
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$j = [IO.File]::ReadAllText($env:TTS_JOBS, [Text.Encoding]::UTF8) | ConvertFrom-Json
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
try { $s.SelectVoice($j.voice) } catch {
  $v = $s.GetInstalledVoices() | Where-Object Enabled | ForEach-Object { "  $($_.VoiceInfo.Name) ($($_.VoiceInfo.Culture))" }
  [Console]::Out.WriteLine("voice '$($j.voice)' is not installed. Installed voices:`n" + ($v -join "`n")); exit 3 }
foreach ($x in $j.jobs) { $s.SetOutputToWaveFile($x.wav); $s.Speak($x.text); $s.SetOutputToNull() }
$s.Dispose()
"""
    with tempfile.TemporaryDirectory() as d:
        jobs_file = Path(d, "jobs.json")
        jobs_file.write_text(json.dumps({"voice": voice, "jobs": [{"text": t, "wav": str(p.resolve())} for t, p in jobs]},
                                        ensure_ascii=False), encoding="utf-8")
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", base64.b64encode(ps.encode("utf-16-le")).decode()],
                           env={**os.environ, "TTS_JOBS": str(jobs_file)}, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode == 3:  # stdout: stderr also carries PowerShell CLIXML progress records
        sys.exit(f"Error: {r.stdout.strip()}\nPass one of them with --voice, or add the Korean text-to-speech voice in Windows settings.")
    if r.returncode:
        sys.exit(f"Error: SAPI failed (exit {r.returncode}): {(r.stderr or r.stdout).strip()[-500:]}")


def edge(jobs, voice):
    """edge-tts (Microsoft online service): every text in jobs is sent over the network."""
    try:
        import edge_tts
    except ImportError:
        sys.exit("Error: edge-tts is not installed. It sends the narration text to Microsoft's online TTS service.\n"
                 "Install it only if that is acceptable: uv add edge-tts")
    print(f"[tts] edge: sending {len(jobs)} line(s) to Microsoft's online TTS service", file=sys.stderr)

    async def run():
        for text, path in jobs:
            try:
                await edge_tts.Communicate(text, voice).save(str(path))
            except (edge_tts.exceptions.NoAudioReceived, ValueError) as e:  # unknown voice: no audio; malformed name: ValueError
                ko = [v["ShortName"] for v in await edge_tts.list_voices() if v["Locale"] == "ko-KR"]
                sys.exit(f"Error: edge-tts cannot use voice '{voice}' ({e}). Korean voices: {', '.join(ko)}")
    asyncio.run(run())


ENGINES = {  # name: (synthesize(jobs=[(text, path)], voice), default voice, file extension)
    "sapi": (sapi, "Microsoft Heami Desktop", ".wav"),
    "edge": (edge, "ko-KR-SunHiNeural", ".mp3"),
}


def duration(path, strict=True):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout)
    except ValueError:
        if strict:
            sys.exit(f"Error: ffprobe could not read {path}: {r.stderr.strip() or r.stdout.strip()}")
        return 0.0


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--narration", default="narration.txt", help="clips and timestamps.json always go to ./narration/")
    p.add_argument("--engine", choices=ENGINES, default="sapi")
    p.add_argument("--voice", help="default: sapi 'Microsoft Heami Desktop', edge 'ko-KR-SunHiNeural'")
    args = p.parse_args()
    sys.stdout.reconfigure(errors="replace")  # a cp1252 pipe cannot encode Hangul; never lose timestamps.json over a log line
    synth, default_voice, ext = ENGINES[args.engine]
    voice = args.voice or default_voice

    entries, todo = {}, []
    for scene, lines in parse(args.narration).items():
        entries[scene] = []
        for k, text in enumerate(lines):
            key = hashlib.sha256(json.dumps([args.engine, voice, text], ensure_ascii=False).encode()).hexdigest()[:16]
            path = OUT / f"{key}{ext}"
            entries[scene].append({"k": k, "text": text, "file": path.as_posix()})
            if not path.exists() and path not in (q for _, q in todo):
                todo.append((text, path))

    OUT.mkdir(exist_ok=True)
    if todo:
        # write to .part files and rename on success, so an interrupted run never leaves a cached half clip
        parts = [(t, q.with_name(q.stem + ".part" + ext)) for t, q in todo]
        try:
            synth(parts, voice)
            for (text, part), (_, final) in zip(parts, todo):
                # SAPI writes a 46-byte header-only WAV for a punctuation-only line; never cache it
                if not part.exists() or not duration(part, strict=False) > 0:
                    sys.exit(f"Error: {args.engine} produced no audio for the line {text!r}. A line of only punctuation "
                             "(e.g. '…') is silent: give it words, or give a silent ## block no narration line and no self.voice()")
                part.replace(final)
        finally:
            for _, part in parts:
                part.unlink(missing_ok=True)
    for scene, items in entries.items():
        for e in items:
            e["duration_s"] = round(duration(e["file"]), 3)
            print(f"{scene}[{e['k']}] {e['duration_s']:6.3f}s  {e['text']}")
    (OUT / "timestamps.json").write_text(json.dumps(entries, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(todo)} new clip(s), the rest from the cache -> {(OUT / 'timestamps.json').as_posix()}")


if __name__ == "__main__":
    main()
