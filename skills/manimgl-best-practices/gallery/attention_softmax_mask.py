"""Causal mask -> softmax on a numeric attention grid.

Source: adithya-s-k/manim_skill @cef0450,
    skills/manimgl-best-practices/examples/attention_softmax_masking.py
License: CC BY-NC-SA 4.0 — original by Grant Sanderson (3Blue1Brown), adapted by Adithya S Kolavi,
    modified for the CodingVillainKor/manimgl fork by manimgl-skill.
Changes: Korean titles, smaller numbers so they fit their cells, smaller "softmax" label,
    the softmax helper (and its dead all-masked branch) replaced by two numpy lines,
    LaggedStart takes a list instead of a generator + group_type=Group, seeded inside construct.

Render (from the folder that holds this file):
    uv run manimgl attention_softmax_mask.py AttentionSoftmaxMasking -sw    # last frame -> videos/*.png
    uv run manimgl attention_softmax_mask.py AttentionSoftmaxMasking -w -l  # 480p draft -> videos/*.mp4
"""
from manimlib import *


class AttentionSoftmaxMasking(InteractiveScene):
    def construct(self):
        np.random.seed(0)  # first line: Scene.__init__ reseeds, and a multi-scene run builds every scene first
        ## Two grids: raw scores and normalized weights
        shape = (6, 6)
        left_grid = Square().get_grid(*shape, buff=0)
        left_grid.set_shape(5.5, 5)
        left_grid.to_edge(LEFT)
        left_grid.set_y(-0.5)
        left_grid.set_stroke(GREY_B, 1)

        right_grid = left_grid.copy()
        right_grid.to_edge(RIGHT)

        grids = VGroup(left_grid, right_grid)
        arrow = Arrow(left_grid, right_grid)
        sm_label = Text("softmax", font_size=36)
        sm_label.next_to(arrow, UP)

        titles = VGroup(
            Text("정규화 전\n어텐션 패턴", font_size=40),
            Text("정규화 후\n어텐션 패턴", font_size=40),
        )
        for title, grid in zip(titles, grids):
            title.next_to(grid, UP, buff=MED_LARGE_BUFF)

        values_array = np.random.normal(0, 2, shape)
        font_size = 26
        raw_values = VGroup(
            DecimalNumber(value, include_sign=True, font_size=font_size).move_to(square)
            for square, value in zip(left_grid, values_array.flatten())
        )

        self.add(grids, titles, arrow, sm_label, raw_values)
        self.wait()

        ## Mask the lower triangle with -inf
        # 3b1b convention: rows = keys, columns = queries, so a key after its query (i > j) is masked.
        # Papers/PyTorch use the transpose (rows = queries, upper triangle masked, softmax over each row).
        changers = VGroup()
        for n, dec in enumerate(raw_values):
            i, j = divmod(n, shape[1])
            if i > j:
                changers.add(dec)
                neg_inf = Tex(R"-\infty", font_size=36)
                neg_inf.move_to(dec)
                neg_inf.set_fill(RED, border_width=1.5)
                dec.target = neg_inf
                values_array[i, j] = -np.inf

        rects = VGroup(map(SurroundingRectangle, changers))
        rects.set_stroke(RED, 3)

        self.play(LaggedStartMap(ShowCreation, rects))
        self.play(
            LaggedStartMap(FadeOut, rects),
            LaggedStartMap(MoveToTarget, changers)
        )
        self.wait()

        ## Softmax down each column; exp(-inf) = 0 gives the masked zeros
        # The diagonal is never masked, so no column is all -inf
        weights = np.exp(values_array - values_array.max(axis=0))
        weights /= weights.sum(axis=0)

        normalized_values = VGroup(
            DecimalNumber(value, font_size=font_size).move_to(square)
            for square, value in zip(right_grid, weights.flatten())
        )

        # Dim small weights, color masked zeros red
        for n, value in enumerate(normalized_values):
            value.set_fill(opacity=interpolate(0.5, 1, min(value.get_value() * 3, 1)))
            if (n // shape[1]) > (n % shape[1]):
                value.set_fill(RED, 0.75)

        # A list, not a generator: with a generator AnimationGroup picks VGroup, which rejects FadeTransform's Group
        self.play(LaggedStart(
            [FadeTransform(v1.copy(), v2) for v1, v2 in zip(raw_values, normalized_values)],
            lag_ratio=0.05,
        ))
        self.wait(2)
