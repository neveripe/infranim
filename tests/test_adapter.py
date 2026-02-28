import pytest
from manim_devops.core import Topology

def test_animated_diagram_manages_global_state_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that the AnimatedDiagram context manager correctly injects itself 
    into a globally accessible module variable upon entering the `with` block,
    and rigorously tears itself down upon exiting the block to prevent test pollution.
    """
    # Import here to simulate Red Phase failure if file doesn't exist
    from manim_devops.adapter import AnimatedDiagram
    import manim_devops.adapter as adapter_module
    
    # 1. State should be uninitialized initially
    assert adapter_module._ACTIVE_DIAGRAM is None
    
    with AnimatedDiagram("Test Architecture", skip_render=True) as diag:
        # 2. Assert Global Injection
        assert adapter_module._ACTIVE_DIAGRAM is diag
        
        # 3. Assert internal topological instantiation
        assert isinstance(diag.topology, Topology)
        assert diag.name == "Test Architecture"
        
    # 4. Assert Tear Down (Critical for testing environments)
    assert adapter_module._ACTIVE_DIAGRAM is None

def test_animated_diagram_cleans_up_on_exception_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that if python code crashes INSIDE the with block, the __exit__
    handler still guarantees that the global _ACTIVE_DIAGRAM is reset to None.
    """
    from manim_devops.adapter import AnimatedDiagram
    import manim_devops.adapter as adapter_module
    
    try:
        with AnimatedDiagram("Crash Test", skip_render=True):
            assert adapter_module._ACTIVE_DIAGRAM is not None
            raise ValueError("Simulated User Code Failure")
    except ValueError:
        pass # Catch the expected error
        
    # Memory leak check
    assert adapter_module._ACTIVE_DIAGRAM is None

def test_cloudnode_rshift_builds_edges_in_active_diagram_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that the ">>" operator on a CloudNode intercepts the command and 
    registers a directional edge into the currently active AnimatedDiagram topology.
    """
    from manim_devops.adapter import AnimatedDiagram
    from manim_devops.assets.aws import EC2, RDS
    
    with AnimatedDiagram("Test RSHIFT", skip_render=True) as diag:
        web = EC2("web", "App")
        db = RDS("db", "Database")
        
        # Action: The Magic Syntax
        result = web >> db
        
        # 1. Assert Chaining Support
        assert result is db
        
        # 2. Assert Global Diagram Interception
        # The underlying topology should have explicitly logged an edge from "web" to "db"
        assert len(diag.topology.edges) == 1
        assert ("web", "db") in diag.topology.edges
        
def test_cloudnode_rshift_raises_error_outside_diagram_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that using the ">>" operator without a surrounding context manager 
    fails fast.
    """
    from manim_devops.assets.aws import EC2, RDS
    
    web = EC2("web_fail", "App")
    db = RDS("db_fail", "Database")
    
    with pytest.raises(RuntimeError, match="AnimatedDiagram"):
        web >> db

def test_cloudnode_lshift_builds_reverse_edges_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that the "<<" operator registers a reversed directional edge.
    """
    from manim_devops.adapter import AnimatedDiagram
    from manim_devops.assets.aws import EC2, RDS
    
    with AnimatedDiagram("Test LSHIFT", skip_render=True) as diag:
        web = EC2("web", "App")
        db = RDS("db", "Database")
        
        # Action: Database connects backwards to Web
        result = web << db
        
        # 1. Assert Chaining Support
        assert result is db
        
        # 2. Assert Reverse Edge recorded correctly (target -> self)
        assert len(diag.topology.edges) == 1
        assert ("db", "web") in diag.topology.edges

def test_cloudnode_sub_builds_bidirectional_edges_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that the "-" operator registers bi-directional routing edges.
    """
    from manim_devops.adapter import AnimatedDiagram
    from manim_devops.assets.aws import EC2, RDS
    
    with AnimatedDiagram("Test SUB", skip_render=True) as diag:
        web = EC2("web", "App")
        db = RDS("db", "Database")
        
        # Action: Web and Database are mutually connected
        result = web - db
        
        # 1. Assert Chaining Support
        assert result is db
        
        # 2. Assert Bi-directional Edges
        assert len(diag.topology.edges) == 2
        assert ("web", "db") in diag.topology.edges
        assert ("db", "web") in diag.topology.edges

from unittest.mock import patch

@patch('manim_devops.core.DevopsScene.render')
def test_adapter_triggers_manim_render_programmatically_IMMUTABLE(mock_render):
    """
    IMMUTABLE TEST
    Asserts that the context manager programmatically attempts to spin up 
    a hidden Manim configuration without forcing the user to touch the CLI.
    """
    from manim_devops.adapter import AnimatedDiagram
    from manim_devops.assets.aws import EC2
    
    with AnimatedDiagram("Test Trigger", skip_render=False):
        EC2("node", "App")
        
def test_cloudnode_lshift_raises_error_outside_diagram_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that using the "<<" operator without a surrounding context manager fails fast.
    """
    from manim_devops.assets.aws import EC2, RDS
    web = EC2("web_fail", "App")
    db = RDS("db_fail", "Database")
    
    with pytest.raises(RuntimeError, match="AnimatedDiagram"):
        web << db

def test_cloudnode_sub_raises_error_outside_diagram_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that using the "-" operator without a surrounding context manager fails fast.
    """
    from manim_devops.assets.aws import EC2, RDS
    web = EC2("web_fail", "App")
    db = RDS("db_fail", "Database")
    
    with pytest.raises(RuntimeError, match="AnimatedDiagram"):
        web - db
