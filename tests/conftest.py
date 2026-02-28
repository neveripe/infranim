import pytest
from manim_devops.core import Topology, CloudNode

@pytest.fixture
def empty_topology():
    """Returns a fresh, mathematical topology model."""
    return Topology()

@pytest.fixture
def aws_3_tier_topology(empty_topology):
    """
    Constructs a mathematical model of a standard AWS 3-Tier Web App.
    This fixture ensures our Layout and Routing engines can handle
    a realistic, multi-layered Graph pattern without rendering it.
    """
    topo = empty_topology
    
    # Tier 1: Networking / Entry
    route53 = CloudNode("dns", "Route53")
    igw = CloudNode("igw", "Internet Gateway")
    alb = CloudNode("alb", "Application Load Balancer")
    
    # Tier 2: Compute
    web1 = CloudNode("web1", "EC2 Web 1")
    web2 = CloudNode("web2", "EC2 Web 2")
    
    # Tier 3: Database
    db_primary = CloudNode("db_master", "RDS Primary")
    db_replica = CloudNode("db_replica", "RDS Read-Replica")
    
    # Add Nodes
    topo.add_nodes([route53, igw, alb, web1, web2, db_primary, db_replica])
    
    # Add Edges (Traffic Flow)
    topo.connect(route53, igw)
    topo.connect(igw, alb)
    
    # ALB Load Balances to both web servers
    topo.connect(alb, web1)
    topo.connect(alb, web2)
    
    # Both web servers connect to the primary DB
    topo.connect(web1, db_primary)
    topo.connect(web2, db_primary)
    
    # Primary replicates to replica
    topo.connect(db_primary, db_replica)
    
    return topo
