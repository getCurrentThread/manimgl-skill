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
        ## Korean goes in Text; sub-select by string
        sentence = Text("양자화는 정밀도를 줄인다", font_size=40)
        sentence["정밀도"].set_color(YELLOW)

        ## Build Korean text and math separately and place them side by side
        loss = VGroup(
            Text("손실", font_size=32),
            Tex(R"= \sum_i (y_i - \hat{y}_i)^2", font_size=40),
        ).arrange(RIGHT, buff=0.15)

        ## Per-word color with t2c
        note = Text("평균 loss 값", font_size=28, t2c={"loss": RED})

        VGroup(sentence, loss, note).arrange(DOWN, buff=0.7)
        self.play(Write(sentence))
        self.play(FadeIn(loss, shift=UP * 0.2))
        self.play(FadeIn(note))
        self.wait()


class KoreanInTex(Scene):
    def construct(self):
        ## Only when Korean is truly needed inside Tex: xelatex template + kotex
        eq = Tex(
            R"\text{손실} = \frac{1}{N} \sum_i \ell_i",
            template="empty_ctex",
            additional_preamble=KOTEX_PREAMBLE,
            t2c={"손실": YELLOW},
            font_size=48,
        )
        self.play(Write(eq))
        self.wait()
