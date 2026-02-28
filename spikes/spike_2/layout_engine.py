import networkx as nx

class GraphModel:
    """
    Internal representation of the Cloud Topology. 
    Strictly decouples User definitions from the Layout math.
    """
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, id: str) -> None:
        """Registers a node ID in the graph."""
        if id not in self.nodes:
            self.nodes.append(id)

    def add_edge(self, source: str, target: str) -> None:
        """Registers a directed edge from source to target."""
        if (source, target) not in self.edges:
            self.edges.append((source, target))

    def get_networkx_graph(self) -> nx.DiGraph:
        """Compiles the internal model into a pure NetworkX Directed Graph."""
        G = nx.DiGraph()
        G.add_nodes_from(list(self.nodes))
        G.add_edges_from(list(self.edges))
        return G


class LayoutEngine:
    """
    Translates abstract NetworkX force-directed coordinate layouts 
    into explicit 3D vectors mapping to Manim's camera frame.
    """
    def __init__(self, scale_factor: float = 3.0):
        # Manim's default camera width is ~14.22x8.0.
        # NetworkX outputs normalized coords tightly packed near 0,0.
        # Scale factor manually stretches the graph.
        self.scale_factor = scale_factor

    def compute_coordinates(self, graph_model: GraphModel) -> dict:
        """
        Calculates normalized NetworkX positions, then scales them
        into Manim 3D Vectors (X, Y, Z=0).
        """
        nx_graph = graph_model.get_networkx_graph()
        
        # multipartite/spring layout returns: {'A': array([0.5, 0.2]), ...}
        # In this minimal spike, we use spring_layout as the generic default.
        nx_coords = nx.spring_layout(nx_graph, seed=42) # seeded for determinism
        
        return self._apply_manim_scaling(nx_coords)

    def _apply_manim_scaling(self, nx_coords: dict) -> dict:
        """
        Multiplies X and Y by the scale factor.
        Appends a Z-axis value of 0.0 (Mandatory for Manim vectors).
        """
        manim_coords = {}
        for node_id, vector_2d in nx_coords.items():
            x = float(vector_2d[0]) * self.scale_factor
            y = float(vector_2d[1]) * self.scale_factor
            
            # Manim Mobjects require a 3D tuple: (X, Y, Z)
            manim_coords[node_id] = (x, y, 0.0)
            
        return manim_coords
