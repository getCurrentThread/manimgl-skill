"""True 3D on the fork: ThreeDScene + self.frame. No set_camera_orientation / begin_ambient_camera_rotation."""
from manimlib import *


class Surface3D(ThreeDScene):
    def construct(self):
        ## ThreeDScene: 기본 카메라 방향 (-30, 70), add 할 때 depth test 적용
        axes = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1), z_range=(-2, 2, 1))
        surface = axes.get_graph(lambda x, y: 0.6 * np.sin(x) * np.cos(y), color=BLUE_D, opacity=0.8)

        ## 화면에 고정할 제목은 fix_in_frame
        title = Text("3D 곡면", font_size=36).to_corner(UL).fix_in_frame()
        self.add(axes, title)
        self.play(ShowCreation(surface), run_time=2)

        ## 카메라 이동은 frame.animate.reorient, 회전은 add_ambient_rotation
        self.play(self.frame.animate.reorient(20, 60, 0), run_time=2)
        self.frame.add_ambient_rotation(10 * DEG)
        self.wait(2)
        self.frame.clear_updaters()
        self.wait()
