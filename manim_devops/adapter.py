import contextvars
from manim_devops.core import Topology
from manim_devops.constants import ADAPTER_SCALE_FACTOR

# Thread-safe and asyncio-safe context variable (replaces module-global)
_ACTIVE_DIAGRAM: contextvars.ContextVar['AnimatedDiagram'] = contextvars.ContextVar(
    '_ACTIVE_DIAGRAM', default=None
)

class AnimatedDiagram:
    """
    A Context Manager that mimics the `diagrams` python library API.
    CloudNodes connected via ``>>``, ``<<``, or ``-`` operators inside the
    ``with`` block are added to an internal Topology and rendered as a Manim
    video on exit.
    
    Note: Nodes are NOT auto-harvested by instantiation alone — they must
    be connected via an operator to appear in the output.
    """
    def __init__(self, name: str = "Animated Infrastructure", skip_render: bool = False):
        self.name = name
        self.skip_render = skip_render
        self.topology = Topology(scale_factor=ADAPTER_SCALE_FACTOR)
        self._context_token = None
        
    def __enter__(self):
        """
        Injects this diagram instance into the context-local state so 
        child CloudNodes can discover it automatically.
        """
        self._context_token = _ACTIVE_DIAGRAM.set(self)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Tears down the context state to prevent pollution and handles 
        the programmatic rendering trigger if no exceptions occurred.
        """
        _ACTIVE_DIAGRAM.reset(self._context_token)
        self._context_token = None
        
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
