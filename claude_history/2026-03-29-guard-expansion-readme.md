# Guard Lint Expansion + README Update

## Date
2026-03-29

## Summary
Expanded guard lint scope from tools-only to entire project, and updated README with current features.

## Changes

### Guard Lint Expansion
- **rules.yaml** — Added `scope: "project"` option to lint section. Supports `"project"` (all .py recursively) and `"tools"` (tools/ only, legacy).
- **checker.py `_check_lint`** — Updated file collection logic: `"project"` scope uses `project.rglob("*.py")`, `"tools"` scope uses `tool_dir.glob("*.py")`. Both skip `__init__.py`.
- **test_checker.py** — Added `TestLintScopeRules` class with 3 tests: project scope catches agent.py errors, skips __init__.py, tools scope ignores agent.py.
- **conftest.py** — Fixed fixture agent.py imports to be ruff-clean under project scope.
- **agent.py.tmpl** — Fixed import ordering and line length for ruff compliance.
- **models.py.tmpl** — Wrapped long Field() lines.
- **test_e2e_render.py** — Updated test_imports ordering and test_cases to use all imports.
- **render_agent.py** — Updated test_imports to match ruff's isolated-mode import grouping.

### README Update
- Added `models.py`, `http_client.py`, `skills/troubleshooting/runbooks/` to Generated Agent Structure tree
- Added "Run modes" section (interactive, --once, --diagnose)
- Added config source and lint rows to Guard Rules table
- Added `render_agent.py` and `ruff check` to Development section

## Verification
- 27 tests pass (24 original + 3 new lint scope tests)
- ruff lint clean
- url-shortener-ops-agent guard check passes
