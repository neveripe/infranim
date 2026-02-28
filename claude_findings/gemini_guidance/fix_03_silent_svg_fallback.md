# Gemini Guidance: Fix 03 — Replace Silent SVG Fallback with Logging

## Context
`AWSNode.__init__` in `manim_devops/assets/aws.py` catches all exceptions silently during SVG loading and falls back to an orange circle with zero user feedback. See `claude_findings/03_silent_svg_fallback.md`.

## Priority: High (User Experience)

## Strict Instructions

### Step 1: Add Logging to `aws.py`

At the top of `manim_devops/assets/aws.py`, add:

```python
import logging
logger = logging.getLogger(__name__)
```

### Step 2: Replace the `AWSNode.__init__` Constructor

Replace the current constructor (lines 13–30) with:

```python
class AWSNode(CloudNode, SVGMobject):
    """
    The provider-specific generic base.
    Inherits Math properties from CloudNode, and Render properties from SVGMobject.
    """
    def __init__(self, node_id: str, label: str, svg_filename: str):
        # 1. Initialize Math Tracker
        CloudNode.__init__(self, node_id, label)
        
        # 2. Initialize Visual Renderer
        svg_path = ASSETS_DIR / svg_filename
        
        try:
            SVGMobject.__init__(self, str(svg_path))
        except FileNotFoundError:
            logger.warning(
                "SVG asset '%s' not found at %s. Using fallback circle for '%s'.",
                svg_filename, svg_path, node_id
            )
            self._apply_fallback()
        except Exception as e:
            logger.warning(
                "Failed to parse SVG '%s': %s. Using fallback circle for '%s'.",
                svg_filename, e, node_id
            )
            self._apply_fallback()

    def _apply_fallback(self):
        """Replaces this node's geometry with a generic colored circle."""
        from manim import Circle
        self.become(Circle(radius=0.5, color="#FF9900", fill_opacity=0.2))
```

**Key changes:**
1. Removed the dead `if not svg_path.exists(): pass` block entirely.
2. Split `except Exception` into `except FileNotFoundError` + `except Exception`.
3. Added `logger.warning()` calls to BOTH exception branches.
4. Extracted the `Circle` fallback into `_apply_fallback()` to reduce duplication.

### Step 3: Update the Existing Test

> **IMPORTANT:** Before modifying the test, ask the user for permission. The test `test_aws_node_fallback_instantiation_IMMUTABLE` is marked IMMUTABLE.

If the user grants permission to amend the test, add a new test (do NOT modify the existing one) that verifies the warning is logged:

```python
def test_aws_node_logs_warning_on_svg_fallback():
    """Asserts that a warning is logged when SVG fallback triggers."""
    import logging
    from manim_devops.assets.aws import EC2
    
    with pytest.raises(Exception):
        # This should NOT raise, but we're testing the log output.
        pass
    
    # Better approach: use caplog fixture
    # def test_aws_node_logs_warning_on_svg_fallback(caplog):
    #     with caplog.at_level(logging.WARNING):
    #         ec2 = EC2("test", "Test")
    #     assert "fallback circle" in caplog.text
```

Actually, the cleanest approach is:

```python
def test_aws_node_logs_warning_on_svg_fallback(caplog):
    """Asserts that SVG fallback triggers a visible warning."""
    import logging
    from manim_devops.assets.aws import EC2
    
    with caplog.at_level(logging.WARNING, logger="manim_devops.assets.aws"):
        ec2 = EC2("test_warn", "Test Warning")
    
    assert "fallback circle" in caplog.text
    assert "test_warn" in caplog.text
```

### Step 4: Run Tests
```bash
python -m pytest tests/test_aws_assets.py -v
```

### Step 5: Verify Manual Output
Run any visual integration test and observe that the console now shows warning messages like:
```
WARNING:manim_devops.assets.aws:SVG asset 'Amazon-EC2.svg' not found at .../assets/aws/Amazon-EC2.svg. Using fallback circle for 'web1'.
```

## What NOT To Do
- Do NOT remove the fallback mechanism itself. It must still work for PoC mode.
- Do NOT change `except Exception` to `except (FileNotFoundError, XMLSyntaxError)` — Manim may throw various SVG parsing exceptions that we can't enumerate.
- Do NOT modify the existing `_IMMUTABLE` test without asking the user.
