"""Orbiting the camera on the fork. frame.animate blends orientations the short way round,
so a single .animate turn of 180 degrees or more goes wrong (360 = no motion). See references/korean-tex-3d.md §C8."""
from manimlib import *


class CameraOrbit(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1), z_range=(-2, 2, 1))
        cube = Cube(side_length=1).set_color(BLUE).shift(2 * RIGHT)  # off-center so the turn is visible
        title = Text("카메라 궤도", font_size=36).to_corner(UL).fix_in_frame()
        self.add(axes, cube, title)

        ## frame.animate only for legs under 180 deg. Four 90-degree legs make a full turn
        for _ in range(4):
            self.play(self.frame.animate.increment_theta(90 * DEG), run_time=0.75, rate_func=linear)

        ## Full turn at constant speed in one play: drive theta directly
        t0 = self.frame.get_theta()
        self.play(UpdateFromAlphaFunc(self.frame, lambda m, a: m.set_theta(t0 + a * TAU)), run_time=3, rate_func=linear)

        ## Open-ended turn: ambient rotation in rad/s, then stop it
        self.frame.add_ambient_rotation(45 * DEG)
        self.wait(2)
        self.frame.clear_updaters()

        ## Settle on an exact view. Give all three angles so no roll is left over
        self.play(self.frame.animate.reorient(-30, 70, 0), run_time=1)
        self.wait(0.5)

        ## Large theta and phi change together: .animate.reorient(140, 10, 0) would roll mid-move, so drive both angles
        t0, p0 = self.frame.get_euler_angles()[:2]
        self.play(UpdateFromAlphaFunc(self.frame, lambda m, a: m.set_euler_angles(
            theta=t0 + a * 170 * DEG, phi=p0 - a * 60 * DEG, gamma=0)), run_time=2, rate_func=linear)
        self.wait(0.5)
