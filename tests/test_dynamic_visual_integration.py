from manim import config, Wait
from manim_devops.core import Topology, DevopsScene, NodeCluster
from manim_devops.cinematics import TrafficFlow, ScaleOutAction
from manim_devops.assets.aws import EC2, RDS, ALB, Route53, IGW

class AutoScalingIntegrationScene(DevopsScene):
    """
    The ultimate test of Phase 4. 
    Can a user declare an AWS layout with a Cluster, render it, and then explicitly command
    a ScaleOutAction to spawn a new EC2 mid-video that automatically registers with the Load Balancer?
    """
    def construct(self):
        topo = Topology(scale_factor=4.0)
        
        # Instantiate actual AWS objects
        route53 = Route53("dns", "Route53")
        igw = IGW("igw", "Internet Gateway")
        alb = ALB("alb", "Application Load Balancer")
        db = RDS("db", "RDS Primary")
        
        # The new Phase 4 Abstraction
        asg = NodeCluster("asg", "Auto-Scaling Group")
        web1 = EC2("web1", "EC2 Web 1")
        web2 = EC2("web2", "EC2 Web 2")
        asg.add_child(web1)
        asg.add_child(web2)
        
        topo.add_nodes([route53, igw, alb, asg, db])
        topo.connect(route53, igw)
        topo.connect(igw, alb)
        topo.connect(alb, asg)
        topo.connect(asg, db)
        
        # Draw the initial state (NetworkX computes 'asg' block, Topology computes web1/web2 relative offsets)
        self.render_topology(topo)
        
        # 1. Normal Traffic showing initial state stability
        self.play(TrafficFlow(self, route53, igw, color="#00FF00"))
        
        # 2. Phase 4 Cinematic Validation: SCALE OUT
        # A new instance spawns during high load!
        new_web3 = EC2("web3", "EC2 Scale-Out")
        
        self.play(ScaleOutAction(self, asg, new_web3, target=alb))
        
        # 3. Validation: Can traffic flow to the newly spawned node dynamically?
        self.play(TrafficFlow(self, igw, alb, color="#FFFF00"))
        self.play(TrafficFlow(self, alb, new_web3, color="#FF00FF"))
        
        self.wait(2)
