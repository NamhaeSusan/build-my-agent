# E2E Render Tests + Guard Checker Fixes

## Date
2026-03-28

## Summary
Added E2E tests that render all templates with sample values and verify the generated project passes guard. Fixed two guard checker bugs discovered during testing.

## Changes

### New: tests/test_e2e_render.py
- `test_rendered_project_passes_guard`: Core guarantee — templates + sample values → guard passes
- `test_rendered_tool_files_have_one_public_function`: AST check on rendered tools
- `test_rendered_config_has_all_sections`: Verify opensearch/prometheus/http config sections
- `test_rendered_agent_py_is_valid_python`: Syntax validation of rendered agent.py

### Fixed: guard/checker.py
1. **Docstring URL false positives**: URL check now skips docstrings (which may contain example URLs like in http_client.py)
2. **Config source path detection**: Now accepts both literal string `"config/agent.yaml"` and Path component style (`"config"` + `"agent.yaml"` as separate strings), supporting the lazy `_get_*_config()` pattern

## Tests
- 22 tests pass (18 existing + 4 new E2E)
