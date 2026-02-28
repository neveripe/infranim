"""
Central configuration constants for the manim-devops library.
All visual, mathematical, and timing defaults are defined here
so they can be tuned in one place instead of grepping the codebase.
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
