# Skill Update + HTTP Client Tool

## Date
2026-03-28

## Summary

Two changes:
1. Update skills 02/03/04 to reflect new template structure (middleware, checkpointer, --once/--diagnose, lazy config, models.py)
2. Add a general-purpose HTTP client tool as a reference implementation + template

## HTTP Client Tool

### Purpose
A generic HTTP request tool that users can include when they want to add HTTP-based actions to their agent (e.g., trigger deploys, call internal APIs, check health endpoints). It is NOT auto-suggested during analysis — users explicitly choose to add it.

### Reference implementation: `tools/http_client.py`

```python
def http_request(
    url: str,
    method: str = "GET",
    headers: dict | None = None,
    body: str | None = None,
    timeout: int = 10,
) -> dict:
```

- Uses stdlib `urllib.request` — no external dependency needed
- Config: `http.base_urls` map for aliased endpoints, `http.default_timeout`
- Returns: `{"status_code": int, "headers": dict, "body": str, "elapsed_ms": float}`
- Lazy config loading via `_get_http_config()` (same pattern as other tools)

### Template: `templates/tools/http_client.py.tmpl`
Same structure as reference, with `{{component_name}}` placeholder in docstring.

### Config addition: `config/agent.yaml.tmpl`
```yaml
http:
  base_urls:
    self: "{{self_endpoint}}"
  default_timeout: 10
```

This section is **optional** — only included when user adds http_client tool.

## Skill Updates

### 02-design-agent
- No change to auto-suggest logic. http_request is NOT auto-suggested.

### 03-generate-agent
- Update config loading guidance: `_load_config()` → `_get_*_config()` lazy pattern
- Add `models.py` to project structure and generation steps
- Update agent.py guidance: mention middleware, checkpointer, --once, --diagnose
- Add note: "For custom HTTP-based tools, reference `tools/http_client.py` pattern"

### 04-validate-structure
- Update quick-start to include `--once` and `--diagnose` usage
- Add `models.py` to project structure listing

### guard/rules.yaml
- No change. `models.py` is not in `tools/` so guard doesn't check it.

## Not Changed
- 00-create-ops-agent: orchestration unchanged
- 01-analyze-codebase: already detects external APIs; no new auto-suggest
- guard/checker.py: no new rules needed
