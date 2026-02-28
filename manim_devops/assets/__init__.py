from typing import Optional

class GraphEntity:
    """
    Pure identity for any object in the topology graph.
    Has an ID and label, and supports operator overloads for edge creation.
    """
    def __init__(self, node_id: str, label: Optional[str] = None):
        self.node_id = node_id
        self.label = label

    def _connect_via_adapter(self, target, operator_symbol, edges):
        """
        Shared logic for all operator overloads (>>, <<, -).
        Registers nodes and edges into the globally active AnimatedDiagram.
        """
        import manim_devops.adapter as adapter
        diagram = adapter._ACTIVE_DIAGRAM.get()
        if diagram is None:
            raise RuntimeError(
                f"CloudNodes can only be connected via `{operator_symbol}` inside an active "
                f"`with AnimatedDiagram():` context block."
            )
        diagram.topology.add_node(self)
        diagram.topology.add_node(target)
        for src, tgt in edges:
            diagram.topology.connect(src, tgt)
        return target

    def __rshift__(self, target):
        """Intercepts `node_a >> node_b`. Forward directional edge."""
        return self._connect_via_adapter(target, ">>", [(self, target)])

    def __lshift__(self, target):
        """Intercepts `node_a << node_b`. Reverse directional edge."""
        return self._connect_via_adapter(target, "<<", [(target, self)])

    def __sub__(self, target):
        """Intercepts `node_a - node_b`. Bi-directional edge."""
        return self._connect_via_adapter(target, "-", [(self, target), (target, self)])

class CloudNode(GraphEntity):
    """
    A renderable entity in the architecture graph.
    Distinguished from GraphEntity for isinstance checks in the rendering pipeline.
    """
    def __init__(self, node_id: str, label: Optional[str] = None):
        super().__init__(node_id, label)
