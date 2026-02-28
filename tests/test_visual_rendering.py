from manim import Scene, Circle, Create, Text, config
from manim_devops.core import Topology, CloudNode
from manim_devops.layout import OrthogonalRouter

def get_3_tier_topology():
    # Helper to avoid pytest fixture dependency in a straight Manim script
    topo = Topology(scale_factor=4.0) # Larger scale for video
    route53 = CloudNode("dns", "Route53")
    igw = CloudNode("igw", "Internet Gateway")
    alb = CloudNode("alb", "Application Load Balancer")
    web1 = CloudNode("web1", "EC2 Web 1")
    web2 = CloudNode("web2", "EC2 Web 2")
    db_primary = CloudNode("db_master", "RDS Primary")
    db_replica = CloudNode("db_replica", "RDS Read-Replica")
    topo.add_nodes([route53, igw, alb, web1, web2, db_primary, db_replica])
    topo.connect(route53, igw)
    topo.connect(igw, alb)
    topo.connect(alb, web1)
    topo.connect(alb, web2)
    topo.connect(web1, db_primary)
    topo.connect(web2, db_primary)
    topo.connect(db_primary, db_replica)
    return topo

class VisualTestScene(Scene):
    """
    This is the manual Red Phase test. We invoke the expected API 
    (DevopsScene doesn't exist yet, so we write what we WANT it to look like).
    """
    def construct(self):
        topology = get_3_tier_topology()
        
        # In the future, this should just be: self.render_topology(topology)
        # But for now, we manually bridge the gap to test if the math holds up visually.
        
        coords = topology.calculate_layout()
        router = OrthogonalRouter()
        
        rendered_nodes = {}
        animations = []
        
        # 1. Render generic circles for nodes
        for node in topology.nodes:
            circle = Circle(radius=0.5, color="#FF9900")
            circle.move_to(coords[node.node_id])
            
            label = Text(node.label or node.node_id, font_size=16)
            label.next_to(circle, direction=[0, -1, 0]) # Down
            
            rendered_nodes[node.node_id] = circle
            animations.extend([Create(circle), Create(label)])
            
        # 2. Render Orthogonal Edges
        from manim import VMobject
        for src_id, tgt_id in topology.edges:
            src_coord = coords[src_id]
            tgt_coord = coords[tgt_id]
            
            # Use radius 0.5 as defined in step 1
            waypoints = router.compute_path(src_coord, tgt_coord, 0.5, 0.5)
            
            line = VMobject(color="#FFFFFF")
            line.set_points_as_corners(waypoints)
            animations.append(Create(line))
            
        # Play all simultaneously
        self.play(*animations, run_time=3.0)
        self.wait(1)
