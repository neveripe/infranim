# Execution Log: Programmatic Manim FFmpeg Execution

## Explanation
The final piece of the `AnimatedDiagram` adapter is the payload delivery. The user writes a standard python script (not a `manim` CLI command). When the `with AnimatedDiagram("My Architecture"):` block finishes, the python interpreter executes the `__exit__` method.

At this exact millisecond, `__exit__` has a fully built mathematical `Topology` object in memory. It must somehow execute the Manim video rendering engine on this topology, silently, without asking the user to drop to the command line and type `manim -ql my_script.py MyScene`.

---

## The 3 Why's (Validating the Execution Method)

1. **Why execute Programmatically instead of generating a `.py` file?**
   Because file generation forces the user into a two-step build process (1. run my code -> generates text file -> 2. run Manim on text file). This destroys the developer experience. The adapter must feel "magic"—you run your standard python file, and an MP4 drops into your local directory.
2. **How do we execute Manim programmatically?**
   Manim natively supports this via the configuration object `tempconfig`. We can dynamically instantiate a `DevopsScene` class subclassed at runtime, pass our `topology` to its `construct()` method, and call `.render()`.
3. **What is the risk of Dynamic Class Generation?**
   Manim uses internal caching based on class hash names. If we dynamically create `class AutoScene(DevopsScene):` internally, Manim might overwrite cached artifacts. We must ensure the `AnimatedDiagram.name` is sanitized into a valid Python class name to provide Manim's file writer with a predictable video output filename (e.g. `media/videos/my_script/480p15/My_Architecture.mp4`).

---

## 3 Deep Technical Questions (The `__exit__` Implementation)

1. **The Abstract Scene Limitation:** The `DevopsScene` requires the user to implement their own `self.play(...)` animations. If we use the adapter, the user isn't writing `self.play()`. How does the scene know what to animate?
   *Answer:* The adapter must dynamically inject a `construct()` method that loops through the topology and calls `self.render_topology(topology)`, followed by an optional global layout animation phase (e.g. `Succession(*[GrowFromCenter(n) for n...])`).
2. **Quality Configs:** How do we tell the programmatic executor to run at `-ql` (low quality/fast) instead of `-qh` (4K/slow)?
   *Answer:* We will use Manim's `tempconfig` context block inside the `_trigger_manim_render` method to force `-ql` parameters (`quality='l'`, `preview=False`).
3. **Test Safety:** Testing FFmpeg rendering is very slow. How do we test `_trigger_manim_render` without waiting 6 seconds every test?
   *Answer:* We will mock `Scene.render()` using `unittest.mock` to assert that the configuration and class instantiation paths were correctly executed by `AnimatedDiagram`, without actually invoking the GPU.

---

## Self-Reflection & Execution Blueprint
Dynamically generating a Manim `Scene` subclass inside another python loop is an advanced API pattern. It circumvents the CLI intentionally.

**The Red Phase Strategy:**
Write `test_adapter_triggers_render_programmatically` using `unittest.mock.patch('manim.Scene.render')` to ensure that exiting a valid `AnimatedDiagram(skip_render=False)` correctly builds a dynamic Manim scene class, loads the topology into it, and triggers the `render()` method internally.
