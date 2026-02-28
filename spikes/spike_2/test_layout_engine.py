import pytest
import networkx as nx
from layout_engine import GraphModel, LayoutEngine

class TestGraphModel:
    def test_add_node(self):
        """Test adding nodes to the internal graph representation."""
        graph = GraphModel()
        graph.add_node("A")
        graph.add_node("B")
        
        assert "A" in graph.nodes
        assert "B" in graph.nodes
        assert len(graph.nodes) == 2

    def test_add_edge(self):
        """Test adding directed edges between nodes."""
        graph = GraphModel()
        graph.add_node("A")
        graph.add_node("B")
        graph.add_edge("A", "B")
        
        assert ("A", "B") in graph.edges

    def test_get_networkx_graph_generates_valid_digraph(self):
        """Test the conversion to a pure NetworkX DiGraph."""
        graph = GraphModel()
        graph.add_node("A")
        graph.add_node("B")
        graph.add_edge("A", "B")
        
        nx_graph = graph.get_networkx_graph()
        
        assert isinstance(nx_graph, nx.DiGraph)
        assert list(nx_graph.nodes) == ["A", "B"]
        assert list(nx_graph.edges) == [("A", "B")]


class TestLayoutEngine:
    @pytest.fixture
    def simple_graph(self):
        graph = GraphModel()
        graph.add_node("A")
        graph.add_node("B")
        graph.add_node("C")
        graph.add_edge("A", "B")
        graph.add_edge("A", "C")
        return graph

    def test_compute_coordinates_returns_manim_vectors(self, simple_graph):
        """
        Test that layout engine returns coordinates mapped 
        as Manim 3D Vectors: (X, Y, Z=0)
        """
        engine = LayoutEngine(scale_factor=1.0)
        coords = engine.compute_coordinates(simple_graph)
        
        assert "A" in coords
        assert "B" in coords
        assert "C" in coords
        
        # Ensure it's a 3D tuple/list (X, Y, Z) expected by Manim
        for node, vector in coords.items():
            assert len(vector) == 3
            assert vector[2] == 0.0  # Z should be 0 for 2D Manim scenes

    def test_apply_manim_scaling(self, simple_graph):
        """
        Test that scaling correctly multiplies the normalized 
        [-1, 1] output of NetworkX so nodes fill the Manim camera frame.
        """
        engine_scale_1 = LayoutEngine(scale_factor=1.0)
        engine_scale_3 = LayoutEngine(scale_factor=3.0)
        
        coords_1 = engine_scale_1.compute_coordinates(simple_graph)
        coords_3 = engine_scale_3.compute_coordinates(simple_graph)
        
        # The coordinates at scale 3 should be exactly 3x the coordinates at scale 1
        assert coords_3["A"][0] == pytest.approx(coords_1["A"][0] * 3.0)
        assert coords_3["A"][1] == pytest.approx(coords_1["A"][1] * 3.0)
        assert coords_3["B"][0] == pytest.approx(coords_1["B"][0] * 3.0)

