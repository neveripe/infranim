import numpy as np

class OrthogonalRouter:
    """
    Handles the mathematical logic for generating 90-degree orthogonal paths 
    between two coordinates, ensuring lines project off the boundary radius.
    """
    def __init__(self):
        pass

    def compute_path(self, source_center: np.ndarray, target_center: np.ndarray, source_radius: float, target_radius: float) -> list[np.ndarray]:
        """
        Calculates an orthogonal path that starts strictly on the boundary 
        of the source node and ends on the boundary of the target node.
        """
        # Ensure points are numpy arrays for vector math
        source_center = np.array(source_center)
        target_center = np.array(target_center)
        
        # Calculate direction vector
        raw_vector = target_center - source_center
        length = np.linalg.norm(raw_vector)
        
        if length == 0:
            return [source_center, target_center]
            
        unit_vector = raw_vector / length
        
        # 1. Start strictly on the boundary of the source
        # Projects a circle radius along the vector mapping.
        start_edge = source_center + (unit_vector * source_radius)
        
        # 2. End strictly on the boundary of the target
        end_edge = target_center - (unit_vector * target_radius)
        
        # 3. Calculate the orthogonal L-bend
        return self._calculate_orthogonal_path(start_edge, end_edge)

    def _calculate_orthogonal_path(self, start: np.ndarray, end: np.ndarray) -> list[np.ndarray]:
        """
        Generates a 90-degree orthogonal path.
        Returns a "X-first" L-bend.
        """
        waypoints = []
        waypoints.append(start)
        
        # The elbow joint (move completely in X direction first, then Y)
        # We explicitly enforce Z-axis = 0.0 for 2D diagramming
        elbow = np.array([end[0], start[1], 0.0])
        
        # Only add the elbow if it's not strictly a straight line already
        if not np.array_equal(elbow, start) and not np.array_equal(elbow, end):
            waypoints.append(elbow)
            
        waypoints.append(end)
        
        return waypoints
