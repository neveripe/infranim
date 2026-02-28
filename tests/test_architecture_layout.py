import pytest
from manim_devops.core import Topology
from manim_devops.layout import OrthogonalRouter
import numpy as np

def test_topology_returns_scaled_manim_coordinates(aws_3_tier_topology: Topology):
    """
    Asserts that passing a complex, multi-layered architecture graph
    successfully forces the Topology to generate a dict of scaled Manim
    Cartesian vectors without trying to draw them.
    """
    layout_coords = aws_3_tier_topology.calculate_layout()
    assert len(layout_coords) == 7
    
    expected_ids = ["dns", "igw", "alb", "web1", "web2", "db_master", "db_replica"]
    for expected_id in expected_ids:
        assert expected_id in layout_coords
        coord = layout_coords[expected_id]
        assert isinstance(coord, tuple)
        assert len(coord) == 3
        assert coord[2] == 0.0

def test_orthogonal_router_generates_math_waypoints(aws_3_tier_topology: Topology):
    """
    Asserts that the routing engine can accept two numeric coordinates
    and calculate a strict 90-degree path that does not start in the 
    direct center (accounting for node boundary radius).
    """
    layout_coords = aws_3_tier_topology.calculate_layout()
    
    # Grab math coordinates for an edge (e.g. Route53 -> IGW)
    src_coord = np.array(layout_coords["dns"])
    tgt_coord = np.array(layout_coords["igw"])
    
    # Abstract generic Node radius we are projecting off of
    dummy_radius = 0.5
    
    router = OrthogonalRouter()
    waypoints = router.compute_path(src_coord, tgt_coord, dummy_radius, dummy_radius)
    
    # By definition, a simple disjoint L-bend has exactly 3 waypoints
    # (Start edge, 90-degree corner, Target edge)
    assert len(waypoints) == 3
    
    # Assert waypoints are 3D Numpy Arrays
    for wp in waypoints:
        assert isinstance(wp, np.ndarray)
        assert len(wp) == 3
        # Z-axis must be 0.0
        assert wp[2] == 0.0

def test_orthogonal_router_handles_zero_length_collision_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that the routing engine safely returns a generic path and does not 
    throw a ZeroDivisionError if given the exact same start and end coordinates.
    """
    router = OrthogonalRouter()
    
    # Identical coordinates
    src = np.array([5.0, 5.0, 0.0])
    tgt = np.array([5.0, 5.0, 0.0])
    
    # The layout must not crash
    waypoints = router.compute_path(src, tgt, 0.5, 0.5)
    
    # It should return exactly 2 waypoints (the start and target themselves)
    assert len(waypoints) == 2
    assert np.array_equal(waypoints[0], src)
    assert np.array_equal(waypoints[1], tgt)
