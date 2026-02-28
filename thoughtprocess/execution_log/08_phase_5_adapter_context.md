# Execution Log: AnimatedDiagram Context Manager (adapter.py)

## Explanation
In Python, the `diagrams` library relies heavily on a global Context Manager block (`with Diagram("Title"):`) to capture state. This allows child objects like `EC2("Web")` to be instantiated anywhere inside that indentation block and automatically register themselves to the global graph without explicitly passing the `Diagram` object as an argument to every node.

To mimic this perfectly, we must build an `AnimatedDiagram` context manager that maintains a thread-local or class-level global reference to a `Topology` object.

---

## The 3 Why's (Validating the Test Necessity)

1. **Why use a global context tracker?**
   Because if a user writes `with AnimatedDiagram():` and then on the next line writes `EC2("web")`, the `EC2` class instantiation logic needs to look up the call stack to see if it's currently inside a diagram. If it is, it must `append` itself to the topology automatically.
2. **Why hook the `__exit__` method?**
   Because when the Python interpreter leaves the `with` indentation block, the diagram architecture is complete. The `__exit__` method is the exact trigger point where we should take the accumulated `Topology`, construct a `DevopsScene`, and hand it over to the Manim rendering CLI programmatically.
3. **Why make these tests Immutable?**
   Because global state mutation in Python is extremely dangerous. If the context manager fails to clear its global state upon exiting, Test A could pollute the Topology of Test B, causing cascading false-positive failures across the entire CI pipeline.

---

## 3 Deep Technical Questions (The `AnimatedDiagram` Implementation)

1. **Global Variable vs Thread Local:** Do we just use a basic module-level `ACTIVE_DIAGRAM = None` global variable? 
   *Answer:* Yes, for the MVP. Since Manim renders locally on a single thread structure, a module-level global is sufficient and avoids the complexity of `threading.local()`.
2. **Mocking Manim Execution:** When `__exit__` runs, we don't want it to actually spin up FFmpeg during our unit tests, because that takes 5 seconds. How do we test the execution logic cleanly?
   *Answer:* The `AnimatedDiagram` constructor should take an optional `skip_render=True` flag used strictly for Pytest integration.
3. **Implicit Edge Overloading:** If `node_a >> node_b` is evaluated, the `__rshift__` method executes. Does it need to know about the `AnimatedDiagram` context?
   *Answer:* Yes. `__rshift__` on `CloudNode` must verify that an `ACTIVE_DIAGRAM` exists, and if so, call `ACTIVE_DIAGRAM.topology.connect(node_a, node_b)`.

---

## Self-Reflection & Execution Blueprint
The `AnimatedDiagram` isn't just a wrapper; it's a completely invisible state dependency injector. It requires defining a global variable inside `adapter.py`, hooking `__enter__` to set the variable, and hooking `__exit__` to clear the variable and trigger the render.

**The Red Phase Strategy:**
Write a Pytest in a new file `test_adapter.py` that asserts that instantiating an `AnimatedDiagram` correctly sets a global variable, that `Topology` nodes can be added to it, and that exiting the context loop resets the global variable to `None` cleanly.
