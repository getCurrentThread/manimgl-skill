"""Optional: raenimgl (imcommit's util lib). Needs `setup.sh --with-raenimgl`.

Importing raenimgl replaces manimlib's full_tex_to_svg (drops the fork's dvisvgm --fontmap flag),
so this file doubles as a check that Tex still renders with raenimgl imported.
"""
from manimlib import *
from raenimgl import *


class RaenimglTex(InteractiveScene, Scene2D):
    def construct(self):
        ## playw = play + wait(1), Create = raenimgl alias of ShowCreation
        eq = Tex(R"\frac{a}{b} = c", font_size=60)
        self.playw(Write(eq))
        self.playw(Create(SurroundingRectangle(eq, buff=0.2)), wait=0.5)
