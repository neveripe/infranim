# Gemini Guidance: Fix 07 — Replace Global State with contextvars

## Context
`_ACTIVE_DIAGRAM` is a module-level global variable that is not thread-safe or asyncio-safe. See `claude_findings/07_thread_unsafe_global_state.md`.

## Priority: Low (Future-proofing)

## Strict Instructions

### Step 1: Update `adapter.py`

Replace the global variable with `contextvars.ContextVar`:

```python
import contextvars
from manim_devops.core import Topology

# Thread-safe and asyncio-safe context variable
_ACTIVE_DIAGRAM: contextvars.ContextVar['AnimatedDiagram'] = contextvars.ContextVar(
    '_ACTIVE_DIAGRAM', default=None
)

class AnimatedDiagram:
    def __init__(self, name: str = "Animated Infrastructure", skip_render: bool = False):
        self.name = name
        self.skip_render = skip_render
        self.topology = Topology(scale_factor=4.0)
        self._context_token = None
        
    def __enter__(self):
        self._context_token = _ACTIVE_DIAGRAM.set(self)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        _ACTIVE_DIAGRAM.reset(self._context_token)
        self._context_token = None
        
        if exc_type is not None:
            return False 
            
        if not self.skip_render:
            self._trigger_manim_render()
            
    # ... _trigger_manim_render remains unchanged
```

### Step 2: Update `assets/__init__.py` Operator Access

In each operator method (or the shared `_connect_via_adapter` if Fix 01 has been applied), change:

```python
# BEFORE:
import manim_devops.adapter as adapter
diagram = adapter._ACTIVE_DIAGRAM

# AFTER:
import manim_devops.adapter as adapter
diagram = adapter._ACTIVE_DIAGRAM.get()  # .get() returns None (the default) if unset
```

If Fix 01 has been applied, this change is needed only once in `_connect_via_adapter`. If not, update all three operator methods.

### Step 3: Update Tests

> **IMPORTANT:** Ask the user for permission before modifying IMMUTABLE tests.

The existing tests check:
```python
assert adapter_module._ACTIVE_DIAGRAM is not None  # inside context
assert adapter_module._ACTIVE_DIAGRAM is None       # outside context
```

These must change to:
```python
assert adapter_module._ACTIVE_DIAGRAM.get() is not None
assert adapter_module._ACTIVE_DIAGRAM.get() is None
```

These changes are in `test_animated_diagram_manages_global_state_IMMUTABLE` and `test_animated_diagram_cleans_up_on_exception_IMMUTABLE`.

### Step 4: Run Tests
```bash
python -m pytest tests/test_adapter.py -v
```

### Step 5: Verify Thread Safety (Optional New Test)

If the user approves adding a new test:

```python
import threading

def test_animated_diagram_is_thread_safe():
    """Verify two concurrent diagrams don't interfere."""
    from manim_devops.adapter import AnimatedDiagram, _ACTIVE_DIAGRAM
    from manim_devops.assets.aws import EC2
    
    results = {}

    def thread_fn(name, node_id):
        with AnimatedDiagram(name, skip_render=True) as diag:
            EC2(node_id, "Test")
            results[name] = len(diag.topology.nodes)

    t1 = threading.Thread(target=thread_fn, args=("Thread1", "web1"))
    t2 = threading.Thread(target=thread_fn, args=("Thread2", "web2"))
    t1.start(); t2.start()
    t1.join(); t2.join()
    
    # Each thread should have exactly 1 node in its own diagram
    assert results["Thread1"] == 1
    assert results["Thread2"] == 1
    assert _ACTIVE_DIAGRAM.get() is None
```

## What NOT To Do
- Do NOT use `threading.local()` — it doesn't work with `asyncio`.
- Do NOT remove the `default=None` from `ContextVar`. It's needed so `.get()` returns `None` outside a context.
- Do NOT store the token on the class itself (`AnimatedDiagram._token = ...`) — store it on the **instance** (`self._context_token`).
