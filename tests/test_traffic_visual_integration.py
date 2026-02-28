from manim import config
from manim_devops.core import Topology, DevopsScene
from manim_devops.cinematics import TrafficFlow
from manim_devops.assets.aws import EC2, RDS, Route53, ALB, IGW

class TrafficFlowIntegrationScene(DevopsScene):
    """
    The ultimate test of Phase 3. 
    Can a user declare an AWS layout, render it, and then explicitly command
    TrafficFlow animations to trace the layout they built?
    """
    def construct(self):
        topo = Topology(scale_factor=4.0)
        
        # Instantiate actual AWS objects
        route53 = Route53("dns", "Route53")
        igw = IGW("igw", "Internet Gateway")
        alb = ALB("alb", "Application Load Balancer")
        web1 = EC2("web1", "EC2 Web 1")
        web2 = EC2("web2", "EC2 Web 2")
        db_primary = RDS("db_master", "RDS Primary")
        db_replica = RDS("db_replica", "RDS Read-Replica")
        
        topo.add_nodes([route53, igw, alb, web1, web2, db_primary, db_replica])
        topo.connect(route53, igw)
        topo.connect(igw, alb)
        topo.connect(alb, web1)
        topo.connect(alb, web2)
        topo.connect(web1, db_primary)
        topo.connect(web2, db_primary)
        topo.connect(db_primary, db_replica)
        
        # Draw the initial state
        self.render_topology(topo)
        
        # Phase 3 Cinematic Validations:
        
        # 1. Forward Ping (A -> B)
        # Should spawn at Route53, travel to IGW, pulse IGW, and fade out.
        self.play(TrafficFlow(self, route53, igw, color="#00FF00"))
        
        # 2. Reverse Ping (B -> A)
        # Tests the dynamic reverse lookup algorithm. 
        # Should spawn at Web1, travel 'backwards' to ALB, pulse ALB.
        self.play(TrafficFlow(self, web1, alb, color="#FF0000"))
        
        # 3. Concurrent Pings
        # Should animate both HTTP requests hitting the primary Database simultaneously.
        self.play(
            TrafficFlow(self, web1, db_primary, color="#00FFFF"),
            TrafficFlow(self, web2, db_primary, color="#00FFFF")
        )
        
        self.wait(2)
