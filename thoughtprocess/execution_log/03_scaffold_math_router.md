# Phase 2: TDD Execution Log

## Step 3: Implement Mathematical Orthogonal Router (RED Phase)

### Intention
With the `Topology` now generating scaled Cartesian coordinates (Step 2), we must prove we can mathematically route connections between those coordinates without Manim. The intention is to port the logic from Spike 3 into an agnostic `OrthogonalRouter` that generates the waypoints (L-bends) for every edge declared in our `aws_3_tier_topology` fixture.

I will:
1.  Define a new test in `tests/test_architecture_layout.py`.
2.  The test will request `(X,Y)` coords from the Topology.
3.  The test will invoke an `OrthogonalRouter` for an edge (e.g., `Route53` -> `Internet Gateway`) and assert that it calculates an array of exactly 3 waypoint coordinates representing a 90-degree L-bend, factoring in the bounding box radius of the generic Node.

### Actions
1.  Write the failing test asserting `OrthogonalRouter` waypoint logic.
2.  Run `pytest` to ensure it fails with `ImportError`.

### Outcome
*(Pending execution)*
