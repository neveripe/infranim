"""
Public API Interface Contracts for `manim-devops`

This file serves as the strict blueprint for the MVP's public-facing API.
It contains no implementation logic, only type signatures and docstrings.
Actual implementation must adhere strictly to these contracts.
"""

from typing import List, Optional
from manim import Scene, VMobject, SVGMobject
import networkx as nx


class CloudNode(SVGMobject):
    """
    Base class for any animatable architecture component.
    Wraps standard Manim SVGMobjects with DevOps-specific metadata.
    """
    node_id: str
    provider: str
    service_name: str

    def __init__(self, node_id: str, label: Optional[str] = None):
        """
        Instantiates a node. The underlying SVG is determined by subclasses 
        (e.g., AWS.EC2, GCP.CloudSQL).
        """
        ...
        
    def ping(self, target: "CloudNode", color: str = "#FF9900") -> "TrafficFlow":
        """
        Syntactic sugar to generate a TrafficFlow animation from this node to a target.
        """
        ...


class Topology:
    """
    The mathematical model representing the architecture state.
    Calculates layouts but performs no rendering itself.
    """
    def __init__(self):
        ...

    def add_node(self, node: CloudNode) -> None:
        """Registers a CloudNode in the topology."""
        ...

    def connect(self, source: CloudNode, target: CloudNode) -> "DevopsLine":
        """
        Creates a directed edge between two nodes. Returns the DevopsLine
        Mobject representing the connection.
        """
        ...

    def calculate_layout(self) -> dict[str, tuple[float, float, float]]:
        """
        Fires the NetworkX engine to calculate Manim coordinates for all nodes in the topology.
        Returns a mapping of node_id -> (X, Y, Z) vectors.
        """
        ...


class DevopsLine(VMobject):
    """
    The visual representation of an edge in the topology.
    Utilizes A* or orthogonal routing to avoid overlapping nodes.
    """
    def __init__(self, source: CloudNode, target: CloudNode):
        ...


class TrafficFlow(VMobject): # Inherits VMobject, utilized as an Animation
    """
    A cinematic animation class that moves a packet (ActionDot) 
    along a specific DevopsLine path.
    """
    def __init__(self, source: CloudNode, target: CloudNode, color: str):
        ...


class DevopsScene(Scene):
    """
    The orchestrator. Replaces the standard Manim Scene to provide
    context-aware rendering of CloudNodes and Topologies.
    """
    topology: Topology

    def render_topology(self, topology: Topology) -> None:
        """
        Takes a fully declared Topology object, calls calculate_layout(),
        positions all CloudNodes at their respective coordinates, draws 
        the DevopsLines between them, and plays a unified FadeIn/Create animation.
        """
        ...
