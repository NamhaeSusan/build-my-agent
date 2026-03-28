# Align templates with deepagents API

## Date
2026-03-28

## Summary
Updated all template and reference tool files to match the actual deepagents API from docs.langchain.com.

## Changes

### 1. Remove config_path from tool signatures
- **templates/tools/log_search.py.tmpl**: Config loaded at module level via `_CONFIG_PATH`
- **templates/tools/metric_query.py.tmpl**: Same pattern
- **tools/opensearch.py**: Lazy config loading via `_get_os_config()`
- **tools/prometheus.py**: Lazy config loading via `_get_prom_config()`
- **Why**: LLM sees function parameters as tool arguments. `config_path` should not be exposed.

### 2. Interactive loop + --once flag (agent.py.tmpl)
- Default: interactive chat loop with `you>` / `agent>` prompts
- `--once "query"`: single invocation mode
- Added `MemorySaver` checkpointer for conversation persistence

### 3. Middleware (agent.py.tmpl)
- Added `SummarizationMiddleware` to compress long conversation history

### 4. Structured output (models.py.tmpl + agent.py.tmpl)
- New `DiagnosisReport` pydantic model (summary, severity, evidence, root_cause, recommendation)
- `--diagnose` flag enables structured output via `response_format`

### 5. Fix requires-python (pyproject.toml.tmpl)
- Changed from `>=3.11` to `>=3.10` to match CLAUDE.md
- Added `langgraph` and `pydantic` to dependencies

### Code review fixes
- Template tools: changed module-level config loading to lazy `_get_*_config()` pattern (matches reference tools)
- Added missing key validation with clear error messages
- `--diagnose` without `--once` now rejected with `parser.error()`
- `structured_response` key access guarded with `.get()` + RuntimeError
- Interactive `thread_id` changed from hardcoded string to `uuid.uuid4()`

## Tests
- All 17 guard tests pass
