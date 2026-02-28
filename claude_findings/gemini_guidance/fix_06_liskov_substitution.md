# Gemini Guidance: Fix 06 — Fix Liskov Substitution Violation

## Context
`NodeCluster` inherits from `CloudNode` but cannot be used where `CloudNode` is expected, requiring `isinstance` guards throughout the codebase. See `claude_findings/06_liskov_substitution_violation.md`.

## Priority: Medium (Architectural, but requires careful migration)

> **⚠️ WARNING:** This is the most invasive refactor. It touches the type hierarchy used across the entire codebase. Proceed with extreme caution and run tests after every sub-step.

## Strict Instructions

### Step 1: Create `GraphEntity` Base Class

In `manim_devops/assets/__init__.py`, add a new base class **above** `CloudNode`:

```python
from typing import Optional

class GraphEntity:
    """
    Pure identity for any object in the topology graph.
    Has an ID and label, but is NOT necessarily renderable.
    """
    def __init__(self, node_id: str, label: Optional[str] = None):
        self.node_id = node_id
        self.label = label

class CloudNode(GraphEntity):
    """
    A renderable entity in the architecture graph.
    Supports operator overloads for edge creation.
    """
    def __init__(self, node_id: str, label: Optional[str] = None):
        super().__init__(node_id, label)

    # ... keep all operator overloads (__rshift__, __lshift__, __sub__) here
```

### Step 2: Make NodeCluster Inherit from GraphEntity

In `manim_devops/core.py`, change:

```python
# BEFORE:
class NodeCluster(CloudNode):

# AFTER:
from manim_devops.assets import GraphEntity
class NodeCluster(GraphEntity):
```

### Step 3: Update Topology Type Hints

In `manim_devops/core.py`, update `Topology` to accept `GraphEntity`:

```python
class Topology:
    def __init__(self, scale_factor: float = 3.0):
        self.nodes: List[GraphEntity] = []  # was List[CloudNode]
        # ...

    def add_node(self, node: GraphEntity) -> None:  # was CloudNode
        # ...

    def connect(self, source: GraphEntity, target: GraphEntity) -> None:  # was CloudNode
        # ...
```

### Step 4: Simplify isinstance Checks in DevopsScene

Now the rendering loop can use `isinstance(node, CloudNode)` as a **positive** check instead of a negative `isinstance(node, NodeCluster)` exclusion:

```python
# BEFORE (line 105):
if isinstance(node, NodeCluster):
    continue

# AFTER:
if not isinstance(node, CloudNode):
    continue
```

The edge radius calculation similarly simplifies:
```python
# BEFORE (line 135):
src_radius = 2.0 if isinstance(src_node, NodeCluster) else src_node.width / 2.0

# AFTER:
src_radius = src_node.width / 2.0 if isinstance(src_node, CloudNode) else CLUSTER_FALLBACK_RADIUS
```

### Step 5: Update cinematics.py Import

```python
# BEFORE:
from manim_devops.assets import CloudNode

# AFTER:
from manim_devops.assets import CloudNode, GraphEntity
```

The `ScaleOutAction` signature type hint changes:
```python
def ScaleOutAction(scene, cluster: NodeCluster, new_child: CloudNode, target: GraphEntity = None):
```

### Step 6: Update conftest.py

The `conftest.py` fixture creates `CloudNode` objects for graph math tests. These should become `GraphEntity` if you want pure-math testing, but since `CloudNode` inherits from `GraphEntity`, the existing `CloudNode("dns", "Route53")` calls still work. **No changes needed in conftest.py.**

### Step 7: Export GraphEntity

In `manim_devops/assets/__init__.py`, ensure both are importable:
```python
# This happens naturally since both classes are defined in the file.
# But verify that other modules can do:
from manim_devops.assets import CloudNode, GraphEntity
```

### Step 8: Run Tests After EACH Step
```bash
python -m pytest tests/ -v
```

Run tests after Step 2, Step 3, Step 4, and Step 6 individually. Fix any breakage before proceeding.

## What NOT To Do
- Do NOT move `NodeCluster` out of `core.py`. It depends on `CloudNode` for its child type.
- Do NOT add operator overloads to `GraphEntity`. Only `CloudNode` should support `>>`.
- Do NOT change test assertions unless they specifically check `isinstance(cluster, CloudNode)` — ask the user first.
- Do NOT rename `CloudNode` to anything else. The name is part of the public API.
