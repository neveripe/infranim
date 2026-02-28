import networkx as nx
import numpy as np
from typing import List, Tuple
from manim import Scene, VMobject, Create, Text, GrowFromCenter
from manim_devops.assets import CloudNode
from manim_devops.layout import OrthogonalRouter

class NodeCluster(CloudNode):
    """
    A logical container that NetworkX treats as a single layout node, 
    but which internally calculates deterministic offsets for its children, 
    preventing sub-graph physics collisions.
    """
    def __init__(self, node_id: str, label: str):
        super().__init__(node_id, label)
        self.children: List[CloudNode] = []
        
    def add_child(self, child: CloudNode):
        if child not in self.children:
            self.children.append(child)
            
    def resolve_child_coordinates(self, center: tuple[float, float, float]) -> dict[str, tuple[float, float, float]]:
        """
        Calculates simple horizontal grid offsets for children relative to the center.
        """
        coords = {}
        # Simple algorithm: offset by X=1.0, alternating left and right
        offsets = [-1.0, 1.0, -2.0, 2.0, -3.0, 3.0] 
        for i, child in enumerate(self.children):
            offset_x = offsets[i % len(offsets)]
            coords[child.node_id] = (center[0] + offset_x, center[1], center[2])
        return coords

class Topology:
    """
    The mathematical model representing the architecture state.
    Calculates layouts utilizing NetworkX.
    """
    def __init__(self, scale_factor: float = 3.0):
        self.nodes: List[CloudNode] = []
        self.edges: List[tuple[str, str]] = []
        self.scale_factor = scale_factor

    def add_node(self, node: CloudNode) -> None:
        if node not in self.nodes:
            self.nodes.append(node)

    def add_nodes(self, nodes: List[CloudNode]) -> None:
        for node in nodes:
            self.add_node(node)

    def connect(self, source: CloudNode, target: CloudNode) -> None:
        edge = (source.node_id, target.node_id)
        if edge not in self.edges:
            self.edges.append(edge)

    def calculate_layout(self) -> dict[str, tuple[float, float, float]]:
        G = nx.DiGraph()
        for node in self.nodes:
            G.add_node(node.node_id)
        for edge in self.edges:
            G.add_edge(edge[0], edge[1])

        nx_coords = nx.spring_layout(G, seed=42)

        manim_coords = {}
        for node_id, vector_2d in nx_coords.items():
            x = float(vector_2d[0]) * self.scale_factor
            y = float(vector_2d[1]) * self.scale_factor
            manim_coords[node_id] = (x, y, 0.0)
            
        # Phase 4: Dynamic Sub-Graph Coordinates
        for node in self.nodes:
            if isinstance(node, NodeCluster):
                cluster_center = manim_coords[node.node_id]
                child_coords = node.resolve_child_coordinates(cluster_center)
                manim_coords.update(child_coords)

        return manim_coords


class DevopsScene(Scene):
    """
    The orchestrator. Replaces standard Manim Scene to provide
    context-aware rendering of Topologies without manual cartesian tracking.
    """
    def render_topology(self, topology: Topology) -> None:
        """
        Takes a Topology, positions all nodes natively, draws the Orthogonal
        edges, and plays a unified FadeIn/Create animation.
        """
        coords = topology.calculate_layout()
        router = OrthogonalRouter()
        
        self.rendered_coords = coords  # Persistent memory for ScaleOut offsets Matrix
        self.rendered_edges = {}  # Persistent memory for Phase 3 TrafficFlow animations
        animations = []
        
        # 1. Place the Mobjects (Nodes) at their mathematical coordinates
        for node in topology.nodes:
            # We assume node is a valid Manim Mobject (e.g., inherited from CloudNode + SVGMobject)
            
            # Phase 4 Bugfix: NodeClusters are purely abstract geometric containers.
            # They do not have visual SVGs or `.move_to()` rendering methods.
            if isinstance(node, NodeCluster):
                continue
                
            numeric_coord = coords[node.node_id]
            node.move_to(numeric_coord)
            
            # To fix the Z-Index issue (edges drawing over nodes),
            # we force nodes to render on top of lines
            node.set_z_index(10)
            
            animations.append(GrowFromCenter(node))
            
            # Keep track of generated visuals for future cinematic actions (Phase 3)
            self.mobjects.append(node)
            
            # Add text label below
            label = Text(node.label or node.node_id, font_size=16)
            label.next_to(node, direction=[0, -1, 0])
            label.set_z_index(10)
            
            animations.append(Create(label))
            
        # 2. Draw the Orthogonal Routing Edges
        for src_id, tgt_id in topology.edges:
            src_node = next(n for n in self.mobjects + topology.nodes if n.node_id == src_id)
            tgt_node = next(n for n in self.mobjects + topology.nodes if n.node_id == tgt_id)
            
            # Phase 4 Bugfix: NodeClusters are abstract logic containers, not SVGs.
            # They do not have a .width attribute, so we fall back to a generic boundary radius 
            # to prevent connection lines from intersecting the Cluster's visual space.
            src_radius = 2.0 if isinstance(src_node, NodeCluster) else src_node.width / 2.0
            tgt_radius = 2.0 if isinstance(tgt_node, NodeCluster) else tgt_node.width / 2.0
            
            waypoints = router.compute_path(
                coords[src_id],
                coords[tgt_id],
                source_radius=src_radius,
                target_radius=tgt_radius
            )
            
            line = VMobject(color="#FFFFFF")
            line.set_points_as_corners(waypoints)
            
            # Z-Index 0 intentionally renders below components
            line.set_z_index(0) 
            
            # Store edge mathematically for future traffic animation (Phase 3)
            self.rendered_edges[(src_id, tgt_id)] = line
            
            animations.append(Create(line))
            
        # Play the cinematic rendering
        self.play(*animations, run_time=3.0)
        self.wait(2)
