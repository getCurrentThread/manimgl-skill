# Interactive preview: embed shell, checkpoint_paste, reload (fork @455a420)

- For a person iterating in the preview window. The plugin workflow renders with `-w`/`-sw` and never needs this.
- Everything here needs a window, so no `-w`. Without a window, `self.embed()` returns at once (F:manimlib/scene/scene.py:208-210).
- `F:` paths are relative to the fork repository root. `U:` is 3b1b/manim @fafa083.
- [verified by run] Same environment as cli-and-output.md. The shell was driven by piped stdin (§5). Window-mode runs opened a real preview window.

## 1. self.embed()

- Opens an IPython shell at that point in `construct`.
- Leaving the shell (`exit()`, Ctrl+D, stdin EOF) **ends the scene**. `embed(close_scene_on_exit=True)` raises `EndScene` (F:manimlib/scene/scene.py:217-219).
  - In the window, nothing after the first `self.embed()` runs. In a `-w` render it all runs [verified by run: a file write after `self.embed()` happened with `-w`, not in the window].
  - So only the first embed point in a `construct` is ever reached.
  - `self.embed(close_scene_on_exit=False)` goes on with `construct` after the shell closes. The window then stays open until you close it (F:manimlib/scene/scene.py:186-201) [verified by run: the file write ran, then the process stayed up until `timeout` killed it, exit 124].
- Call it directly in `construct`. The shell takes the locals of the frame three levels up (F:manimlib/scene/scene_embed.py:45,49). Called from a helper method, it shows the helper's locals, not those of `construct` [verified by run].
- Opening the shell runs the scene file again as a new module (F:manimlib/scene/scene_embed.py:48, F:manimlib/module_loader.py:40-50).
  - Module-level code runs again, and the shell sees fresh copies of module-level objects. A module-level list that `construct` appended to is empty in the shell [verified by run].
  - Keep anything you want to inspect in `construct` locals.

### What the shell has

- The module's globals, the locals of `construct` (including `self`), and these shortcuts (F:manimlib/scene/scene_embed.py:59-80): `play`, `wait`, `add`, `remove`, `remove_all_except`, `clear`, `focus`, `save_state`, `undo`, `redo`, `i2g`, `i2m`, `checkpoint_paste`, `clear_checkpoints`, `reload`.

| Written (old manimgl docs) | Fork | Evidence |
|---|---|---|
| `touch()` | not defined. Use the window keys (§4). Upstream @fafa083 has no `touch` either | [verified by run: `touch` not in the shell globals] |
| `frame` | not defined. Use `self.frame` | [verified by run] |
| `restore()` after `self.save_state()` | not defined. Scene `save_state()` pairs with `undo()`/`redo()` | [verified by run] |

- `save_state()` pushes a snapshot of the whole scene. It skips the push if nothing changed, and keeps at most 50 (F:manimlib/scene/scene.py:57,666-673).
  - `undo()` goes back one snapshot and `redo()` forward again (:675-683).
  - This is not `mob.save_state()` + `Restore(mob)`, which work on one mobject.
- `clear()` and `remove_all_except()` also remove `self.frame`, so frame updaters such as ambient rotation stop (SKILL.md §9).
- `i2g(...)`/`i2m(...)` turn `id()` values into mobjects (F:manimlib/scene/scene.py:433-446).
- An exception in a cell prints the traceback and flashes a red border. The shell stays open (F:manimlib/scene/scene_embed.py:102-111) [verified by run: an `IndentationError` played the red `FullScreenRectangle` flash, and the next cells ran].
  - The traceback style is `embed.exception_mode` (default `Verbose`, F:manimlib/default_config.yml:96). Source evidence.

## 2. checkpoint_paste()

- Runs the clipboard text as a shell cell (pyperclip, F:manimlib/scene/scene_embed.py:200-212). The pasted code can use the shortcuts (`play(...)`) or `self.`.
- **Checkpoint key**: the first line of the clipboard, if it is a comment (F:manimlib/scene/scene_embed.py:214-219).
  - The first paste of a key saves the scene state under it.
  - Pasting a block with the same first line again first **reverts** to that state, and drops the keys saved after it (:221-234).
  - Without a leading comment, the block just runs again and the changes add up [verified by run: `# move` + `c.shift(RIGHT)` pasted twice gives x=1; `c.shift(RIGHT)` pasted twice adds 2].
  - So copy each block starting at its `## ...` line (house style has one per block). Editing the comment text makes a new key, and nothing reverts. `clear_checkpoints()` forgets all keys.
  - imcommit's `_mhelper.py` copies from the last `##` line, so it uses this key (imcommit-patterns.md).
- A revert calls `mob.become(saved_copy)` on the same objects, and also rewinds `self.time` and `num_plays` (F:manimlib/scene/scene.py:933-939).
  - Names in the shell still point at the right mobjects.
  - Mobjects added after the checkpoint leave the scene. Source evidence.
- Copy whole lines.
  - A block indented 8 spaces (copied from inside `construct`), an indented `## block` line, and CRLF line endings all work [verified by run].
  - A selection that starts mid-line (first line unindented, the rest indented) fails with `IndentationError` and a red flash [verified by run].
  - The fork lacks upstream's `textwrap.dedent` step (U:manimlib/scene/scene_embed.py:217-220).

| Call | Effect | Evidence |
|---|---|---|
| `checkpoint_paste(skip=True)` | Animations jump to their end state. `self.time` still moves on by their run_time. dt updaters run twice per play (cli-and-output.md §7) | F:manimlib/scene/scene.py:714-722 [verified by run: a 1 s play moved `self.time` by 1.0; a 2 s play advanced a dt tracker by 4.0 instead of 2.0] |
| `checkpoint_paste(record=True)` | Writes only what this paste plays to `videos/inserts/<Scene>_<n>.mp4`. n is the first unused number, so nothing is overwritten | F:manimlib/scene/scene_file_writer.py:245-260 [verified by run: two calls gave `CP_0.mp4`, `CP_1.mp4`] |

- With no resolution flag, an insert is 1920x1080, 30fps, h264, yuv420p [verified by run: ffprobe]. So it concatenates with final `-w` renders, not with `-l` drafts.
- Typical loop:
  1. Put `self.embed()` just before the block you are working on, and run without `-w`.
  2. Edit the block in the editor. Copy it from its `##` line to the end.
  3. Call `checkpoint_paste()` in the shell. Each repeat reverts first.
  4. The `self.embed()` can stay. A `-w` render ignores it and runs the block. Before `reload(N)` to a later block, move this `self.embed()` down (§3).

## 3. -e / -se and reload()

- `-e N` inserts `self.embed()` after line N of the file, then runs the module again (F:manimlib/extract_scene.py:146-178).
  - The indent is that of the nearest non-empty line at or above N, plus 4 if that line ends with `:` (:128-143).
  - Without a scene name, it uses the nearest `class` line above N (:165-171) [verified by run].
  - Everything after line N is skipped, because the embed ends the scene (§1) [verified by run].
  - With `-w` it does nothing: the whole scene renders [verified by run].
  - Module-level code runs three times: import, the `-e` re-exec, and the shell's module (§1) [verified by run].

| `-e N` where line N is | Result [verified by run] |
|---|---|
| the last line of a complete statement in `construct` | shell opens after it, exit 0 when it closes |
| the first line of a multi-line call (`self.play(`) | `SyntaxError`, exit 1 |
| the last argument line of a multi-line call, ending in `,` | no error: the embed becomes an argument, so the shell opens before that call runs, exit 0 |
| at module level | `NameError: name 'self' is not defined`, exit 1 |
| missing (`-e` alone) | exit 2, `argument -e/--embed: expected one argument` |

- `-se N` is `-s -e N`. The animations before line N are skipped, not played, and the shell opens with the same mobject positions (`embed()` calls `stop_skipping()`, F:manimlib/scene/scene.py:212) [verified by run: with a 4 s play before N, wall time went from 7 s to 3 s, same object position].
  - dt updaters are the exception: each skipped `play` calls them twice with dt=run_time (cli-and-output.md §7), so a clock or ambient rotation is further along than with `-e N` or in a `-w` render [verified by run: after a 2 s play and a 1 s wait, a dt-driven `ValueTracker` read 5.0 at the shell with `-se`, 3.0 with `-e`].
- `reload()` in the shell checks the file's syntax, then runs it again with the same CLI arguments in the same window (F:manimlib/scene/scene_embed.py:138-176, F:manimlib/__main__.py:34-44) [verified by run].
  - A syntax error in the file cancels the reload and keeps the shell (F:manimlib/scene/scene_embed.py:165-167) [verified by run].
  - Anything else ends the session with exit 1 and closes the window: an N that gives `SyntaxError` with `-e N` (table above), or any exception the re-run raises before it reaches the embed. `run_scenes` catches only `KillEmbedded` and `KeyboardInterrupt` (F:manimlib/__main__.py:41-46) [verified by run: `reload(6)` on a `self.play(` line, and a `NameError` after an edit, both gave exit 1].
  - `reload(N)` adds a `self.embed()` after line N, as `-e N` does (F:manimlib/extract_scene.py:157-158). The file's own `self.embed()` stays, so N only takes effect when it is above the file's first embed. Otherwise the re-run stops at the file's embed [verified by run: own embed at line 6, `reload(9)` reopened at line 6; own embed at line 10, `reload(7)` reopened after line 7].
  - **N sticks.** A later plain `reload()` inserts at N again (F:manimlib/scene/scene_embed.py:172-173) [verified by run]. To jump to a later block, delete or move the earlier `self.embed()` first, or restart `manimgl`.
- `--autoreload` (or `embed: {autoreload: true}`) imports the file again before every cell, so edited helpers in other files are picked up (F:manimlib/scene/scene_embed.py:178-184, F:manimlib/config.py:335-337). Source evidence.

## 4. Window keys

`Scene` (F:manimlib/scene/scene.py:749-870; letters from F:manimlib/default_config.yml:118-134):

| Input | Effect | Evidence |
|---|---|---|
| hold `d` + move the mouse | orbit (θ, φ) | :751-755 |
| hold `c` + move the mouse | orbit, and φ can go below 0 (fork only) | :758-761 |
| hold `e` + move the mouse | yaw about the screen's up axis (fork only) | :767-771 |
| hold `f` + move the mouse, or drag | pan | :773-774, :784-785 |
| scroll | zoom about the cursor. `z` is not zoom, although the startup Tips log names it | :815-831, :194-197 |
| `r` | animate the frame back to its default state: orientation, centre and height (F:manimlib/camera/camera_frame.py:62-66), so pan and zoom are reset too | :859-860 |
| Ctrl+Z | `undo()`. A plain `Scene` pushes no snapshot unless you call `save_state()` | :861-862 |
| Ctrl+Shift+Z | also `undo()`: the undo branch matches first | :861-862 [verified by run] |
| Shift+Z | `redo()`. In an `InteractiveScene`, the z-grab `save_state()` that follows (F:manimlib/scene/interactive_scene.py:534-536) empties the redo stack, so only one step comes back | :863-864 [verified by run: headless key calls] |
| Ctrl+Q | quit | :866-867 |
| space / → | release a presenter-mode (`-p`) hold | :869-870 |

`InteractiveScene` adds (F:manimlib/scene/interactive_scene.py:477-536). Source evidence:
- `s`: select (hold Shift too and move to sweep). `u`: unselect.
- `g`/`h`/`v`/`z`: grab freely / along x / y / z. Each grab key also calls `save_state()` (:534-536).
- Ctrl+Z / Ctrl+Shift+Z: `z` is also the z-grab key, so after the undo the scene calls `save_state()` (:534-536). This pushes the restored state back and empties the redo stack. In an `InteractiveScene`, Ctrl+Z goes back only one step, and `redo()` afterwards does nothing. For more steps, call `undo()` in the shell [verified by run: 3 snapshots, three Ctrl+Z presses all stayed one step back, redo stack 0; a plain `Scene` went back three steps].
- `c`: colour palette for the selection. It shares the key with the `c` orbit (fork-diff.md).
- `i`: info. `k`: crosshair.
- Ctrl+C copies the shell names of the selected mobjects (the `id()` for unnamed ones). Ctrl+V duplicates mobjects only when the clipboard holds ids. Any other clipboard text is added as a new `Text` (`Tex` if it contains one of `\^=+`), so Ctrl+C/Ctrl+V on a named mobject adds its name as text, and Ctrl+X deletes it (F:manimlib/scene/interactive_scene.py:360-398) [verified by run].
- Backspace deletes, Ctrl+A selects all. Arrow keys nudge (Shift = 10x).

### Recording a camera angle

- Shift+D (InteractiveScene) copies a `reorient(...)` call for the current frame to the clipboard (F:manimlib/scene/interactive_scene.py:631-645). Paste it after `self.frame.` or `self.frame.animate.`.
  - If the frame centre is exactly the origin and the height is not 8 (e.g. `set_height(12)` or `reorient(..., ORIGIN, 10)`, then orbiting with `d`), the copied call leaves out the centre but keeps the height: `reorient(-22, 63, 0, 12.00)`. Pasted, 12.00 lands in the `center` slot, so the frame moves to (12, 12, 12) and keeps height 8 (F:manimlib/scene/interactive_scene.py:640-643, F:manimlib/camera/camera_frame.py:211-217) [verified by run]. Write `ORIGIN, ` before the height when you paste: `reorient(-22, 63, 0, ORIGIN, 12.00)` [verified by run]. Upstream does the same (U:manimlib/scene/interactive_scene.py:643-646).
  - Angles are cut toward zero (`astype(int)`, :638). A frame at θ = -29.6 comes out as `-29`, and so does an exact `reorient(-30, ...)` (float error) [verified by run]. Upstream's `%d` does the same (U:manimlib/scene/interactive_scene.py:642).
  - With numpy 2, the center prints as `(np.float32(1.5), np.float32(-0.25), np.float32(0.0))` (:641) [verified by run, numpy 2.2.6]. It runs under `from manimlib import *` but is noisy. Upstream formats it with `%.2f` (U:manimlib/scene/interactive_scene.py:644).
  - Shift+C (cursor point, :647-648) has the same `np.float64(...)` noise [verified by run].
- For exact values, type in the shell: `self.frame.get_euler_angles() / DEG`, `self.frame.get_center()`, `self.frame.get_height()`.
  - `get_theta()` and `get_phi()` return **radians**, while `reorient` takes degrees (F:manimlib/camera/camera_frame.py:68-92,211-228) [verified by run: after `reorient(-29.6, 70.9)`, `get_theta()` = -0.5166].

## 5. Checking without a person

- Pipe the shell commands in: `printf 'print(self.time)\nexit()\n' | uv run manimgl main.py S`. A non-tty stdin gives IPython's simple prompt [verified by run].
  - IPython then prints `Cannot install event loop hook for "manim"`. The window still redraws after each cell (F:manimlib/scene/scene_embed.py:94-100). Source evidence.
- To test `checkpoint_paste` without touching the user's clipboard, put `pyperclip.paste = lambda: CODE` in the probe file [verified by run].
- Never run a window-mode probe with stdin at EOF and read exit 0 as success: the shell exits at once and nothing is written (cli-and-output.md §1).
