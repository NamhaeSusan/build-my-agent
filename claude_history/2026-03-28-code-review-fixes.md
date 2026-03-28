# Code Review Fixes

## Date
2026-03-28

## Summary
Comprehensive code review of the entire project, fixing 8 critical/high issues.

## Changes

### Critical Fixes
1. **agent.py.tmpl:56** — Fixed brace escaping bug. `{{{{component_name}}}}` was rendering as literal `{component_name}` at runtime. Changed to plain string `"{{component_name}}"` (no f-string needed since template substitution happens at generation time).

2. **agent.yaml.tmpl** — Quoted all endpoint values in YAML. Unquoted URLs with colons (e.g., `http://host:9200`) would break YAML parsing.

3. **metric_query.py.tmpl** — Removed invalid `disable_ssl` parameter from `PrometheusConnect`. `prometheus-api-client>=0.5.0` does not have this parameter.

### High Fixes
4. **checker.py** — `_check_lint` was hardcoding `project / "tools"` instead of using `structure.get("tool_dir", "tools")`. Updated function signature to accept `structure` dict and use it consistently with other checkers.

5. **test_e2e_render.py** — Changed `ast.walk` to `ast.iter_child_nodes` in public function count test, matching checker.py behavior (module-level functions only).

6. **pyproject.toml** — Fixed ruff `target-version` from `py310` to `py311` to match `requires-python = ">=3.11"`.

7. **tools/__init__.py** — Added missing `http_request` export from `tools.http_client`.

8. **agent.py.tmpl** — Changed `run_once` to use `uuid.uuid4()` for `thread_id` instead of hardcoded `"once"`, preventing message bleed across invocations.

### Test Update
- Removed now-unnecessary `{{{{component_name}}}}` pre-processing in `_render()` since the template no longer uses escaped braces.

### Round 2 Fixes
9. **tools/prometheus.py** — Same `disable_ssl` bug as template; removed invalid parameter from reference implementation.

10. **tools/opensearch.py** — Added missing KeyError guard for `opensearch` config section (was bare `_config["opensearch"]`, now matches http_client.py pattern).

11. **tools/prometheus.py** — Added missing KeyError guard for `prometheus` config section.

12. **checker.py `_check_naming`** — Changed `ast.walk` to `ast.iter_child_nodes` for function naming check. Previously caught nested functions incorrectly; now consistent with `_check_patterns`.

13. **checker.py `_check_lint`** — Now reports `result.stderr` as a violation instead of silently discarding ruff internal errors.

14. **test_cli.py** — Changed `assert result.returncode != 0` to `== 2` for no-command test, distinguishing argparse usage error from guard failure.

### Round 3 Fixes
15. **test_e2e_render.py `_render`** — Now raises `KeyError` on unknown template placeholders instead of silently passing them through, catching template/sample value mismatches.

16. **checker.py `_check_lint`** — Added `--isolated` flag to ruff invocation to prevent config discovery from parent directories or generated projects from interfering with guard's own ruff_select/ruff_ignore settings.

17. **models.py.tmpl** — Changed `severity: str` to `severity: Literal["critical", "warning", "info"]` to enforce the documented allowed values via Pydantic validation.

### Round 4 Fixes
18. **agent.py.tmpl `create_agent`** — `Path("prompts/system.md")` used CWD-relative path. If the agent is executed from a different directory, the file won't be found. Reordered to define `project_root` first and use `project_root / "prompts" / "system.md"`.

19. **pyproject.toml.tmpl** — Added missing `[build-system]` section (`hatchling`). Without it, `pip install -e '.[dev]'` may fail on some setups.

## Verification
- All 24 tests pass
- ruff lint clean
