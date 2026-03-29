# Fix conftest fixture and templates for project-scope lint

## What
Fixed test fixtures and templates so all `.py` files pass ruff `--isolated --select E,F,I`.

## Changes
- `tests/conftest.py`: Fixed `agent.py` fixture — added blank line between import groups and sorted imported names alphabetically (`query_metrics, search_logs`)
- `templates/agent.py.tmpl`: Added blank line before `from tools import` (ruff I001) and wrapped long `--diagnose` argument line (E501)
- `templates/models.py.tmpl`: Wrapped long Field() lines to stay under 88 chars (E501)
- `tests/test_e2e_render.py`: Fixed `test_imports` ordering to match ruff's isort expectations under `--isolated`, added usage of all imported symbols to avoid F401

## Notes
- ruff 0.15.8 under `--isolated` separates `from tools.http_client` into its own import group, distinct from `from tools.log_search` / `from tools.metric_query` — likely a heuristic in ruff's module classification
- All 27 tests pass
