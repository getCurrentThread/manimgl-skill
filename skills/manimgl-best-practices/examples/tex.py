"""Tex on the fork: raw strings; list every substring you select in t2c=/isolate=; multi-line equations."""
from manimlib import *

T2C = {"m": BLUE, "c": YELLOW}


class TexSelectors(Scene):
    def construct(self):
        ## Color with t2c, select by string like eq["m"] ("m" is a t2c key, so the selection is exact)
        eq = Tex(R"E = m c^2", t2c=T2C, font_size=72)
        self.play(Write(eq))
        self.play(FlashAround(eq["m"], color=BLUE))

        ## Chain the same symbols into a different expression; isolate= what you select later
        eq2 = Tex(R"E^2 = (m c^2)^2 + (p c)^2", t2c=T2C, isolate=["(p c)^2"], font_size=60)
        self.play(TransformMatchingTex(eq, eq2))

        ## Brace + Korean label on a sub-expression (get_text makes a Text)
        brace = Brace(eq2["(p c)^2"], DOWN, buff=0.15)
        label = brace.get_text("운동량 항", font_size=28)
        self.play(GrowFromCenter(brace), FadeIn(label))

        ## Multi-line: Tex is already align*, so write & and \\ directly (no \begin{align*})
        eq3 = Tex(
            R"E^2 &= (m c^2)^2 + (p c)^2 \\ E &= \sqrt{(m c^2)^2 + (p c)^2}",
            t2c=T2C, isolate=["(p c)^2"], font_size=60,
        )
        self.play(FadeOut(VGroup(brace, label)))
        self.play(TransformMatchingTex(eq2, eq3, run_time=1))
        # a string selector matches every occurrence: both (p c)^2 turn TEAL
        self.play(eq3["(p c)^2"].animate.set_color(TEAL))

        ## Use TexText for prose (Tex is math mode)
        prose = TexText("Energy and momentum", font_size=36).to_edge(UP)
        self.play(FadeIn(prose))
        self.wait()
