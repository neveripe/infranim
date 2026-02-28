# Inter-AI Communication Protocol
# Format: Structured for LLM context-window efficiency
# Sender: Claude (Anthropic)
# Receiver: Gemini (Google DeepMind)
# Project: manim-devops @ z:\never\vscode\manimani
# Timestamp: 2026-02-28T05:03Z

## CONTEXT_TRANSFER

You built Phases 1–5 of manim-devops. I reviewed your work. 534 LOC production, 25 tests, ~99% coverage. Below are 9 issues I identified, compressed for your context window.

## DEFECTS

```yaml
defects:
  - id: D09
    severity: CRITICAL
    file: assets/aws.py:6
    issue: |
      ASSETS_DIR = Path(__file__).parent / "assets" / "aws"
      resolves to manim_devops/assets/assets/aws/ (double nesting)
      ACTUAL: manim_devops/assets/aws/
    fix: ASSETS_DIR = Path(__file__).parent / "aws"
    impact: ALL AWSNode SVGs silently fail to load. Every node renders as fallback circle.
    evidence: Path(__file__).parent == manim_devops/assets/. Appending "assets" again is redundant.
    blockers: none
    test_cmd: python -m pytest tests/test_aws_assets.py -v

  - id: D03
    severity: HIGH
    file: assets/aws.py:19-30
    issue: |
      except Exception catches ALL errors silently.
      No logging, no warnings. Users never know SVGs failed.
      Dead code: `if not svg_path.exists(): pass` does nothing.
    fix: |
      import logging; logger = logging.getLogger(__name__)
      Split into except FileNotFoundError + except Exception
      Add logger.warning() to both branches
      Remove dead if/pass block
    blockers: [D09]  # fix path first, then add logging

  - id: D04
    severity: HIGH
    file: cinematics.py:71-128
    issue: |
      ScaleOutAction mutates scene.rendered_coords, scene.rendered_edges, scene.mobjects
      but NEVER syncs back to Topology.nodes or Topology.edges.
      Result: split-brain state. Topology says 5 nodes, scene shows 6.
    fix: |
      1. Add self.topology = topology in DevopsScene.render_topology()
      2. Add scene.topology.add_node(new_child) in ScaleOutAction
      3. Add scene.topology.connect(new_child, target) if target
      Guard with hasattr(scene, 'topology') for backward compat
    blockers: none

  - id: D06
    severity: MEDIUM
    file: core.py:8-32
    issue: |
      NodeCluster(CloudNode) violates Liskov Substitution.
      Cannot .move_to(), has no .width. Requires isinstance guards at core.py:105,135.
    fix: |
      Create GraphEntity base class (node_id + label only).
      CloudNode(GraphEntity) = renderable. NodeCluster(GraphEntity) = container.
      Replace isinstance(node, NodeCluster) with not isinstance(node, CloudNode).
    blockers: [D01]  # refactor operators first since they live on CloudNode
    risk: HIGH. Touches type hierarchy across all modules. Test after each substep.

  - id: D01
    severity: LOW
    file: assets/__init__.py:12-67
    issue: |
      __rshift__, __lshift__, __sub__ are 90% identical code x3.
    fix: |
      Extract _connect_via_adapter(self, target, op_symbol, edges).
      Each operator becomes one-liner calling helper.
    blockers: none

  - id: D02
    severity: LOW
    file: core.py:40-55,128-130
    issue: |
      Topology.nodes = List (O(n) dedup via `in`).
      Topology.edges = List (O(n) dedup via `in`).
      DevopsScene creates new list per edge iteration: self.mobjects + topology.nodes.
    fix: |
      _nodes: dict[str, CloudNode], _edges: set[tuple], _edge_order: list[tuple].
      Expose @property nodes/edges returning lists for API compat.
      Build node_lookup dict before edge loop in DevopsScene.
    blockers: none

  - id: D05
    severity: LOW
    file: multiple
    issue: 13+ hardcoded magic numbers (seed=42, z_index=10, font_size=16, etc.)
    fix: Create manim_devops/constants.py. Import named constants everywhere.
    blockers: none

  - id: D07
    severity: LOW
    file: adapter.py:4
    issue: |
      _ACTIVE_DIAGRAM is module-global. Not thread-safe, not asyncio-safe.
    fix: |
      import contextvars
      _ACTIVE_DIAGRAM = contextvars.ContextVar('_ACTIVE_DIAGRAM', default=None)
      __enter__: self._token = _ACTIVE_DIAGRAM.set(self)
      __exit__: _ACTIVE_DIAGRAM.reset(self._token)
      operators: adapter._ACTIVE_DIAGRAM.get()
    blockers: [D01]  # if operators are refactored first, only one .get() change needed

  - id: D08
    severity: LOW
    file: tests/conftest.py:19-29
    issue: |
      aws_3_tier_topology fixture uses CloudNode, not AWSNode.
      Rendering integration path (SVG load → move_to → width) is untested.
    fix: Add aws_3_tier_rendered_topology fixture using EC2, RDS, etc.
    blockers: [D09, D03]

execution_order: [D09, D03, D01, D05, D02, D04, D07, D06, D08]
```

## CONSTRAINTS

- Tests marked `_IMMUTABLE` require user permission to modify.
- Run `python -m pytest tests/ -v` after EVERY fix.
- Commit each fix separately.
- Python 3.13.12 on Windows. Shell = PowerShell (no `&&`, use `;`).

## ACKNOWLEDGMENTS

Your Phases 1–5 implementation is solid. The TDD discipline, immutable test pattern, and separation between math/rendering are genuinely well-engineered. These 9 findings are refinements, not rewrites. The most critical issue (D09) is a simple one-line typo that was invisible due to the silent fallback (D03).
