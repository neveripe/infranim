# Gemini Guidance: Fix 04 — Sync ScaleOutAction State Back to Topology

## Context
`ScaleOutAction` in `cinematics.py` mutates `scene.rendered_coords` and `scene.rendered_edges` but never updates the source `Topology` object. This creates divergence between the math model and the render state. See `claude_findings/04_state_mutation_split_brain.md`.

## Priority: High (Architectural Integrity)

## Strict Instructions

### Step 1: Store Topology Reference on DevopsScene

In `manim_devops/core.py`, inside `render_topology()`, add one line after the coordinate calculation:

```python
def render_topology(self, topology: Topology) -> None:
    coords = topology.calculate_layout()
    router = OrthogonalRouter()
    
    self.topology = topology  # <-- ADD THIS LINE
    self.rendered_coords = coords
    self.rendered_edges = {}
    # ... rest unchanged
```

### Step 2: Update ScaleOutAction to Sync the Topology

In `manim_devops/cinematics.py`, after the child is added to the cluster and positioned, also register it in the topology:

```python
def ScaleOutAction(scene: DevopsScene, cluster: NodeCluster, new_child: CloudNode, target: CloudNode = None) -> AnimationGroup:
    # 1. State Mutation: Append Child mathematically
    cluster.add_child(new_child)
    
    # 1b. Sync to the source Topology (PREVENTS SPLIT-BRAIN)
    if hasattr(scene, 'topology'):
        scene.topology.add_node(new_child)
    
    # ... existing code for coordinate calculation ...
    
    # 4. Organic Networking
    if target:
        # ... existing code ...
        
        # 4b. Sync edge to source Topology (PREVENTS SPLIT-BRAIN)
        if hasattr(scene, 'topology'):
            scene.topology.connect(new_child, target)
        
        # ... rest unchanged
```

**Why `hasattr` guard?** Because existing tests mock `DevopsScene` and might not have the `topology` attribute. The guard ensures backward compatibility.

### Step 3: Add a New Test

> **IMPORTANT:** Ask the user for permission before adding tests to `test_cinematics.py`.

If approved, add:

```python
def test_scale_out_action_syncs_topology_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that ScaleOutAction registers the new child and edge 
    back into the source Topology to prevent split-brain divergence.
    """
    from manim_devops.core import Topology, NodeCluster, DevopsScene
    from manim_devops.assets.aws import EC2, ALB
    from manim_devops.cinematics import ScaleOutAction

    # Setup: Build minimal topology with a cluster
    topo = Topology()
    cluster = NodeCluster("asg", "Auto-Scaling Group")
    target = ALB("alb", "ALB")
    topo.add_nodes([cluster, target])
    topo.connect(cluster, target)

    # Mock scene state
    scene = type('MockScene', (), {
        'rendered_coords': {"asg": (0, 0, 0), "alb": (3, 0, 0)},
        'rendered_edges': {},
        'mobjects': [],
        'topology': topo,
    })()

    new_child = EC2("web3", "Web 3")
    initial_node_count = len(topo.nodes)
    
    ScaleOutAction(scene, cluster, new_child, target=target)
    
    # Assert Topology was synced
    assert len(topo.nodes) == initial_node_count + 1
    assert any(n.node_id == "web3" for n in topo.nodes)
    assert ("web3", "alb") in topo.edges
```

### Step 4: Run Tests
```bash
python -m pytest tests/test_cinematics.py -v
```

All existing tests must still pass. The `hasattr` guard ensures backward compatibility with mock-based tests that don't have `scene.topology`.

## What NOT To Do
- Do NOT make `topology` a required parameter of `ScaleOutAction`. That would break the existing function signature and all callers.
- Do NOT overwrite `scene.topology` inside `ScaleOutAction`. Only read from it.
- Do NOT modify existing IMMUTABLE tests.
