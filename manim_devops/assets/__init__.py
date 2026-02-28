from typing import Optional

class CloudNode:
    """
    Agnostic mathematical representation of a node in the architecture graph.
    It holds an ID and eventually coordinates, but does not know how to draw itself.
    """
    def __init__(self, node_id: str, label: Optional[str] = None):
        self.node_id = node_id
        self.label = label

    def __rshift__(self, target):
        """
        Intercepts the `node_a >> node_b` syntax to seamlessly build topology edges
        inside a globally active AnimatedDiagram context.
        """
        import manim_devops.adapter as adapter
        diagram = adapter._ACTIVE_DIAGRAM
        
        if diagram is None:
            raise RuntimeError(
                "CloudNodes can only be connected via `>>` inside an active "
                "`with AnimatedDiagram():` context block."
            )
            
        # Register both nodes incase they were instantiated inline
        diagram.topology.add_node(self)
        diagram.topology.add_node(target)
        
        # Register the directional edge mathematically
        diagram.topology.connect(self, target)
        
        # Return the target to support chaining syntax `a >> b >> c`
        return target
        
    def __lshift__(self, target):
        """
        Intercepts the `node_a << node_b` syntax. Reverses the topological connection.
        """
        import manim_devops.adapter as adapter
        diagram = adapter._ACTIVE_DIAGRAM
        if diagram is None:
            raise RuntimeError("CloudNodes can only be connected via `<<` inside an active `with AnimatedDiagram():` context block.")
            
        diagram.topology.add_node(self)
        diagram.topology.add_node(target)
        
        # Reverse edge `target` -> `self`
        diagram.topology.connect(target, self)
        return target
        
    def __sub__(self, target):
        """
        Intercepts the `node_a - node_b` syntax. Creates a bi-directional edge.
        """
        import manim_devops.adapter as adapter
        diagram = adapter._ACTIVE_DIAGRAM
        if diagram is None:
            raise RuntimeError("CloudNodes can only be connected via `-` inside an active `with AnimatedDiagram():` context block.")
            
        diagram.topology.add_node(self)
        diagram.topology.add_node(target)
        
        # Bi-directional edge
        diagram.topology.connect(self, target)
        diagram.topology.connect(target, self)
        return target
