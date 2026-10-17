"""
Word vector analogy: 왕 - 남자 + 여자 ≈ 여왕, drawn as arrows in a 3D embedding space.

Source: adithya-s-k/manim_skill @cef0450,
skills/manimgl-best-practices/examples/word_vector_analogy.py
(based on 3b1b/videos _2024/transformers/embedding.py, KingQueenExample).
CC BY-NC-SA 4.0 — original by Grant Sanderson (3Blue1Brown), adapted by Adithya S Kolavi,
modified for the CodingVillainKor/manimgl fork by manimgl-skill.

Changes: Korean words; arrows colored with set_color (stroke_color= only outlined a gray
fill arrow) and turned toward the camera every frame; labels billboarded so they stay
readable after the final reorient (points-only reset, so FadeIn still fades); the overlay
equation is one Text in which "왕" also matches inside "여왕", so the standalone one is
picked with select_part; overlay text colored with set_color; Scene instead of
InteractiveScene; dead style code removed; seeded inside construct.

Render: uv run manimgl word_vector_analogy.py WordVectorAnalogy -w -l
"""
from manimlib import *


class WordVectorAnalogy(Scene):
    def construct(self):
        np.random.seed(0)  # first line: Scene.__init__ reseeds, and a multi-scene run builds every scene first
        frame = self.frame
        frame.reorient(-20, 70, 0)
        frame.add_ambient_rotation(2 * DEG)

        ## Axes and a vertical reference plane
        axes = ThreeDAxes((-4, 4, 1), (-4, 4, 1), (-3, 3, 1), width=8, height=8, depth=6)
        axes.set_stroke(width=2)
        plane = NumberPlane(
            axes.x_range[:2], axes.y_range[:2],
            width=axes.get_width(),
            height=axes.get_height(),
            background_line_style=dict(stroke_color=GREY, stroke_width=1),
            faded_line_style=dict(stroke_opacity=0.25, stroke_width=0.5),
            faded_line_ratio=1,
        )
        plane.rotate(90 * DEG, LEFT)
        self.add(axes, plane)

        ## Word vectors with labels that keep facing the camera
        words = {
            "남자": ([1, -1, 0.5], BLUE_B),
            "여자": ([1, 1, 0.5], RED_B),
            "왕": ([-2, -1, 1.5], BLUE_D),
            "여왕": ([-2, 1, 1.5], RED_D),
        }

        def face_camera(arrow):
            # Arrow is a flat filled shape: it goes edge-on as the camera turns (SKILL.md §9)
            return arrow.add_updater(lambda m: m.set_perpendicular_to_camera(frame))

        def billboard(label, point):
            flat = label.copy()

            def update(m):
                # Reset points only: FadeIn's start/target copies carry this updater and run it
                # every frame (animation.py:40-43), so become() would reset their opacity too
                for sm, src in zip(m.get_family(), flat.get_family()):
                    sm.set_points(src.get_points())
                m.apply_matrix(frame.get_orientation().as_matrix()).move_to(point)

            return label.add_updater(update)

        vectors, labels = {}, {}
        for word, (coords, color) in words.items():
            tip = axes.c2p(*coords)
            vectors[word] = face_camera(Arrow(axes.get_origin(), tip, buff=0).set_color(color))
            label = Text(word, font_size=30).set_backstroke(BLACK, 3)
            offset = 0.35 + label.get_width() / 2  # clear the tip even for a foreshortened vector
            labels[word] = billboard(label, tip + offset * normalize(tip - axes.get_origin()))

        ## Screen-fixed equation; "왕" also matches inside "여왕", so pick the 2nd match
        equation = Text("여자 − 남자 ≈ 여왕 − 왕", font_size=32)
        equation["여자"].set_color(RED_B)
        equation["남자"].set_color(BLUE_B)
        equation["여왕"].set_color(RED_D)
        equation.select_part("왕", 1).set_color(BLUE_D)
        equation.fix_in_frame()
        equation.to_corner(UR)

        top_rect = FullScreenFadeRectangle()
        top_rect.set_height(1.2, about_edge=UP, stretch=True)
        top_rect.fix_in_frame()

        def show(word):
            return GrowArrow(vectors[word]), FadeIn(labels[word])

        ## 남자 and 여자
        self.play(*show("남자"), *show("여자"), run_time=2)
        self.wait()

        ## The difference vector 남자 -> 여자
        diff = face_camera(Arrow(vectors["남자"].get_end(), vectors["여자"].get_end(), buff=0))
        diff.set_color(YELLOW)
        self.play(GrowArrow(diff))
        self.wait()

        self.add(top_rect)
        self.play(Write(equation))
        self.wait()

        ## The same difference, moved to the tip of 왕, lands on 여왕
        self.play(*show("왕"), run_time=1.5)
        king_to_queen = diff.copy()
        king_to_queen.shift(vectors["왕"].get_end() - vectors["남자"].get_end())
        self.play(TransformFromCopy(diff, king_to_queen))
        self.wait()
        self.play(*show("여왕"))
        self.wait()

        ## Turn the view so the parallelogram is seen from above
        frame.clear_updaters()
        self.play(frame.animate.reorient(-100, 20, 100), run_time=4)
        frame.add_ambient_rotation(2 * DEG)

        ## Flash the gender direction all over the space
        lines = Line(ORIGIN, 1.5 * normalize(diff.get_vector())).replicate(100)
        lines.insert_n_curves(20)
        lines.set_stroke(YELLOW, 3)
        for line in lines:
            line.move_to(np.random.uniform(-2, 2, 3))
        self.play(LaggedStartMap(VShowPassingFlash, lines, lag_ratio=1 / len(lines), run_time=3))

        dir_label = Text("성별 방향", font_size=30).set_color(YELLOW)
        dir_label.fix_in_frame()
        dir_label.next_to(equation, DOWN, buff=0.5)
        self.play(Write(dir_label))
        self.wait(3)

        ## Another pair along the same direction
        new_eq = Text("삼촌 − 이모 ≈ 남자 − 여자", font_size=26)
        new_eq.fix_in_frame()
        new_eq.next_to(dir_label, DOWN, buff=0.3)
        self.play(Write(new_eq))
        self.wait(5)
