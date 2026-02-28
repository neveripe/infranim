# Gemini Guidance: Fix 05 — Extract Magic Numbers into Constants

## Context
13+ hardcoded numeric constants are scattered across 4 files with no named references. See `claude_findings/05_magic_numbers.md`.

## Priority: Low (Maintainability)

## Strict Instructions

### Step 1: Create `manim_devops/constants.py`

```python
"""
Central configuration constants for the manim-devops library.
All visual, mathematical, and timing defaults should be defined here.
"""

# ─── Layout Engine ───────────────────────────────────────────
LAYOUT_SEED = 42
DEFAULT_SCALE_FACTOR = 3.0
ADAPTER_SCALE_FACTOR = 4.0

# ─── Z-Index Layering ───────────────────────────────────────
# Higher values render on TOP of lower values.
Z_EDGE = 0           # Connection lines (bottom layer)
Z_PACKET = 5         # Moving traffic dots (middle layer)
Z_NODE = 10          # Infrastructure icons (top layer)

# ─── Visual Sizing ──────────────────────────────────────────
LABEL_FONT_SIZE = 16
PACKET_RADIUS = 0.1
PULSE_SCALE_FACTOR = 1.2
CLUSTER_FALLBACK_RADIUS = 2.0
SCALE_OUT_NODE_RADIUS = 0.5
FALLBACK_CIRCLE_RADIUS = 0.5

# ─── Animation Timing ───────────────────────────────────────
RENDER_DURATION = 3.0      # seconds for the initial topology draw
POST_RENDER_WAIT = 2.0     # seconds to pause after drawing

# ─── Colors ─────────────────────────────────────────────────
EDGE_COLOR = "#FFFFFF"
DEFAULT_TRAFFIC_COLOR = "#00FF00"
AWS_FALLBACK_COLOR = "#FF9900"
```

### Step 2: Update Each File to Import Constants

**`core.py`** — Replace hardcoded values:
```python
from manim_devops.constants import (
    LAYOUT_SEED, DEFAULT_SCALE_FACTOR, Z_NODE, Z_EDGE,
    LABEL_FONT_SIZE, CLUSTER_FALLBACK_RADIUS,
    RENDER_DURATION, POST_RENDER_WAIT, EDGE_COLOR
)

# Line 39: scale_factor=3.0 → scale_factor=DEFAULT_SCALE_FACTOR
# Line 64: seed=42 → seed=LAYOUT_SEED
# Line 113: set_z_index(10) → set_z_index(Z_NODE)
# Line 121: font_size=16 → font_size=LABEL_FONT_SIZE
# Line 123: set_z_index(10) → set_z_index(Z_NODE)
# Line 135-136: 2.0 → CLUSTER_FALLBACK_RADIUS
# Line 145: color="#FFFFFF" → color=EDGE_COLOR
# Line 149: set_z_index(0) → set_z_index(Z_EDGE)
# Line 157: run_time=3.0 → run_time=RENDER_DURATION
# Line 158: self.wait(2) → self.wait(POST_RENDER_WAIT)
```

**`cinematics.py`** — Replace hardcoded values:
```python
from manim_devops.constants import (
    Z_PACKET, PACKET_RADIUS, PULSE_SCALE_FACTOR,
    SCALE_OUT_NODE_RADIUS, Z_EDGE, EDGE_COLOR, DEFAULT_TRAFFIC_COLOR
)

# Line 6: color="#00FF00" → color=DEFAULT_TRAFFIC_COLOR
# Line 32: radius=0.1 → radius=PACKET_RADIUS
# Line 34: set_z_index(5) → set_z_index(Z_PACKET)
# Line 59: scale_factor=1.2 → scale_factor=PULSE_SCALE_FACTOR
# Line 113-114: source_radius=0.5 → source_radius=SCALE_OUT_NODE_RADIUS (same for target)
# Line 117: color="#FFFFFF" → color=EDGE_COLOR
# Line 119: set_z_index(0) → set_z_index(Z_EDGE)
```

**`adapter.py`** — Replace hardcoded values:
```python
from manim_devops.constants import ADAPTER_SCALE_FACTOR

# Line 15: scale_factor=4.0 → scale_factor=ADAPTER_SCALE_FACTOR
```

**`assets/aws.py`** — Replace hardcoded values:
```python
from manim_devops.constants import FALLBACK_CIRCLE_RADIUS, AWS_FALLBACK_COLOR

# Line 30: radius=0.5 → radius=FALLBACK_CIRCLE_RADIUS
# Line 30: color="#FF9900" → color=AWS_FALLBACK_COLOR
```

### Step 3: Run ALL Tests
```bash
python -m pytest tests/ -v
```

All 25 tests must pass. No semantic behavior changes — only naming.

### Step 4: Run Coverage
```bash
python -m pytest --cov=manim_devops tests/ --cov-report=term-missing
```

Coverage of `constants.py` should be 100% (all constants are used).

## What NOT To Do
- Do NOT change any numeric values. This refactor is **naming only** — same numbers, just referenced by name.
- Do NOT make constants configurable via constructor parameters yet. That's a separate enhancement.
- Do NOT add `constants.py` to `__init__.py` exports. It's an internal module.
