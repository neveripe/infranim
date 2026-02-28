# Execution Log: ScaleOutAction (cinematics.py)

## Explanation
In order to dynamically scale a topology during the animation, we need a function that injects a new `CloudNode` into an existing `NodeCluster`, calculates its new coordinate without disturbing the others, animates its materialization on screen, and physically draws its geometric connections to external targets.

We are designing `ScaleOutAction(scene: DevopsScene, cluster: NodeCluster, new_child: CloudNode, target: CloudNode = None) -> Animation`.

---

## The 3 Why's (Validating the Test Necessity)

1. **Why does it only animate the newly spawned child?**
   Because our grid math in `NodeCluster` (`[-1.0, 1.0, -2.0, 2.0...]`) is deterministic and additive. Adding child index 2 (`-2.0`) does not alter the absolute coordinates of child index 0 (`-1.0`) and child index 1 (`1.0`). Therefore, we don't need to rebuild the entire cluster; we just spawn the new element.
2. **Why must we pass `target` explicitly?**
   Because an EC2 instance spawned in an Auto-Scaling Group doesn't just float in the void. It must instantly register with a Load Balancer (or a DB). The cinematic action must synchronously route an orthogonal line from the *new* EC2 coordinate to the *existing* Load Balancer coordinate.
3. **Why make these tests Immutable?**
   Because `ScaleOutAction` mutates the layout state and the internal dictionary state of `DevopsScene` (`scene.rendered_edges`). This is highly destructive matrix math. If it fails, all future `TrafficFlow` packets will throw `KeyError` or hit `ZeroDivisionError` floating point anomalies.

---

## 3 Deep Technical Questions (The `ScaleOut` Implementation)

1. **Center Centroid Memory:** `NodeCluster.resolve_child_coordinates()` requires the `center` of the cluster. But `NodeCluster` itself doesn't save its own `center` during Phase 2 layout generation; it returns it in the array and `DevopsScene` consumes it. How does `ScaleOutAction` know what the center coordinate is? 
   *Answer:* It has to extract it dynamically from the `cluster` object's literal Manim `get_center()` geometrical property, rather than NetworkX.
2. **Edge Injection:** When `ScaleOutAction` draws the new path to `target`, it must add that `VMobject` to `scene.rendered_edges`. Should the function return an animation, AND mutate the system Dictionary asynchronously, or should the mutation happen instantly upon python execution? 
   *Answer:* Instant python execution ensures that immediately calling a `TrafficFlow` animation in the very next script line will safely succeed.
3. **Mobjects State Registration:** Should `ScaleOutAction` also inject `new_child` into `scene.mobjects`? 
   *Answer:* Yes. Phase 3 relies on searching `scene.mobjects` to find the target object to pulse. If the newly spawned EC2 isn't appended to the mobjects list, `TrafficFlow` hitting the new child will fallback to pulsing abstract dots instead of flashing the instance.

---

## Self-Reflection & Execution Blueprint
Question 1 and 3 exposed critical orchestration flaws. The Cinematic action isn't just an animation; it's a full State Mutation wrapper. It must:
1. Append the new node to the cluster list.
2. Read the cluster's `.get_center()`.
3. Calculate the `.move_to(new_coord)`.
4. Run `OrthogonalRouter` between `new_child.get_center()` and `target.get_center()`.
5. Update `scene.rendered_edges`.
6. Update `scene.mobjects`.
7. Return `AnimationGroup(GrowFromCenter(node), Create(line))`.

**The Red Phase Strategy:**
Write an Pytest that creates a cluster with a database, calls `ScaleOutAction` to add a new `EC2`, and asserts that the `new_child` exists in `scene.mobjects` and the edge exists in `scene.rendered_edges`.
