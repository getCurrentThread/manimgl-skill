"""Narration for fork scenes (opt-in). Copy this file next to main.py; see references/voiceover.md.

    import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # manimgl does not put the script folder on sys.path
    from manimlib import *
    from voiceover import Narrated

    class Intro(Narrated, Scene):   # every scene of a narrated video, silent ones too
        def construct(self):
            with self.voice(0):     # narration/timestamps.json["Intro"][0], written by tools/tts.py
                self.play(...)      # leaving the block waits out the rest of the clip

Under -w each scene gets one 48 kHz mono audio track exactly as long as its video, so the concat in
references/voiceover.md §2 step 6 (video copied, audio re-encoded) keeps the audio in sync, plus videos/<Scene>.srt,
which video_viewer.py joins into /subtitles.srt.
"""
import json
from contextlib import contextmanager
from pathlib import Path

from pydub import AudioSegment  # a fork dependency (setup.cfg:47)

RATE = 48000  # one sample rate for every scene: concat -c copy needs identical audio streams
TIMESTAMPS = Path("narration/timestamps.json")  # relative to the cwd, src/<video>


def _srt_time(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


class Narrated:
    def _narration(self):
        # loaded lazily, so scenes that override setup() without super() still work
        if not hasattr(self, "_voice_lines"):
            self._voice_cues = {}
            self._voice_lines = json.loads(TIMESTAMPS.read_text(encoding="utf-8")).get(str(self), []) if TIMESTAMPS.exists() else []
            src = Path("narration.txt")
            if TIMESTAMPS.exists() and src.exists() and src.stat().st_mtime > TIMESTAMPS.stat().st_mtime:
                print(f"[voice] narration.txt is newer than {TIMESTAMPS.as_posix()}: rerun tts.py")
        return self._voice_lines

    @contextmanager
    def voice(self, k):
        lines = self._narration()
        if self.start_at_animation_number is not None and self.file_writer.write_to_movie:
            raise RuntimeError("Render narrated scenes whole: -n drops the clips before the start animation and misplaces the rest")
        if not lines and not TIMESTAMPS.exists():
            raise FileNotFoundError(f"{TIMESTAMPS.resolve()} not found: run tts.py, and run manimgl from src/<video>")
        if not 0 <= k < len(lines):
            raise IndexError(f"{TIMESTAMPS.as_posix()} has no {self}[{k}]: add the line to narration.txt and rerun tts.py")
        line = lines[k]
        start = self.get_time()
        self.add_sound(line["file"])  # placed at get_time(); a no-op under -s
        yield line["duration_s"]
        left = start + line["duration_s"] - self.get_time()
        if left > 0:
            self.wait(left)
        elif left < -0.05:  # up to one frame per play of rounding is normal
            print(f"[voice] {self} #{k}: animations overran the clip by {-left:.2f}s (silence until the next clip)")
        self._voice_cues[k] = (start, start + line["duration_s"], line["text"])

    def tear_down(self):
        lines = self._narration()
        if unused := [k for k in range(len(lines)) if k not in self._voice_cues]:
            print(f"[voice] {self}: narration lines {unused} are never voiced")
        fw = self.file_writer
        if fw.write_to_movie:
            t = self.get_time()
            fw.add_audio_segment(AudioSegment.silent(0, frame_rate=RATE), time=t)  # pads the track up to the video length
            # trim: the fork starts every track as 1 s of silence, longer than a short scene
            fw.audio_segment = fw.audio_segment[:round(1000 * t)].set_frame_rate(RATE).set_channels(1)
            cues = sorted(self._voice_cues.values())
            srt = "".join(f"{i}\n{_srt_time(a)} --> {_srt_time(b)}\n{text}\n\n" for i, (a, b, text) in enumerate(cues, 1))
            Path(fw.get_movie_file_path()).with_suffix(".srt").write_text(srt, encoding="utf-8", newline="\n")
        super().tear_down()
