# Reality Check: Code vs Docs vs Common Sense

> Authored: 2026-02-28 by Claude (Opus 4.6)
> Method: Line-by-line source audit matched against README claims, docstrings, and real-world usage expectations

---

## Finding R-01: The Package Is Named Wrong

**File:** `pyproject.toml:6`

```python
name = "manim-devops"
```

We just published to GitHub as **`infranim`**. The PyPI package name is still `manim-devops`. The import is `import manim_devops`. The GitHub repo is `infranim`. That's three names for the same thing.

A user who finds `github.com/neveripe/infranim` will run `pip install infranim` and get nothing. They'd need to run `pip install manim-devops` — but only if they know that's the internal name.

### 3 Questions
1. Should the package name match the repo name?
2. Would renaming the package break existing imports?
3. Is `infranim` even the right name for the *module* (currently `manim_devops`)?

### Self-Reflection
This is the #1 issue. Everything else in this document is secondary to the fact that the project can't be found or installed by its public name. This happened because naming the repo was done at the very end, after the package structure was already hardcoded. That's backwards — naming should come first.

### 3 Whys
1. **Why does it matter?** Because discoverability is adoption. A user who can't `pip install infranim` will assume the project is broken.
2. **Why wasn't this caught?** Because I treated "create a GitHub repo" and "name the Python package" as separate concerns. They're the same concern.
3. **Why is it so hard to fix now?** Because renaming the module from `manim_devops` to `infranim` requires updating every import in every file, test, and doc. It's possible (and necessary), but it's a 30-minute refactor, not a 1-minute find-replace.

---

## Finding R-02: `import numpy` Is Unused in `core.py`

**File:** `core.py:2`

```python
import numpy as np
```

`numpy` is never used in `core.py`. It was needed during the spike phase when coordinates were `np.ndarray`, but now they're plain `tuple[float, float, float]`. The import persists as an unused dependency in this file.

### 3 Questions
1. Could removing it break anything?
2. Is `numpy` still needed in the project at all?
3. Does this indicate other dead imports?

### Self-Reflection
It won't break anything because `layout.py` and `cinematics.py` still use numpy legitimately. But it's the kind of sloppiness that signals "nobody reviewed this" — which is literally true, as stated in our DEVELOPMENT.md. Dead imports are a smell of code that evolved without cleanup.

### 3 Whys
1. **Why is it there?** Because it was needed in an earlier phase and never removed.
2. **Why wasn't it caught?** Because no linter is configured. There's no `ruff`, `flake8`, or `pylint` in the dev dependencies.
3. **Why does it matter?** It doesn't, functionally. But it matters perceptually — serious projects lint their code.

---

## Finding R-03: `OrthogonalRouter.corner_radius` Is Accepted But Never Used

**File:** `layout.py:8-9`

```python
def __init__(self, corner_radius: float = 0.2):
    self.corner_radius = corner_radius
```

The `corner_radius` parameter is stored but never read. The actual L-bend path has sharp 90-degree corners, not radiused ones. The constructor promises something the implementation doesn't deliver.

### 3 Questions
1. Was this planned for rounded corners that were never implemented?
2. Should we document that this parameter is a no-op?
3. Or should we implement rounded corners?

### Self-Reflection
This is a classic "aspirational API" pattern — the interface was designed before the implementation, and the implementation never caught up. It's harmless but dishonest. Any user who passes `corner_radius=1.5` expecting rounded bends will get sharp corners and wonder what's broken.

### 3 Whys
1. **Why was it added?** Because Gemini's strategy doc mentioned smooth routing as a goal.
2. **Why wasn't it implemented?** Because the L-bend path math (`_calculate_orthogonal_path`) is simple and functional — rounded corners require Bézier curves, which is a much harder problem.
3. **Why is it dangerous?** Because a documented parameter that does nothing is worse than no parameter at all. It's a lie in the API contract.

---

## Finding R-04: `AnimatedDiagram` Docstring Promises Auto-Harvesting That Doesn't Exist

**File:** `adapter.py:13-14`

```python
"""Any CloudNodes instantiated within the `with AnimatedDiagram():` block will 
automatically be harvested, routed, and optionally rendered via Manim upon exit."""
```

This is false. CloudNodes are NOT automatically harvested. They are only added to the topology when connected via `>>`, `<<`, or `-`. If you write:

```python
with AnimatedDiagram("Test"):
    alb = ALB("alb", "Load Balancer")
    web = EC2("web", "Server")
    # No >> connection
```

The nodes are **silently discarded**. No error, no warning, no auto-harvest. The user gets an empty video.

In the real `diagrams` library this docstring claims to mimic, nodes ARE auto-harvested just by being instantiated inside the `with` block. Our implementation doesn't do that.

### 3 Questions
1. Should we implement auto-harvesting (like `diagrams` does)?
2. Or should we fix the docstring to be honest?
3. Or should we raise a warning for unreachable nodes?

### Self-Reflection
This is the most dangerous finding because it looks like it works but silently fails. A user who writes `alb = ALB(...)` inside the context block and doesn't connect it will assume it'll appear in the video. It won't. They'll debug for 20 minutes before realizing they forgot `>>`.

### 3 Whys
1. **Why does the docstring say "automatically harvested"?** Because Gemini modeled the API after the `diagrams` library, which does auto-harvest.
2. **Why doesn't the implementation do it?** Because auto-harvesting requires metaclass magic or `__init_subclass__` hooks — Gemini implemented the simpler operator-based approach.
3. **Why is it the most dangerous issue?** Because "silent success that is actually failure" is the hardest class of bug to diagnose.

---

## Finding R-05: `NodeCluster` Silently Wraps at 6 Children

**File:** `core.py:36`

```python
offsets = [-1.0, 1.0, -2.0, 2.0, -3.0, 3.0] 
for i, child in enumerate(self.children):
    offset_x = offsets[i % len(offsets)]
```

The `%` modulo wrapping means that the 7th child gets the same position as the 1st, the 8th gets the same as the 2nd, etc. They'll be drawn on top of each other with no error or warning.

In a real auto-scaling group, having 7+ instances is common. This code handles it by stacking them invisibly.

### 3 Questions
1. Should the offsets be generated dynamically instead of hardcoded?
2. Should this raise a warning when wrapping occurs?
3. Does anyone actually test with >6 children?

### Self-Reflection
This is a time-bomb. It works perfectly for the demo (which has 3 children) and all the tests (which use 1-2 children). But the first real user who models an 8-node Kubernetes cluster will get overlapping icons and think the library is broken.

### 3 Whys
1. **Why hardcoded?** Because the spike was designed for a simple demo, not production.
2. **Why does `%` silently wrap instead of erroring?** Because Python's modulo operator is designed to never fail — it's doing exactly what it's told.
3. **Why is 6 the magic limit?** It isn't — it's just how many values Gemini typed into the list. There's no mathematical rationale for 6 as a limit.

---

## Finding R-06: `Topology.connect()` Type Hint Lies

**File:** `core.py:71`

```python
def connect(self, source: CloudNode, target: CloudNode) -> None:
    edge = (source.node_id, target.node_id)
```

The type hint says `CloudNode` but the method only accesses `.node_id`. It works with any `GraphEntity` — and it MUST, because `NodeCluster(GraphEntity)` is passed to `connect()` in the visual adapter test. The type hint actively misleads: it says "I need a CloudNode" when really it needs "anything with a node_id".

### 3 Questions
1. Should the type hint be `GraphEntity` instead of `CloudNode`?
2. Are there other type hints that lie like this?
3. Should `Topology._nodes` be typed as `dict[str, GraphEntity]` too?

### Self-Reflection
Yes, there are other lying type hints. `Topology._nodes` is typed `dict[str, CloudNode]` but stores `NodeCluster` objects which are `GraphEntity`, not `CloudNode`. The entire Topology is type-confused after the Liskov refactor — we changed the inheritance but didn't update the type annotations.

### 3 Whys
1. **Why are the types wrong?** Because the Liskov refactor (Finding 06) changed `NodeCluster`'s parent from `CloudNode` to `GraphEntity`, but I only updated the runtime behavior — not the type annotations.
2. **Why does it still work?** Because Python type hints are not enforced at runtime. They're purely advisory.
3. **Why does it matter?** Because users with `mypy` or `pyright` will get false type errors, and contributors who read the hints will build wrong mental models.

---

## Finding R-07: The README Example Doesn't Match the Actual API

**File:** `README.md:47-57`

```python
class MyScene(DevopsScene):
    def construct(self):
        topo = Topology()
        web = EC2("web", "Web Server")
        db = RDS("db", "Database")
        topo.add_nodes([web, db])
        topo.connect(web, db)
        self.render_topology(topo)
        self.play(TrafficFlow(self, web, db))
```

This works correctly — but it doesn't mention that `render_topology` has **side effects that are critical for `TrafficFlow` to work**. Specifically, `render_topology` populates `self.rendered_edges` and `self.rendered_coords`. If someone calls `TrafficFlow` without calling `render_topology` first, they get a cryptic `KeyError` with no explanation of what went wrong.

There's no documented API contract for "you must call X before Y."

### 3 Questions
1. Should `TrafficFlow` raise a helpful error if the scene hasn't been rendered yet?
2. Should `render_topology` return something explicit that `TrafficFlow` requires?
3. Is state being stored in the right place (scene attributes vs explicit objects)?

### Self-Reflection
This is the "it works if you follow the happy path" problem. The README shows the happy path. But every non-trivial user will eventually deviate — calling animations before rendering, calling `render_topology` twice, or mixing programmatic and adapter APIs. None of these scenarios produce helpful errors.

### 3 Whys
1. **Why is state hidden in scene attributes?** Because Manim's architecture encourages storing state on `self` — the Scene is the god object.
2. **Why no guard clause?** Because the code was built test-first against known-good scenarios. Nobody wrote a test for "what if I call TrafficFlow before render_topology?"
3. **Why is this a user problem?** Because the user didn't write the code — two AIs did. And neither AI tested the unhappy paths.

---

## Severity Summary

| Finding | Severity | Effort to Fix |
|---------|----------|---------------|
| R-01: Package named wrong | 🔴 **Critical** | 30 min (rename module + all imports) |
| R-02: Unused numpy import | 🟢 Trivial | 1 min |
| R-03: Unused corner_radius | 🟡 Moderate | 5 min (remove or implement) |
| R-04: Docstring lies about auto-harvest | 🔴 **Critical** | 5 min (fix docstring) or 2 hr (implement it) |
| R-05: NodeCluster wraps at 6 | 🟡 Moderate | 15 min (dynamic offset calculation) |
| R-06: Type hints lie post-Liskov | 🟡 Moderate | 15 min (update all annotations) |
| R-07: Undocumented call ordering | 🟡 Moderate | 20 min (add guard clauses + docs) |
