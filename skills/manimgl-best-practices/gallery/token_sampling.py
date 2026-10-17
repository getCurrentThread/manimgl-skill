"""Next-token sampling from a probability distribution, and how temperature reshapes it.

Source: adithya-s-k/manim_skill @cef0450, skills/manimgl-best-practices/examples/token_sampling.py
License: CC BY-NC-SA 4.0 — original by Grant Sanderson (3Blue1Brown), adapted by Adithya S Kolavi,
modified for the CodingVillainKor/manimgl fork by manimgl-skill.
Changes: Korean prompt/tokens/labels; bars share one left edge; chosen token fills the prompt;
seeded inside construct; set_color instead of Text(color=); TemperatureSampling is one large chart
reshaped live by a ValueTracker instead of three static mini charts.

Render (from the folder that holds this file):
    uv run manimgl token_sampling.py TokenSamplingAnimation -sw
    uv run manimgl token_sampling.py TokenSamplingAnimation TemperatureSampling -w -l
"""
from manimlib import *

TOKENS = ["숲", "산", "동굴", "들판", "강가"]


def bar_chart(probs, width_100p, bar_height=0.5, font_size=36):
    """Rows of VGroup(token, bar, percent). Bars are aligned first so they share one left edge."""
    bars = VGroup(*(Rectangle(max(p * width_100p, 1e-3), bar_height) for p in probs))
    bars.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
    rows = VGroup()
    for token, p, bar in zip(TOKENS, probs, bars):
        bar.set_fill(interpolate_color(BLUE_E, TEAL, p / max(probs)), opacity=0.9)
        bar.set_stroke(WHITE, 1)
        label = Text(token, font_size=font_size).next_to(bar, LEFT, buff=0.3)
        # Integer truncates floats (int(), F:manimlib/mobject/numbers.py:135-136) -> round first
        pct = Integer(round(100 * p), unit="%", font_size=0.8 * font_size)
        pct.next_to(bar, RIGHT, buff=SMALL_BUFF)
        rows.add(VGroup(label, bar, pct))
    return rows


def softmax(logits, temperature):
    z = np.exp((logits - logits.max()) / temperature)
    return z / z.sum()


class TokenSamplingAnimation(InteractiveScene):
    def construct(self):
        # Seed here: Scene.__init__ reseeds with random_seed (default 0), and a multi-scene run builds every
        # scene before the first runs (F:manimlib/scene/scene.py:139-141, F:manimlib/extract_scene.py:106-109)
        np.random.seed(3)
        ## Prompt and next-token distribution
        title = Text("분포에서 다음 토큰 샘플링", font_size=44).to_edge(UP, buff=0.5)
        prompt = Text("곰이 사는 곳은", font_size=36).set_color(GREY_B)
        blank = Text("___", font_size=36).set_color(GREY_B)
        VGroup(prompt, blank).arrange(RIGHT, buff=0.2, aligned_edge=DOWN).next_to(title, DOWN, buff=0.5)
        self.play(Write(title))
        self.play(FadeIn(prompt), FadeIn(blank))

        probs = np.array([0.35, 0.28, 0.20, 0.12, 0.05])
        rows = bar_chart(probs, width_100p=8.0).center().shift(0.7 * DOWN)
        self.play(FadeIn(rows, lag_ratio=0.1))
        self.wait(0.5)

        ## Highlight jumps between samples, then settles on the last one
        picks = np.random.choice(len(TOKENS), size=16, p=probs)
        highlight = SurroundingRectangle(rows[picks[0]], buff=0.1)
        highlight.set_stroke(YELLOW, 3).set_fill(YELLOW, 0.25)
        highlight.set_z_index(-1)  # Scene.add sorts by z_index, so the fill stays behind the text
        self.play(FadeIn(highlight))
        self.play(
            UpdateFromAlphaFunc(highlight, lambda r, a: r.surround(rows[picks[int(15 * a)]])),
            run_time=2.5,
            rate_func=linear,
        )

        ## The chosen token fills the prompt
        token = rows[picks[-1]][0]
        chosen = token.copy().set_color(GREEN).scale(1.2)
        chosen.next_to(prompt, RIGHT, buff=0.2).align_to(prompt, DOWN)
        self.play(highlight.animate.set_stroke(GREEN, 4).set_fill(GREEN, 0.3), run_time=0.5)
        self.play(FadeOut(blank), TransformFromCopy(token, chosen))
        self.wait(2)


class TemperatureSampling(InteractiveScene):
    def construct(self):
        ## One chart, reshaped live by T: p = softmax(logits / T)
        logits = np.array([2.5, 2.0, 1.5, 1.0, 0.5])
        width_100p = 7.0
        T = ValueTracker(1.0)

        title = Text("온도에 따른 샘플링 분포", font_size=44).to_edge(UP, buff=0.5)
        t_label = Text("온도 T =", font_size=36)
        t_value = DecimalNumber(1.0, num_decimal_places=1, font_size=36)
        readout = VGroup(t_label, t_value).arrange(RIGHT, buff=0.2)
        readout.next_to(title, DOWN, buff=0.5).shift(1.5 * LEFT)
        t_value.f_always.set_value(T.get_value)

        rows = bar_chart(softmax(logits, 1.0), width_100p)
        rows.next_to(readout, DOWN, buff=0.7)
        # Bars grow to the right from x = -2.8, so leave room for the T = 0.3 peak (81%)
        rows.shift((-2.8 - rows[0][1].get_x(LEFT)) * RIGHT)

        def update_chart(chart):
            probs = softmax(logits, T.get_value())
            for (label, bar, pct), p in zip(chart, probs):
                # floor > 0: set_width returns early on a zero-width mobject (F:manimlib/mobject/mobject.py:1150-1152)
                bar.set_width(max(p * width_100p, 1e-3), stretch=True, about_edge=LEFT)
                bar.set_fill(interpolate_color(BLUE_E, TEAL, p / probs.max()))
                pct.set_value(round(100 * p)).next_to(bar, RIGHT, buff=SMALL_BUFF)

        def note(text, color):
            return Text(text, font_size=32).set_color(color).next_to(readout, RIGHT, buff=0.8)

        self.play(Write(title))
        self.play(FadeIn(readout), FadeIn(rows, lag_ratio=0.1))
        rows.add_updater(update_chart)
        current = note("균형", GREEN)
        self.play(FadeIn(current))
        self.wait()

        ## Low T sharpens the peak, high T flattens the distribution
        for t, text, color in [(0.3, "더 결정적", BLUE), (3.0, "더 무작위", RED)]:
            new = note(text, color)
            self.play(
                T.animate.set_value(t),
                LaggedStart(FadeOut(current), FadeIn(new), lag_ratio=0.6),
                run_time=2.5,
            )
            current = new
            self.wait()

        rows.clear_updaters()
        t_value.clear_updaters()
        self.wait()
