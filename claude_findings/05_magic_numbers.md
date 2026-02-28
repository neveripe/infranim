# Finding 05: Magic Numbers Scattered Across the Codebase

## Location
Multiple files — at least 10 hardcoded numeric constants with no named references.

## The Issue
The codebase is littered with unexplained numeric literals that control critical visual and mathematical behavior:

| Value | Location | Purpose | Problem |
|-------|----------|---------|---------|
| `42` | `core.py:64` | `spring_layout` seed | Why 42? Determinism is good, but the choice is unexplained |
| `3.0` | `core.py:39` | Default `scale_factor` | Why 3? What if the camera frame changes? |
| `4.0` | `adapter.py:15` | Adapter's `scale_factor` | Why 4.0 and not the default 3.0? |
| `10` | `core.py:113,123` | Node Z-index | Magic layer number, repeated twice |
| `0` | `core.py:149` | Edge Z-index | Paired with the `10` above |
| `5` | `cinematics.py:34` | Packet Z-index | Sandwiched between 0 and 10 |
| `16` | `core.py:121` | Label font size | Why 16? Is this readable at 480p? |
| `0.1` | `cinematics.py:32` | Packet dot radius | Tiny. Visible at low quality? |
| `1.2` | `cinematics.py:59` | Indicate scale factor | Why 1.2x and not 1.5x? |
| `3.0` | `core.py:157` | Animation `run_time` | 3 seconds — why? |
| `2` | `core.py:158` | Post-render `wait` time | 2 seconds — why? |
| `0.5` | `cinematics.py:113-114` | ScaleOut radius | Why 0.5 when other radii are dynamic? |
| `2.0` | `core.py:135-136` | Cluster fallback radius | Why 2.0? |

## Proposed Change
Create a `constants.py` module:

```python
# manim_devops/constants.py

# Layout
LAYOUT_SEED = 42
DEFAULT_SCALE_FACTOR = 3.0
ADAPTER_SCALE_FACTOR = 4.0

# Z-Index Layers
Z_EDGE = 0
Z_PACKET = 5
Z_NODE = 10

# Visual Sizing
LABEL_FONT_SIZE = 16
PACKET_RADIUS = 0.1
PULSE_SCALE_FACTOR = 1.2
CLUSTER_FALLBACK_RADIUS = 2.0
SCALE_OUT_NODE_RADIUS = 0.5

# Animation Timing
RENDER_DURATION = 3.0
POST_RENDER_WAIT = 2.0
```

---

## 3 Questions

1. **Why are there two different `scale_factor` values (3.0 vs 4.0)?** The `Topology` default is 3.0, but `AnimatedDiagram` overrides to 4.0. Is this because the adapter generates larger topologies? Or was it a late-phase tweak that was never reconciled?
2. **Are the Z-index values (0, 5, 10) safe against Manim's internal Z-index usage?** Manim may assign its own Z-indices to built-in objects like Camera backgrounds.
3. **Is `PACKET_RADIUS = 0.1` visible at `low_quality` (480p15)?** A 0.1 Manim-unit circle on a 480p canvas is approximately 4 pixels wide. This might be invisible on some monitors.

## Self-Reflection
Magic numbers are the *most common* code smell in rapid-prototype codebases. Each number was reasonable in isolation when it was typed, but in aggregate they form an invisible configuration layer that's impossible to tune without reading every file. The Z-index layering system (0/5/10) is particularly fragile — it works perfectly until someone needs a Z-index between 5 and 10 for a new visual element.

## 5 Whys
1. **Why are there magic numbers?** Because each was chosen during a specific TDD step where the value "just worked" visually.
2. **Why weren't they extracted earlier?** Because the project followed strict Red→Green→Refactor, but the "Refactor" step focused on logic, not aesthetics.
3. **Why does this matter for users?** Because a user who wants to adjust packet size, animation speed, or font size must grep the source code.
4. **Why use a `constants.py` instead of constructor parameters?** Both. Constants provide sane defaults; constructor parameters allow override. `DevopsScene(label_font_size=24)`.
5. **Why is the dual scale_factor (3.0 vs 4.0) especially problematic?** Because it means the same topology renders at different visual sizes depending on whether you use `DevopsScene` directly or the `AnimatedDiagram` adapter. This is surprising behavior.
