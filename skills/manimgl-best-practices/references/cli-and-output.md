# manimgl CLI and output (fork @455a420)

- Form: `uv run manimgl <file.py> <Scene> [<Scene> ...] [options]`. `manimgl` and `manim-render` are the same entry point (F:setup.cfg:65-66).
- [verified by run] Environment: Windows 11, Git Bash, uv Python 3.10, ffmpeg gyan.dev 2025-12-24 build (on PATH). The installed `manimlib` is file-for-file identical to the fork @455a420 source (`diff -rq`).
- `F:` paths in this document are relative to the fork repository root. In the §2 table, `:NN` means `F:manimlib/config.py:NN`.

## 1. What to know first

| Rule | Evidence |
|---|---|
| Without `-w` it runs in window mode. The process does not end until the window is closed | `show_in_window = not write_file` (F:manimlib/config.py:331), `interact()` loop (F:manimlib/scene/scene.py:186-201). `-s`, `-ql`, `-sql`, `-a` used alone hang until `timeout` (20-60 s) kills them (124) and leave no file behind [verified by run] |
| The save switch is `-w`. `-o` and `--finder` also turn on `-w` | F:manimlib/config.py:233 |
| `-s -w` (`-sw`) writes only a PNG, and `-w` alone writes only a video | `write_to_movie = not s and w`, `save_last_frame = s and w` (F:manimlib/config.py:278,280) [verified by run] |
| Always pass the scene name. If the file has 2 or more scenes and the name is missing or wrong, it stops at an `input()` prompt | F:manimlib/extract_scene.py:94-104,48. If stdin is `/dev/null`, it exits 1 immediately [verified by run] |
| `-p` is presenter mode (not CE's preview). Combined with `-w`, it hangs forever at the first `play`/`wait` | `hold_loop()` in `pre_play` (F:manimlib/scene/scene.py:519-521,605,623-626). Without a window, the space key cannot be received. `-w -l -p` ended with exit 124 under `timeout 40` and `videos/` was empty [verified by run] |
| Output accumulates in `videos/` relative to the **cwd**. The script location does not matter | F:manimlib/default_config.yml:20,23, F:manimlib/config.py:244,393. Running `../w/one.py` from another folder creates `<cwd>/videos/Only.mp4` [verified by run] |
| Merely importing `manimlib` parses `sys.argv` as the manimgl CLI | `manim_config = initialize_manim_config()` → `parse_cli()` (F:manimlib/config.py:33,406). `python -c "import manimlib" --bogus` → `unrecognized arguments`, exit 2 [verified by run]. A tool script that imports manimlib must not take its own arguments |

## 2. All flags

All flags of `manimgl --help`, grouped by topic (the order differs from help). "Effect" is written from reading the implementation, not from the help text.

| Flag | Definition | Implemented effect |
|---|---|---|
| `file` | F:manimlib/config.py:59 | If omitted, opens `BlankScene` (InteractiveScene + `embed()`) in a window (F:manimlib/extract_scene.py:22-25,115). If stdin is EOF, IPython ends right away and exits 0 [verified by run] |
| `scene_names` | :64 | If several are given, they are rendered in order [verified by run]. If the file has only 1 scene, that scene is rendered even when the name is wrong (F:manimlib/extract_scene.py:95) [verified by run] |
| `-w, --write_file` | :69 | Writes a video file and does not open a window (F:manimlib/config.py:278,331) [verified by run] |
| `-s, --skip_animations` | :74 | Skips all animations and produces only the final state. Saves a PNG only when `-w` is present; otherwise it opens a window and hangs [verified by run] |
| `-l` / `-m` / `--hd` / `--uhd` | :79,84,89,94 | Sets the resolution to 854x480 / 1280x720 / 1920x1080 / 3840x2160 (F:manimlib/default_config.yml:101-104). fps is unchanged [verified by run, §3.1] |
| `-r, --resolution WxH` | :176 | Sets the resolution directly. If combined with `-l` etc., `-r` wins (F:manimlib/config.py:358-368) [verified by run] |
| `--fps N` | :180 | Changes `camera.fps` (F:manimlib/config.py:262-263) [verified by run]. In window mode it is fixed at 30 (F:manimlib/scene/scene.py:104, source evidence) |
| `-c, --color` | :185 | Background color. It is parsed with `colour.Color`, so `red` is the CSS color `#FF0000`, not manim's `RED` (`#FC6255`, F:manimlib/default_config.yml:163) [verified by run]. An invalid color prints `Please use a valid color` and exits 2 [verified by run] |
| `-t, --transparent` | :120 | Writes `.mov` with `prores_ks` (ffprobe: `prores`, `yuva444p12le`). Sets `background_opacity=0` (F:manimlib/config.py:271-272,292-294). With `-sw -t`, the PNG background alpha is 0 [verified by run] |
| `-i, --gif` | :115 | Writes `.gif`. `video_codec=''`, so ffmpeg picks the encoder from the extension (F:manimlib/config.py:295-296,374-375). Combined with `-t`, `-t` wins and the output is `.mov` [verified by run] |
| `--vcodec` | :125 | ffmpeg `-vcodec`. Takes precedence over `-t`/`-i` (F:manimlib/config.py:290-291). A nonexistent codec gives `BrokenPipeError`, exit 1 [verified by run] |
| `--pix_fmt` | :129 | ffmpeg `-pix_fmt` (F:manimlib/config.py:298-299). `--pix_fmt yuv444p` → yuv444p [verified by run] |
| `-q, --quiet` | :133 | Turns off the file-writing progress bar and the `File ready at` log (F:manimlib/scene/scene_file_writer.py:232,340). The banner still appears [verified by run]. The window-mode Tips log also appears regardless of `-q` (F:manimlib/scene/scene.py:194-198, source evidence) |
| `-a, --write_all` | :138 | Renders every scene in the file (F:manimlib/extract_scene.py:95). It does not turn on `-w`, so `-a` alone opens a window and hangs. Use `-a -w` [verified by run] |
| `-o, --open` | :143 | Turns on `-w` and opens the result file when done. On Windows it uses `os.startfile` (F:manimlib/scene/scene_file_writer.py:363-364, source evidence) |
| `--finder` | :148 | Turns on `-w`. On Windows it opens the file itself, exactly like `-o` (same lines, source evidence) |
| `--subdivide` | :153 | Writes `videos/<Scene>/00000.mp4`, `00001.mp4` … per animation and does not create `<Scene>.mp4` (F:manimlib/scene/scene_file_writer.py:94-95,121-123) [verified by run] |
| `--file_name` | :159 | Replaces the scene name and the `-n` suffix. The extension is changed by `with_suffix` (F:manimlib/scene/scene_file_writer.py:88-92,104-105). So `v1.2` → `v1.mp4` and `x.mp4` → `x.mp4` [verified by run] |
| `-n, --start_at_animation_number` | :163 | §3.2 |
| `-e, --embed LINE` | :170 | Inserts `self.embed()` after that line and re-runs the module. If there is no scene name, it picks the nearest `class` above (F:manimlib/extract_scene.py:146-178). Without a window, `embed()` does nothing (F:manimlib/scene/scene.py:208). Source evidence |
| `-f, --full_screen` | :99 | Window mode only. Makes the window width the whole monitor (F:manimlib/window.py:108). Source evidence |
| `--always_on_top` | :104 | Window mode, Windows only. Exists only in the fork (F:manimlib/window.py:53-54,82-97). Source evidence |
| `-p, --presenter_mode` | :109 | Pauses with `hold_loop()` in `pre_play` of the first `play`/`wait` and at every `wait`. Released only by the space or → key in the window (F:manimlib/scene/scene.py:519-521,607-610,623-626,869-870). Combined with `-w`, which has no window, it never ends (§1) [verified by run] |
| `--leave_progress_bars` | :189 | `scene.leave_progress_bars=True` (F:manimlib/config.py:316-317). Source evidence |
| `--show_animation_progress` | :194 | Additionally shows a per-animation progress bar on stderr. `scene.py:129-130` tries to turn it off when the file-writing progress bar exists, but that bar is created in `file_writer.begin()` of `run()` after `Scene.__init__` finishes, so it is always absent at the check (F:manimlib/scene/scene.py:116,129-130,152, F:manimlib/scene/scene_file_writer.py:232-238). So both progress bars appear together even with `-w` [verified by run] |
| `--prerun` | :199 | Before rendering, runs once more in skip mode to count the total frames (F:manimlib/extract_scene.py:63-84). The progress bar shows like `46/150`, and exceptions occur before any file is written [verified by run] |
| `--video_dir DIR` | :205 | Changes the output folder (relative to cwd, created if missing). Takes precedence over `directories.base` (F:manimlib/config.py:393) [verified by run] |
| `--config_file PATH` | :209 | §5. Even if the path does not exist it is **silently ignored** and exits 0 (F:manimlib/config.py:343-348) [verified by run] |
| `-v, --version` | :213 | Used without a file, it prints only the banner and ends. With a file it is ignored and rendering proceeds (F:manimlib/__main__.py:53-57) [verified by run] |
| `--log-level` | :218 | Changes the logger level (F:manimlib/config.py:41). With `WARNING`, the `File ready` log disappears [verified by run] |
| `--clear-cache` | :222 | §6. Clears the entire disk cache, then runs as usual (F:manimlib/__main__.py:58-61) |
| `--autoreload` | :227 | `embed.autoreload=True` (F:manimlib/config.py:335-337). IPython embed only. Source evidence |

`-ql` is parsed as `-q -l`. There is no `-w`, so a window opens and hangs. `-sql` is the same [verified by run]. `-w -ql` quietly writes an 854x480 video [verified by run].

## 3. Meanings verified by running

### 3.1 Resolution and fps (ffprobe, 1-second scene) [verified by run]

| Option | Result |
|---|---|
| (none) / `--hd` | 1920x1080, 30fps, h264, yuv420p |
| `-l` | 854x480, 30fps |
| `-m` | 1280x720 |
| `--uhd` | 3840x2160 |
| `-r 640x360` / `-r 1000x1000` | 640x360 / 1000x1000 |
| `-l -r 320x240` | 320x240 (`-r` wins) |
| `--fps 12` / `-l --fps 60` | 1920x1080 12fps / 854x480 60fps |

- If the aspect ratio changes, `FRAME_HEIGHT` stays 8 and `FRAME_WIDTH` follows the ratio (F:manimlib/constants.py:13-20).
  - `-r 1080x1920` gives 4.5, `-r 1000x1000` gives 8.0 [verified by run].
  - Make vertical videos with `-r 1080x1920`, and lay out the content for a width of 4.5.

### 3.2 `-n` (animation number) [verified by run]

- `play` and `wait` each use one number (`play` calls `pre_play`/`post_play` at F:manimlib/scene/scene.py:590,594, `wait` at :605,621). Numbers count from 0.
- `-n a` runs from number a to the end, and `-n a,b` runs from a up to but not including b. `EndScene` is raised in the `pre_play` of number b (F:manimlib/scene/scene.py:450-458).
- Everything before number a runs in skip mode (F:manimlib/scene/scene.py:127-128). Object placement is correct, but each skipped `play` calls `dt` updaters twice with dt=run_time, so if a time updater exists, the state at number a differs from the full render (last item of §7) [verified by run].
- The file names are `<Scene>_a.mp4` and `<Scene>_a_b.mp4` (F:manimlib/scene/scene_file_writer.py:109-115). They do not overwrite the full-render result `<Scene>.mp4`.
- The test scene has 0.5s, 1s, and 1.5s animations followed by `wait(2)` (5s in total). Results:

| Command | Result |
|---|---|
| `-n 2` | `A_2.mp4` 3.5s (numbers 2 and 3) |
| `-n 1,3` | `A_1_3.mp4` 2.5s (numbers 1 and 2) |
| `-n 0` | `A_0.mp4` 5s (the whole thing, but with a different name) |
| `-n 10` (out of range) | exit 0, but `A_10.mp4` is 261 bytes and has no video stream |
| `-sw -n 0,2` | `A_0_2.png`, the state just before animation number 2 (the circle that appears afterward is absent) |

### 3.3 Scene selection (`timeout 20`, stdin `</dev/null`) [verified by run]

| Case | Result |
|---|---|
| 1 scene, no name | Renders that scene, exit 0 |
| 1 scene, wrong name | Still renders that scene, exit 0 |
| 2 scenes, no name | A `1: A / 2: B` list and a `Select which scene to render` prompt appear. On EOF, exit 1 |
| 2 scenes, wrong name | `ERROR No scene named Nope found`, then the same prompt, exit 1 |
| 2 scenes, `2` on stdin | Renders B |
| `SCENES_IN_ORDER = [Q]` in the module | The candidates are replaced by that list (F:manimlib/extract_scene.py:116-117). If there is only one entry, `Q` is rendered even when `P` is specified |

- Candidates are `Scene` subclasses whose `__module__` **starts with** the file's module name (F:manimlib/extract_scene.py:35, prefix comparison). So scenes in `other.py` imported by `main.py` are left out, but scenes in `main_parts.py` become candidates [verified by run].
- `manimgl` puts neither the script folder nor the cwd on `sys.path` (F:manimlib/module_loader.py:40-49). To import a neighboring file, pass `PYTHONPATH=.`. Without it, it exits 1 with `ModuleNotFoundError` [verified by run].

### 3.4 Exit codes [verified by run]

| Case | exit | Files left |
|---|---|---|
| Normal | 0 | Result file |
| Exception inside `construct()` (with `-w`, `-sw`, and `--prerun` alike) | 1, traceback | With `-w`, `videos/<Scene>_temp.mp4` remains (with `--prerun` it fails in the prerun stage, so nothing remains). **The previous `<Scene>.mp4` is not deleted and stays as it was** |
| Module import error (`ModuleNotFoundError`) | 1 | None |
| A later scene among several fails | 1 | The earlier scenes' results and the failed scene's `_temp.mp4`. With `--prerun`, the prerun of every scene runs before rendering (F:manimlib/extract_scene.py:81-85,106-109), so the earlier scenes' results are not produced either [verified by run] |
| Unknown key in config (§5) | 1, `TypeError` | None |
| `-c` invalid color, unknown flag | 2 | None |
| Scene selection prompt + EOF | 1 | None |
| `--config_file` path missing, `-n` out of range | **0** | The config is ignored / an empty mp4 is created |

- In `Scene.run`, only `EndScene` and `KeyboardInterrupt` are caught (F:manimlib/scene/scene.py:155-164). Anything else propagates and the process fails.
- On Ctrl-C, the `_temp` file is not moved to its final name and the normal exit path is taken (F:manimlib/scene/scene.py:160-164, F:manimlib/scene/scene_file_writer.py:298-301). This is source evidence; the exit code was not checked.
- In scripts, judge success **by the exit code, not by whether a result file exists**. A failure still leaves an old result file behind.

### 3.5 Output streams [verified by run]

- The banner `ManimGL v1.7.2` and the rich log (`File ready at …`) go to stdout, and the tqdm progress bar goes to stderr (F:manimlib/logger.py:10).
- The progress bar refreshes its line with `\r`. Pass it through `tr '\r' '\n'` before grepping.
- rich wraps paths across several lines to fit the terminal width. With `COLUMNS=400` it comes out on one line.
  - Even so, do not parse the path; computing it with the rules in §4 is better.
- Without `--prerun`, the total frame count is unknown, so the progress bar shows only a count, like `15it`.

## 4. Output layout

| Item | Rule | Evidence |
|---|---|---|
| Folder | `--video_dir` > `<directories.base>/videos`. The default base is `""`, so it is `videos/` relative to cwd. Created if missing | F:manimlib/config.py:240-244,393, F:manimlib/utils/file_ops.py:20-23 [verified by run] |
| Video | `<Scene>.mp4` (default), `.mov` (`-t`), `.gif` (`-i`) | F:manimlib/config.py:371-378 [verified by run] |
| Last frame | `<Scene>.png` (`-sw`). Even without `-t` it is an RGBA PNG with alpha 255 | `png_mode` is only stored and never read (F:manimlib/config.py:281, F:manimlib/scene/scene_file_writer.py:55). `Camera.get_image` writes RGBA (F:manimlib/camera/camera.py:149-154) [verified by run] |
| `-n` | `<Scene>_a[_b].<ext>` | §3.2 |
| `--file_name X` | `X.<ext>`. Whatever follows the last `.` is replaced by the extension | §2 |
| `--subdivide` | `<Scene>/00000.mp4` … (animation number) | §2 |
| While writing | Writes to `<name>_temp.<ext>`, then moves it to the final name with `shutil.move` when done | F:manimlib/scene/scene_file_writer.py:205,299 |
| Overwriting | Overwrites without asking. ffmpeg gets `-y` and `move` replaces the file. Re-rendering changes the mtime and length | F:manimlib/scene/scene_file_writer.py:215,299 [verified by run] |
| `-a --file_name X` | All scenes write the same `X.<ext>` and overwrite each other | F:manimlib/scene/scene_file_writer.py:104-105, source evidence |

`directories.mirror_module_path: True` (default False, F:manimlib/default_config.yml:15) [verified by run]
- Without `removed_mirror_prefix` it fails with `TypeError: startswith first arg must be str or a tuple of str, not Dict` (F:manimlib/config.py:396). This is because the default yml has no such key.
- If the script's absolute path starts with the prefix, the output is `videos/<remaining path without .py>/<Scene>.png`. Example: `videos/w/one/Only.png`.
- If it does not match the prefix, the output is `videos/<file stem>/<Scene>.png` (F:manimlib/config.py:394-401).

With `directories.base: outbase`, it writes to `outbase/videos/` [verified by run]. The image and sound search folders (`raster_images`, `vector_images`, `sounds`) are also relative to base (F:manimlib/default_config.yml:24-29, F:manimlib/utils/images.py:20,28, F:manimlib/utils/sounds.py:14).

## 5. Config merging

Order (later wins):

1. The package's `manimlib/default_config.yml` (F:manimlib/config.py:34)
2. `custom_config.yml`. It is looked up **only in the cwd**, because it is a relative-path `open("custom_config.yml")` (F:manimlib/config.py:37). If you put it next to the script and run from another folder, it is ignored [verified by run]
3. `--config_file` (F:manimlib/config.py:38). Takes precedence over custom_config [verified by run]
4. CLI flags. `update_*_config` overrides (F:manimlib/config.py:43-49). `-l` beats the 640x360 resolution in custom_config [verified by run]
5. Scene class attributes `default_camera_config` / `default_file_writer_config`. **They take precedence over the CLI** (F:manimlib/scene/scene.py:58-59,89-98). A scene with `default_camera_config = dict(background_color="#00FF00", fps=10)` comes out with a green background at 10fps even if you pass `-c "#0000FF" --fps 24` [verified by run]

The merge is a recursive per-key merge (F:manimlib/utils/dict_ops.py:5).

Unknown keys [verified by run]:

| Location | Result |
|---|---|
| Top level (`foo: 1`), a new key under `directories` | Ignored |
| Under `scene:` (e.g. upstream `invert_zoom_scroll`) | `TypeError: Scene.__init__() got an unexpected keyword argument`, exit 1 |
| Under `camera:` (upstream `bundle_draws`, `draw_together`) | `TypeError: Camera.__init__() …`, exit 1 |
| Under `file_writer:` (upstream `crf`) | `TypeError: SceneFileWriter.__init__() …`, exit 1 |
| `tex.template: nosuch` | `WARNING Cannot recognize template nosuch, falling back to 'default'.` then renders normally (F:manimlib/utils/tex_file_writing.py:24-26) |
| Under `window:` | Passed as `Window(**manim_config.window)` in window mode (F:manimlib/__main__.py:31). By source evidence the same TypeError would occur |

`crf`, `bundle_draws`, `draw_together`, and `invert_zoom_scroll` exist only in upstream (U:manimlib/scene/scene_file_writer.py:52, U:manimlib/default_config.yml:56,59,87). If you use a config file written for upstream as is, rendering does not start.

## 6. Cache

| What | Where | Evidence |
|---|---|---|
| Tex→SVG, Text(markup)→SVG results | `diskcache`, using `appdirs.user_cache_dir("manim")` if `directories.cache` is empty. On Windows it is `%LOCALAPPDATA%\manim\manim\Cache\cache.db`. All projects share the same cache. Size limit 1GB | F:manimlib/utils/cache.py:17-18, F:manimlib/utils/directories.py:17-18, F:manimlib/utils/tex_file_writing.py:84, F:manimlib/mobject/svg/text_mobject.py:53-54 [verified by run: path] |
| Cache key | A string hash of the function name + all arguments. For Tex, the arguments are the whole document including the preamble, the compiler, and the progress message (`Writing …`) | F:manimlib/utils/cache.py:24, F:manimlib/utils/tex_file_writing.py:81,85 |
| LaTeX working folder | `<base>/latex_cache/` = **`latex_cache/` in the cwd** (`working.tex/.dvi/.log/.aux`). Created only on a cache miss | F:manimlib/default_config.yml:35, F:manimlib/utils/tex_file_writing.py:97-101. It appeared on the first render and did not reappear when rendering again after deleting it [verified by run] |
| Text SVG temp file | `%TEMP%/<hash>.svg` | F:manimlib/mobject/svg/text_mobject.py:78 |

`--clear-cache` [verified by run]
- It clears only the `diskcache` (F:manimlib/utils/cache.py:33-34). It does not touch the `latex_cache/` folder.
- Attach it to a render command: `manimgl main.py S -sw --clear-cache`. Tex is then recompiled, so `latex_cache/` is created again.
- Used alone, `--clear-cache` clears and then opens a `BlankScene` window and IPython.
- The cache is global, so other projects' caches disappear too. Those projects recompile on their next render.
- When to use: when a bad result such as an empty SVG remains in the cache (SKILL.md §8 cm-super).

## 7. Recipes (plugin workflow)

Run everything with `cd <project>/src/<video>`, because output goes to `videos/` in the cwd. When automating, add `</dev/null`. In a file with several scenes, a missing or wrong scene name does not stop at the prompt but ends with exit 1 (if there is 1 scene, that scene is rendered, §3.3).

```bash
# Check the last frame -> videos/<Scene>.png
uv run manimgl main.py <Scene> -sw </dev/null

# Check an intermediate state: just before animation k -> videos/<Scene>_0_k.png
uv run manimgl main.py <Scene> -sw -n 0,k </dev/null

# Draft 854x480 30fps -> videos/<Scene>.mp4
uv run manimgl main.py <Scene> -w -l </dev/null

# Final 1920x1080 30fps -> overwrites the same videos/<Scene>.mp4
uv run manimgl main.py <Scene> -w </dev/null

# Re-render one scene only: same quality options as the other scenes, pass only that scene name
uv run manimgl main.py <Scene> -w -l </dev/null || echo "FAILED: videos/<Scene>.mp4 is the old one"

# Repeat-check a segment only (does not overwrite the full result) -> videos/<Scene>_3_6.mp4
uv run manimgl main.py <Scene> -w -l -n 3,6 </dev/null

# Several scenes at once (always include -w)
uv run manimgl main.py Intro Body Outro -w -l </dev/null
```

- Judge success by the exit code. On failure, `<Scene>_temp.mp4` and the old `<Scene>.mp4` remain (§3.4).
- Scenes to be joined with `ffmpeg -f concat … -c copy` must have the same resolution, fps, and codec. Render them all with the same options (`-w -l` or `-w`).
- Do not use: `-p` (hangs), `-s` alone, `-ql`/`-sql` (no `-w`), `-a` alone, `-o`/`--finder` (an external player opens).
- If you need a transparent-background source, use `-w -t` → `.mov` (ProRes, `yuva444p12le`). This file cannot be mixed into an mp4 concat.
- With `-s`, for every `play`, `dt` updaters are called **twice** with dt=run_time. Once in `update_frame` of the progress loop (F:manimlib/scene/scene.py:474-475,557-564), and once in `finish_animations` (F:manimlib/scene/scene.py:571-572). `wait` is called once. So time updaters advance further in `-sw` than in the video, and the last frame may differ from the video's last frame [verified by run: during `play(run_time=1)`, the `increment_value(dt)` accumulation is 2.0 with `-sw` and 1.0 with `-w`].
