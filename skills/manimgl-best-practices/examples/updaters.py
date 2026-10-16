"""Updaters on the fork: dt is detected by the parameter NAME `dt`; add_updater runs the updater once immediately."""
from manimlib import *


class Trackers(Scene):
    def construct(self):
        ## ValueTracker 하나로 숫자와 점을 같이 움직인다
        t = ValueTracker(0)
        line = NumberLine((0, 10, 1), width=10).to_edge(DOWN, buff=1.5)
        line.add_numbers(font_size=20)
        dot = Dot(fill_color=YELLOW)  # Dot(color=...) stays white: Dot forces fill_color
        dot.add_updater(lambda m: m.move_to(line.n2p(t.get_value())))
        number = DecimalNumber(0, num_decimal_places=2, font_size=48).next_to(line, UP, buff=1.5)
        number.f_always.set_value(t.get_value)

        ## 시간 기반 업데이터: 두 번째 인자 이름이 반드시 dt
        spinner = Square(0.8, color=BLUE).to_corner(UR, buff=0.8)
        spinner.add_updater(lambda m, dt: m.rotate(dt))

        ## always_redraw 는 매 프레임 새로 만든다 (Tex 를 넣으면 느리다)
        bar = always_redraw(lambda: Line(line.n2p(0), dot.get_center(), color=YELLOW, stroke_width=6))

        self.add(line, bar, dot, number, spinner)
        self.play(t.animate.set_value(10), run_time=2)
        self.play(t.animate.set_value(4), run_time=1)

        ## 끝나면 업데이터를 정리한다
        for mob in (dot, number, spinner, bar):
            mob.clear_updaters()
        self.wait()
