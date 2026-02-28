import pytest
from manim import tempconfig
from manim_devops.core import Topology, DevopsScene
from manim_devops.assets import CloudNode
from manim_devops.assets.aws import EC2, RDS

def test_topology_deduplication_and_bulk_loading_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that the internal math lists correctly reject duplicate nodes
    and duplicate edges, while also testing the bulk 'add_nodes' logic.
    """
    topo = Topology()
    node1 = CloudNode("test1", "Label")
    node2 = CloudNode("test2", "Label")
    
    # Bulk loading
    topo.add_nodes([node1, node2])
    assert len(topo.nodes) == 2
    
    # Duplicate loading
    topo.add_node(node1)
    topo.add_nodes([node1])
    assert len(topo.nodes) == 2 # Must still be 2
    
    # Duplicate Edges
    topo.connect(node1, node2)
    topo.connect(node1, node2)
    assert len(topo.edges) == 1

def test_devops_scene_renders_topology_without_crashes_IMMUTABLE(aws_3_tier_topology):
    """
    IMMUTABLE TEST
    Utilizes Manim's dry_run tempconfig to execute the entirety of the
    render_topology loop (including Z-Index assignments and Mobject creation)
    purely in memory, guaranteeing the execution logic works before FFmpeg is invoked.
    """
    # Replace dummy string nodes in fixture with actual objects 
    # so we don't hit Mobject width/height attribute errors inside the router
    topo = Topology()
    topo.add_nodes([EC2("node1", "N1"), RDS("node2", "N2")])
    topo.connect(topo.nodes[0], topo.nodes[1])
    
    # Dry run silences FFmpeg and file I/O
    with tempconfig({"dry_run": True, "quality": "low_quality", "disable_caching": True}):
        scene = DevopsScene()
        # Explicit call to trace lines
        scene.render_topology(topo)
        
        # If it didn't throw an error, we successfully traced the execution path!
        assert True

def test_topology_calculates_cluster_and_child_coordinates_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that a NodeCluster explicitly handles its own internal layout math
    for its children gracefully, ensuring that NetworkX treats the Cluster as
    one solid entity, and the Topology injects deterministic relative coordinates 
    for the children recursively.
    """
    # Import here for Red Phase failure
    from manim_devops.core import NodeCluster
    
    topo = Topology(scale_factor=1.0)
    
    # Simple cluster with 2 children
    cluster = NodeCluster("asg", "Auto-Scaling Group")
    child1 = CloudNode("web1", "EC2")
    child2 = CloudNode("web2", "EC2")
    cluster.add_child(child1)
    cluster.add_child(child2)
    
    # Add standalone node
    db = CloudNode("db", "RDS")
    
    topo.add_nodes([cluster, db])
    topo.connect(cluster, db)
    
    manim_coords = topo.calculate_layout()
    
    # Assert the Cluster centroid was calculated by NetworkX
    assert "asg" in manim_coords
    cluster_x = manim_coords["asg"][0]
    cluster_y = manim_coords["asg"][1]
    
    # Assert the children were injected into the global layout dict 
    # relative to the parent centroid (e.g. basic horizontal offset)
    assert "web1" in manim_coords
    assert "web2" in manim_coords
    
    # Explicit deterministic offset tests
    # Child 1 should be offset to the left of centroid
    assert manim_coords["web1"][0] == cluster_x - 1.0  
    assert manim_coords["web1"][1] == cluster_y
    
    # Child 2 should be offset to the right of centroid 
    assert manim_coords["web2"][0] == cluster_x + 1.0
    assert manim_coords["web2"][1] == cluster_y

def test_devops_scene_stores_edge_memory_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that the DevopsScene persistently stores the generated VMobject mathematically
    routed paths during render_topology() into an internal 'rendered_edges' dictionary using 
    the generic (source_id, target_id) tuple.
    """
    topo = Topology()
    topo.add_nodes([EC2("src", "Source"), RDS("tgt", "Target")])
    topo.connect(topo.nodes[0], topo.nodes[1])
    
    with tempconfig({"dry_run": True, "quality": "low_quality", "disable_caching": True}):
        scene = DevopsScene()
        scene.render_topology(topo)
        
        # 1. Assert memory dict exists
        assert hasattr(scene, 'rendered_edges')
        assert isinstance(scene.rendered_edges, dict)
        
        # 2. Assert tuple edge key exists
        edge_key = ("src", "tgt")
        assert edge_key in scene.rendered_edges
        
        # 3. Assert it actually holds a Manim VMobject reference capable of being animated later
        from manim import VMobject
        stored_edge = scene.rendered_edges[edge_key]
        assert isinstance(stored_edge, VMobject)
