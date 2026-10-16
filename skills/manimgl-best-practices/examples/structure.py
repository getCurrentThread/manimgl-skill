"""One video = one main.py with several scene classes in narrative order (imcommit layout).

Render (from the folder that holds this file):
    uv run manimgl structure.py Intro -sw     # last frame -> videos/Intro.png
    uv run manimgl structure.py Intro -w      # movie      -> videos/Intro.mp4
"""
from manimlib import *
from random import seed

# random_color() uses np.random, random_bright_color() uses random -> seed both
seed(41)
np.random.seed(41)


class Intro(Scene):
    def construct(self):
        ## 모델은 큰 숫자 행렬이다
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
        self.play(LaggedStart(*[FadeIn(w, scale=0.5) for w in weights], lag_ratio=0.05))
        self.wait()

        ## 하나만 강조하고 나머지는 흐리게
        focus = weights[5]
        # focus 는 weights 의 자식이라 weights.animate 와 겹친다 -> 나머지만 묶어 animate
        others = VGroup(*(w for w in weights if w is not focus))
        self.play(others.animate.set_opacity(0.2), focus.animate.set_opacity(1), run_time=0.5)
        self.play(FlashAround(focus, color=YELLOW))
        self.wait()


class Quantize(Scene):
    def construct(self):
        ## 이전 씬과 독립: 필요한 상태는 이 클래스에서 다시 만든다
        # Text/Tex/Dot ignore color= (fill_color is forced to white) -> set_color() or fill_color=
        src = Text("32-bit", font_size=36).set_color(RED)
        dst = Text("8-bit", font_size=36).set_color(GREEN)
        arrow = Arrow(LEFT, RIGHT, buff=0.1, thickness=2)
        VGroup(src, arrow, dst).arrange(RIGHT, buff=0.5)
        self.play(FadeIn(src, shift=RIGHT * 0.3))
        self.play(GrowArrow(arrow), TransformFromCopy(src, dst), run_time=1)
        self.play(Indicate(dst, color=GREEN, scale_factor=1.1))

        ## 결과를 상자로 묶고 설명을 단다
        rect = SurroundingRectangle(dst, buff=0.15, color=YELLOW)
        note = Text("메모리 1/4", font_size=24).set_color(GREY_B).next_to(rect, DOWN, buff=0.2)
        self.play(ShowCreation(rect), FadeIn(note, shift=UP * 0.2))
        self.wait()

        ## 오버레이로 나머지를 가린다: z_index 는 self.add 할 때 정렬되므로 다시 add
        overlay = FullScreenFadeRectangle(fill_opacity=0.7)
        group = VGroup(dst, rect, note)
        group.set_z_index(1)
        self.add(group)
        self.play(FadeIn(overlay), run_time=0.5)
        self.wait()
