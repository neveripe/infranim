import numpy as np
from manim import VMobject, SVGMobject

class EdgeRouter:
    """
    Handles the mathematical logic for generating 90-degree orthogonal paths 
    between two nodes, ensuring the lines don't overlap the node bodies.
    """
    def __init__(self, corner_radius: float = 0.2):
        self.corner_radius = corner_radius

    def compute_path(self, source_center: np.ndarray, target_center: np.ndarray, source_radius: float, target_radius: float) -> list:
        """
        Calculates an orthogonal path that starts exactly on the boundary 
        of the source node and ends on the boundary of the target node.
        """
        # Calculate the direct vector to know which direction we are heading
        raw_vector = target_center - source_center
        length = np.linalg.norm(raw_vector)
        
        if length == 0:
            return [source_center, target_center]
            
        unit_vector = raw_vector / length
        
        # 1. Start strictly on the boundary of the source
        # In a real app we'd project to the bounding box, 
        # but for this spike we project a circle radius along the X-axis mapping.
        start_edge = source_center + (unit_vector * source_radius)
        
        # 2. End strictly on the boundary of the target
        end_edge = target_center - (unit_vector * target_radius)
        
        # 3. Calculate the orthogonal route between the two boundary points
        return self._calculate_orthogonal_path(start_edge, end_edge)

    def _calculate_orthogonal_path(self, start: np.ndarray, end: np.ndarray) -> list:
        """
        Generates a 90-degree orthogonal path.
        For this simplified spike, we generate an "X-first" L-bend.
        """
        waypoints = []
        waypoints.append(start)
        
        # The elbow joint (move completely in X direction first, then Y)
        elbow = np.array([end[0], start[1], 0.0])
        
        # Only add the elbow if it's not strictly a straight line already
        if not np.array_equal(elbow, start) and not np.array_equal(elbow, end):
            waypoints.append(elbow)
            
        waypoints.append(end)
        
        return waypoints


class DevopsLine:
    """
    A unified wrapper that connects two Manim `Mobjects` with a beautiful 
    orthogonal path drawn by the `EdgeRouter`.
    """
    def __init__(self, source: VMobject, target: VMobject):
        self.source_mobject = source
        self.target_mobject = target
        self.router = EdgeRouter()
        
        # We need to extract the centers and radii natively from Manim
        src_center = self.source_mobject.get_center()
        tgt_center = self.target_mobject.get_center()
        
        # Manim's width is the total diameter. Radius is half.
        src_radius = self.source_mobject.width / 2.0
        tgt_radius = self.target_mobject.width / 2.0
        
        self.waypoints = self.router.compute_path(src_center, tgt_center, src_radius, tgt_radius)

    def render(self) -> VMobject:
        """
        Takes the calculated waypoints and draws a literal Manim Mobject.
        For the spike, we draw a continuous VMobject path.
        """
        line_path = VMobject()
        line_path.set_points_as_corners(self.waypoints)
        return line_path
