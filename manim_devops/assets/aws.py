from pathlib import Path
from manim import SVGMobject
from manim_devops.assets import CloudNode

# The absolute path to the bundled official SVG assets
ASSETS_DIR = Path(__file__).parent / "assets" / "aws"

class AWSNode(CloudNode, SVGMobject):
    """
    The provider-specific generic base.
    Inherits Math properties from CloudNode, and Render properties from SVGMobject.
    """
    def __init__(self, node_id: str, label: str, svg_filename: str):
        # 1. Initialize Math Tracker
        CloudNode.__init__(self, node_id, label)
        
        # 2. Initialize Visual Renderer
        svg_path = ASSETS_DIR / svg_filename
        if not svg_path.exists():
            # For this PoC, if we haven't downloaded the real SVG yet, 
            # we fallback to a dummy shape so the engine doesn't crash.
            # In production, this raises a FileNotFoundError.
            pass
            
        try:
            SVGMobject.__init__(self, str(svg_path))
        except Exception:
            # Fallback for PoC if SVG isn't present
            from manim import Circle
            self.become(Circle(radius=0.5, color="#FF9900", fill_opacity=0.2))


class EC2(AWSNode):
    def __init__(self, node_id: str, label: str):
        super().__init__(node_id, label, "Amazon-EC2.svg")

class RDS(AWSNode):
    def __init__(self, node_id: str, label: str):
        super().__init__(node_id, label, "Amazon-RDS.svg")

class Route53(AWSNode):
    def __init__(self, node_id: str, label: str):
        super().__init__(node_id, label, "Amazon-Route-53.svg")

class ALB(AWSNode):
    def __init__(self, node_id: str, label: str):
        super().__init__(node_id, label, "Elastic-Load-Balancing.svg")

class IGW(AWSNode):
    def __init__(self, node_id: str, label: str):
        super().__init__(node_id, label, "Internet-Gateway.svg")
