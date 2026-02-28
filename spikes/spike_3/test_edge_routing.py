import pytest
import numpy as np
from manim import Circle, VMobject
from edge_router import EdgeRouter, DevopsLine

class TestEdgeRouter:
    def test_calculate_orthogonal_path(self):
        """
        Given a start (0, 0) and end (2, 2), an orthogonal route should
        go (0,0) -> (1,0) -> (1,2) -> (2,2) OR (0,0) -> (0,1) -> (2,1) -> (2,2),
        ensuring only 90 degree turns. As a simplified spike, we'll test a 
        basic X-first L-bend: (0,0) -> (2,0) -> (2,2) or (0,0) -> (1,0) -> (1,2) -> (2,2).
        For simplicity in this spike, we test an X-first routing.
        """
        router = EdgeRouter()
        start = np.array([0.0, 0.0, 0.0])
        end = np.array([2.0, 2.0, 0.0])
        
        # We expect a path of at least 3 points, starting at start, ending at end,
        # where every consecutive point shares either an X or Y coordinate (orthogonal).
        path = router._calculate_orthogonal_path(start, end)
        
        assert len(path) >= 3
        np.testing.assert_array_equal(path[0], start)
        np.testing.assert_array_equal(path[-1], end)
        
        for i in range(len(path) - 1):
            p1 = path[i]
            p2 = path[i+1]
            # Orthogonal check: either X is same or Y is same
            assert p1[0] == p2[0] or p1[1] == p2[1]

    def test_compute_path_accounts_for_radius(self):
        """
        If a node is at (0,0) with radius 1, and target is at (5,0) with radius 1,
        the line should start at (1,0) and end at (4,0), so it doesn't overlap the node.
        """
        router = EdgeRouter()
        
        source = np.array([0.0, 0.0, 0.0])
        target = np.array([5.0, 0.0, 0.0])
        
        path = router.compute_path(source, target, source_radius=1.0, target_radius=1.0)
        
        np.testing.assert_array_equal(path[0], np.array([1.0, 0.0, 0.0]))
        np.testing.assert_array_equal(path[-1], np.array([4.0, 0.0, 0.0]))


class TestDevopsLine:
    def test_init_accepts_mobjects(self):
        """Test wrapper accepts standard Manim Mobjects and calculates."""
        circ1 = Circle(radius=1.0)
        circ1.move_to(np.array([0.0, 0.0, 0.0]))
        
        circ2 = Circle(radius=1.0)
        circ2.move_to(np.array([5.0, 0.0, 0.0]))
        
        line = DevopsLine(circ1, circ2)
        
        assert line.source_mobject == circ1
        assert line.target_mobject == circ2
        assert len(line.waypoints) >= 2
        
    def test_render_creates_valid_vmobject(self):
        """Test DevopsLine.render() returns a valid Manim VMobject."""
        circ1 = Circle(radius=1.0)
        circ1.move_to(np.array([0.0, 0.0, 0.0]))
        
        circ2 = Circle(radius=1.0)
        circ2.move_to(np.array([5.0, 0.0, 0.0]))
        
        line = DevopsLine(circ1, circ2)
        mobject = line.render()
        
        assert isinstance(mobject, VMobject)
