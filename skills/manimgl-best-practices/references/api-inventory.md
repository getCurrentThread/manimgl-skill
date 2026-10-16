# 포크 API 목록 (`from manimlib import *` 기준)

- 생성 방법: 포크 @455a4201이 설치된 환경에서 `from manimlib import *`로 들어오는 클래스를 기반 클래스별로 나누어 자동 생성했다. 손으로 옮겨 적은 목록이 아니다.
- 여기 없는 이름은 star-import로 쓸 수 없다. 예: `OldTex`, `OldTexText`는 export되지 않는다.
- 시그니처는 설치된 소스에서 직접 확인한다.
  ```
  uv run python -c "import inspect, manimlib; print(inspect.signature(manimlib.Axes.get_graph))"
  ```

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

