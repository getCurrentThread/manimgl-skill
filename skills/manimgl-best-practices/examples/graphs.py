"""Axes on the fork: get_graph / add_coordinate_labels / get_area_under_graph / ParametricCurve
(ManimCE: plot / add_coordinates / get_area / ParametricFunction do not exist here)."""
from manimlib import *


class Graphs(Scene):
    def construct(self):
        ## 좌표축과 눈금 숫자 (숫자는 DecimalNumber -> LaTeX 불필요)
        axes = Axes(x_range=(-3, 3, 1), y_range=(-1, 9, 2), width=8, height=5.5)
        axes.add_coordinate_labels(font_size=20)
        self.play(FadeIn(axes))

        ## 그래프, 라벨(Tex), 넓이
        graph = axes.get_graph(lambda x: x ** 2, color=BLUE)
        label = axes.get_graph_label(graph, R"x^2")
        area = axes.get_area_under_graph(graph, x_range=(0, 2))
        self.play(ShowCreation(graph), FadeIn(label))
        self.play(FadeIn(area))

        ## 매개변수 곡선
        curve = ParametricCurve(
            lambda t: axes.c2p(-1.5 + 0.6 * np.cos(t), 6 + 1.45 * np.sin(t)),
            t_range=(0, TAU, 0.05),
            color=YELLOW,
        )
        self.play(ShowCreation(curve))
        self.wait()
