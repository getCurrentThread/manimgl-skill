"""Animation composition on the fork: which object survives a transform, sequencing, delays, joint targets.

Rules and evidence: references/animation-semantics.md. The asserts check scene membership after
TransformMatchingTex, Transform, ReplacementTransform and the frame-safe clear, so a render that exits 0
also checks those rules.
"""
from manimlib import *


class RebindDerivation(Scene):
    def construct(self):
        ## Equation chain: transform the on-screen object, then rebind the name to the target
        eq = Tex(R"x^2 - 4 = 0", font_size=72).shift(UP)
        self.play(Write(eq))
        for tex in (R"x^2 = 4", R"x = \pm 2"):
            nxt = Tex(tex, font_size=72).move_to(eq)
            # not eq.copy(): the original would stay on screen and every step would stack
            self.play(TransformMatchingTex(eq, nxt, run_time=1))
            eq = nxt
        assert self.mobjects == [self.frame, eq]

        ## Transform(a, b) keeps a on screen (shaped like b); ReplacementTransform puts b there
        a = Square().set_color(BLUE).shift(LEFT * 3 + DOWN * 2)
        b = Circle().set_color(GREEN).move_to(a)
        c = Square().set_color(BLUE).shift(RIGHT * 3 + DOWN * 2)
        d = Circle().set_color(GREEN).move_to(c)
        self.play(FadeIn(a), FadeIn(c))
        self.play(Transform(a, b), ReplacementTransform(c, d))
        assert a in self.mobjects and b not in self.mobjects
        assert d in self.mobjects and c not in self.mobjects
        self.play(a.animate.shift(UP * 0.5), d.animate.shift(UP * 0.5))  # keep using a and d
        self.wait()


class LaggedVsSuccession(Scene):
    def construct(self):
        ## Top: Succession shows b at full opacity while a is drawn, then b jumps to its start state
        a = Square().set_color(BLUE).shift(LEFT * 3 + UP * 1.5)
        b = Circle().set_fill(GREEN, 1).set_stroke(width=0).shift(RIGHT * 3 + UP * 1.5)
        ## Bottom: LaggedStart(lag_ratio=1) begins every member at t=0, so b2 waits invisible
        a2 = Square().set_color(BLUE).shift(LEFT * 3 + DOWN * 2)
        b2 = Circle().set_fill(YELLOW, 1).set_stroke(width=0).shift(RIGHT * 3 + DOWN * 2)
        self.add(
            Text("Succession", font_size=28).next_to(a, UP).set_x(0),
            Text("LaggedStart(lag_ratio=1)", font_size=28).next_to(a2, UP).set_x(0),
        )
        self.play(
            Succession(ShowCreation(a), FadeIn(b)),  # the pitfall, shown on purpose  # lint: ok
            LaggedStart(ShowCreation(a2), FadeIn(b2), lag_ratio=1),
        )
        self.wait()


class SpanDelays(Scene):
    def construct(self):
        ## Wave: easing goes on each member (a group-level rate_func is ignored)
        dots = VGroup(*[Dot() for _ in range(15)]).arrange(RIGHT, buff=0.4)
        self.add(dots)
        self.play(LaggedStart(*[d.animate(rate_func=there_and_back).shift(UP) for d in dots], lag_ratio=0.1))

        ## Clear the screen without removing self.frame (self.mobjects starts with it) or InteractiveScene's highlight
        self.play(FadeOut(Group(*(m for m in self.mobjects if m is not self.frame and m is not getattr(self, "selection_highlight", None)))))
        assert self.mobjects == [self.frame]

        ## Delay inside one play without Wait: time_span on the member, or squish_rate_func
        sq = Square().set_color(BLUE).shift(LEFT * 4)
        circ = Circle().set_color(GREEN)
        tri = Triangle().set_color(YELLOW).shift(RIGHT * 4)
        self.play(
            ShowCreation(sq, time_span=(0, 1)),
            FadeIn(circ, time_span=(1, 2)),  # invisible (start state) until t=1
            FadeIn(tri, run_time=3, rate_func=squish_rate_func(smooth, 2 / 3, 1)),  # same idea, t=2..3
        )
        self.wait()


class JointTargets(Scene):
    def construct(self):
        ## Lay out targets together, then move: final positions depend on each other
        a = Square(1.5).set_color(BLUE).shift(LEFT * 2)
        b = Circle(radius=0.75).set_color(GREEN).shift(RIGHT * 2)
        self.play(FadeIn(a), FadeIn(b))
        new = Triangle().set_color(YELLOW)
        VGroup(a.generate_target(), b.generate_target(), new).arrange(RIGHT, buff=0.5).shift(UP * 1.5)
        self.play(MoveToTarget(a), MoveToTarget(b), FadeIn(new))

        ## Per-submobject edits: generate_target() once, then edit target[i]
        row = VGroup(*[Square(0.6).set_fill(TEAL, 0.8).set_stroke(width=0) for _ in range(6)])
        row.arrange(RIGHT, buff=0.2).shift(DOWN * 1.5)
        self.play(FadeIn(row))
        row.generate_target()
        for i, t in enumerate(row.target):
            t.shift(UP * 0.25 * i).set_fill(interpolate_color(TEAL, RED, i / 5))
        self.play(MoveToTarget(row))

        ## Turns of 90 degrees or more: Rotate (rigid), not .animate.rotate (collapses mid-way)
        self.play(Rotate(new, PI))
        self.wait()
