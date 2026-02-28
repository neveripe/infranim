# Coverage Strategy: AWS Asset Fallbacks (aws.py)

## Explanation
The coverage report flagged `manim_devops/assets/aws.py` at 53%. The logic we built during Phase 2 implemented a safety fallback: if it tries to load a branded SVG (like `Amazon-EC2.svg`) but the file hasn't been downloaded or sanitized yet, it falls back to rendering a generic orange `Circle()` in Manim. Because the `test_final_integration.py` script ran natively via Manim, Pytest missed covering this fallback. To achieve 100% coverage, we must write a native pytest suite that explicitly instantiates these AWS models without the engine crashing, proving the fallback logic executes safely.

---

## The 3 Why's (Validating the Test Necessity)

1. **Why does this fallback logic exist?**
   In a production setup, if an SVG is missing, the engine should raise a hard `FileNotFoundError`. But during this PoC, we wanted to prove the layout math quickly without downloading hundreds of SVGs. The fallback allows the engine to draw a circle so the user can see the layout math working even if the icon is physically missing.
2. **Why didn't Pytest cover it earlier?**
   Because we didn't write a unit test for `test_aws_assets.py`. The only script instantiating `EC2` and `RDS` objects was the Manim Visual Integration script (`test_final_integration.py`), which executes in a completely separate CLI process `manim -ql ...`. Thus, the Pytest coverage tracker couldn't see the code executing.
3. **Why make these instantiation tests Immutable?**
   Because the syntax of the constructor (e.g., `EC2("node_id", "Label")`) is the public, outward-facing API. By locking these tests in as Immutable, we guarantee that future refactoring doesn't break the user's ability to easily instantiate AWS nodes with a simple two-argument constructor.

---

## 3 Deep Technical Questions (Asset Safeties)

1. **Silent Fallbacks vs Logging:** Currently, the engine falls back to a Circle completely silently. If a user expects an EC2 icon and gets an orange circle, shouldn't the library at least emit an explicit python `logging.warning()` so they know *why* the icon didn't load?
2. **Path Resolution Dependencies:** `aws.py` uses `__file__` to calculate the relative path to the `/aws/` folder. What happens if this package is installed via a zip file or wheel where `__file__` behaves differently? 
3. **SVG Parser Isolation:** Should the `try/except` block catching Manim's XML parser crash be decoupled entirely from the file-loading logic? Currently, a missing file and a corrupt file trigger the exact same Orange Circle fallback.

---

## Self-Reflection
By viewing the missing coverage, I realize the "pass" block on `if not path.exists()` is technically redundant if we are immediately doing a blanket `try/except` on the `SVGMobject` instantiation anyway. 
However, for the scope of reaching 100% coverage on the MVP logic, we will write a generic Pytest file that instantiates `EC2`, `RDS`, `Route53`, `ALB`, and `IGW`. We will assert that they successfully inherit from both `CloudNode` and `VMobject` (meaning Manim loaded them), and we will assert that their IDs and Labels were set properly. This will execute the entire module natively inside Pytest.
