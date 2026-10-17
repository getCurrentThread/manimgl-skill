# Fork class list (Scene / Animation / Mobject, based on `from manimlib import *`)

- How it was made: auto-generated in an environment with fork @455a4201 installed, by grouping the classes that `from manimlib import *` brings in by base class. It is not a hand-copied list. Re-check with `uv run --project <uv project> python ${CLAUDE_PLUGIN_ROOT}/scripts/check_inventory.py` (exit 0 = no drift).
- Scope: only subclasses of Scene, Animation and Mobject are listed. Functions (`always_redraw`), rate functions (`smooth`), constants (`UP`, `BLUE`, `DEG`) and other classes (`Camera`, `CoordinateSystem`) come in through star-import even though they are not in the list.
- Scene/Animation/Mobject classes not listed here cannot be used through star-import. Example: `OldTex` and `OldTexText` are not exported (defined at F:manimlib/mobject/svg/old_tex_mobject.py:181,317).
- Check signatures directly in the installed source.
  ```
  uv run python -c "import inspect, manimlib; print(inspect.signature(manimlib.Axes.get_graph))"
  ```
- This document holds only the class list. `CameraFrame` method signatures are in [korean-tex-3d.md](korean-tex-3d.md) §C2, and updater cautions are in [SKILL.md](../SKILL.md) §10.

## Scene (3)

- `scene.interactive_scene`: InteractiveScene
- `scene.scene`: Scene, ThreeDScene

## Animation (80)

- `animation.animation`: Animation
- `animation.composition`: AnimationGroup, LaggedStart, LaggedStartMap, Succession
- `animation.creation`: AddTextWordByWord, DrawBorderThenFill, ShowCreation, ShowIncreasingSubsets, ShowPartial, ShowSubmobjectsOneByOne, Uncreate, Write
- `animation.fading`: Fade, FadeIn, FadeInFromPoint, FadeOut, FadeOutToPoint, FadeTransform, FadeTransformPieces, VFadeIn, VFadeInThenOut, VFadeOut
- `animation.growing`: GrowArrow, GrowFromCenter, GrowFromEdge, GrowFromPoint
- `animation.indication`: AnimationOnSurroundingRectangle, ApplyWave, CircleIndicate, Flash, FlashAround, FlashUnder, FlashyFadeIn, FocusOn, Indicate, ShowCreationThenDestruction, ShowCreationThenDestructionAround, ShowCreationThenFadeAround, ShowCreationThenFadeOut, ShowPassingFlash, ShowPassingFlashAround, TurnInsideOut, VShowPassingFlash, WiggleOutThenIn
- `animation.movement`: ComplexHomotopy, Homotopy, MoveAlongPath, PhaseFlow, SmoothedVectorizedHomotopy
- `animation.numbers`: ChangeDecimalToValue, ChangingDecimal, CountInFrom
- `animation.rotation`: Rotate, Rotating
- `animation.specialized`: Broadcast
- `animation.transform`: ApplyComplexFunction, ApplyFunction, ApplyMatrix, ApplyMethod, ApplyPointwiseFunction, ApplyPointwiseFunctionToCenter, CyclicReplace, FadeToColor, MoveToTarget, ReplacementTransform, Restore, ScaleInPlace, ShrinkToCenter, Swap, Transform, TransformFromCopy
- `animation.transform_matching_parts`: TransformMatchingParts, TransformMatchingShapes, TransformMatchingStrings, TransformMatchingTex
- `animation.update`: MaintainPositionRelativeTo, UpdateFromAlphaFunc, UpdateFromFunc
- `mobject.svg.drawings`: ClockPassesTime

## Mobject (149)

- `camera.camera_frame`: CameraFrame
- `mobject.boolean_ops`: Difference, Exclusion, Intersection, Union
- `mobject.changing`: AnimatedBoundary, TracedPath, TracingTail
- `mobject.coordinate_systems`: Axes, ComplexPlane, NumberPlane, ThreeDAxes
- `mobject.frame`: FullScreenFadeRectangle, FullScreenRectangle, ScreenRectangle
- `mobject.functions`: FunctionGraph, ImplicitFunction, ParametricCurve
- `mobject.geometry`: AnnularSector, Annulus, Arc, ArcBetweenPoints, Arrow, ArrowTip, Circle, CubicBezier, CurvedArrow, CurvedDoubleArrow, DashedLine, Dot, Elbow, Ellipse, Line, Polygon, Polyline, Rectangle, RegularPolygon, RoundedRectangle, Sector, SmallDot, Square, StrokeArrow, TangentLine, TipableVMobject, Triangle, Vector
- `mobject.interactive`: Button, Checkbox, ColorSliders, ControlMobject, ControlPanel, EnableDisableButton, LinearNumberSlider, MotionMobject, Textbox
- `mobject.matrix`: DecimalMatrix, IntegerMatrix, Matrix, MobjectMatrix, TexMatrix
- `mobject.mobject`: Group, Mobject, Point
- `mobject.number_line`: NumberLine, Slider, UnitInterval
- `mobject.numbers`: DecimalNumber, Integer
- `mobject.probability`: BarChart, SampleSpace
- `mobject.shape_matchers`: BackgroundRectangle, Cross, SurroundingRectangle, Underline
- `mobject.svg.brace`: Brace, BraceLabel, BraceText, LineBrace
- `mobject.svg.drawings`: Bubble, Checkmark, Clock, Dartboard, DieFace, DoubleSpeechBubble, Exmark, Laptop, Lightbulb, OldSpeechBubble, OldThoughtBubble, Piano, Piano3D, SpeechBubble, Speedometer, ThoughtBubble, VectorizedEarth, VideoIcon, VideoSeries
- `mobject.svg.special_tex`: BulletedList, TexTextFromPresetString, Title
- `mobject.svg.string_mobject`: StringMobject
- `mobject.svg.svg_mobject`: SVGMobject, VMobjectFromSVGPath
- `mobject.svg.tex_mobject`: Tex, TexText
- `mobject.svg.text_mobject`: Code, MarkupText, Text
- `mobject.three_dimensions`: Cone, Cube, Cylinder, Disk3D, Dodecahedron, Line3D, Prism, Prismify, Sphere, Square3D, SurfaceMesh, Torus, VCube, VGroup3D, VPrism
- `mobject.types.dot_cloud`: DotCloud, GlowDot, GlowDots, TrueDot
- `mobject.types.image_mobject`: ImageMobject
- `mobject.types.point_cloud_mobject`: PGroup, PMobject
- `mobject.types.surface`: ParametricSurface, SGroup, Surface, TexturedGeometry, TexturedSurface, ThreeDModel
- `mobject.types.vectorized_mobject`: CurvesAsSubmobjects, DashedVMobject, VGroup, VHighlight, VMobject, VectorizedPoint
- `mobject.value_tracker`: ComplexValueTracker, ExponentialValueTracker, ValueTracker
- `mobject.vector_field`: AnimatedStreamLines, StreamLines, TimeVaryingVectorField, VectorField

