"""W·x, one output entry per row: sign-coloured DecimalMatrix with ellipses, row-by-vector highlight.

Source: adithya-s-k/manim_skill @cef0450,
    skills/manimgl-best-practices/examples/weight_matrix_product.py
License: CC BY-NC-SA 4.0 — original by Grant Sanderson (3Blue1Brown), adapted by Adithya S Kolavi,
    modified for the CodingVillainKor/manimgl fork by manimgl-skill.
Changes: result is the real W @ x (the source summed only the first 4 row×vector products for the first three rows,
    and never computed the last row, which kept its random start value),
    result rows pair with matrix rows by index and the skipped row follows ellipses_row, the vector
    highlight covers every entry, brackets are sized for the final values,
    Korean caption, row shifted left to centre it, dead kwargs dropped.

Render (from the folder that holds this file):
    uv run manimgl matrix_vector_product.py WeightMatrixProduct -sw      # last frame -> videos/WeightMatrixProduct.png
    uv run manimgl matrix_vector_product.py WeightMatrixProduct -w -l    # 480p draft -> videos/WeightMatrixProduct.mp4
"""
from manimlib import *


def value_to_color(
    value,
    low_positive_color=BLUE_E,
    high_positive_color=BLUE_B,
    low_negative_color=RED_E,
    high_negative_color=RED_B,
    min_value=0.0,
    max_value=10.0
):
    """Map a value to a color based on sign and magnitude."""
    alpha = clip(float(inverse_interpolate(min_value, max_value, abs(value))), 0, 1)
    if value >= 0:
        return interpolate_color(low_positive_color, high_positive_color, alpha)
    else:
        return interpolate_color(low_negative_color, high_negative_color, alpha)


class WeightMatrix(DecimalMatrix):
    """A matrix with entries coloured by sign, brightness scaled to the largest |value|."""
    def __init__(self, values, ellipses_row=-2, ellipses_col=-2, num_decimal_places=1, bracket_h_buff=0.1):
        self.ellipses_row = ellipses_row
        super().__init__(
            values,
            num_decimal_places=num_decimal_places,
            bracket_h_buff=bracket_h_buff,
            decimal_config=dict(include_sign=True),
            ellipses_row=ellipses_row,
            ellipses_col=ellipses_col,
        )
        max_value = np.abs(values).max()
        for entry in self.get_entries():
            entry.set_fill(value_to_color(entry.get_value(), max_value=max_value))


class NumericEmbedding(WeightMatrix):
    """A column vector (embedding) with colour-coded entries."""
    def __init__(self, values, ellipses_row=-2, **kwargs):
        super().__init__(np.reshape(values, (-1, 1)), ellipses_row=ellipses_row, ellipses_col=None, **kwargs)


class WeightMatrixProduct(InteractiveScene):
    def construct(self):
        np.random.seed(42)  # in construct, so it also holds when batched with other scenes
        # The ellipses only hide entries: the result below is the true product of the full arrays
        W = np.random.uniform(-9.9, 9.9, size=(5, 7))
        x = np.random.uniform(-9.9, 9.9, size=7)

        matrix = WeightMatrix(W)
        matrix.set_height(3.5)
        matrix.to_edge(LEFT, buff=0.7)  # centres the whole W x = Q row (buff=1 pushed Q to the right edge)

        in_vect = NumericEmbedding(x)
        in_vect.match_height(matrix)
        in_vect.next_to(matrix, RIGHT, buff=0.3)

        # Labels
        mat_brace = Brace(matrix, UP)
        mat_label = Tex("W_Q", font_size=48)
        mat_label.set_color(YELLOW)
        mat_label.next_to(mat_brace, UP, SMALL_BUFF)

        vect_label = Tex(R"\vec{E}", font_size=48)
        vect_label.set_color(TEAL)
        vect_label.next_to(in_vect, UP, buff=0.5)

        self.play(
            FadeIn(matrix, lag_ratio=0.01),
            FadeIn(in_vect),
            GrowFromCenter(mat_brace),
            FadeIn(mat_label, shift=0.25 * UP),
            FadeIn(vect_label, shift=0.25 * DOWN),
        )
        self.wait()

        # Result vector, built from its final values so the brackets fit them
        eq = Tex("=", font_size=60)
        eq.next_to(in_vect, RIGHT, buff=0.4)

        result = NumericEmbedding(W @ x)
        result.match_height(matrix)
        result.next_to(eq, RIGHT, buff=0.4)

        result_label = Tex(R"\vec{Q}", font_size=48)
        result_label.set_color(YELLOW)
        result_label.next_to(result, UP, buff=0.5)

        self.play(
            FadeIn(eq),
            FadeIn(result.get_brackets()),
        )

        # Animate row-by-vector products
        rows = matrix.get_rows()
        result_cells = result.get_columns()[0]  # one cell per row; the ellipsis row's cell is vdots
        vect_cells = in_vect.get_columns()[0]
        skip = matrix.ellipses_row % len(rows)
        assert result_cells[skip] in result.ellipses  # matrix and result hide the same row

        last_rects = VGroup()
        for n, (row, cell) in enumerate(zip(rows, result_cells)):
            if n == skip:
                self.add(cell)
                continue

            # Highlight current row and vector
            row_rects = VGroup(SurroundingRectangle(r, buff=0.05) for r in row)
            vect_rects = VGroup(SurroundingRectangle(v, buff=0.05) for v in vect_cells)
            row_rects.set_stroke(YELLOW, 2)
            vect_rects.set_stroke(YELLOW, 2)

            self.play(
                ShowIncreasingSubsets(row_rects),
                ShowIncreasingSubsets(vect_rects),
                CountInFrom(cell, 0),  # keeps the final value's colour (set_value keeps style)
                FadeOut(last_rects),
                rate_func=linear,
                run_time=0.8,
            )
            last_rects = VGroup(row_rects, vect_rects)

        self.play(FadeOut(last_rects))

        # Show result label
        self.play(FadeIn(result_label, shift=0.25 * DOWN))
        self.wait()

        # Add explanation
        explanation = Text("각 행과 벡터의 내적이 출력 성분 하나가 된다", font_size=36)
        explanation.to_edge(DOWN)
        self.play(Write(explanation))
        self.wait(2)
