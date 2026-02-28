# Gemini Guidance: Fix 09 — Correct the ASSETS_DIR Path

## Context
`ASSETS_DIR` in `aws.py` resolves to `manim_devops/assets/assets/aws/` (double "assets") instead of `manim_devops/assets/aws/`. This means SVGs are NEVER loaded, and all nodes silently fall back to orange circles. See `claude_findings/09_incorrect_assets_dir_path.md`.

## Priority: 🔴 CRITICAL (Live Bug)

## Strict Instructions

### Step 1: Verify the Bug

Run this in a Python shell or temporary script to confirm the incorrect path:

```python
from pathlib import Path
import manim_devops.assets.aws as aws_module

print(f"aws.py location: {Path(aws_module.__file__).parent}")
print(f"ASSETS_DIR resolves to: {aws_module.ASSETS_DIR}")
print(f"ASSETS_DIR exists: {aws_module.ASSETS_DIR.exists()}")
```

Expected output:
```
aws.py location: Z:\...\manim_devops\assets
ASSETS_DIR resolves to: Z:\...\manim_devops\assets\assets\aws
ASSETS_DIR exists: False
```

### Step 2: Fix the Path

In `manim_devops/assets/aws.py`, line 6, change:

```python
# BEFORE:
ASSETS_DIR = Path(__file__).parent / "assets" / "aws"

# AFTER:
ASSETS_DIR = Path(__file__).parent / "aws"
```

**Explanation:** `Path(__file__).parent` already resolves to `manim_devops/assets/`. Adding `"assets"` again creates a double nesting.

### Step 3: Verify the Directory Exists

Check if `manim_devops/assets/aws/` actually exists and contains SVG files:

```bash
dir Z:\never\vscode\manimani\manim_devops\assets\aws\
```

If the directory does NOT exist or is empty, create it:

```bash
mkdir Z:\never\vscode\manimani\manim_devops\assets\aws
```

And note in the commit message that SVG files still need to be downloaded from the [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/) package.

### Step 4: Run Tests
```bash
python -m pytest tests/test_aws_assets.py -v
```

The existing fallback test should still pass (since SVGs likely aren't present yet). But now the **path is correct**, so once SVGs are added, they'll actually load.

### Step 5: Verify the Fix

Run the same verification from Step 1:

```python
from pathlib import Path
import manim_devops.assets.aws as aws_module

print(f"ASSETS_DIR resolves to: {aws_module.ASSETS_DIR}")
print(f"ASSETS_DIR exists: {aws_module.ASSETS_DIR.exists()}")
```

Expected output after fix:
```
ASSETS_DIR resolves to: Z:\...\manim_devops\assets\aws
ASSETS_DIR exists: True  (if directory was created)
```

### Step 6: Run Full Test Suite
```bash
python -m pytest tests/ -v
```

All tests must pass.

## What NOT To Do
- Do NOT change the SVG filenames (e.g., `"Amazon-EC2.svg"`). They match AWS's official naming.
- Do NOT remove the fallback mechanism. Until real SVGs are bundled, the fallback is still needed.
- Do NOT hardcode an absolute path. The relative `Path(__file__).parent / "aws"` pattern is correct.
- Do NOT modify any test without asking the user first.

## Commit Message Suggestion
```
fix(assets): correct ASSETS_DIR path — remove duplicate 'assets' directory

ASSETS_DIR resolved to manim_devops/assets/assets/aws/ (double 'assets')
instead of manim_devops/assets/aws/. This caused every AWSNode to silently
fall back to a generic circle because SVG files were never found at the
incorrect path.
```
