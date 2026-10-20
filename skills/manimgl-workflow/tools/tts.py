#!/usr/bin/env python3
"""narration.txt -> one audio clip per line + narration/timestamps.json, for tools/voiceover.py.

Run from src/<video>:
    uv run python <tools>/tts.py                  # engine sapi (Windows, local)
    uv run python <tools>/tts.py --engine edge    # edge-tts: NETWORK, sends every new line to Microsoft
    uv run python <tools>/tts.py --engine gemini  # Gemini TTS: NETWORK, sends every new line to Google; needs $GEMINI_API_KEY
    uv run python <tools>/tts.py --selftest       # offline checks, no network

narration.txt: a `[SceneClass]` header, then one `- <spoken line>` per `with self.voice(k):` block
(k counts from 0 within the scene). Blank lines and `#` comments are allowed.
Clips are cached by sha256(engine, voice, text): a rerun synthesizes only new or changed lines.
--say FROM=TO (repeatable, any engine) rewrites the text the engine speaks (pronunciation); timestamps.json keeps the
original text, which is what voiceover.py shows as subtitles.

Cache-by-hash, ffprobe durations and the timestamps.json idea are adapted from
Yusuke710/manim-skill tools/tts-generate.py (MIT, Copyright (c) 2025 Yusuke Miyashita; see LICENSE-manim-skill).
"""

import argparse, asyncio, base64, functools, hashlib, io, json, math, os, re, subprocess, sys, tempfile, time, wave
from array import array
from pathlib import Path

OUT = Path("narration")
MODEL = "gemini-3.8-flash-tts"
STYLE = "calm, clear Korean lecture narration, moderate pace"  # in the gemini cache key
SEP = " <long pause> "  # between the lines of one --batch request
FRAME = 0.02  # RMS frame of split()
PAD = 0.2  # silence added to both ends of every gemini clip
SPS = (3.5, 6.5)  # accepted Hangul syllables/s: catches cut-off speech and stray pauses


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


def read_wav(data):
    """mono 16-bit WAV bytes -> (params, array('h'))."""
    try:
        with wave.open(io.BytesIO(data)) as r:
            if (r.getnchannels(), r.getsampwidth()) != (1, 2):
                raise ValueError("not a mono 16-bit WAV")
            return r.getparams(), array("h", r.readframes(r.getnframes()))
    except (wave.Error, EOFError) as e:
        raise ValueError(f"unreadable WAV: {e}") from e


def write_wav(params, samples):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setparams(params)
        w.writeframes(samples.tobytes())
    return buf.getvalue()


def padded(params, samples, sec=PAD):
    gap = array("h", bytes(2 * round(sec * params.framerate)))
    return write_wav(params, gap + samples + gap)


def store(path, data):
    """Write next to the target as .part, then rename (a killed run never leaves a half file)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(f"{path.name}.{os.getpid()}.part")
    part.write_bytes(data)
    part.replace(path)


def tag(text):
    return f"line {text[:15]!r}"


@functools.cache
def client(key_env):
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        sys.exit("Error: google-genai is not installed. It sends the narration text to Google's Gemini API.\n"
                 "Install it only if that is acceptable: uv add google-genai")
    if not os.environ.get(key_env):
        sys.exit("Error: the API key environment variable is not set or empty (see --key-env).")  # never echo the --key-env value
    # The SDK's own retry skips 429: on a daily quota it would sleep for Retry-After (~19 h) without a word. request() retries.
    return genai.Client(api_key=os.environ[key_env], http_options=types.HttpOptions(
        timeout=300_000, retry_options=types.HttpRetryOptions(attempts=1, http_status_codes=[503])))


def request(label, model, key_env, voice, text):
    """WAV bytes. 429 and 5xx are retried up to 3 attempts, except daily-quota errors; anything else exits at once."""
    for attempt in range(3):
        try:
            out = client(key_env).interactions.create(
                model=model,
                input=[{"type": "user_input", "content": [{"type": "text", "text": text,
                        "annotations": [{"type": "speech_metadata", "style": STYLE}]}]}],
                response_format={"type": "audio"},
                generation_config={"speech_config": [{"voice": voice}]})
        except Exception as e:  # noqa: BLE001 - interactions raises its own APIError, not genai.errors
            status = getattr(e, "status_code", None) or getattr(e, "code", None)
            err = (str(e).strip().splitlines() or [type(e).__name__])[-1].replace(os.environ[key_env], "***")[:200]  # mask before cutting
            low = str(e).lower()
            retry = isinstance(status, int) and (status == 429 or status >= 500) and "per day" not in low and "perday" not in low
            if not retry or attempt == 2:
                sys.exit(f"[FAIL] {label} {err}")
            time.sleep(((10, 30) if status == 429 else (2, 6))[attempt])  # rate limits need longer than server hiccups
            continue
        try:
            return base64.b64decode(out.output_audio.data)
        except Exception as e:  # noqa: BLE001
            sys.exit(f"[FAIL] {label} unreadable response: {type(e).__name__}")


def pace(text, sec):
    n = len(re.findall("[가-힣]", text))
    if sec < 0.5 or (n >= 5 and not SPS[0] <= n / sec <= SPS[1]):  # short or non-Korean lines have no usable rate
        raise ValueError(f"{sec:.2f}s for {n} syllables")


def split(samples, rate, weights, floor_db=-40, min_run=0.35, edge=0.05):
    """Cut a batch's PCM at silences into len(weights) pieces. Returns (pieces, [(cut time, silence length)])."""
    n = round(rate * FRAME)
    rms = [(sum(x * x for x in samples[i:i + n]) / n) ** 0.5 for i in range(0, len(samples) - n + 1, n)]
    thr = max(rms) * 10 ** (floor_db / 20)
    runs, start = [], None
    for i, v in enumerate(rms + [max(rms)]):  # the last value is a sentinel that closes a silence reaching the end
        if v < thr and start is None:
            start = i
        elif v >= thr and start is not None:
            if (i - start) * FRAME >= min_run:
                runs.append((start, i))
            start = None
    cuts, cum = [], 0
    win = 0.25 * len(rms) / len(weights)
    for w in weights[:-1]:
        cum += w
        expect = len(rms) * cum / sum(weights)
        near = [r for r in runs if abs((r[0] + r[1]) / 2 - expect) <= win]
        if not near:
            raise ValueError(f"no silence of {min_run}s or more near boundary {len(cuts) + 1}")
        cuts.append(max(near, key=lambda r: r[1] - r[0]))
        # position gate: the chosen silence must be pause-like (long) and near where the character counts predict it
        gap, off = (cuts[-1][1] - cuts[-1][0]) * FRAME, abs(sum(cuts[-1]) / 2 - expect) * FRAME
        if gap < 0.5 or off > 2.0:
            raise ValueError(f"boundary {len(cuts)}: silence {gap:.2f}s, {off:.1f}s from the predicted position")
    mids = [(a + b) // 2 for a, b in cuts]
    if mids != sorted(set(mids)):
        raise ValueError("boundaries overlap")
    bounds, segs, pad_ = [0, *mids, len(rms)], [], round(edge * rate)
    for a, b in zip(bounds, bounds[1:]):
        loud = [i for i in range(a, b) if rms[i] >= thr]
        if not loud:
            raise ValueError("a piece is all silence")
        segs.append(samples[max(a * n, loud[0] * n - pad_):min(b * n, (loud[-1] + 1) * n + pad_)])
    return segs, [(m * FRAME, (b - a) * FRAME) for m, (a, b) in zip(mids, cuts)]


def gemini(jobs, voice, model, key_env, batch):
    """NETWORK. Each clip is stored at its .part path as soon as it passes the gates, so a later failure keeps it."""
    print(f"[tts] gemini: sending {len(jobs)} line(s) to Google's Gemini API ({model})", file=sys.stderr)
    failed = False
    for k in range(0, len(jobs), batch):
        group = jobs[k:k + batch]
        texts = [t for t, _ in group]
        data = request(" + ".join(map(tag, texts)), model, key_env, voice, SEP.join(texts))
        try:
            params, samples = read_wav(data)
        except ValueError as e:  # not a split problem: a smaller --batch would not help
            sys.exit(f"[FAIL] {' | '.join(map(tag, texts))} reply is not a WAV: {e}")
        try:
            if len(group) == 1:
                pace(texts[0], len(samples) / params.framerate)
                segs = [samples]
            else:
                segs, info = split(samples, params.framerate, [max(1, len(re.findall(r"[가-힣A-Za-z]", t))) for t in texts])
                for t, seg in zip(texts, segs):
                    pace(t, len(seg) / params.framerate)
        except ValueError as e:
            if len(group) == 1:
                print(f"[FAIL] {tag(texts[0])} {e}")
            else:
                # keep the paid reply so the failure can be inspected without another request
                store(OUT / "batches" / f"{hashlib.sha256(SEP.join(texts).encode()).hexdigest()[:16]}.wav", data)
                print(f"[SPLIT-FAIL] {' | '.join(map(tag, texts))} {e}; rerun with a smaller --batch")
            failed = True
            continue
        if len(group) > 1:
            for j, (at, gap) in enumerate(info):
                print(f"[CUT] {j}|{j + 1} t={at:.2f}s silence={gap:.2f}s")
        for (_, path), seg in zip(group, segs):
            store(path, padded(params, seg))
    if failed:
        sys.exit(1)


ENGINES = {  # name: (synthesize(jobs=[(text, path)], voice), default voice, file extension)
    "sapi": (sapi, "Microsoft Heami Desktop", ".wav"),
    "edge": (edge, "ko-KR-SunHiNeural", ".mp3"),
    "gemini": (gemini, "Charon", ".wav"),
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


def cache_key(engine, voice, text, *extra):
    return hashlib.sha256(json.dumps([engine, voice, text, *extra], ensure_ascii=False).encode()).hexdigest()[:16]


def say(text, pairs):
    for old, new in pairs:
        text = text.replace(old, new)
    return text


def env_name(value):
    """argparse type for --key-env. A fixed message: argparse would echo a ValueError's value, and a pasted key must not appear."""
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value) or value.startswith("AIza") or len(value) > 40:
        raise argparse.ArgumentTypeError("--key-env must be an environment variable NAME, not a key")
    return value


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--narration", default="narration.txt", help="clips and timestamps.json always go to ./narration/")
    p.add_argument("--engine", choices=ENGINES, default="sapi")
    p.add_argument("--voice", help="default: sapi 'Microsoft Heami Desktop', edge 'ko-KR-SunHiNeural', gemini 'Charon'")
    p.add_argument("--model", default=MODEL, help="gemini only (default %(default)s)")
    p.add_argument("--key-env", type=env_name, default="GEMINI_API_KEY", help="gemini only: environment variable holding the API key; "
                   "read only when a line is not cached (default %(default)s)")
    p.add_argument("--batch", type=int, default=1, help="gemini only: K uncached lines per request, split at silences "
                   "(saves daily requests; on [SPLIT-FAIL] rerun with a smaller K)")
    p.add_argument("--say", action="append", default=[], metavar="FROM=TO",
                   help="repeatable: replace FROM by TO in the text the engine speaks (pronunciation). Subtitles keep the original")
    p.add_argument("--selftest", action="store_true", help="offline checks (needs ffprobe), then exit")
    args = p.parse_args(argv)
    if args.selftest:
        return _selftest()
    sys.stdout.reconfigure(errors="replace")  # a cp1252 pipe cannot encode Hangul; never lose timestamps.json over a log line
    if args.batch < 1 or (args.batch > 1 and args.engine != "gemini"):
        p.error("--batch must be >= 1, and above 1 only with --engine gemini")
    pairs = []
    for item in args.say:
        old, eq, new = item.partition("=")
        if not eq or not old:
            p.error(f"--say expects FROM=TO, got {item!r}")
        pairs.append((old, new))
    synth, default_voice, ext = ENGINES[args.engine]
    voice = args.voice or default_voice
    extra = (args.model, STYLE) if args.engine == "gemini" else ()
    if args.engine == "gemini":
        synth = functools.partial(synth, model=args.model, key_env=args.key_env, batch=args.batch)

    entries, todo = {}, []
    for scene, lines in parse(args.narration).items():
        entries[scene] = []
        for k, text in enumerate(lines):
            spoken = say(text, pairs)
            path = OUT / f"{cache_key(args.engine, voice, spoken, *extra)}{ext}"
            entries[scene].append({"k": k, "text": text, "file": path.as_posix()})
            if not path.exists() and path not in (q for _, q in todo):
                todo.append((spoken, path))

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
            for (_, part), (_, final) in zip(parts, todo):
                if args.engine == "gemini" and part.exists():  # gemini writes a part only after its gates passed: keep it for the rerun
                    part.replace(final)
                part.unlink(missing_ok=True)
    for scene, items in entries.items():
        for e in items:
            e["duration_s"] = round(duration(e["file"]), 3)
            print(f"{scene}[{e['k']}] {e['duration_s']:6.3f}s  {e['text']}")
    store(OUT / "timestamps.json", json.dumps(entries, ensure_ascii=False, indent=1).encode("utf-8"))
    print(f"{len(todo)} new clip(s), the rest from the cache -> {(OUT / 'timestamps.json').as_posix()}")


def _wav(sig, rate=24000):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(array("h", sig).tobytes())
    return buf.getvalue()


def _exits(fn):
    try:
        fn()
    except SystemExit as e:
        return e.code
    raise AssertionError("did not exit")


def _selftest():
    """Offline: no network, no API key. The end-to-end part needs ffprobe, like a real run."""
    from types import SimpleNamespace
    from unittest import mock
    rate = 24000
    tone = lambda sec: [round(8000 * math.sin(i * 0.1)) for i in range(round(sec * rate))]
    quiet = lambda sec: [0] * round(sec * rate)
    # sapi/edge keys are what earlier versions wrote; gemini adds model and style
    assert cache_key("sapi", "Microsoft Heami Desktop", "테스트") == "18923ca2b34a827a"
    assert cache_key("edge", "ko-KR-SunHiNeural", "테스트") == "5d3a6f8b15bbf34d"
    assert cache_key("gemini", "Charon", "t", MODEL, STYLE) != cache_key("gemini", "Charon", "t", "other-model", STYLE)
    assert say("RAG와 RAG", [("RAG", "래그"), ("와", "과")]) == "래그과 래그"
    # fake batch: tones of 2.1 / 2.5 / 1.5 s, 0.8 s silences between, and a 0.3 s silence inside the first piece that is no boundary
    segs, info = split(array("h", tone(1.9) + quiet(0.3) + tone(0.2) + quiet(0.8) + tone(2.5) + quiet(0.8) + tone(1.5)), rate, [24, 25, 15])
    assert [round(len(x) / rate, 2) for x in segs] == [2.45, 2.6, 1.55], [len(x) / rate for x in segs]
    assert [round(t, 1) for t, _ in info] == [2.8, 6.1] and all(g >= 0.8 for _, g in info), info
    # gate: a silence 2 s+ from the predicted position, or under 0.5 s, is no boundary
    for sig, weights in ((tone(9.6) + quiet(0.8) + tone(9.6), [62, 38]), (tone(2) + quiet(0.45) + tone(2), [1, 1])):
        try:
            split(array("h", sig), rate, weights)
        except ValueError:
            continue
        raise AssertionError("gate let a wrong boundary through")
    params, got = read_wav(padded(read_wav(_wav([1000] * 2400))[0], array("h", [1000] * 2400)))
    edge_ = round(PAD * rate)
    assert len(got) == 2400 + 2 * edge_ and not any(got[:edge_]) and not any(got[-edge_:]) and got[edge_] == 1000

    syl = lambda t: len(re.findall("[가-힣]", t))
    calls = []

    def fake(label, model, key_env, voice, text):  # 5 syllables/s, 0.8 s pauses; a line starting with 불량 comes back as one tone
        calls.append(text)
        if text.startswith("불량"):
            return _wav(tone(syl(text) / 5))
        return _wav(sum(([*quiet(0.8)] * (i > 0) + tone(syl(t) / 5) for i, t in enumerate(text.split(SEP))), []))

    lines = ["RAG는 찾아서 덧붙여 답하는 방식입니다.", "벡터 디비는 뜻으로 찾을 때 씁니다.", "이제 네 단계를 차례로 살펴보겠습니다.", "마지막으로 다음 단계를 예고합니다."]
    out = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    old_cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as d, mock.patch.dict(globals(), request=fake), \
            mock.patch("sys.stdout", out), mock.patch("sys.stderr", out):
        os.chdir(d)
        try:
            body = lambda ls: "[A]\n" + "".join(f"- {t}\n" for t in ls[:3]) + "[B]\n" + "".join(f"- {t}\n" for t in ls[3:])
            Path("narration.txt").write_text(body(lines), encoding="utf-8")
            main(["--engine", "gemini", "--batch", "3", "--say", "RAG=래그"])
            assert not Path("narration/batches").exists()  # replies are kept only when a split fails
            assert len(calls) == 2 and calls[0].count(SEP) == 2 and "래그는" in calls[0] and "RAG" not in "".join(calls), calls
            ts = json.loads(Path("narration/timestamps.json").read_text(encoding="utf-8"))
            assert ts["A"][0]["text"] == lines[0], ts["A"][0]  # subtitles stay original
            for e, t in zip(ts["A"] + ts["B"], lines):
                assert abs(e["duration_s"] - (syl(say(t, [("RAG", "래그")])) / 5 + 2 * PAD)) < 0.15, e
            main(["--engine", "gemini", "--batch", "3", "--say", "RAG=래그"])
            assert len(calls) == 2  # all cached: no request, so no key needed either
            main(["--engine", "gemini", "--say", "RAG=래그"])
            assert len(calls) == 2
            main(["--engine", "gemini", "--say", "RAG=래그", "--model", "m2"])  # model is part of the key
            assert len(calls) == 6  # four single requests
            # a failing group stores no clip and exits 1, the other group's clip is kept
            n = len(list(Path("narration").glob("*.wav")))
            Path("bad.txt").write_text(body(["불량 한 줄이 통째로 이어진 소리입니다.", "정상 줄 하나가 뒤따릅니다 둘째.", "다른 정상 줄이 하나 더 있습니다 셋째.", "넷째 줄도 정상으로 들어갑니다."]), encoding="utf-8")
            assert _exits(lambda: main(["--engine", "gemini", "--batch", "2", "--narration", "bad.txt"])) == 1
            assert "[SPLIT-FAIL]" in (out.flush(), out.buffer.getvalue().decode())[1]
            assert len(list(Path("narration").glob("*.wav"))) == n + 2 and not list(Path("narration").glob("*.part*"))
            assert len(list(Path("narration/batches").glob("*.wav"))) == 1
            # a reply that is no WAV stops at once as [FAIL], not as a split problem
            with mock.patch.dict(globals(), request=lambda *a: b"not audio"):
                Path("junk.txt").write_text("[A]\n- 아무 줄이나 하나 넣어 봅니다 정말로.\n", encoding="utf-8")
                msg = _exits(lambda: main(["--engine", "gemini", "--narration", "junk.txt"]))
                assert msg.startswith("[FAIL]") and "not a WAV" in msg and "SPLIT" not in msg, msg
            for bad in ("my key", "AIzaSyFAKEFAKEFAKEFAKEFAKE", "X" * 41):  # key-like values: rejected without being echoed
                assert _exits(lambda: main(["--engine", "gemini", "--key-env", bad])) == 2
            out.flush()
            assert not any(bad in out.buffer.getvalue().decode() for bad in ("my key", "AIza", "X" * 41))
            assert _exits(lambda: main(["--batch", "2"])) == 2 and _exits(lambda: main(["--say", "RAG"])) == 2
            # sapi/edge keep their cache names and never reach the gemini path
            def fake_sapi(jobs, voice):
                for _, path in jobs:
                    path.write_bytes(_wav(tone(1)))
            with mock.patch.dict(ENGINES, sapi=(fake_sapi, "V", ".wav")), mock.patch.dict(globals(), request=None):
                main(["--engine", "sapi"])
                assert all(Path("narration", cache_key("sapi", "V", t) + ".wav").is_file() for t in lines)
                main(["--engine", "sapi", "--say", "RAG=래그"])
                assert Path("narration", cache_key("sapi", "V", say(lines[0], [("RAG", "래그")])) + ".wav").is_file()
        finally:
            os.chdir(old_cwd)
    # retry policy: 503 then ok retries; a daily quota exits at once; the key never reaches the message
    ok = SimpleNamespace(output_audio=SimpleNamespace(data=base64.b64encode(b"x")))
    def api(*errors):
        seq = iter([*errors, ok])
        def create(**kw):
            r = next(seq)
            if isinstance(r, Exception):
                raise r
            return r
        return SimpleNamespace(interactions=SimpleNamespace(create=create))
    def err(status, msg):
        e = Exception(msg)
        e.status_code = status
        return e
    with mock.patch.dict(os.environ, {"TTS_TEST_KEY": "sekret"}), mock.patch.object(time, "sleep"):
        with mock.patch.dict(globals(), client=(lambda c: lambda k: c)(api(err(503, "overloaded")))):
            assert request("x", "m", "TTS_TEST_KEY", "v", "t") == b"x"
        with mock.patch.object(time, "sleep") as nap:  # 429 waits longer than 5xx
            with mock.patch.dict(globals(), client=(lambda c: lambda k: c)(api(err(429, "rate"), err(429, "rate")))):
                assert request("x", "m", "TTS_TEST_KEY", "v", "t") == b"x"
            with mock.patch.dict(globals(), client=(lambda c: lambda k: c)(api(err(503, "down")))):
                request("x", "m", "TTS_TEST_KEY", "v", "t")
            assert [c.args[0] for c in nap.call_args_list] == [10, 30, 2]
        with mock.patch.dict(globals(), client=(lambda c: lambda k: c)(api(err(429, "Quota exceeded: requests per day, key sekret")))):
            msg = _exits(lambda: request("line 'a'", "m", "TTS_TEST_KEY", "v", "t"))
            assert msg.startswith("[FAIL] line 'a'") and "sekret" not in msg and "per day" in msg, msg
        with mock.patch.dict(globals(), client=(lambda c: lambda k: c)(api(err(400, "bad")))):
            assert _exits(lambda: request("x", "m", "TTS_TEST_KEY", "v", "t")).startswith("[FAIL]")
    print("selftest ok", file=sys.__stdout__)


if __name__ == "__main__":
    main()
