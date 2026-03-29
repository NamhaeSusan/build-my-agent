# Add tests for project-wide lint scope

## What
Added `TestLintScopeRules` class to `tests/test_checker.py` with 3 tests:
1. `test_project_scope_catches_agent_py_lint_error` — expects ruff to catch F401 in agent.py (FAILS because _check_lint only scans tools/)
2. `test_project_scope_skips_init_files` — verifies __init__.py files are excluded from lint
3. `test_tools_scope_ignores_agent_py` — with lint.scope: "tools", agent.py errors are not reported

## Why
Preparation for expanding lint scope from tools-only to project-wide. Test 1 is intentionally red (TDD).
