"""Tex on the fork: raw strings, select parts by substring instead of glyph indices."""
from manimlib import *

T2C = {"m": BLUE, "c": YELLOW}


class TexSelectors(Scene):
    def construct(self):
        ## Color with t2c, select by string like eq["m"]
        eq = Tex(R"E = m c^2", t2c=T2C, font_size=72)
        self.play(Write(eq))
        self.play(FlashAround(eq["m"], color=BLUE))

        ## Chain the same symbols into a different expression
        eq2 = Tex(R"E^2 = (m c^2)^2 + (p c)^2", t2c=T2C, font_size=60)
        self.play(TransformMatchingTex(eq, eq2))

        ## Brace + Korean label on a sub-expression (get_text makes a Text)
        brace = Brace(eq2["(p c)^2"], DOWN, buff=0.15)
        label = brace.get_text("운동량 항", font_size=28)
        self.play(GrowFromCenter(brace), FadeIn(label))

        ## Use TexText for prose (Tex is math mode)
        prose = TexText("Energy and momentum", font_size=36).to_edge(UP)
        self.play(FadeIn(prose))
        self.wait()
