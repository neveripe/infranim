from manim_devops.core import Topology

# Global state tracker for the currently active Diagram context
_ACTIVE_DIAGRAM = None

class AnimatedDiagram:
    """
    A Context Manager designed to mimic the popular `diagrams` python library API.
    Any CloudNodes instantiated within the `with AnimatedDiagram():` block will 
    automatically be harvested, routed, and optionally rendered via Manim upon exit.
    """
    def __init__(self, name: str = "Animated Infrastructure", skip_render: bool = False):
        self.name = name
        self.skip_render = skip_render
        self.topology = Topology(scale_factor=4.0)
        
    def __enter__(self):
        """
        Injects this diagram instance into the global module state so 
        child CloudNodes can discover it automatically.
        """
        global _ACTIVE_DIAGRAM
        _ACTIVE_DIAGRAM = self
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Tears down the global state to prevent pollution and handles 
        the programmatic rendering trigger if no exceptions occurred.
        """
        global _ACTIVE_DIAGRAM
        _ACTIVE_DIAGRAM = None
        
        # If an exception happened inside the `with` block, abort rendering
        if exc_type is not None:
            return False 
            
        if not self.skip_render:
            self._trigger_manim_render()
            
    def _trigger_manim_render(self):
        """
        Programmatically executes the Manim FFmpeg CLI-equivalent logic targeting 
        this dynamically built topology.
        """
        from manim import tempconfig
        from manim_devops.core import DevopsScene
        
        # 1. Sanitize the diagram name into a valid python Class name for Manim's file writer
        safe_name = "".join([c if c.isalnum() else "" for c in self.name.title()])
        if not safe_name: safe_name = "AnimatedDiagramScene"
        
        topology_ref = self.topology
        
        # 2. Dynamically construct the Scene subclass definition
        class CustomFacadeScene(DevopsScene):
            def construct(self):
                # Simply loop over the mathematical matrix and draw it
                self.render_topology(topology_ref)
                
        # Rename the class so Manim writes the output file nicely (e.g. MyDiagram.mp4)
        CustomFacadeScene.__name__ = safe_name
        
        # 3. Suppress GUI popup and force Fast render quality programmatically
        with tempconfig({"quality": "low_quality", "preview": False}):
            scene = CustomFacadeScene()
            scene.render()
