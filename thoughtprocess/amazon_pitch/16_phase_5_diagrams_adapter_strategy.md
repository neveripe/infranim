# Execution Strategy: Phase 5 (The `diagrams` Adapter Engine)

## Explanation
To achieve viral adoption, `manim-devops` needs a "killer feature" with zero onboarding friction. The Python `diagrams` library currently has over 30,000 GitHub stars and is the industry standard for programmatic architecture diagrams. 
However, it only produces static PNGs.

Phase 5 will establish a `diagrams2manim` translation layer. Instead of forcing users to learn our custom `DevopsScene` API and `Topology` matrix math, a user can write standard `diagrams` code, and our engine will intercept the nodes and edges, convert them into `CloudNode` objects, and automatically generate an MP4 video of the architecture.

---

## The 3 Why's (Validating Phase 5)

1. **Why build an adapter instead of forcing our API?**
   Because developers hate learning new DSLs (Domain Specific Languages). The fastest way to user acquisition is to integrate into the workflow they already use. If they can change one import command and suddenly get video outputs instead of static PNGs, the value proposition is infinite.
2. **Why target the `diagrams` library specifically?**
   Because `diagrams` is also built underneath on graph relationships (nodes connected by vertices). Their code `EC2("Web") >> RDS("Database")` mathematically maps perfectly to our `topology.connect(web, db)` logic.
3. **Why do this now?**
   Because Phases 1-4 successfully built a robust, tested mathematical matrix engine (`Topology`) and a rendering engine (`DevopsScene`). The foundation is stable enough to build an ingestion facade on top of it.

---

## 3 Deep Technical Questions (The Implementation)

1. **Context Managers vs AST Parsing:** The `diagrams` library uses Python Context Managers (`with Diagram("My Stack"):`) to globally capture instantiated nodes and edges. Should we monkeypatch their internal state tracker, or write our own `DevopsDiagram` context manager that mimics their syntax but builds our `Topology` instead?
2. **Asset Subclass Mapping:** The `diagrams` library has hundreds of nodes (e.g. `diagrams.aws.compute.EC2`). We currently only have 5 explicitly defined in `manim_devops.assets.aws`. How do we lazily map their imports to ours, or fallback safely to a generic `CloudNode` when they import an AWS service we haven't rigged an SVG for yet?
3. **The Rendering Loop:** An adapter script translates the layout, but how does the user trigger the Manim FFmpeg engine? Do we spawn a subprocess behind the scenes `os.system("manim...")` when the context manager exits, or output a compiled `.py` script that the user runs manually?

---

## Self-Reflection & Execution Blueprint
Question 1 reveals the cleanest path: **Do not AST parse.** We will provide our own Context Manager called `AnimatedDiagram` that flawlessly mimics the `diagrams` interface. It will capture the `>>` (dunder `__rshift__`) overloading to build edges, compile the `Topology`, and programmatically invoke Manim's Scene renderer internally without requiring the user to touch the CLI.

**Execution Blueprint (Phase 5):**
1. Add `AnimatedDiagram` Context Manager in `manim_devops/adapter.py`.
2. Implement python "dunder" methods (`__rshift__`, `__lshift__`) on `CloudNode` to support the `node_a >> node_b` syntax.
3. Hook the context exit `__exit__` to automatically synthesize a generic `DevopsScene` class and call `.render()` programmatically via Manim's core python API.
4. **Red Phase:** Write a test that executes a standard `diagrams` script structure and asserts the resulting topology edges exist.
