from pathlib import Path
import logging
from manim import SVGMobject
from manim_devops.assets import CloudNode
from manim_devops.constants import FALLBACK_CIRCLE_RADIUS, AWS_FALLBACK_COLOR

logger = logging.getLogger(__name__)

# The path to bundled SVG icon assets
ASSETS_DIR = Path(__file__).parent / "aws"

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
        
        try:
            SVGMobject.__init__(self, str(svg_path))
            self.scale(0.5)
            # Ensure internal SVG elements stack correctly (last element on top)
            for i, submob in enumerate(self.submobjects):
                submob.set_z_index(i)
        except FileNotFoundError:
            logger.warning("SVG '%s' not found at %s. Using fallback circle for '%s'.", svg_filename, svg_path, node_id)
            self._apply_fallback()
        except Exception as e:
            logger.warning("Failed to parse SVG '%s': %s. Using fallback for '%s'.", svg_filename, e, node_id)
            self._apply_fallback()

    def _apply_fallback(self):
        """Replaces this node's geometry with a generic colored circle."""
        from manim import Circle
        self.become(Circle(radius=FALLBACK_CIRCLE_RADIUS, color=AWS_FALLBACK_COLOR, fill_opacity=0.2))


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
