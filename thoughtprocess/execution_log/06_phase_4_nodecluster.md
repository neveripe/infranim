# Phase 4 Execution Log

## Step 1: Implement NodeCluster (RED Phase)

### Intention
The global `NetworkX` spring layout shifts all nodes if a new node is added. To support Auto-Scaling without ruining the existing visualization, we need a Container abstraction: `NodeCluster`. 
A `NodeCluster` is treated as a single massive `CloudNode` by NetworkX. It computes its central `(X, Y, Z)` coordinate normally. 
However, it internally manages a list of child nodes (`EC2`, etc.). When we ask the cluster for child coordinates, it calculates them deterministically relative to its own center (e.g., using a basic grid or circular layout), fully bypassing NetworkX on the sub-graph level.

### Actions
1.  **Red Phase:** Write Pytest `test_dynamic_cluster_calculates_relative_child_coordinates_IMMUTABLE`. Instantiate a `NodeCluster`, add it to a standard `Topology` alongside an `RDS` node. Assert layout calculations yield predictable, non-shifting offset coordinates for the cluster's internal children while preserving the overall NetworkX layout seed.
2.  **Green Phase:** Implement `NodeCluster` in `manim_devops/core.py`. Add `children` array and `get_child_coordinates(center_coord)` offset math.
3.  **Refactor (Coverage):** Ensure 100% test coverage. Update `Topology` to recursively return all nested children coordinates so the router can find them.

### Outcome
*(Pending execution)*
