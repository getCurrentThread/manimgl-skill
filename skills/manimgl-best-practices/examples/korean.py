"""Korean text on the fork.

- Text uses the fork default font "Noto Sans KR" (default_config.yml text.font), so no font= is needed.
- Korean + math: Text and Tex side by side (imcommit convention).
- Korean inside Tex only via xelatex + kotex (KoreanInTex; needs a TeX distribution with kotex).
"""
from manimlib import *

# xcolor: t2c, isolate and BulletedList insert \color commands
KOTEX_PREAMBLE = R"\usepackage{amsmath}\usepackage{xcolor}\usepackage{kotex}\setmainhangulfont{Noto Sans KR}"


class KoreanText(Scene):
    def construct(self):
        ## 한글은 Text 로, 부분 선택은 문자열로
        sentence = Text("양자화는 정밀도를 줄인다", font_size=40)
        sentence["정밀도"].set_color(YELLOW)

        ## 한글과 수식은 따로 만들어 나란히 놓는다
        loss = VGroup(
            Text("손실", font_size=32),
            Tex(R"= \sum_i (y_i - \hat{y}_i)^2", font_size=40),
        ).arrange(RIGHT, buff=0.15)

        ## 단어별 색은 t2c
        note = Text("평균 loss 값", font_size=28, t2c={"loss": RED})

        VGroup(sentence, loss, note).arrange(DOWN, buff=0.7)
        self.play(Write(sentence))
        self.play(FadeIn(loss, shift=UP * 0.2))
        self.play(FadeIn(note))
        self.wait()


class KoreanInTex(Scene):
    def construct(self):
        ## Tex 안에 한글이 꼭 필요할 때만: xelatex 템플릿 + kotex
        eq = Tex(
            R"\text{손실} = \frac{1}{N} \sum_i \ell_i",
            template="empty_ctex",
            additional_preamble=KOTEX_PREAMBLE,
            t2c={"손실": YELLOW},
            font_size=48,
        )
        self.play(Write(eq))
        self.wait()
