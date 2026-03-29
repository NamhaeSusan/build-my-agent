# Expand guard lint scope to entire project

## What
- Added `scope: "project"` option to `guard/rules.yaml` lint section
- Updated `_check_lint` in `guard/checker.py` to collect `.py` files based on scope:
  - `"project"` (default): all `.py` files recursively via `rglob`
  - `"tools"`: only `tools/*.py` (previous behavior)
- Added `--output-format concise` to ruff command for consistent single-line output

## Why
Previously guard only linted `tools/*.py`. Project-wide linting catches issues in `agent.py`, `models.py`, test files, etc.

## Test status
- 3 new `TestLintScopeRules` tests: 2 pass, 1 blocked by fixture issue (Task 3)
- Several existing tests fail because fixture `agent.py` has I001 lint errors under project scope (Task 3 fix)
