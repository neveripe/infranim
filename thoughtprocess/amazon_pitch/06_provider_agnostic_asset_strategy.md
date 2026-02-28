# Provider-Agnostic Asset Strategy: `manim-devops`

## Explanation
A core risk of domain-specific diagramming tools is tight coupling to a single vendor (e.g., hardcoding AWS-specific logic into the layout engine). If the layout math knows what an "EC2 Instance" is, the architecture has failed. 

To ensure long-term viability and cross-cloud support (AWS, GCP, Azure, On-Premises), `manim-devops` must adopt a strict separation of concerns between Mathematical Topology (Agnostic) and Visual Rendering (Vendor-Specific). This document outlines the ingestion pipeline for branded SVGs and the inheritance model that guarantees a resilient, provider-agnostic core.

---

## The 3 Why's (Asset Sourcing & Coupling)

1. **Why do we need official AWS/GCP/Azure models?**
   While the mathematical layout engine (`NetworkX`) perfectly routes generic abstract nodes (circles and squares), the primary value proposition of `manim-devops` is generating professional, highly recognizable cinematic marketing and educational materials. A generic circle labeled "Database" does not convey the same professional fidelity or instant cognitive recognition as the official, branded AWS RDS or GCP CloudSQL SVG icon. The branded assets are mandatory for market adoption.
2. **Where and how do we get these models?**
   All major cloud providers officially publish their architecture icon sets as royalty-free `.zip` files containing raw SVGs (e.g., [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/)). We do not manually trace or redraw these. `manim-devops` will utilize an automated GitHub Actions pipeline (incorporating the regex logic from Spike 1) to download the official `.zip` files, sanitize the SVGs of Manim-crashing CSS `<style>` blocks, and bundle the cleaned `.svg` files directly into the Python package (`manim_devops/assets/aws/`, `manim_devops/assets/gcp/`).
3. **Why must the core design remain provider-agnostic despite bundling these assets?**
   Because cloud architectures are increasingly multi-cloud or hybrid. If our routing engine (Spike 3) or layout engine (Spike 2) contains `if node.provider == 'aws':` logic, the codebase will become an unmaintainable monolithic nightmare of edge cases. Abstracting the core math allows a user to trivially connect an on-premises generic server to an AWS API Gateway without the underlying engine crashing.

---

## The Provider-Agnostic Inheritance Architecture

To achieve a fully agnostic core while supporting rich vendor assets, we will implement a strict Object-Oriented inheritance model:

### 1. The Core Abstraction: `core.Node`
This is the only object the Layout Engine and Edge Router are allowed to interact with. It contains zero visual rendering logic and no concept of cloud providers.
*   **Responsibilities:** Tracking `node_id`, storing `(X, Y, Z)` Cartesian coordinates, maintaining the `bounding_box` radius for orthogonal edge projection (Spike 3).

### 2. The Generic Base Renderers
Instead of jumping straight to AWS, we build generic shapes that inherit from `core.Node` but add Manim drawing logic.
*   **`assets.generic.CircleNode(Node)`:** Applies the `(X, Y)` coordinates to a Manim `Circle()`.
*   **`assets.generic.TextNode(Node)`:** Applies the coordinates to a Manim `Text()`.

### 3. The Vendor-Specific Implementations
These inherit the agnostic math operations from `core.Node`, but specifically instruct Manim to parse our sanitized branded SVGs.
*   **`assets.aws.AWSNode(Node)`:** A base class for AWS that sets default branding colors (e.g., AWS Orange `#FF9900` for animations).
*   **`assets.aws.EC2(AWSNode)`:** Initializes by loading the sanitized `compute/EC2.svg` from the packaged asset folder. The layout engine places it perfectly, entirely unaware that it is rendering an EC2 icon rather than a plain circle.

**Example Multi-Cloud Interoperability:**
Because everything inherits from `core.Node`, the Topology engine natively supports hybrid architectures out-of-the-box:
```python
# The pure-math Topology engine connects them seamlessly.
on_prem = generic.ServerNode("local-datacentre")
aws_lb = aws.ALB("us-east-1")
gcp_db = gcp.CloudSQL("europe-west1")

topology.connect(on_prem, aws_lb)
topology.connect(aws_lb, gcp_db)
```

---

## 3 Deep Technical Questions (The PoC Implementation)

1. **Bounding Box Heterogeneity:** If `assets.aws.S3` is shaped like a tall bucket, and `assets.gcp.CloudRun` is shaped like a wide hexagon, how does `core.Node` calculate a universally accurate bounding box radius so the Orthogonal Router guarantees edges don't intersect the differing form factors?
2. **Asset Packaging Bloat:** If we script the downloading and sanitization of *all* 500+ AWS, GCP, and Azure SVG icons, will the resulting `manim-devops.whl` Python package be too massive for a fast `pip install`? Do we need to dynamically download SVGs at runtime, or ship a subset?
3. **The Proof of Concept (PoC) Scope:** To mathematically prove the inheritance model without getting bogged down in the 500+ AWS SVGs, what is the absolute minimum asset surface area required for the Phase 2 MVP?

---

## Self-Reflection (The PoC Scope constraint)
This feature is highly susceptible to "Asset Grooming" procrastination—spending three days hand-tweaking 500 AWS icons instead of writing the core routing engine.

**Strict Constraint:** The `manim-devops` PoC (Phase 2) is explicitly restricted to **three** AWS assets required for the 3-Tier Web App fixture:
1. `aws.Route53`
2. `aws.EC2`
3. `aws.RDS`

We will manually download and sanitize *only* these three SVGs using Spike 1's script to create the `assets.aws` namespace. Once the underlying engine successfully generates the agnostic coordinates (Red/Green/Refactor), we will simply swap out `generic.CircleNode` with `aws.EC2Node` in the fixture to prove the visual render works. The automated 500+ SVG pipeline will be deferred to a later Git issue.
