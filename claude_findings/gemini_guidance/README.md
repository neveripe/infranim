# Gemini Guidance: Master Index

## Recommended Execution Order

Execute fixes in this order to minimize merge conflicts and maximize test stability:

| Order | Fix | File(s) Modified | Risk | Dependencies |
|-------|-----|-------------------|------|-------------|
| 1 | [Fix 09 — Assets Path](fix_09_assets_dir_path.md) | `assets/aws.py` | 🔴 Critical bug | None |
| 2 | [Fix 03 — SVG Logging](fix_03_silent_svg_fallback.md) | `assets/aws.py` | High | After Fix 09 |
| 3 | [Fix 01 — DRY Operators](fix_01_operator_duplication.md) | `assets/__init__.py` | Low | None |
| 4 | [Fix 05 — Constants](fix_05_magic_numbers.md) | New `constants.py` + 4 files | Low | None |
| 5 | [Fix 02 — Data Structures](fix_02_linear_lookups.md) | `core.py` | Low | After Fix 05 |
| 6 | [Fix 04 — Split-Brain](fix_04_split_brain_state.md) | `core.py`, `cinematics.py` | High | After Fix 02 |
| 7 | [Fix 07 — Thread Safety](fix_07_thread_safety.md) | `adapter.py`, `assets/__init__.py` | Low | After Fix 01 |
| 8 | [Fix 06 — Liskov](fix_06_liskov_substitution.md) | `assets/__init__.py`, `core.py` | Medium | After all others |
| 9 | [Fix 08 — Fixtures](fix_08_conftest_fixture.md) | `conftest.py` | Low | After Fix 06 |

## Global Rules for Gemini

1. **Run `python -m pytest tests/ -v` after EVERY fix.** All 25+ tests must pass.
2. **Do NOT modify any test marked `_IMMUTABLE` without asking the user first.**
3. **Commit each fix separately** with a descriptive commit message.
4. **If a fix requires modifying tests**, ask the user for explicit permission before proceeding.
5. **Read the corresponding `claude_findings/XX_*.md` analysis document** before starting each fix to understand the full reasoning.
