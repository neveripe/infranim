# manim-devops

Animate your cloud infrastructure as code. Converts architecture topologies into cinematic [Manim](https://www.manim.community/) videos.

## What It Does

```
Your AWS Architecture  ──→  manim-devops  ──→  Animated MP4 Video
   (Python code)            (this library)      (with traffic flows,
                                                 scaling animations,
                                                 orthogonal routing)
```

## Quickstart

```bash
pip install -e ".[dev]"
```

### Option A: `diagrams`-Style Syntax

If you've used the [diagrams](https://diagrams.mingrammer.com/) library, this will feel familiar:

```python
from manim_devops.adapter import AnimatedDiagram
from manim_devops.assets.aws import EC2, RDS, ALB

with AnimatedDiagram("Web App"):
    alb = ALB("alb", "Load Balancer")
    web = EC2("web", "Web Server")
    db = RDS("db", "Database")

    alb >> web >> db
```

This generates an MP4 in `./media/`.

### Option B: Programmatic API

For full control over cinematics:

```python
from manim_devops.core import Topology, DevopsScene
from manim_devops.assets.aws import EC2, RDS
from manim_devops.cinematics import TrafficFlow

class MyScene(DevopsScene):
    def construct(self):
        topo = Topology()
        web = EC2("web", "Web Server")
        db = RDS("db", "Database")
        topo.add_nodes([web, db])
        topo.connect(web, db)

        self.render_topology(topo)
        self.play(TrafficFlow(self, web, db))
```

```bash
manim -pql my_scene.py MyScene
```

## Features

| Feature | Status |
|---------|--------|
| Graph → Manim coordinate mapping | ✅ |
| Orthogonal L-bend edge routing | ✅ |
| `>>`, `<<`, `-` operator syntax | ✅ |
| `AnimatedDiagram` context manager | ✅ |
| TrafficFlow animation | ✅ |
| ScaleOutAction (dynamic node spawning) | ✅ |
| NodeCluster (logical grouping) | ✅ |
| AWS provider icons (EC2, RDS, ALB, Route53, IGW) | ✅ |
| Multi-provider support (GCP, Azure) | ❌ Planned |
| Terraform/CloudFormation ingestion | ❌ Planned |

## Running Tests

```bash
pytest tests/ -v
```

## Architecture

```
manim_devops/
├── core.py          # Topology, NodeCluster, DevopsScene
├── layout.py        # OrthogonalRouter (L-bend pathfinding)
├── cinematics.py    # TrafficFlow, ScaleOutAction animations
├── adapter.py       # AnimatedDiagram (diagrams-style API)
├── constants.py     # Central configuration constants
└── assets/
    ├── __init__.py  # GraphEntity, CloudNode base classes
    ├── aws.py       # EC2, RDS, ALB, Route53, IGW
    └── aws/         # Bundled SVG icons
```

## Authorship

This project was written entirely by AI — **Google Gemini** (architecture &amp; implementation) and **Anthropic Claude** (code review &amp; refactoring) — with human guidance. The code has not been formally reviewed by a human engineer. See [DEVELOPMENT.md](DEVELOPMENT.md) for details.

## License

BSD 2-Clause — see [LICENSE](LICENSE).
