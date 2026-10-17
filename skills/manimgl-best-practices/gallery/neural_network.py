"""Reusable MLP diagram: neuron layers, weight-coloured edges, a forward-pass flash.

Source: adithya-s-k/manim_skill @cef0450,
    skills/manimgl-best-practices/examples/neural_network_basic.py
    (forward-pass flash from examples/mlp_network_icon.py:28-41)
License: CC BY-NC-SA 4.0 — original by Grant Sanderson (3Blue1Brown), adapted by Adithya S Kolavi,
    modified for the CodingVillainKor/manimgl fork by manimgl-skill.
Changes: added get_forward_pass() (layer by layer, fixed flash width instead of 2 * get_width()),
    Korean title and layer labels in one row under the network, dropped the unused numpy import,
    seeded inside construct.

Render (from the folder that holds this file):
    uv run manimgl neural_network.py NeuralNetworkBasic -sw      # last frame -> videos/NeuralNetworkBasic.png
    uv run manimgl neural_network.py NeuralNetworkBasic -w -l    # 480p draft -> videos/NeuralNetworkBasic.mp4
"""
from manimlib import *
import itertools as it
import random


def value_to_color(
    value,
    low_positive_color=BLUE_E,
    high_positive_color=BLUE_B,
    low_negative_color=RED_E,
    high_negative_color=RED_B,
    min_value=0.0,
    max_value=10.0
):
    """Blue for positive weights, red for negative, brighter for larger |value|."""
    alpha = clip(float(inverse_interpolate(min_value, max_value, abs(value))), 0, 1)
    if value >= 0:
        colors = (low_positive_color, high_positive_color)
    else:
        colors = (low_negative_color, high_negative_color)
    return interpolate_color_by_hsl(*colors, alpha)


class NeuralNetwork(VGroup):
    """network.layers[i] = VGroup of Dots, network.lines[i] = edges from layer i to i+1."""

    def __init__(
        self,
        layer_sizes=[6, 12, 6],
        neuron_radius=0.1,
        v_buff_ratio=1.0,
        h_buff_ratio=7.0,
        max_stroke_width=2.0,
        stroke_decay=2.0,
    ):
        self.max_stroke_width = max_stroke_width
        self.stroke_decay = stroke_decay

        layers = VGroup(*(
            Dot(radius=neuron_radius).get_grid(n, 1, v_buff_ratio=v_buff_ratio)
            for n in layer_sizes
        ))
        layers.arrange(RIGHT, buff=h_buff_ratio * layers[0].get_width())

        lines = VGroup(*(
            VGroup(*(
                Line(n1.get_center(), n2.get_center(), buff=n1.get_width() / 2)
                for n1, n2 in it.product(l1, l2)
            ))
            for l1, l2 in zip(layers, layers[1:])
        ))

        super().__init__(layers, lines)
        self.layers = layers
        self.lines = lines

        self.randomize_layer_values()
        self.randomize_line_style()

    def randomize_layer_values(self):
        """Fill opacity = activation."""
        for layer in self.layers:
            for dot in layer:
                dot.set_stroke(WHITE, 1)
                dot.set_fill(WHITE, random.random())
        return self

    def randomize_line_style(self):
        """Colour = sign and size of the weight, width decays so most edges are faint."""
        for group in self.lines:
            for line in group:
                line.set_stroke(
                    value_to_color(random.uniform(-10, 10)),
                    self.max_stroke_width * random.random()**self.stroke_decay,
                )
        return self

    def get_forward_pass(self, width=4, run_time=3):
        """A flash runs along the edges one layer after another; the flash copies remove themselves."""
        flashes = []
        for group in self.lines:
            lines = group.copy().set_stroke(width=width)  # uniform width so faint edges flash too
            # A Line is one curve; the flash sets width per point, so give it points to travel along
            lines.insert_n_curves(20)
            flashes.append(LaggedStartMap(VShowPassingFlash, lines, time_width=1.5, lag_ratio=5e-3))
        return LaggedStart(*flashes, lag_ratio=0.6, run_time=run_time)


class NeuralNetworkBasic(Scene):
    def construct(self):
        random.seed(0)  # first line: Scene.__init__ reseeds, and a multi-scene run builds every scene first
        ## Title and network
        title = Text("신경망", font_size=60).to_edge(UP)
        network = NeuralNetwork([5, 10, 5])
        network.set_height(5)
        network.center()

        self.play(FadeIn(title, shift=DOWN))
        self.wait(0.5)

        ## Build layer by layer
        self.play(
            FadeIn(network.layers[0]),
            ShowCreation(network.lines[0], lag_ratio=0.01),
            FadeIn(network.layers[1], lag_ratio=0.5),
            run_time=2
        )
        self.play(
            ShowCreation(network.lines[1], lag_ratio=0.01),
            FadeIn(network.layers[2], lag_ratio=0.5),
            run_time=2
        )

        ## Weights and activations change
        for _ in range(4):
            self.play(
                network.animate.randomize_line_style().randomize_layer_values(),
                run_time=2,
                lag_ratio=1e-4
            )

        ## Layer labels in one row under the network
        labels = VGroup(*(Text(s, font_size=36).set_color(GREY_B) for s in ["입력", "은닉", "출력"]))
        for label, layer in zip(labels, network.layers):
            label.next_to(network, DOWN).match_x(layer)
        self.play(LaggedStartMap(FadeIn, labels, shift=UP, lag_ratio=0.3))
        self.wait()

        ## Forward pass
        self.play(network.get_forward_pass())
        self.wait()

        ## Keep it alive
        for _ in range(2):
            self.play(
                network.animate.randomize_line_style().randomize_layer_values(),
                run_time=2,
            )
        self.wait()
