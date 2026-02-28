from manim import config
from manim_devops.core import Topology, DevopsScene
from manim_devops.assets.aws import EC2, RDS, Route53, ALB, IGW

class FinalIntegrationScene(DevopsScene):
    """
    The ultimate test of Phase 2. 
    Can a user script a complex AWS layout with native inherited assets
    and have it render a flawless video with zero math required?
    """
    def construct(self):
        topo = Topology(scale_factor=4.0)
        
        # Instantiate actual AWS objects (which inherit from SVGMobject under the hood)
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
        
        # The single cinematic wrapper call. 
        # If this doesn't crash, Phase 2 is complete.
        self.render_topology(topo)
