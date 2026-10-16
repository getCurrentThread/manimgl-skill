"""True 3D on the fork: ThreeDScene + self.frame. No set_camera_orientation / begin_ambient_camera_rotation."""
from manimlib import *


class Surface3D(ThreeDScene):
    def construct(self):
        ## ThreeDScene: default camera orientation (-30, 70), depth test applied on add
        axes = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1), z_range=(-2, 2, 1))
        surface = axes.get_graph(lambda x, y: 0.6 * np.sin(x) * np.cos(y), color=BLUE_D, opacity=0.8)

        ## Use fix_in_frame for a title pinned to the screen
        title = Text("3D 곡면", font_size=36).to_corner(UL).fix_in_frame()
        self.add(axes, title)
        self.play(ShowCreation(surface), run_time=2)

        ## Move the camera with frame.animate.reorient, rotate with add_ambient_rotation
        self.play(self.frame.animate.reorient(20, 60, 0), run_time=2)
        self.frame.add_ambient_rotation(10 * DEG)
        self.wait(2)
        self.frame.clear_updaters()
        self.wait()
