"""Camera on the fork: self.frame (CameraFrame) on any Scene. No MovingCameraScene / move_camera."""
from manimlib import *


class CameraMoves(Scene):
    def construct(self):
        ## 넓은 캔버스: 영역 사이를 카메라가 이동한다
        left = VGroup(Square(2, color=BLUE), Text("A", font_size=60)).move_to(LEFT * 3)
        right = VGroup(Circle(radius=1).set_color(GREEN), Text("B", font_size=60)).move_to(RIGHT * 12)
        self.add(left, right)

        self.frame.save_state()
        self.play(self.frame.animate.move_to(right).set_height(5), run_time=1.5)
        self.wait(0.5)
        self.play(Restore(self.frame))

        ## 2D 씬에서 기울이기: reorient(theta, phi, gamma, center, height), 각도는 degree
        label = Text("기울어진 라벨", font_size=32).next_to(left, UP, buff=0.3)
        label.rotate(60 * DEG, axis=RIGHT)  # 카메라 phi 와 같은 각도로 돌려 카메라를 보게 한다
        self.play(
            self.frame.animate.reorient(0, 60, 0, left.get_center(), 6),
            FadeIn(label),
            run_time=1.5,
        )
        self.wait()
