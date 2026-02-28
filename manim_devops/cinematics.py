from manim import Animation, Succession, AnimationGroup, MoveAlongPath, Indicate, Dot, FadeOut, GrowFromCenter, Create, VMobject
from manim_devops.core import DevopsScene, NodeCluster
from manim_devops.assets import CloudNode
from manim_devops.layout import OrthogonalRouter
from manim_devops.constants import (
    Z_PACKET, Z_EDGE, PACKET_RADIUS, PULSE_SCALE_FACTOR,
    SCALE_OUT_NODE_RADIUS, EDGE_COLOR, DEFAULT_TRAFFIC_COLOR,
)

def TrafficFlow(scene: DevopsScene, source: CloudNode, target: CloudNode, color: str = DEFAULT_TRAFFIC_COLOR) -> Animation:
    """
    Constructs a cinematic animation sequence representing abstract data 
    flowing between two architected nodes.
    
    Args:
        scene: The active DevopsScene containing the rendered topology memory.
        source: The CloudNode where the traffic originates.
        target: The CloudNode where the traffic is sent.
        color: The hex color of the glowing data packet.
    """
    src_id = source.node_id
    tgt_id = target.node_id
    
    # 1. Edge Lookup & Reverse Path Resolution
    is_reversed = False
    
    if (src_id, tgt_id) in scene.rendered_edges:
        edge = scene.rendered_edges[(src_id, tgt_id)]
    elif (tgt_id, src_id) in scene.rendered_edges:
        edge = scene.rendered_edges[(tgt_id, src_id)]
        is_reversed = True
    else:
        raise KeyError(f"TrafficFlow Error: No rendered edge found between '{src_id}' and '{tgt_id}'")
        
    # 2. Spawn the Abstract Packet
    packet = Dot(color=color, radius=PACKET_RADIUS)
    # Packets render on top of lines but below nodes
    packet.set_z_index(Z_PACKET) 
    
    # 3. Construct the Path Animation
    # If the user asked for B->A, but the math line is A->B, we must reverse the vector sequence.
    travel_anim = MoveAlongPath(packet, edge)
    
    if is_reversed:
        # Manim's rate_func inversion allows a MoveAlongPath to run backwards
        # effectively tracing B->A without mutating the underlying VMobject
        def reverse_rate(t):
            return 1 - t
        travel_anim = MoveAlongPath(packet, edge, rate_func=reverse_rate)
        
    # 4. Success Indicator (Flash the Target Node)
    # We must find the actual instantiated Mobject inside the topology
    target_mobject = None
    for node in scene.mobjects:
        # Safe check, since we added non-CloudNode labels to the scene as well
        if isinstance(node, CloudNode) and node.node_id == tgt_id:
            target_mobject = node
            break
            
    # Fallback to flashing the abstract point if the Mobject somehow wasn't drawn
    flash_target = target_mobject if target_mobject else packet
    
    pulse_anim = Indicate(flash_target, scale_factor=PULSE_SCALE_FACTOR, color=color)
    
    # 5. Cleanup
    cleanup_anim = FadeOut(packet)
    
    # 6. Compose the Sequence
    # The packet travels, then AT THE SAME TIME it fades out while the target pulses
    return Succession(
        travel_anim,
        AnimationGroup(pulse_anim, cleanup_anim)
    )

def ScaleOutAction(scene: DevopsScene, cluster: NodeCluster, new_child: CloudNode, target: CloudNode = None) -> AnimationGroup:
    """
    Dynamically spawns a new CloudNode into an existing NodeCluster during a scene.
    Automatically calculates deterministic layouts mid-animation, updates the Scene's memory
    structures, and dynamically draws orthogonal connecting lines if a target is provided.
    """
    # 1. State Mutation: Append Child mathematically
    cluster.add_child(new_child)
    
    # 1b. Sync to source Topology to prevent split-brain state divergence (Finding 04)
    if hasattr(scene, 'topology'):
        scene.topology.add_node(new_child)
    
    # 2. Calculate New Geographic Center Offset
    if cluster.node_id not in scene.rendered_coords:
        raise KeyError(f"ScaleOutAction Error: NodeCluster '{cluster.node_id}' not found in Scene memory.")
        
    center_tuple = scene.rendered_coords[cluster.node_id]
    coords = cluster.resolve_child_coordinates(center_tuple)
    new_coord = coords[new_child.node_id]
    
    # Save the new child's mathematical coordinate for future Scaling actions
    scene.rendered_coords[new_child.node_id] = new_coord
    
    # Force the visual CloudNode to its absolute calculated location
    new_child.move_to(new_coord)
    
    # 3. State Registration: Inject into global mobjects array so TrafficFlow can find it
    scene.mobjects.append(new_child)
    
    # Prepare the organic spawner animation
    animations = [GrowFromCenter(new_child)]
    
    # 4. Organic Networking (Draw dynamic line to target)
    if target:
        if target.node_id not in scene.rendered_coords:
             raise KeyError(f"ScaleOutAction Error: Target '{target.node_id}' not found in Scene memory.")
             
        target_coord = scene.rendered_coords[target.node_id]
        
        router = OrthogonalRouter()
        waypoints = router.compute_path(
            new_coord,
            target_coord,
            source_radius=SCALE_OUT_NODE_RADIUS,
            target_radius=SCALE_OUT_NODE_RADIUS
        )
        
        line = VMobject(color=EDGE_COLOR)
        line.set_points_as_corners(waypoints)
        line.set_z_index(Z_EDGE) 
        
        # State Registration: store edge for future TrafficFlow animations
        scene.rendered_edges[(new_child.node_id, target.node_id)] = line
        
        # 4b. Sync edge to source Topology (Finding 04)
        if hasattr(scene, 'topology'):
            scene.topology.connect(new_child, target)
        
        # Add the line drawing to the unified cinematic sequence
        animations.append(Create(line))
        
    return AnimationGroup(*animations)
