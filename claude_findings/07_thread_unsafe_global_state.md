# Finding 07: Global State is Not Thread-Safe

## Location
[adapter.py](file:///Z:/never/vscode/manimani/manim_devops/adapter.py) — Line 4 and [assets/__init__.py](file:///Z:/never/vscode/manimani/manim_devops/assets/__init__.py) — Lines 17, 40, 56

## The Issue
The entire adapter system relies on a **single module-level global variable**:

```python
# adapter.py
_ACTIVE_DIAGRAM = None
```

Every `__rshift__`, `__lshift__`, and `__sub__` call reads this global. Every `__enter__` writes it. Every `__exit__` clears it.

If two threads each create an `AnimatedDiagram` context:

```python
# Thread 1                          # Thread 2
with AnimatedDiagram("Prod"):       with AnimatedDiagram("Staging"):
    # _ACTIVE_DIAGRAM = Prod            # _ACTIVE_DIAGRAM = Staging (OVERWRITES Prod!)
    ec2 >> rds                          lambda_fn >> dynamo
    # ec2 and rds register into         # Both register into Staging's topology
    # STAGING's topology, not Prod's!   # Thread 1's edges are lost
```

This also affects **async** code. If someone uses `asyncio.gather()` to render multiple diagrams concurrently, the global will be corrupted.

## Proposed Change
Replace the module global with Python's `contextvars.ContextVar`, which is both thread-safe and asyncio-safe:

```python
# adapter.py
import contextvars

_ACTIVE_DIAGRAM: contextvars.ContextVar['AnimatedDiagram'] = contextvars.ContextVar(
    '_ACTIVE_DIAGRAM', default=None
)

class AnimatedDiagram:
    def __enter__(self):
        self._token = _ACTIVE_DIAGRAM.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _ACTIVE_DIAGRAM.reset(self._token)
        # ... rest of exit logic
```

And in `CloudNode`:
```python
def __rshift__(self, target):
    import manim_devops.adapter as adapter
    diagram = adapter._ACTIVE_DIAGRAM.get()  # .get() instead of direct access
    if diagram is None:
        raise RuntimeError(...)
```

---

## 4 Questions

1. **Is anyone actually using this in threads today?** Probably not. But `contextvars` is zero-overhead for single-threaded code and provides correctness for free.
2. **Does `contextvars.ContextVar.reset()` guarantee cleanup even on exceptions?** Yes. `reset(token)` restores the previous value regardless of how the context exited.
3. **Will this break the existing tests?** The tests access `adapter._ACTIVE_DIAGRAM` directly (`assert adapter._ACTIVE_DIAGRAM is None`). These would need to change to `adapter._ACTIVE_DIAGRAM.get()`.
4. **Is `threading.local()` a viable alternative?** It works for threads but NOT for asyncio tasks. `contextvars` handles both.

## Self-Reflection
Global mutable state is the original sin of software engineering. The `diagrams` library itself uses the same pattern (`_default_graph = None`), so this was a conscious decision to match their API. But the `diagrams` library is a code-generation tool that runs in a single-shot script. `manim-devops` could realistically be used in a server context (e.g., a CI pipeline rendering multiple architecture diagrams in parallel), where thread safety matters.

## 5 Whys
1. **Why use a global variable?** Because `diagrams` uses one, and the adapter mimics `diagrams`' API.
2. **Why is a global variable dangerous?** Because it creates an implicit coupling between the `with` block and every `CloudNode` operator call, mediated by shared mutable state.
3. **Why not pass the diagram explicitly?** Because `EC2("web", "App")` inside the `with` block has no syntactic way to receive the diagram reference — the magic of `>>` depends on the global.
4. **Why does this matter for CI/CD?** Because a CI pipeline might render `prod.py`, `staging.py`, and `dev.py` in parallel threads via `concurrent.futures.ThreadPoolExecutor`.
5. **Why `contextvars` over `threading.local`?** Because Python's async ecosystem is growing, and `contextvars` was designed specifically for this problem by PEP 567.
