"""Equation derivations: a stacked TransformMatchingTex chain and a color-coded substitution.

Source: adithya-s-k/manim_skill @cef0450, skills/manimgl-best-practices/examples/equation_transforms.py
(scenes QuadraticFormula, ColorCodedSubstitution).
License: CC BY-NC-SA 4.0 — by Adithya S Kolavi, inspired by 3Blue1Brown (Grant Sanderson)
(source header: 'Inspired by 3b1b's equation transformation style'),
modified for the CodingVillainKor/manimgl fork by manimgl-skill.
Changes: dropped BraceAnnotations/HighlightAndTransform; steps folded into a loop and shrunk to fit 8 units;
Korean step labels colored with set_color (Text ignores color=); boxed parts listed in isolate= (dx box added);
= signs of the last two lines aligned.

Render (one scene name per call, run from a scratch dir):
    uv run manimgl equation_derivation.py QuadraticFormula -w -l
    uv run manimgl equation_derivation.py ColorCodedSubstitution -sw
"""
from manimlib import *

T2C = {"a": RED, "b": GREEN, "c": BLUE, "x": YELLOW}


class QuadraticFormula(InteractiveScene):
    def construct(self):
        ## Start from the general quadratic; font 36 and buff 0.3 keep all six lines inside the frame
        eq = Tex(R"ax^2 + bx + c = 0", t2c=T2C, font_size=36).to_edge(UP, buff=0.4)
        self.play(Write(eq))
        self.wait()

        ## Each step: the next line grows out of a copy of the previous one, with a Korean label on the left
        steps = [
            (R"x^2 + \frac{b}{a}x + \frac{c}{a} = 0", "a로 나누기"),
            (R"\left(x + \frac{b}{2a}\right)^2 - \frac{b^2}{4a^2} + \frac{c}{a} = 0", "완전제곱식 만들기"),
            (R"\left(x + \frac{b}{2a}\right)^2 = \frac{b^2 - 4ac}{4a^2}", "정리"),
            (R"x + \frac{b}{2a} = \pm\frac{\sqrt{b^2 - 4ac}}{2a}", "제곱근"),
        ]
        for tex, label in steps:
            nxt = Tex(tex, t2c=T2C, font_size=36).next_to(eq, DOWN, buff=0.3)
            note = Text(label, font_size=24).set_color(GREY_B)  # Text(color=) renders white
            note.to_edge(LEFT, buff=0.8).match_y(nxt)
            # eq.copy() on purpose: the source line stays, so the derivation stacks. For an in-place
            # step pass eq itself and rebind (examples/compositions.py RebindDerivation).
            # Pairs come from source-symbol counts, so near \frac a b or c briefly morphs into a fraction
            # bar (end state is exact); TransformMatchingShapes pairs glyphs by shape instead.
            self.play(TransformMatchingTex(eq.copy(), nxt), FadeIn(note, LEFT))
            self.wait()
            eq = nxt

        ## Final formula, larger, in a box
        final = Tex(R"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}", t2c=T2C, font_size=48)
        final.next_to(eq, DOWN, buff=0.45)
        box = SurroundingRectangle(final, buff=0.15).set_color(GOLD)
        self.play(TransformMatchingTex(eq.copy(), final))
        self.play(ShowCreation(box))
        self.wait(2)


class ColorCodedSubstitution(InteractiveScene):
    def construct(self):
        ## The substitution rule at the top
        sub_def = Tex(R"u = x^2 + 1", t2c={"u": RED, "x": BLUE}).to_edge(UP)
        self.play(Write(sub_def))
        self.wait()

        ## Every part boxed later is in isolate=; an unlisted selector is found by counting source
        ## symbols and can land on the wrong glyphs (F:manimlib/mobject/svg/string_mobject.py:542-547)
        integral1 = Tex(
            R"\int 2x(x^2 + 1)^3 \, dx",
            t2c={"x": BLUE}, isolate=["(x^2 + 1)", "2x", "dx"], font_size=48,
        )
        self.play(Write(integral1))
        self.wait()

        u_rect = SurroundingRectangle(integral1["(x^2 + 1)"], buff=0.05).set_color(RED)
        self.play(ShowCreation(u_rect))
        self.wait()

        ## du = 2x dx: box both factors in the integral
        du_def = Tex(R"du = 2x \, dx", t2c={"u": RED, "x": BLUE}).next_to(sub_def, DOWN)
        du_rects = VGroup(
            SurroundingRectangle(integral1[s], buff=0.05) for s in ("2x", "dx")
        ).set_color(GREEN)
        self.play(Write(du_def), ShowCreation(du_rects))
        self.wait()

        ## In-place step: pass integral1 itself (no copy), integral2 is what stays on screen
        integral2 = Tex(R"\int u^3 \, du", t2c={"u": RED}, font_size=48).shift(LEFT)
        self.play(
            FadeOut(u_rect),
            FadeOut(du_rects),
            TransformMatchingTex(integral1, integral2),
        )
        self.wait()

        ## Solve, then substitute back (copy on purpose: both lines stay); aligned_edge=LEFT lines up the = signs
        solution = Tex(R"= \frac{u^4}{4} + C", t2c={"u": RED}, font_size=48)
        solution.next_to(integral2, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(Write(solution))
        self.wait()

        final = Tex(R"= \frac{(x^2+1)^4}{4} + C", t2c={"x": BLUE}, font_size=48)
        final.next_to(solution, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(TransformMatchingTex(solution.copy(), final))
        self.wait(2)
