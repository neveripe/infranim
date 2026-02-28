import networkx as nx
import numpy as np
from typing import List, Tuple
from manim import Scene, VMobject, Create, Text, GrowFromCenter
from manim_devops.assets import GraphEntity, CloudNode
from manim_devops.layout import OrthogonalRouter
from manim_devops.constants import (
    LAYOUT_SEED, DEFAULT_SCALE_FACTOR, Z_NODE, Z_EDGE,
    LABEL_FONT_SIZE, CLUSTER_FALLBACK_RADIUS,
    RENDER_DURATION, POST_RENDER_WAIT, EDGE_COLOR,
)

class NodeCluster(GraphEntity):
    """
    A logical container that NetworkX treats as a single layout node, 
    but which internally calculates deterministic offsets for its children, 
    preventing sub-graph physics collisions.
    
    Inherits from GraphEntity (not CloudNode) because it is NOT renderable —
    it has no SVG, no .move_to(), and no .width. This prevents Liskov violations.
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
    def __init__(self, scale_factor: float = DEFAULT_SCALE_FACTOR):
        self._nodes: dict[str, CloudNode] = {}
        self._edges: set[tuple[str, str]] = set()
        self._edge_order: list[tuple[str, str]] = []  # preserve draw order
        self.scale_factor = scale_factor

    @property
    def nodes(self) -> list[CloudNode]:
        """Public API — returns nodes in insertion order."""
        return list(self._nodes.values())

    @property
    def edges(self) -> list[tuple[str, str]]:
        """Public API — returns edges in insertion order."""
        return list(self._edge_order)

    def add_node(self, node: CloudNode) -> None:
        if node.node_id not in self._nodes:
            self._nodes[node.node_id] = node

    def add_nodes(self, nodes: list[CloudNode]) -> None:
        for node in nodes:
            self.add_node(node)

    def connect(self, source: CloudNode, target: CloudNode) -> None:
        edge = (source.node_id, target.node_id)
        if edge not in self._edges:
            self._edges.add(edge)
            self._edge_order.append(edge)

    def calculate_layout(self) -> dict[str, tuple[float, float, float]]:
        G = nx.DiGraph()
        for node_id in self._nodes:
            G.add_node(node_id)
        for edge in self._edge_order:
            G.add_edge(edge[0], edge[1])

        nx_coords = nx.spring_layout(G, seed=LAYOUT_SEED)

        manim_coords = {}
        for node_id, vector_2d in nx_coords.items():
            x = float(vector_2d[0]) * self.scale_factor
            y = float(vector_2d[1]) * self.scale_factor
            manim_coords[node_id] = (x, y, 0.0)
            
        # Phase 4: Dynamic Sub-Graph Coordinates
        for node in self._nodes.values():
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
        
        self.topology = topology  # Store reference so ScaleOutAction can sync (Finding 04)
        self.rendered_coords = coords  # Persistent memory for ScaleOut offsets Matrix
        self.rendered_edges = {}  # Persistent memory for Phase 3 TrafficFlow animations
        animations = []
        
        # 1. Place the Mobjects (Nodes) at their mathematical coordinates
        for node in topology.nodes:
            # Phase 4 Bugfix: NodeClusters are purely abstract geometric containers.
            # They do not have visual SVGs or `.move_to()` rendering methods.
            if isinstance(node, NodeCluster):
                continue
                
            numeric_coord = coords[node.node_id]
            node.move_to(numeric_coord)
            
            # Force nodes to render on top of lines
            node.set_z_index(Z_NODE)
            
            animations.append(GrowFromCenter(node))
            
            # Keep track of generated visuals for future cinematic actions (Phase 3)
            self.mobjects.append(node)
            
            # Add text label below
            label = Text(node.label or node.node_id, font_size=LABEL_FONT_SIZE)
            label.next_to(node, direction=[0, -1, 0])
            label.set_z_index(Z_NODE)
            
            animations.append(Create(label))
            
        # 2. Build a lookup dict for O(1) node access during edge rendering
        node_lookup = {n.node_id: n for n in topology.nodes}
        for mob in self.mobjects:
            if hasattr(mob, 'node_id'):
                node_lookup[mob.node_id] = mob
        
        # 3. Draw the Orthogonal Routing Edges
        for src_id, tgt_id in topology.edges:
            src_node = node_lookup[src_id]
            tgt_node = node_lookup[tgt_id]
            
            # Phase 4 Bugfix: NodeClusters don't have .width
            src_radius = CLUSTER_FALLBACK_RADIUS if isinstance(src_node, NodeCluster) else src_node.width / 2.0
            tgt_radius = CLUSTER_FALLBACK_RADIUS if isinstance(tgt_node, NodeCluster) else tgt_node.width / 2.0
            
            waypoints = router.compute_path(
                coords[src_id],
                coords[tgt_id],
                source_radius=src_radius,
                target_radius=tgt_radius
            )
            
            line = VMobject(color=EDGE_COLOR)
            line.set_points_as_corners(waypoints)
            
            # Z-Index renders below components
            line.set_z_index(Z_EDGE) 
            
            # Store edge mathematically for future traffic animation (Phase 3)
            self.rendered_edges[(src_id, tgt_id)] = line
            
            animations.append(Create(line))
            
        # Play the cinematic rendering
        self.play(*animations, run_time=RENDER_DURATION)
        self.wait(POST_RENDER_WAIT)

