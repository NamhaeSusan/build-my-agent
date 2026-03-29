# Pytest Collection Scope Fix

## Date
2026-03-29

## Summary
Restricted root pytest discovery to `tests/` and added a regression test for collection scope.

## Changes
- Added a regression test covering root `pytest --collect-only` behavior with a transient generated project
- Added `[tool.pytest.ini_options]` with `testpaths = ["tests"]` to `pyproject.toml`
- Verified both `python3 -m pytest -q` and `python3 -m pytest tests -q`
