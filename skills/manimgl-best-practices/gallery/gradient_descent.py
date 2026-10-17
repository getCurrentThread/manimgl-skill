"""Gradient descent on a 2D loss (level sets) and on a 3D loss surface.

Source: adithya-s-k/manim_skill @cef0450, skills/manimgl-best-practices/examples/gradient_descent_basic.py
License: CC BY-NC-SA 4.0 — original by Grant Sanderson (3Blue1Brown), adapted by Adithya S Kolavi,
modified for the CodingVillainKor/manimgl fork by manimgl-skill.
Changes: exact level sets through axes.c2p and the true gradient (the source drew axis-aligned ellipses
and used 0.15 for the 0.3xy term), .set_color() where color= is ignored, DecimalNumber/Integer counters
instead of rebuilt Text, axes that fit the frame, self.frame.reorient, surface colored by height,
ball drawn before the translucent surface.

Render: uv run manimgl gradient_descent.py GradientDescentBasic GradientDescent3D -w -l   (-sw for the last frames)
"""
from manimlib import *


def loss_2d(x, y):
    return 0.5 * x**2 + 0.8 * y**2 + 0.3 * x * y


def loss_3d(x, y):
    return 0.3 * x**2 + 0.4 * y**2


class GradientDescentBasic(Scene):
    def construct(self):
        ## Weight space on the left, title and readouts on the right
        axes = Axes(x_range=(-3, 3, 1), y_range=(-3, 3, 1), width=6.5, height=6.5).to_edge(LEFT)
        # w_1 right of the axis end: the default DL spot sits on the outer contour
        labels = VGroup(axes.get_x_axis_label("w_1", direction=RIGHT), axes.get_y_axis_label("w_2"))
        title = Text("Gradient Descent", font_size=54).to_corner(UR)

        ## Level sets L = c. L is a quadratic form, so along direction u the radius is sqrt(c / L(u))
        def level_set(c):
            def point(t):
                u = np.array([np.cos(t), np.sin(t)])
                return axes.c2p(*np.sqrt(c / loss_2d(*u)) * u)
            return ParametricCurve(point, t_range=(0, TAU, TAU / 120))

        levels = np.linspace(0.75, 3.75, 5)  # 0.75 leaves room for the label, 3.75 still fits the +-3 axes
        contours = VGroup(*(
            level_set(c).set_stroke(interpolate_color(BLUE, RED, a), 2, 0.7)
            for c, a in zip(levels, np.linspace(0, 1, len(levels)))
        ))

        self.play(FadeIn(title))
        self.play(FadeIn(axes), FadeIn(labels))
        self.play(LaggedStartMap(FadeIn, contours, lag_ratio=0.1))

        ## Minimum and start. Dot/Text ignore color=, so set_color after construction
        min_dot = Dot(axes.c2p(0, 0)).set_color(GREEN)
        # UL: clear of both axes and of the path, which arrives from the lower right
        min_label = Text("Minimum", font_size=20).set_color(GREEN).next_to(min_dot, UL, buff=0.08)
        self.play(FadeIn(min_dot, scale=2), FadeIn(min_label))

        start = np.array([2.5, -2.0])
        dot = Dot(axes.c2p(*start)).set_color(YELLOW).set_z_index(1)  # z_index keeps it above the arrows
        start_label = Text("Start", font_size=24).next_to(dot, UR, buff=0.1)
        self.play(FadeIn(dot, scale=2), FadeIn(start_label))

        ## Path with the exact gradient (x + 0.3y, 1.6y + 0.3x)
        lr = 0.2
        path = [start]
        for _ in range(16):
            x, y = path[-1]
            path.append(path[-1] - lr * np.array([x + 0.3 * y, 1.6 * y + 0.3 * x]))

        ## Readouts: numbers update in place instead of rebuilding Text each step
        iter_num = Integer(0, font_size=30)
        loss_num = DecimalNumber(loss_2d(*start), num_decimal_places=3, font_size=30)
        info = VGroup(
            VGroup(Text("Iteration:", font_size=30), iter_num).arrange(RIGHT, buff=0.15),
            VGroup(Text("Loss:", font_size=30), loss_num).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, aligned_edge=LEFT).next_to(title, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(FadeIn(info), FadeOut(start_label))

        ## One step per iteration: arrow, dot, loss
        for i, (p1, p2) in enumerate(zip(path, path[1:])):
            arrow = Arrow(axes.c2p(*p1), axes.c2p(*p2), buff=0).set_color(RED)
            iter_num.set_value(i + 1)
            self.play(
                GrowArrow(arrow),
                dot.animate.move_to(axes.c2p(*p2)),
                ChangeDecimalToValue(loss_num, loss_2d(*p2)),
                run_time=0.5,
            )
            self.play(FadeOut(arrow), run_time=0.2)

        converged = Text("Converged!", font_size=48).set_color(GREEN)
        converged.next_to(info, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(FadeIn(converged, scale=1.5))

        ## Whole path as the corners GD actually visited
        trail = VMobject().set_points_as_corners([axes.c2p(*p) for p in path]).set_stroke(YELLOW, 3)
        self.play(ShowCreation(trail), run_time=2)
        self.wait(2)


class GradientDescent3D(ThreeDScene):
    def construct(self):
        self.frame.reorient(30, 70)

        ## z range covers the surface corners (loss_3d(3, 3) = 6.3). ThreeDAxes centers x and y only;
        ## z = 0 stays at world z = 0, so lower the axes to put the bowl mid-frame and place everything via c2p
        axes = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1), z_range=(0, 7, 1), width=6, height=6, depth=4)
        axes.shift(2 * IN)
        surface = axes.get_graph(loss_3d, u_range=(-3, 3), v_range=(-3, 3), opacity=0.7)
        # color = height; set_color_by_gradient on a surface follows point order, not height
        surface.set_color_by_xyz_func("z", axes.c2p(0, 0, 0)[2], axes.c2p(0, 0, loss_3d(3, 3))[2])

        title = Text("Loss Landscape", font_size=48).to_corner(UL).fix_in_frame()
        self.play(FadeIn(axes), FadeIn(surface), FadeIn(title))

        self.play(self.frame.animate.reorient(-30), run_time=3)

        ## The translucent surface still writes depth: a ball drawn after it vanishes wherever the bowl's
        ## near wall covers it. z_index -1 sorts the ball before the surface, so the wall tints it instead
        def on_surface(p):
            return axes.c2p(*p, loss_3d(*p)) + 0.15 * OUT

        p = np.array([2.5, 2.0])
        ball = Sphere(radius=0.15, color=YELLOW).move_to(on_surface(p)).set_z_index(-1)
        self.play(FadeIn(ball, scale=2))

        for _ in range(12):
            p = p - 0.4 * np.array([0.6 * p[0], 0.8 * p[1]])
            self.play(ball.animate.move_to(on_surface(p)), run_time=0.4)

        self.play(self.frame.animate.reorient(60, 60), run_time=3)
        self.wait(2)
