import pytest
from manim.mobject.mobject import Mobject
from manim_devops.assets import CloudNode
from manim_devops.assets.aws import EC2, RDS, Route53, ALB, IGW, AWSNode

def test_aws_node_fallback_instantiation_IMMUTABLE():
    """
    IMMUTABLE TEST
    Asserts that the five specified AWS nodes can be instantiated natively via Pytest,
    validating that they correctly inherit the math boundary properties of CloudNode
    and the rendering execution pipeline of Manim's standard Objects, gracefully
    falling back to circles if the physical SVGs are missing.
    """
    web_server = EC2("web1", "EC2 Web 1")
    database = RDS("db_master", "RDS Primary")
    dns = Route53("dns", "Route53")
    load_balancer = ALB("alb", "Application Load Balancer")
    gateway = IGW("igw", "Internet Gateway")
    
    components = [web_server, database, dns, load_balancer, gateway]
    
    for comp in components:
        # Verify it inherits our mathematical tracking base
        assert isinstance(comp, CloudNode)
        
        # Verify it inherits Manim's rendering base (SVGMobject or VMobject)
        assert isinstance(comp, Mobject)
        
        # Verify it successfully captured the kwargs
        assert comp.node_id is not None
        assert comp.label is not None
