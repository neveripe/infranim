# Coverage Strategy: Core Engine Orchestration (core.py)

## Explanation
The final piece of the 100% coverage puzzle is `manim_devops/core.py`, sitting at 61% (23 lines missing). The missing lines fall into two specific buckets:
1.  **Topology Bulk Loading:** The `add_nodes(self, nodes: List[CloudNode])` helper wrapper hasn't been directly tested natively using Pytest.
2.  **DevopsScene Rendering:** The massive `render_topology(self, topology: Topology)` wrapper that loops through nodes, invokes coordinates, explicitly sets the Z-Index, and builds the visual `Create()` animation array. Because our execution thus far ran this via a separate `manim -ql` subprocess, Pytest missed covering it. We must trick Pytest into running a Manim Scene "dry run" natively to trace the execution path.

---

## The 3 Why's (Validating the Test Necessity)

1. **Why do we need to test `add_nodes` explicitly when it just loops `add_node`?**
   Because maintaining 100% coverage is binary. Even if a function is just a python `for` loop, if it's not covered, it's a hole in the contract. What if a developer accidentally refactors it to pass a single object instead of a list? The `TypeError` would crash the application.
2. **Why is it hard to test `DevopsScene` directly in Pytest?**
   `DevopsScene` inherits from Manim's `Scene`. Manim scenes are inherently stateful and rely on a global `config` object to know where to write MP4 files to the hard drive, what resolution to use, and when to invoke FFmpeg. Calling `scene.play()` in a raw Python test usually crashes without a proper context. We have to invoke `manim.tempconfig({"dry_run": True})` to bypass the FFmpeg rendering and only execute the Python logic in memory.
3. **Why make these tests Immutable?**
   Because the Z-Index logic living inside `render_topology()` is critical. We explicitly wrote `node.set_z_index(10)` and `line.set_z_index(0)`. If a future developer deletes those lines, the test must scream that the visual contract was violated before the MP4 renders.

---

## 3 Deep Technical Questions (Visual Engine Testing)

1. **Dry Run Validation:** Does Manim's `"dry_run": True` configuration actually populate the Mobjects into the Scene's internal state array, or does it skip memory allocation entirely? If it skips allocation, we can't assert the Z-Indices are correct.
2. **Scene Instantiation State:** When we manually instantiate `DevopsScene()`, Manim often executes the `construct()` method immediately if running through the CLI, but defers it in Pytest. If `construct()` is deferred, we can safely invoke `render_topology()` manually.
3. **Integration Mocking:** Should we use `unittest.mock` to intercept networkx and geometry arrays to keep this test "purely unit", or is it okay for an integration test to trace the whole system from math to Mobject?

---

## Self-Reflection
Testing visual frame-by-frame rendering libraries in native Pytest is notoriously fragile. Our goal here is not to assert that "Pixel 50x50 is Orange" (which is effectively impossible without snapshot testing). Our goal is to assert that the Python logic arrays executed without throwing an error before the video render.

We will write `test_core.py`.
First, we will test `add_nodes` with a duplicate insertion to ensure the deduplication logic executes. 
Second, we will wrap `DevopsScene` in a `tempconfig` dry run and invoke `render_topology()` to trace every missing line of code organically.
