"""Tex on the fork: raw strings, select parts by substring instead of glyph indices."""
from manimlib import *

T2C = {"m": BLUE, "c": YELLOW}


class TexSelectors(Scene):
    def construct(self):
        ## 색은 t2c, 선택은 eq["m"] 처럼 문자열로
        eq = Tex(R"E = m c^2", t2c=T2C, font_size=72)
        self.play(Write(eq))
        self.play(FlashAround(eq["m"], color=BLUE))

        ## 같은 기호를 이어 붙이며 다른 식으로
        eq2 = Tex(R"E^2 = (m c^2)^2 + (p c)^2", t2c=T2C, font_size=60)
        self.play(TransformMatchingTex(eq, eq2))

        ## 부분 식에 Brace + 한글 설명(get_text 는 Text 를 만든다)
        brace = Brace(eq2["(p c)^2"], DOWN, buff=0.15)
        label = brace.get_text("운동량 항", font_size=28)
        self.play(GrowFromCenter(brace), FadeIn(label))

        ## 산문은 TexText (Tex 는 수식 모드)
        prose = TexText("Energy and momentum", font_size=36).to_edge(UP)
        self.play(FadeIn(prose))
        self.wait()
