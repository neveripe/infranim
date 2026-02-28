# Execution Roadmap & Anti-Hallucination Strategy: `manim-devops`

## Explanation
Large Language Models (like myself) and overly optimistic engineers share a common flaw: we assume the "Happy Path." When drafting the Six-Pager, it is easy to hallucinate a world where `pygraphviz` installs flawlessly on Windows, and Manim natively parses complex AWS `.svg` files with perfect colors and gradients. 

Deep technical research reveals this is fundamentally false. `pygraphviz` requires C-binaries that notoriously fail on Windows setups. Manim's `SVGMobject` relies on a rudimentary XML parser that completely ignores embedded CSS `<style>` tags, crashes on `<clipPath>` masks, and frequently renders complex Adobe Illustrator SVGs as solid black or white boxes.

If we blindly start writing a massive `manim-devops` framework based on these hallucinated assumptions, we will hit a wall in two weeks and have to rewrite everything. Therefore, this Execution Roadmap is entirely focused on **Spike-Driven Development**. We must isolate the highest-risk technical assumptions and build tiny, throwaway Proofs of Concept (PoCs) to validate them before we write a single line of the actual framework.

---

## The 5 Whys (Root Cause of Execution Failure)
1. **Why do complex programmatic wrappers fail early in development?**
   Because developers build massive API abstractions before validating the underlying engine's capabilities.
2. **Why wouldn't the underlying engine (Manim) work for us?**
   Because we are trying to force it to do things it wasn't built for: rendering complex, web-standard SVGs and calculating force-directed graph layouts.
3. **Why do complex SVGs break Manim?**
   Because Manim was built by mathematicians to render simple LaTeX math formulas (which are just simple, single-color vector paths), not multi-layered, CSS-styled branding icons from Google Cloud.
4. **Why do force-directed layouts break our plan?**
   Because the best library for them (`pygraphviz`) has a massive C-dependency barrier that will alienate 50% of our user base (Windows users) on `pip install`.
5. **Why must we pivot our execution plan based on this?**
   Because if the core asset pipeline (SVGs) and the core layout engine (installability) fail, the cinematic API (the "cool" part) is worthless. We must solve the ugly foundation first.

---

## 5 Deep Questions (Challenging our Assumptions)
1. **The SVG Flattening Pipeline:** Can we write a preprocessing script (using `svgo` or Inkscape CLI) that reliably strips an AWS `.svg` of all CSS/metadata and bakes the colors directly into raw `<path fill="#HEX">` tags so Manim doesn't choke?
2. **NetworkX over PyGraphviz:** Since NetworkX is pure Python and installs perfectly on Windows, can its built-in `spring_layout` or `multipartite_layout` generate acceptable, predictable X/Y coordinates, or are we absolutely forced to use Graphviz for hierarchical topologies?
3. **The Coordinate Translation Math:** NetworkX outputs coordinates on an arbitrary normalized scale (e.g., `-1.0` to `1.0`). How exactly do we mathematically map and scale those abstract coordinates into Manim's `config["frame_width"]` camera canvas without nodes flying off-screen?
4. **Edge Anchoring:** If Node A is at `[0,0]` and Node B is at `[5,0]`, drawing a line between them goes through the center of the nodes. How do we extract the bounding box of a Manim `SVGMobject` so the line anchors gracefully to the *edge* of the icon, rather than overlapping it?
5. **Manim Caching:** If we generate the graph structure programmatically via NetworkX dicts, how do we ensure Manim's hash-based caching system recognizes the scene so it doesn't re-render 500 frames of video every time we change a tiny text label?

---

## Self-Reflection
By stepping back and acknowledging my own tendency to hallucinate "easy" solutions, the project's true risk profile emerges. We cannot afford to write `class DatabaseNode(ManimMobject):` yet. We don't even know if we can render a database icon! 

The next step is not to build the library. The next step is to build isolated experiments. If we can prove that Manim can render an AWS SVG, and if we can prove that NetworkX can map coordinates to a Manim Scene, then the core hypothesis is validated. From there, building the API wrapper is just standard software engineering.

---

## Next Steps: The Technical Spikes

Do NOT build the library. Execute these three PoC Spikes in order:

### Spike 1: The `SVGMobject` Reality Check
**Goal:** Prove we can render a complex Cloud vector.
*   Download an official, complex AWS icon (e.g., `Amazon-RDS.svg`).
*   Attempt to load it in a raw Manim scene `SVGMobject("Amazon-RDS.svg")`.
*   Observe it fail or render improperly.
*   Task: Build a minimal, reproducible preprocessing step (e.g., passing it through an SVG optimizer to flatten shapes) until Manim renders it perfectly with correct colors. 

### Spike 2: The Pure Python Layout Engine (`NetworkX`)
**Goal:** Prove we can avoid `pygraphviz` and use `networkx` to position Manim objects.
*   Write a minimal script that imports `networkx`.
*   Create a 4-node graph: `A -> B -> C`, `A -> D`.
*   Ask NetworkX for a planar or multipartite layout (which returns a dict of `node: (x, y)` coordinates).
*   Task: Write a tiny Manim scene that spawns 4 circles, loops through the NetworkX coordinate dictionary, scales the coordinates by a factor of 3, and places the circles on the Manim camera frame. Do not draw lines yet. Just prove the nodes position correctly.

### Spike 3: The Edge Anchoring Check
**Goal:** Prove we can connect two SVGs with a line that doesn't overlap the SVG body.
*   Place two circles in a Manim scene.
*   Task: Use Manim's explicit `Line()` or `Arrow()` parameters (like `buff` or boundary mapping) to draw a line that perfectly touches the *outer edge* of Circle A and Circle B, regardless of their scaling.

**Once (and only once) these three spikes succeed**, we officially begin architecting the `manim-devops` package structure.
