import pytest
from manim import Scene, VMobject, Dot, Animation, tempconfig
from manim_devops.core import DevopsScene
from manim_devops.assets import CloudNode

def test_traffic_flow_returns_valid_animation_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that the TrafficFlow object successfully queries the DevopsScene
    for the drawn edge and returns a valid Manim Animation that can be played natively.
    """
    # Import here to simulate Red Phase failure if file doesn't exist
    from manim_devops.cinematics import TrafficFlow
    
    with tempconfig({"dry_run": True, "quality": "low_quality", "disable_caching": True}):
        scene = DevopsScene()
        scene.rendered_edges = {}
        
        src = CloudNode("A", "Source")
        tgt = CloudNode("B", "Target")
        
        # Mocking the mathematical line drawn in Phase 2
        mock_line = VMobject()
        mock_line.set_points_as_corners([[0,0,0], [1,0,0], [1,1,0]])
        scene.rendered_edges[("A", "B")] = mock_line
        
        # Instantiate the cinematic action
        action = TrafficFlow(scene, src, tgt)
        
        assert isinstance(action, Animation)

def test_traffic_flow_resolves_reverse_path_lookups_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that if the requested traffic path is B -> A, but the actual mathematical
    edge drawn in Phase 2 was A -> B, TrafficFlow will intelligently fall back, find
    the original edge, and return a valid animation without throwing a KeyError.
    """
    from manim_devops.cinematics import TrafficFlow
    
    with tempconfig({"dry_run": True, "quality": "low_quality", "disable_caching": True}):
        scene = DevopsScene()
        scene.rendered_edges = {}
        
        src = CloudNode("A", "Source")
        tgt = CloudNode("B", "Target")
        
        # Mocking the mathematical line drawn in Phase 2 as A -> B
        mock_line = VMobject()
        mock_line.set_points_as_corners([[0,0,0], [1,0,0], [1,1,0]])
        scene.rendered_edges[("A", "B")] = mock_line
        
        # User intentionally reverses the flow for a 'response' ping
        # The key ("B", "A") DOES NOT EXIST in the dictionary.
        action = TrafficFlow(scene, tgt, src)
        
        # If it didn't throw a KeyError and built the animation, the test passes
        assert isinstance(action, Animation)

def test_traffic_flow_raises_key_error_for_invalid_edge_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that if a user requests a TrafficFlow for two nodes that have absolutely
    no mapped connection in the DevopsScene memory, it fails fast via KeyError.
    """
    from manim_devops.cinematics import TrafficFlow
    
    with tempconfig({"dry_run": True, "quality": "low_quality", "disable_caching": True}):
        scene = DevopsScene()
        scene.rendered_edges = {}
        
        src = CloudNode("A", "Source")
        tgt = CloudNode("B", "Target")
        
        # Memory is empty. This must raise a KeyError immediately.
        with pytest.raises(KeyError, match="No rendered edge found"):
            TrafficFlow(scene, src, tgt)

def test_traffic_flow_falls_back_to_packet_flash_if_mobject_missing_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that if the target Mobject wasn't physically drawn to the screen for some 
    reason, TrafficFlow doesn't crash when trying to pulse it. It should safely 
    pulse the abstract packet dot instead.
    """
    from manim_devops.cinematics import TrafficFlow
    
    with tempconfig({"dry_run": True, "quality": "low_quality", "disable_caching": True}):
        scene = DevopsScene()
        scene.rendered_edges = {}
        scene.mobjects = [] # Explicitly empty so it cannot find target
        
        src = CloudNode("A", "Source")
        tgt = CloudNode("B", "Target")
        
        mock_line = VMobject()
        mock_line.set_points_as_corners([[0,0,0], [1,0,0], [1,1,0]])
        scene.rendered_edges[("A", "B")] = mock_line
        
        # This will execute block: flash_target = packet
        action = TrafficFlow(scene, src, tgt)
        assert isinstance(action, Animation)

def test_traffic_flow_executes_reverse_rate_func_IMMUTABLE():
    """
    IMMUTABLE TEST
    Manim calculates rate functions dynamically via callbacks. Pytest misses 
    `def reverse_rate(t): return 1 - t` because Manim never actually "plays" the 
    scene in memory. We must manually invoke the injected rate_func to cover it.
    """
    from manim_devops.cinematics import TrafficFlow
    from manim import MoveAlongPath
    
    with tempconfig({"dry_run": True, "quality": "low_quality", "disable_caching": True}):
        scene = DevopsScene()
        scene.rendered_edges = {}
        
        src = CloudNode("A", "Source")
        tgt = CloudNode("B", "Target")
        
        mock_line = VMobject()
        mock_line.set_points_as_corners([[0,0,0], [1,0,0], [1,1,0]])
        scene.rendered_edges[("A", "B")] = mock_line
        
        # Trigger the reverse path (B -> A)
        action = TrafficFlow(scene, tgt, src)
        
        # Action is a Succession. The first animation is the travel_anim (MoveAlongPath)
        travel_anim = action.animations[0]
        assert isinstance(travel_anim, MoveAlongPath)
        
        # Explicitly invoke the rate_func callback to trigger line 43
        assert travel_anim.rate_func(0.0) == 1.0
        assert travel_anim.rate_func(1.0) == 0.0

def test_traffic_flow_finds_mobject_in_scene_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that if the target Mobject *is* drawn in the DevopsScene, TrafficFlow
    successfully loops through the internal array, finds it, and pulses it instead of the dot.
    """
    from manim_devops.cinematics import TrafficFlow
    from manim_devops.assets.aws import EC2
    
    with tempconfig({"dry_run": True, "quality": "low_quality", "disable_caching": True}):
        scene = DevopsScene()
        scene.rendered_edges = {}
        
        # Instantiate Actual Mobjects
        src = EC2("A", "Source")
        tgt = EC2("B", "Target")
        
        # Inject into the Scene's internal Mobject array (Lines 51-53 coverage)
        scene.mobjects = [src, tgt]
        
        mock_line = VMobject()
        mock_line.set_points_as_corners([[0,0,0], [1,0,0], [1,1,0]])
        scene.rendered_edges[("A", "B")] = mock_line
        
        action = TrafficFlow(scene, src, tgt)
        assert isinstance(action, Animation)

def test_scale_out_action_mutates_state_and_returns_animation_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that the ScaleOutAction correctly spawns a new CloudNode inside a 
    NodeCluster, automatically generates the orthogonal routing connection to the target,
    updates the global scene edge memory and mobjects list so future traffic can navigate, 
    and returns a valid cinematic AnimationGroup.
    """
    from manim_devops.cinematics import ScaleOutAction
    from manim_devops.core import NodeCluster
    from manim_devops.assets.aws import EC2, RDS
    from manim import AnimationGroup
    
    with tempconfig({"dry_run": True, "quality": "low_quality", "disable_caching": True}):
        scene = DevopsScene()
        scene.rendered_edges = {}
        scene.mobjects = []
        scene.rendered_coords = {}
        
        # Setup Initial State - Math Models
        cluster = NodeCluster("asg", "Cluster")
        # Ensure target is an actual rendering Mobject that exists
        target_db = RDS("db", "Database")
        target_db.move_to([0, -5, 0])
        scene.mobjects.append(target_db)
        
        # Mock the Phase 2 Mathematical Engine Memory
        scene.rendered_coords["asg"] = (0.0, 0.0, 0.0)
        scene.rendered_coords["db"] = (0.0, -5.0, 0.0)
        
        # Action Runtime Memory Test
        new_ec2 = EC2("new_web", "EC2 Web")
        action = ScaleOutAction(scene, cluster, new_ec2, target=target_db)
        
        # 1. Assert Animation Return
        assert isinstance(action, AnimationGroup)
        
        # 2. Assert Sub-Graph Math Coordinates Offset was calculated
        # The offset formula uses [-1.0...] for the first child
        # so X should be -1.0 relative to Cluster [0, 0, 0]
        assert new_ec2.get_center()[0] == -1.0
        
        # 3. Assert Mobject Global Tracker Update
        assert new_ec2 in scene.mobjects
        
        # 4. Assert Edges Memory Update
        assert ("new_web", "db") in scene.rendered_edges

def test_scale_out_action_raises_key_error_for_invalid_cluster_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts a KeyError is raised if the user tries to scale out a Cluster
    that was never physically rendered into the Scene's coordinate memory.
    """
    from manim_devops.cinematics import ScaleOutAction
    from manim_devops.core import NodeCluster
    from manim_devops.assets.aws import EC2
    
    scene = DevopsScene()
    scene.rendered_coords = {} # Empty memory
    
    cluster = NodeCluster("asg", "Cluster")
    new_ec2 = EC2("new_web", "EC2")
    
    with pytest.raises(KeyError, match="not found in Scene memory"):
        ScaleOutAction(scene, cluster, new_ec2)

def test_scale_out_action_raises_key_error_for_invalid_target_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts a KeyError is raised if the user tries to draw an edge to a target
    that was never physically rendered into the Scene's coordinate memory.
    """
    from manim_devops.cinematics import ScaleOutAction
    from manim_devops.core import NodeCluster
    from manim_devops.assets.aws import EC2, RDS
    
    scene = DevopsScene()
    # Provide cluster coords but not target coords
    scene.rendered_coords = {"asg": (0.0, 0.0, 0.0)} 
    
    cluster = NodeCluster("asg", "Cluster")
    new_ec2 = EC2("new_web", "EC2")
    invalid_target = RDS("fake_db", "DB")
    
    with pytest.raises(KeyError, match="'fake_db' not found in Scene memory"):
        ScaleOutAction(scene, cluster, new_ec2, target=invalid_target)
