"""d/dt e^t = e^t with a moving tangent; the e^{st} family; e^{(a+bi)t} as a spiral.

Source: adithya-s-k/manim_skill @cef0450, skills/manimgl-best-practices/examples/exponential_derivative.py
(itself adapted from 3b1b's Laplace transform video, 2025).
License: CC BY-NC-SA 4.0 — original by Grant Sanderson (3Blue1Brown), adapted by Adithya S Kolavi,
modified for the CodingVillainKor/manimgl fork by manimgl-skill.
Changes: graphs kept inside their axes; Tex parts via isolate=/t2c=; spiral s label tracker-driven, old trail dimmed.
Render: uv run manimgl exponential_derivative.py ExpDerivative ExpFamilyGraph ComplexExpSpiral -w -l
(ComplexExpSpiral runs on a dt updater + TracedPath, so judge it from the mp4, not the -sw PNG.)
"""
from manimlib import *


class ExpDerivative(InteractiveScene):
    def construct(self):
        ## Axes and e^t, cut at the top of the axes (e^4 = 55 would leave the frame)
        axes = Axes(x_range=(-1, 4), y_range=(0, 20), width=10, height=6)
        axes.to_edge(RIGHT)
        t_label = Tex("t")
        t_label.next_to(axes.x_axis.get_right(), UL, MED_SMALL_BUFF)
        axes.add(t_label)

        graph = axes.get_graph(np.exp, x_range=(-1, np.log(20)))
        graph.set_stroke(BLUE, 3)

        title = Tex(R"\frac{d}{dt} e^t = e^t", t2c={"t": GREY_B}, font_size=60)
        title.to_edge(UP)
        title.match_x(axes.c2p(1.5, 0))
        self.add(axes, graph, title)

        ## Height e^t at a tracked point (i2gp uses graph.underlying_function, so it works past the cut)
        t_tracker = ValueTracker(1)
        get_t = t_tracker.get_value
        v_line = always_redraw(
            lambda: axes.get_v_line_to_graph(get_t(), graph, line_func=Line).set_stroke(RED, 3)
        )
        height_label = Tex(R"e^t", font_size=42)
        height_label.always.next_to(v_line, RIGHT, SMALL_BUFF)
        height_label_height = height_label.get_height()
        height_label.add_updater(lambda m: m.set_height(min(height_label_height, 0.7 * v_line.get_height())))

        self.play(
            ShowCreation(v_line, suspend_mobject_updating=True),
            FadeIn(height_label, UP, suspend_mobject_updating=True),
        )
        self.wait()

        ## Tangent line, a run of 1, and the rise over it
        tangent_line = always_redraw(
            lambda: axes.get_tangent_line(get_t(), graph, length=10).set_stroke(BLUE_A, 1)
        )
        unit_size = axes.x_axis.get_unit_size()
        unit_line = Line(axes.c2p(0, 0), axes.c2p(1, 0))
        unit_line.add_updater(lambda m: m.move_to(v_line.get_end(), LEFT))
        unit_line.set_stroke(WHITE, 2)
        unit_label = Integer(1, font_size=24)
        unit_label.add_updater(lambda m: m.next_to(unit_line.pfp(0.6), UP, 0.5 * SMALL_BUFF))
        tan_v_line = always_redraw(
            lambda: v_line.copy().shift(v_line.get_vector() + unit_size * RIGHT)
        )

        # Parts selected later are listed in isolate= (post-hoc selection counts source symbols)
        deriv_label = Tex(R"\frac{d}{dt} e^t = e^t", isolate=[R"\frac{d}{dt}", "e^t"], font_size=42)
        deriv_label[R"\frac{d}{dt}"].scale(0.75, about_edge=RIGHT)
        deriv_label_height = deriv_label.get_height()
        deriv_label.add_updater(lambda m: m.set_height(min(deriv_label_height, 0.8 * v_line.get_height())))
        deriv_label.always.next_to(tan_v_line, RIGHT, SMALL_BUFF)

        self.play(ShowCreation(tangent_line, suspend_mobject_updating=True))
        self.play(
            VFadeIn(unit_line),
            VFadeIn(unit_label),
            VFadeIn(tan_v_line, suspend_mobject_updating=True),
            TransformFromCopy(title, deriv_label),
        )

        ## The rise equals the height: swing a copy of the height line onto it
        self.play(
            ReplacementTransform(v_line.copy().clear_updaters(), tan_v_line, path_arc=45 * DEG),
            FadeTransform(height_label.copy(), deriv_label["e^t"][1], path_arc=45 * DEG, remover=True),
        )
        self.wait()

        ## Same relation everywhere
        for t in [2.2, 0, 1, 2]:
            self.play(t_tracker.animate.set_value(t), run_time=4)
        self.wait()


class ExpFamilyGraph(InteractiveScene):
    def construct(self):
        ## Axes and a graph bound to e^{st}
        axes = Axes(x_range=(-1, 8), y_range=(-1, 5), width=FRAME_WIDTH - 2, height=FRAME_HEIGHT - 2)
        axes.to_edge(DOWN)

        s_tracker = ValueTracker(0.2)
        get_s = s_tracker.get_value
        graph = axes.get_graph(np.exp)
        graph.set_stroke(BLUE, 3)
        axes.bind_graph_to_func(graph, lambda t: np.exp(get_s() * t))

        ## Labels; the s readout follows the tracker
        label = Tex(R"e^{st}", t2c={"s": YELLOW}, font_size=90)
        label.move_to(UP)
        s_label = Tex(R"s = 0.20", t2c={"s": YELLOW}, font_size=48)
        s_value = s_label.make_number_changeable("0.20")
        s_value.f_always.set_value(get_s)
        s_label.to_corner(UR)
        self.add(axes, label, s_label)

        self.play(ShowCreation(graph, suspend_mobject_updating=True))
        self.wait()

        ## Decay, constant, growth (s <= 0.2 keeps e^{8s} under the y max of 5)
        self.play(s_tracker.animate.set_value(-1), graph.animate.set_color(YELLOW), run_time=4)
        self.wait()
        self.play(s_tracker.animate.set_value(0), run_time=2)
        self.wait()
        self.play(s_tracker.animate.set_value(0.1), graph.animate.set_color(GREEN), run_time=2)
        self.wait()
        self.play(s_tracker.animate.set_value(0.2), run_time=2)
        self.wait(2)


class ComplexExpSpiral(InteractiveScene):
    def construct(self):
        ## Complex plane on the left, labels in the right half
        plane = ComplexPlane(
            x_range=(-3, 3),
            y_range=(-3, 3),
            background_line_style=dict(stroke_color=BLUE, stroke_width=1),
        )
        plane.set_height(7)
        plane.to_edge(LEFT)
        plane.add_coordinate_labels(font_size=20)

        s_tracker = ComplexValueTracker(-0.1 + 1j)
        get_s = s_tracker.get_value
        t_tracker = ValueTracker(0)
        get_t = t_tracker.get_value

        exp_label = Tex(R"e^{st}", t2c={"s": YELLOW}, font_size=72)
        s_label = VGroup(
            Tex("s =", t2c={"s": YELLOW}, font_size=48),
            DecimalNumber(get_s(), hide_zero_components_on_complex=False, font_size=48),
        )
        s_label.arrange(RIGHT, buff=0.2)
        s_label[1].f_always.set_value(get_s)
        labels = VGroup(exp_label, s_label).arrange(DOWN, buff=0.6)
        labels.move_to((plane.get_right() + RIGHT_SIDE) / 2)
        self.add(plane, labels)

        ## Point e^{st}, vector from 0, traced trail
        def get_z():
            return plane.n2p(np.exp(get_s() * get_t()))

        dot = GlowDot(color=TEAL)
        dot.add_updater(lambda m: m.move_to(get_z()))
        vector = Vector().set_color(YELLOW)
        vector.add_updater(lambda m: m.put_start_and_end_on(plane.n2p(0), get_z()))
        path = TracedPath(dot.get_center, stroke_color=TEAL, stroke_width=2)
        self.add(vector, path, dot)

        ## t runs on a dt updater (second parameter must be named dt)
        t_tracker.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(t_tracker)
        self.wait(8)

        ## Stop, freeze the old trail, rewind t, change s
        t_tracker.clear_updaters()
        path.clear_updaters()  # TracedPath re-applies its stroke every update; dim only after this
        self.play(t_tracker.animate.set_value(0), path.animate.set_stroke(opacity=0.3), run_time=2)
        self.play(s_tracker.animate.set_value(0.1 + 1.5j))

        ## New trail for the new s
        path = TracedPath(dot.get_center, stroke_color=GREEN, stroke_width=2)
        self.add(path)
        t_tracker.add_updater(lambda m, dt: m.increment_value(dt))
        self.wait(8)
