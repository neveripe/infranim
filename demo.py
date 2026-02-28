"""
manim-devops PoC Demo — All Features in One Video

Run with:
    manim -pql demo.py DemoScene
"""
from manim_devops.core import Topology, NodeCluster, DevopsScene
from manim_devops.assets.aws import EC2, RDS, ALB
from manim_devops.cinematics import TrafficFlow, ScaleOutAction


class DemoScene(DevopsScene):
    """
    Demonstrates the complete manim-devops pipeline:
    1. Build a topology from AWS nodes
    2. Render it with orthogonal routing
    3. Animate traffic flow between nodes
    4. Dynamically scale out a new node mid-scene
    5. Animate traffic to the newly spawned node
    """
    def construct(self):
        # ── Phase 1: Build the Architecture ──────────────────
        topo = Topology(scale_factor=2.5)
        
        alb = ALB("alb", "Load Balancer")
        asg = NodeCluster("asg", "Auto-Scaling Group")
        web1 = EC2("web1", "Web Server 1")
        web2 = EC2("web2", "Web Server 2")
        db = RDS("db", "Database")
        
        asg.add_child(web1)
        asg.add_child(web2)
        
        topo.add_nodes([alb, asg, web1, web2, db])
        topo.connect(alb, web1)
        topo.connect(alb, web2)
        topo.connect(web1, db)
        topo.connect(web2, db)
        
        # ── Phase 2: Render the Topology ─────────────────────
        self.render_topology(topo)
        
        # ── Phase 3: Animate Traffic ─────────────────────────
        self.play(TrafficFlow(self, alb, web1))
        self.play(TrafficFlow(self, web1, db))
        self.play(TrafficFlow(self, alb, web2))
        self.play(TrafficFlow(self, web2, db))
        
        # ── Phase 4: Dynamic Scale-Out ───────────────────────
        web3 = EC2("web3", "Web Server 3")
        self.play(ScaleOutAction(self, asg, web3, target=db))
        
        # Traffic to the new node
        self.play(TrafficFlow(self, web3, db))
        
        self.wait(2)
