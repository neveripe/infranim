# Finding 02: O(n) Linear Lookups Where O(1) Dicts Should Be Used

## Location
[core.py](file:///Z:/never/vscode/manimani/manim_devops/core.py) — Lines 44–55 (Topology) and Lines 128–130 (DevopsScene)

## The Issue
Both `Topology` and `DevopsScene` use **linear lists** for data that is primarily accessed by key lookup:

**Problem 1 — `Topology.nodes` is a `List`, searched by identity:**
```python
self.nodes: List[CloudNode] = []

def add_node(self, node: CloudNode) -> None:
    if node not in self.nodes:      # O(n) scan every time
        self.nodes.append(node)
```

**Problem 2 — `Topology.edges` is a `List`, searched by tuple:**
```python
self.edges: List[tuple[str, str]] = []

def connect(self, source, target) -> None:
    edge = (source.node_id, target.node_id)
    if edge not in self.edges:      # O(n) scan every time
        self.edges.append(edge)
```

**Problem 3 — `DevopsScene` does linear scans to find nodes for edge rendering:**
```python
src_node = next(n for n in self.mobjects + topology.nodes if n.node_id == src_id)
```
This is O(n) per edge and also **creates a new concatenated list** on every iteration.

## Proposed Change

For `Topology`:
```python
class Topology:
    def __init__(self, scale_factor: float = 3.0):
        self._nodes: dict[str, CloudNode] = {}   # keyed by node_id
        self._edges: set[tuple[str, str]] = set()
        self.scale_factor = scale_factor

    @property
    def nodes(self) -> list[CloudNode]:
        return list(self._nodes.values())

    @property
    def edges(self) -> list[tuple[str, str]]:
        return list(self._edges)

    def add_node(self, node: CloudNode) -> None:
        self._nodes.setdefault(node.node_id, node)  # O(1)

    def connect(self, source, target) -> None:
        self._edges.add((source.node_id, target.node_id))  # O(1)
```

For `DevopsScene`, build a lookup dict once:
```python
node_lookup = {n.node_id: n for n in self.mobjects}
# ...
src_node = node_lookup.get(src_id) or next(n for n in topology.nodes if n.node_id == src_id)
```

---

## 4 Questions

1. **Does changing `nodes` from a list to a dict break insertion order?** In Python 3.7+, `dict` preserves insertion order, so `list(self._nodes.values())` maintains the same sequence. However, `NetworkX.spring_layout` with `seed=42` should still produce identical results regardless.
2. **Does changing `edges` from a list to a set change behavior?** Sets are unordered. If the order in which edges are drawn visually matters (e.g., Z-index layering), this could cause subtle rendering differences.
3. **How bad is the current performance?** For 5-node demos, it's unnoticeable. For a 100-node EKS cluster with 300 edges, `add_node` calls `if node not in self.nodes` (O(n)) up to 600 times via the `>>` operator (once per `add_node(self)` + `add_node(target)` per edge).
4. **Would the `@property` interface break existing tests?** Tests assert `len(diag.topology.edges)` and `("web", "db") in diag.topology.edges`. The property returns a list, so `len()` works, and `in` checks work on lists. No test changes needed.

## Self-Reflection
This is a classic case of choosing the wrong data structure early and never revisiting it. Lists are intuitive for small-scale iteration, but deduplication via `if x not in list` is O(n) while `set.add()` is O(1). The Topology module was designed during the "prove it works" spike phase where performance was irrelevant. Now that the library is functional, optimizing data structures is the correct next step.

## 5 Whys
1. **Why are lists used instead of dicts/sets?** Because the initial TDD Red Phase tests simply checked `len(topology.nodes) == 5`, and lists satisfied that ASAP.
2. **Why wasn't this caught during the coverage phase?** Because coverage tools measure *line execution*, not *algorithmic complexity*.
3. **Why does it matter beyond 100 nodes?** Because the `>>` operator calls `add_node` twice per invocation. A 50-edge graph means 100 `add_node` calls, each scanning the full list.
4. **Why does the list concatenation in `DevopsScene` matter?** Because `self.mobjects + topology.nodes` creates a brand-new list object per loop iteration, generating garbage for the Python GC.
5. **Why use `@property` instead of replacing the public attribute?** Because existing test code and the `conftest.py` fixture directly access `topo.nodes` and `topo.edges`. A property preserves the public API while changing the internal representation.
