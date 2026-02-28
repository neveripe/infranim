# Gemini Guidance: Fix 02 — Replace Linear Lookups with O(1) Data Structures

## Context
`Topology.nodes` is a `List` with O(n) deduplication. `Topology.edges` is a `List` with O(n) membership checks. `DevopsScene` constructs new lists per loop iteration. See `claude_findings/02_linear_lookups_performance.md`.

## Priority: Low (Performance, future-proofing)

## Strict Instructions

### Step 1: Refactor `Topology` in `manim_devops/core.py`

Change the internal storage from lists to dict/set, but expose properties so the public API stays the same:

```python
class Topology:
    def __init__(self, scale_factor: float = 3.0):
        self._nodes: dict[str, CloudNode] = {}
        self._edges: set[tuple[str, str]] = set()
        self._edge_order: list[tuple[str, str]] = []  # preserve draw order
        self.scale_factor = scale_factor

    @property
    def nodes(self) -> list[CloudNode]:
        """Public API: returns nodes in insertion order."""
        return list(self._nodes.values())

    @property
    def edges(self) -> list[tuple[str, str]]:
        """Public API: returns edges in insertion order."""
        return list(self._edge_order)

    def add_node(self, node: CloudNode) -> None:
        if node.node_id not in self._nodes:
            self._nodes[node.node_id] = node

    def add_nodes(self, nodes: list[CloudNode]) -> None:
        for node in nodes:
            self.add_node(node)

    def connect(self, source: CloudNode, target: CloudNode) -> None:
        edge = (source.node_id, target.node_id)
        if edge not in self._edges:
            self._edges.add(edge)
            self._edge_order.append(edge)
```

**Why `_edge_order`?** The `edges` property must return a deterministic order because `DevopsScene.render_topology()` iterates edges to draw lines. Changing the draw order would change the visual Z-stacking.

### Step 2: Update `calculate_layout` Internal Access

Inside `calculate_layout()`, change iterations to use internal storage:

```python
def calculate_layout(self) -> dict[str, tuple[float, float, float]]:
    G = nx.DiGraph()
    for node_id, node in self._nodes.items():
        G.add_node(node_id)
    for edge in self._edge_order:
        G.add_edge(edge[0], edge[1])
    # ... rest unchanged
    
    # Phase 4: use self._nodes.values() instead of self.nodes
    for node in self._nodes.values():
        if isinstance(node, NodeCluster):
            # ... unchanged
```

### Step 3: Optimize DevopsScene Node Lookups

In `DevopsScene.render_topology()`, build a lookup dict before the edge loop:

```python
# Before the edge-drawing loop (around line 127), add:
node_lookup = {n.node_id: n for n in topology.nodes}
for mob in self.mobjects:
    if hasattr(mob, 'node_id'):
        node_lookup[mob.node_id] = mob

# Then replace lines 129-130 with:
src_node = node_lookup[src_id]
tgt_node = node_lookup[tgt_id]
```

### Step 4: Run ALL Tests
```bash
python -m pytest tests/ -v
```

All 25 tests must pass. The properties ensure backward compatibility.

### Step 5: Run Coverage
```bash
python -m pytest --cov=manim_devops tests/ --cov-report=term-missing
```

Coverage must remain at 99%+.

## What NOT To Do
- Do NOT change any test assertions that reference `topology.nodes` or `topology.edges`. The `@property` preserves the public API.
- Do NOT remove `_edge_order`. Edge drawing order matters for visual determinism.
- Do NOT use `OrderedDict` — Python 3.7+ dicts already preserve insertion order.
