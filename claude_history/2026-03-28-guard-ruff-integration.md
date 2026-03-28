# Guard Ruff Integration

## Date
2026-03-28

## Summary
Integrated ruff lint into guard checker so `python -m guard check <path>` runs both structure validation and ruff lint on tool files.

## Changes

### guard/checker.py
- Added `_check_lint()` function that runs ruff on tool files via subprocess
- Scoped to `tools/*.py` only (excludes `__init__.py`, tests, agent.py)
- Configurable via rules.yaml: `lint.ruff`, `lint.ruff_select`, `lint.ruff_ignore`
- Handles ruff not installed gracefully

### guard/rules.yaml
- Added `lint` section: `ruff: true`, `ruff_select: "E,F,I"`, `ruff_ignore: ""`

### tests/conftest.py
- Updated fixture tool code to be ruff-clean (no unused variables, proper spacing)

### tests/test_checker.py
- Added `TestLintRules` class with 2 tests: valid passes, unused import caught
- Updated inline tool stubs to be ruff-clean

## Tests
- 24 tests pass, ruff clean
