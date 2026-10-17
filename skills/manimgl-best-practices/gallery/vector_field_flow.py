"""
Vector fields and particles carried along them (the core visual of flow matching / diffusion).

Source: adithya-s-k/manim_skill @cef0450, skills/manimgl-best-practices/examples/vector_fields.py
License: CC BY-NC-SA 4.0 — by Adithya S Kolavi, inspired by 3Blue1Brown (Grant Sanderson)
(source header: 'Inspired by 3b1b's vector field visualizations'),
modified for the CodingVillainKor/manimgl fork by manimgl-skill.
Changes: stroke_color added to background_line_style (KeyError otherwise); Dot colors via set_color;
magnitude colors clipped to [0, 1]; particles integrated by sub-stepped paths so -sw matches the video;
ParticleFlow starts spread over radii; GradientFieldDemo dropped; native VectorField/StreamLines scene added
(seeded inside construct).

Render: uv run manimgl vector_field_flow.py VFParticleFlow -w -l   (-sw for the last frame)
"""
from manimlib import *

# Passing background_line_style replaces the whole default dict, and NumberPlane reads its stroke_color
PLANE_STYLE = dict(stroke_color=BLUE_D, stroke_opacity=0.3)


def flow_path(func, start, max_step=1 / 30):
    """Path that grows along func (point -> velocity) by Euler steps of at most max_step seconds.

    In -sw a dt updater gets dt = the whole wait time once, so a single Euler step would fling the
    particle off-screen; sub-stepping makes the -sw PNG match the video's last frame.
    """
    # shortcut: in -sw a play() calls dt updaters twice with dt=run_time, so only wait() while paths
    # grow; to grow during a play, drive the path from a ValueTracker instead of dt
    path = VMobject().start_new_path(start)

    def grow(path, dt):
        n = int(np.ceil(dt / max_step))
        for _ in range(n):
            end = path.get_last_point()
            path.add_line_to(end + func(end) * dt / n)

    path.add_updater(grow)
    return path


def particle_on(path, radius, color):
    """Dot that sits on the growing end of path; add it to the scene after the path."""
    dot = Dot(radius=radius).set_color(color)  # Dot(color=) stays white
    return dot.add_updater(lambda m: m.move_to(path.get_last_point()))


class VFSimpleVectorField(Scene):
    def construct(self):
        ## Rotation field F = (-y, x) as a hand-rolled arrow grid
        plane = NumberPlane((-4, 4, 1), (-3, 3, 1), background_line_style=PLANE_STYLE)
        self.add(plane)

        arrows = VGroup()
        for x in np.arange(-3.5, 4, 0.7):
            for y in np.arange(-2.5, 3, 0.7):
                vx, vy = -y * 0.15, x * 0.15
                if abs(vx) < 0.01 and abs(vy) < 0.01:
                    continue
                arrow = Arrow([x, y, 0], [x + vx, y + vy, 0], buff=0, max_tip_length_to_length_ratio=0.3)
                # interpolate_color with alpha > 1 gives NaN channels, drawn white
                arrow.set_color(interpolate_color(BLUE, YELLOW, min(np.hypot(vx, vy) / 0.5, 1)))
                arrows.add(arrow)

        self.play(LaggedStartMap(GrowArrow, arrows, lag_ratio=0.02, run_time=2))
        self.wait()

        ## A particle carried by the field, with its trail
        path = flow_path(lambda p: 0.5 * np.array([-p[1], p[0], 0]), 2 * RIGHT + UP)
        path.set_stroke(RED, 2)
        self.add(path, particle_on(path, 0.1, RED))
        self.wait(8)


class VFParticleFlow(Scene):
    def construct(self):
        ## Vortex field: unit-speed rotation, so inner particles lap the outer ones
        plane = NumberPlane((-5, 5, 1), (-4, 4, 1), background_line_style=PLANE_STYLE)
        self.add(plane)

        def vortex(p):
            r = np.hypot(p[0], p[1]) + 0.1
            return 0.8 * np.array([-p[1], p[0], 0]) / r

        n = 15
        paths = VGroup()
        dots = VGroup()
        for i in range(n):
            angle = i * TAU / n
            start = (0.6 + 0.2 * i) * np.array([np.cos(angle), np.sin(angle), 0])
            path = flow_path(vortex, start).set_stroke(BLUE, 1.5, 0.7)
            paths.add(path)
            dots.add(particle_on(path, 0.08, YELLOW))

        self.add(paths, dots)
        self.wait(10)


class VFElectricDipole(Scene):
    def construct(self):
        ## Two point charges
        q1_pos = np.array([-2, 0, 0])
        q2_pos = np.array([2, 0, 0])
        q_plus = Dot(q1_pos, radius=0.25).set_color(RED)
        q_minus = Dot(q2_pos, radius=0.25).set_color(BLUE)
        q_plus_label = Tex("+", font_size=36).move_to(q1_pos)
        q_minus_label = Tex("-", font_size=36).move_to(q2_pos)
        self.add(q_plus, q_plus_label, q_minus, q_minus_label)

        ## Field arrows: E = r1/|r1|^3 - r2/|r2|^3, drawn at capped length, colored by magnitude
        arrows = VGroup()
        for x in np.arange(-4, 4.5, 0.6):
            for y in np.arange(-3, 3.5, 0.6):
                pos = np.array([x, y, 0])
                if min(np.linalg.norm(pos - q1_pos), np.linalg.norm(pos - q2_pos)) < 0.5:
                    continue
                r1 = pos - q1_pos
                r2 = pos - q2_pos
                E = r1 / (np.linalg.norm(r1) + 0.1) ** 3 - r2 / (np.linalg.norm(r2) + 0.1) ** 3
                mag = np.linalg.norm(E)
                if mag < 0.001:
                    continue
                arrow = Arrow(pos, pos + E / mag * min(0.4, mag * 2), buff=0)
                arrow.set_color(interpolate_color(BLUE_E, YELLOW, min(mag * 5, 1)))
                arrows.add(arrow)

        self.play(LaggedStartMap(GrowArrow, arrows, lag_ratio=0.01, run_time=3))
        self.wait()


class VFNativeStreamLines(Scene):
    def construct(self):
        np.random.seed(0)  # first line: StreamLines/AnimatedStreamLines draw np.random noise (vector_field.py:415,468)
        ## The fork's own VectorField / StreamLines / AnimatedStreamLines (manimlib/mobject/vector_field.py)
        plane = NumberPlane((-7, 7, 1), (-4, 4, 1), background_line_style=PLANE_STYLE)

        def spiral_sink(coords):
            # VectorField passes (N, 2) arrays; StreamLines passes one (2,) state and a p2c tuple
            x, y = np.asarray(coords).T
            return np.array([-y - 0.3 * x, x - 0.3 * y]).T

        field = VectorField(spiral_sink, plane, density=1, stroke_opacity=0.5)
        lines = StreamLines(spiral_sink, plane, density=1, magnitude_range=(0, 6))
        self.add(plane)
        self.play(FadeIn(field))
        self.add(AnimatedStreamLines(lines))
        self.wait(6)
