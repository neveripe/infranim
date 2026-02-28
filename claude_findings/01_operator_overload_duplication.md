# Finding 01: Massive Code Duplication in Operator Overloads

## Location
[assets/__init__.py](file:///Z:/never/vscode/manimani/manim_devops/assets/__init__.py) — Lines 12–67

## The Issue
`__rshift__`, `__lshift__`, and `__sub__` contain **nearly identical code** repeated three times. Each method:
1. Imports `manim_devops.adapter`
2. Checks if `_ACTIVE_DIAGRAM is None`
3. Raises a `RuntimeError` with a slightly different operator symbol
4. Calls `diagram.topology.add_node()` on both operands
5. Calls `diagram.topology.connect()` with a variation

The only differences between the three methods are: (a) the error message string, (b) the direction of `connect()`, and (c) whether `connect()` is called once or twice.

```python
# This block is copy-pasted THREE times with minor variations:
import manim_devops.adapter as adapter
diagram = adapter._ACTIVE_DIAGRAM
if diagram is None:
    raise RuntimeError("...")
diagram.topology.add_node(self)
diagram.topology.add_node(target)
diagram.topology.connect(self, target)
return target
```

## Proposed Change
Extract the common logic into a private `_connect_via_adapter` method:

```python
def _connect_via_adapter(self, target, operator_name, edges):
    import manim_devops.adapter as adapter
    diagram = adapter._ACTIVE_DIAGRAM
    if diagram is None:
        raise RuntimeError(
            f"CloudNodes can only be connected via `{operator_name}` "
            f"inside an active `with AnimatedDiagram():` context block."
        )
    diagram.topology.add_node(self)
    diagram.topology.add_node(target)
    for src, tgt in edges:
        diagram.topology.connect(src, tgt)
    return target

def __rshift__(self, target):
    return self._connect_via_adapter(target, ">>", [(self, target)])

def __lshift__(self, target):
    return self._connect_via_adapter(target, "<<", [(target, self)])

def __sub__(self, target):
    return self._connect_via_adapter(target, "-", [(self, target), (target, self)])
```

---

## 5 Questions

1. **Does the deferred import (`import manim_devops.adapter`) execute 3 separate times** if a user chains `a >> b >> c` in one expression? Python caches module imports, so the overhead is minimal, but should we cache the reference to `adapter` at the class level after first access?
2. **Should `_connect_via_adapter` validate that `target` is a `CloudNode`?** Currently, `a >> 42` would pass the `RuntimeError` check and crash inside `add_node()` with a confusing `AttributeError` instead of a clear type error.
3. **Is the error message actually helpful?** A user who writes `a >> b` at the module level (not inside any function) will get "inside an active `with AnimatedDiagram():` context block" — but they might not know what `AnimatedDiagram` is if they came from the `diagrams` library.
4. **Does extracting to a shared method break the immutable test contract?** The tests assert on `RuntimeError` with `match="AnimatedDiagram"`. The refactored version preserves this string, so tests should pass unchanged.
5. **Should the `edges` parameter be a list of tuples or just a direction enum?** A tuple list is more flexible but slightly over-engineered for 3 fixed patterns.

## Self-Reflection
This is textbook DRY (Don't Repeat Yourself) violation. The original code was likely written incrementally — `__rshift__` first, then `__lshift__` and `__sub__` were copy-pasted. The fix is trivial, reduces the class from 58 lines to ~30, and makes adding new operators (e.g., `__or__` for `|` pipe syntax) a one-liner.

## 5 Whys
1. **Why is this duplicated?** Because each operator was implemented as a separate TDD step (Red → Green) and never refactored.
2. **Why wasn't it refactored?** Because the tests passed immediately and attention moved to the next phase.
3. **Why does this matter?** Because if the `_ACTIVE_DIAGRAM` lookup logic ever changes (e.g., to `contextvars`), you must update it in three places.
4. **Why is three repetitions dangerous?** Because the third copy is the one most likely to have a subtle drift (different error phrasing, missing a check).
5. **Why extract to a helper instead of a decorator?** Because the logic involves return values and parameter variations, which decorators handle awkwardly.
