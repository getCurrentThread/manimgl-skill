"""One video = one main.py with several scene classes in narrative order (imcommit layout).

Render (from the folder that holds this file):
    uv run manimgl structure.py Intro -sw     # last frame -> videos/Intro.png
    uv run manimgl structure.py Intro -w      # movie      -> videos/Intro.mp4
"""
from manimlib import *


class Intro(Scene):
    def construct(self):
        # Seed here: Scene.__init__ reseeds with random_seed (default 0), and `manimgl structure.py Intro Quantize`
        # builds both scenes before Intro runs (F:manimlib/scene/scene.py:139-141, F:manimlib/extract_scene.py:106-109)
        random.seed(41); np.random.seed(41)
        ## A model is a big matrix of numbers
        title = Text("모델 압축", font_size=40).to_edge(UP, buff=0.5)
        box = Rectangle(width=4, height=3, color=GREY_C)
        label = Text("Model", font_size=24).set_color(GREY_B)
        label.next_to(box, UP, buff=0.1).align_to(box, LEFT)
        self.play(FadeIn(title, shift=DOWN * 0.3))
        self.play(ShowCreation(box), FadeIn(label))

        weights = VGroup(*[
            Square(0.5).set_stroke(width=0).set_fill(random_color(), 0.8)
            for _ in range(16)
        ])
        weights.arrange_in_grid(4, 4, buff=0.1).move_to(box)
        # FadeIn(scale=s) starts at 1/s size: 0.5 shrinks in from double size
        self.play(LaggedStart(*[FadeIn(w, scale=0.5) for w in weights], lag_ratio=0.05))
        self.wait()

        ## Highlight one, dim the rest
        focus = weights[5]
        # focus is a child of weights and overlaps weights.animate -> group only the rest and animate it
        others = VGroup(*(w for w in weights if w is not focus))
        self.play(others.animate.set_opacity(0.2), focus.animate.set_opacity(1), run_time=0.5)
        self.play(FlashAround(focus, color=YELLOW))
        self.wait()


class Quantize(Scene):
    def construct(self):
        ## Independent of the previous scene: rebuild needed state in this class
        # Text/Tex/Dot ignore color= (fill_color is forced to white) -> set_color() or fill_color=
        src = Text("32-bit", font_size=36).set_color(RED)
        dst = Text("8-bit", font_size=36).set_color(GREEN)
        arrow = Arrow(LEFT, RIGHT, buff=0.1, thickness=2)
        VGroup(src, arrow, dst).arrange(RIGHT, buff=0.5)
        self.play(FadeIn(src, shift=RIGHT * 0.3))
        self.play(GrowArrow(arrow), TransformFromCopy(src, dst), run_time=1)
        self.play(Indicate(dst, color=GREEN, scale_factor=1.1))

        ## Box the result and add a caption
        rect = SurroundingRectangle(dst, buff=0.15, color=YELLOW)
        note = Text("메모리 1/4", font_size=24).set_color(GREY_B).next_to(rect, DOWN, buff=0.2)
        self.play(ShowCreation(rect), FadeIn(note, shift=UP * 0.2))
        self.wait()

        ## Cover the rest with an overlay: z_index is sorted on self.add, so add again
        overlay = FullScreenFadeRectangle(fill_opacity=0.7)
        group = VGroup(dst, rect, note)
        group.set_z_index(1)
        self.add(group)
        self.play(FadeIn(overlay), run_time=0.5)
        self.wait()
