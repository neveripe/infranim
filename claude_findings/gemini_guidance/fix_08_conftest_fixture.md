# Gemini Guidance: Fix 08 — Add AWSNode-Based Test Fixture

## Context
The shared `conftest.py` fixture constructs topologies using base `CloudNode` instead of `AWSNode` subclasses, so the rendering integration path is untested. See `claude_findings/08_conftest_fixture_type_gap.md`.

## Priority: Low (Test Completeness)

## Strict Instructions

### Step 1: Add a New Fixture to `tests/conftest.py`

Do NOT modify the existing `aws_3_tier_topology` fixture. Add a **new** fixture below it:

```python
@pytest.fixture
def aws_3_tier_rendered_topology(empty_topology):
    """
    Constructs a full-stack 3-Tier topology using actual AWSNode subclasses.
    This fixture exercises the SVG loading + fallback path, enabling 
    rendering integration tests.
    """
    from manim_devops.assets.aws import Route53, IGW, ALB, EC2, RDS
    
    topo = empty_topology
    
    # Tier 1: Networking
    route53 = Route53("dns", "Route53")
    igw = IGW("igw", "Internet Gateway")
    alb = ALB("alb", "Application Load Balancer")
    
    # Tier 2: Compute
    web1 = EC2("web1", "EC2 Web 1")
    web2 = EC2("web2", "EC2 Web 2")
    
    # Tier 3: Database
    db_primary = RDS("db_master", "RDS Primary")
    db_replica = RDS("db_replica", "RDS Read-Replica")
    
    # Build graph
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

### Step 2: Add a Rendering Integration Test

> **IMPORTANT:** Ask the user for permission before adding new test files.

Create a new test or add to an existing test file:

```python
def test_devops_scene_renders_aws_nodes_without_crash(aws_3_tier_rendered_topology):
    """
    Verifies that DevopsScene.render_topology works end-to-end 
    with actual AWSNode objects (which trigger SVG loading + fallback).
    """
    from manim_devops.core import DevopsScene
    from unittest.mock import patch
    
    with patch.object(DevopsScene, 'play'):
        with patch.object(DevopsScene, 'wait'):
            scene = DevopsScene()
            scene.render_topology(aws_3_tier_rendered_topology)
            
            # Verify all 7 nodes were placed (minus NodeClusters)
            cloud_nodes = [m for m in scene.mobjects 
                          if hasattr(m, 'node_id')]
            assert len(cloud_nodes) == 7
            
            # Verify all 7 edges were drawn
            assert len(scene.rendered_edges) == 7
```

### Step 3: Run Tests
```bash
python -m pytest tests/ -v
```

Both the old `aws_3_tier_topology` (CloudNode-based) tests AND the new `aws_3_tier_rendered_topology` (AWSNode-based) test must pass.

## What NOT To Do
- Do NOT modify or delete the existing `aws_3_tier_topology` fixture. It's used by existing math-only tests.
- Do NOT rename the existing fixture.
- Do NOT add AWSNode imports to the existing fixture — keep them separate.
