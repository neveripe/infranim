# Finding 09: Incorrect ASSETS_DIR Path — Double "assets" Directory

## Location
[assets/aws.py](file:///Z:/never/vscode/manimani/manim_devops/assets/aws.py) — Line 6

## The Issue
This is likely a **live bug**. The assets directory path is:

```python
ASSETS_DIR = Path(__file__).parent / "assets" / "aws"
```

`Path(__file__).parent` resolves to `manim_devops/assets/` (since `aws.py` lives inside `manim_devops/assets/`).

So the full resolved path becomes:
```
manim_devops/assets/assets/aws/
```

Note the **double `assets`**. The intended path is almost certainly:
```
manim_devops/assets/aws/
```

Which means:
```python
ASSETS_DIR = Path(__file__).parent / "aws"
```

Let me verify:

```
manim_devops/
├── assets/
│   ├── __init__.py      # CloudNode base
│   ├── aws.py           # AWSNode (this file)
│   └── aws/             # Where SVGs should live (but currently listed as "assets/aws")
│       ├── Amazon-EC2.svg
│       └── ...
```

The current code tries to load SVGs from `manim_devops/assets/assets/aws/Amazon-EC2.svg`, which **does not exist**. This means every `AWSNode` construction hits the `except Exception` fallback and renders as an orange circle.

**Combined with Finding 03 (silent fallback), this bug is completely invisible.** The system works "fine" — it just never renders actual AWS icons.

## Proposed Change
```python
ASSETS_DIR = Path(__file__).parent / "aws"
```

And verify that the `aws/` subdirectory actually exists with SVG files. If it doesn't, creating the directory and downloading the official AWS Architecture Icons would complete the fix.

---

## 3 Questions

1. **Has ANY test or demo ever rendered an actual AWS SVG icon?** Given this path bug, the answer is almost certainly no. Every node in every video has been an orange circle.
2. **Does the `aws/` directory even exist?** It was listed in `list_dir` as a subdirectory of `assets/`, but we haven't verified it contains any `.svg` files.
3. **Should the path be configurable?** Users might want to use their own icon packs. A class-level `ASSETS_DIR` override or an environment variable would make this flexible.

## Self-Reflection
This is the bug that, combined with Finding 03, creates the most impact. It's a simple one-line typo — `"assets"` instead of nothing — but because the fallback is silent, it has persisted through 5 development phases, hundreds of test runs, and multiple demo video renderings without anyone noticing. This is a powerful argument for why silent fallbacks are dangerous.

## 5 Whys
1. **Why is the path wrong?** Likely a mental model error — the developer was thinking "I need the assets/aws directory" without considering that `__file__` already resolves inside the `assets/` directory.
2. **Why wasn't this caught?** Because the `except Exception` fallback silently replaces the icon with a circle, and the video still renders.
3. **Why didn't any test catch it?** Because `test_aws_assets.py` tests the *fallback mechanism itself*, not the *correct SVG loading path*. There's no test that asserts "an actual SVG was loaded."
4. **Why is this a systemic issue?** Because the testing philosophy validated the error-handling path but never the happy path.
5. **Why fix the path AND the fallback?** Because fixing only the path still leaves the system vulnerable to future file-not-found scenarios with no user feedback.
