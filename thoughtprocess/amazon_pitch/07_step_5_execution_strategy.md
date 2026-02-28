# Phase 2 Validation & Step 5 TDD Strategy: `manim-devops`

## Explanation
Steps 1-4 successfully validated that the foundational math engines (`NetworkX` Topology and `OrthogonalRouter`) can natively translate abstract nodes and edges into collision-free Cartesian layouts and 90-degree orthogonal vectors. The temporary visual test in Manim (using generic circles) confirmed the math aligns perfectly on the Z=0.0 plane.

Step 5 is the final phase of the MVP: building the "Cinematic Wrapper." We must discard the generic circles, build the official `core.DevopsScene` engine, and implement the authentic AWS SVG assets required by our `aws_3_tier_topology` fixture.

---

## The 3 Why's (Validating the Final Step)

1. **Why do we need a specialized `DevopsScene` instead of standard `manim.Scene`?**
   Because forcing the user to manually loop over nodes and create `Circle()` objects (like we did in the visual test script) defeats the entire purpose of "Infrastructure as Code." The user's script should strictly declare the Architecture. The `DevopsScene` is a superclass that internally houses the `Topology` math, the `OrthogonalRouter`, and the `SVGMobject` rendering logic, allowing the user to simply call `self.render_topology(my_aws_layout)` to generate the entire video.
2. **Why must `CloudNode` become an `SVGMobject` now?**
   In Steps 1-3, `CloudNode` was a purely mathematical dataclass. It had an ID and a label. Now that we are rendering the actual video, `CloudNode` (or its AWS subclasses) must integrate directly into Manim's rendering pipeline so that the layout engine can query its *actual* width and height. If we don't know the exact bounding box of the AWS RDS `.svg` file, the Orthogonal Router will draw lines that cut through the icon.
3. **Why are we implementing `AWSNode` subclasses right now?**
   Because we need to prove that the provider-agnostic inheritance model defined in `06_provider_agnostic_asset_strategy.md` actually works. We need to define `aws.EC2`, `aws.RDS`, and `aws.Route53` objects that inherit from the generic math engine but inject their own SVG asset paths.

---

## 3 Deep Technical Questions (The `DevopsScene` Implementation)

1. **The Asynchronous Z-Index Problem:** SVGs have opaque fills. Lines have solid strokes. If Manim renders the orthogonal edge lines *after* it renders the AWS icons, the lines will be drawn directly over the top borders of the icons. How do we ensure the `DevopsScene` strictly orders the Z-Index so that lines are always drawn *underneath* the icons they connect to?
2. **Animation Orchestration:** When `self.render_topology()` is called, should Manim instantly pop the entire diagram onto the screen in 1 frame, or should it automatically calculate a staggered `FadeIn` or `Create` sequence? If it staggers, do the edges grow dynamically *after* the nodes appear, or simultaneously?
3. **SVG Asset Loading & The Testing Environment:** Pytest runs from the root of the workspace. If `aws.EC2` hardcodes a relative path to `assets/aws/EC2.svg`, how do we guarantee that path resolves correctly regardless of where the user executes the rendering script from?

---

## Self-Reflection
This is the most dangerous step in the MVP because it bridges the abstract math into the chaotic reality of standardizing external SVGs. 

If we try to build the SVG Sanitization pipeline, the `DevopsScene` renderer, and the `aws` subclasses all at once, we will violate our strict TDD protocol and get lost in a massive refactoring loop. We must isolate the "Red" phase:
1.  **Red:** Write an `integration_test.py` that imports `DevopsScene`, instantiates `aws.EC2`, and attempts to `render_topology()`.
2.  **Green:** We will physically download the 3 required AWS SVGs, run Spike 1's regex script manually to generate `assets/aws/sanitized_ec2.svg`, and hardcode the `aws.EC2` class to read it. We will write the bare minimum generic loop in `DevopsScene.render_topology()`.
3.  **Refactor:** Only once the Manim CLI successfully outputs a video of the True AWS 3-tier architecture do we consider Phase 2 complete.

---

## Step 5 Execution Blueprint
1. Copy the 3 needed AWS icons from Spike 1 / external sources into `manim_devops/assets/aws/`.
2. Create `manim_devops/aws.py` containing `EC2`, `RDS`, `Route53`, `ALB`, and `IGW` subclasses.
3. Scaffold `manim_devops.core.DevopsScene`.
4. Create `tests/test_final_integration.py` to trigger the final Manim video render.
