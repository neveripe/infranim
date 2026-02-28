# Gemini Guidance: Fix 01 — Extract Operator Overload Duplication

## Context
Claude identified that `__rshift__`, `__lshift__`, and `__sub__` in `manim_devops/assets/__init__.py` contain near-identical code repeated 3 times. See `claude_findings/01_operator_overload_duplication.md` for the full analysis.

## Priority: Low (Code Quality)

## Strict Instructions

### Step 1: Read the Current File
Open `manim_devops/assets/__init__.py` and confirm lines 12–67 contain three operator methods with duplicated logic.

### Step 2: Add a Private Helper Method
Insert the following method into `CloudNode`, **before** `__rshift__`:

```python
def _connect_via_adapter(self, target, operator_symbol, edges):
    """
    Shared logic for all operator overloads (>>, <<, -).
    Registers nodes and edges into the globally active AnimatedDiagram.
    
    Args:
        target: The right-hand operand CloudNode.
        operator_symbol: String like ">>" for error messages.
        edges: List of (source, target) tuples to register as directed edges.
    
    Returns:
        The target CloudNode (enables chaining).
    """
    import manim_devops.adapter as adapter
    diagram = adapter._ACTIVE_DIAGRAM
    if diagram is None:
        raise RuntimeError(
            f"CloudNodes can only be connected via `{operator_symbol}` inside an active "
            f"`with AnimatedDiagram():` context block."
        )
    diagram.topology.add_node(self)
    diagram.topology.add_node(target)
    for src, tgt in edges:
        diagram.topology.connect(src, tgt)
    return target
```

### Step 3: Refactor the Three Operator Methods
Replace the existing `__rshift__`, `__lshift__`, and `__sub__` with:

```python
def __rshift__(self, target):
    """Intercepts `node_a >> node_b` syntax. Forward directional edge."""
    return self._connect_via_adapter(target, ">>", [(self, target)])

def __lshift__(self, target):
    """Intercepts `node_a << node_b` syntax. Reverse directional edge."""
    return self._connect_via_adapter(target, "<<", [(target, self)])

def __sub__(self, target):
    """Intercepts `node_a - node_b` syntax. Bi-directional edge."""
    return self._connect_via_adapter(target, "-", [(self, target), (target, self)])
```

### Step 4: Run Tests — ZERO Changes to Tests
```bash
python -m pytest tests/test_adapter.py -v
```

All 9 tests in `test_adapter.py` must pass without modification. The tests match on `RuntimeError` with `match="AnimatedDiagram"`, and the refactored error message preserves that string.

### Step 5: Verify Coverage
```bash
python -m pytest --cov=manim_devops/assets tests/test_adapter.py --cov-report=term-missing
```

The `_connect_via_adapter` method must show 100% coverage.

## What NOT To Do
- Do NOT change any test file.
- Do NOT rename the operator methods.
- Do NOT change the return value (must return `target`, not `self`).
- Do NOT add type hints to the `edges` parameter that would require importing `CloudNode` inside the method.
