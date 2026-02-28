# Finding 08: conftest Fixtures Use CloudNode Instead of AWSNode

## Location
[tests/conftest.py](file:///Z:/never/vscode/manimani/tests/conftest.py) — Lines 19–29

## The Issue
The shared `aws_3_tier_topology` fixture constructs the topology using **base `CloudNode` objects**:

```python
route53 = CloudNode("dns", "Route53")
igw = CloudNode("igw", "Internet Gateway")
alb = CloudNode("alb", "Application Load Balancer")
web1 = CloudNode("web1", "EC2 Web 1")
```

But the actual library user writes:

```python
from manim_devops.assets.aws import Route53, IGW, ALB, EC2
dns = Route53("dns", "Route 53")
igw = IGW("igw", "Internet Gateway")
```

The fixture tests a **different code path** than the production code:

1. `CloudNode` does NOT initialize `SVGMobject`. `AWSNode` does.
2. `CloudNode` does NOT have `.width`, `.height`, or any Manim rendering methods. `AWSNode` does (via `SVGMobject`).
3. The `DevopsScene.render_topology()` method calls `node.move_to()` and `node.width / 2.0` — these work on `AWSNode` but would fail on raw `CloudNode` objects (they silently succeed only because the test mocks prevent actual rendering).

**This means the test suite verifies the mathematical graph logic (`Topology`, `calculate_layout`) but does NOT verify the rendering integration path that real users exercise.**

## Proposed Change
Create a separate fixture for rendering tests that uses `AWSNode` subclasses:

```python
@pytest.fixture
def aws_3_tier_rendered_topology(empty_topology):
    """Uses actual AWSNode subclasses for rendering integration tests."""
    from manim_devops.assets.aws import Route53, IGW, ALB, EC2, RDS
    topo = empty_topology

    route53 = Route53("dns", "Route53")
    igw = IGW("igw", "Internet Gateway")
    alb = ALB("alb", "Application Load Balancer")
    web1 = EC2("web1", "EC2 Web 1")
    web2 = EC2("web2", "EC2 Web 2")
    db_primary = RDS("db_master", "RDS Primary")
    db_replica = RDS("db_replica", "RDS Read-Replica")

    topo.add_nodes([route53, igw, alb, web1, web2, db_primary, db_replica])
    topo.connect(route53, igw)
    topo.connect(igw, alb)
    topo.connect(alb, web1)
    topo.connect(alb, web2)
    topo.connect(web1, db_primary)
    topo.connect(web2, db_primary)
    topo.connect(db_primary, db_replica)
    return topo
```

Keep the existing `CloudNode`-based fixture for pure math tests, and use the new fixture for rendering integration tests.

---

## 3 Questions

1. **Do any tests currently call `render_topology()` with the `aws_3_tier_topology` fixture?** If so, they're relying on mocks to bypass the rendering calls that would crash on raw `CloudNode` objects.
2. **Would using `AWSNode` in fixtures slow down the test suite?** Slightly — `AWSNode.__init__` triggers `SVGMobject.__init__`, which attempts SVG file loading (triggering the fallback). But this is <100ms per test.
3. **Should the fixture be parameterized** to test both `CloudNode` (math-only) and `AWSNode` (full-stack) paths? This would double test coverage without duplicating test functions.

## Self-Reflection
This is a subtle but important testing gap. The fixture was created during Phase 2 when only `CloudNode` existed. When `AWSNode` was introduced in Phase 2b, the fixture wasn't updated because the tests still passed — they never needed the rendering methods. But this means the integration path between `Topology → DevopsScene → AWSNode.move_to()` is only actually tested in the visual integration scripts, which aren't run by `pytest`.

## 5 Whys
1. **Why does the fixture use `CloudNode`?** Because it was written before `AWSNode` existed.
2. **Why wasn't it updated when `AWSNode` was created?** Because the existing tests still passed — they only test `calculate_layout()`, not `render_topology()`.
3. **Why does this matter?** Because a regression in `AWSNode.__init__` (e.g., a change to the SVG fallback logic) would not be caught by the fixture-based tests.
4. **Why not just replace `CloudNode` with `AWSNode` in the existing fixture?** Because the pure-math tests (`test_topology_returns_scaled_manim_coordinates`) genuinely don't need rendering, and adding SVG initialization overhead to every test is wasteful.
5. **Why have two fixtures instead of one?** Because testing at two different abstraction levels catches different categories of bugs: graph-math bugs vs. rendering-integration bugs.
