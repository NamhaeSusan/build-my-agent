# E2E Test: url-shortener Agent Generation

## Date
2026-03-29

## Summary
End-to-end test of the build-my-agent pipeline by generating a complete ops agent for a sample URL shortener service.

## Changes

### New Files
- **scripts/render_agent.py** — Standalone template renderer for generating agent projects from CLI. Replaces manual file-by-file creation with a single command.

### Template Improvements (found during E2E)
- **skills/troubleshooting/SKILL.md.tmpl** — Restructured from monolithic file to index + runbooks format:
  - `SKILL.md` is now a concise index with links to runbooks
  - `runbooks/triage.md.tmpl` — general first-response triage steps
  - `runbooks/common-issues.md.tmpl` — known failure patterns
- **tests/test_agent.py.tmpl** — Removed unused `Path` import
- **tests/test_tools.py.tmpl** — Removed unused `MagicMock, patch` imports
- **pyproject.toml.tmpl** — Added `[tool.ruff]` with `line-length = 120` and `[tool.ruff.lint.isort]` with `known-first-party` for clean lint in generated projects
- **test_e2e_render.py** — Updated file_map for new runbook structure, fixed import order in sample values

### Infrastructure
- **.gitignore** — Added `*-ops-agent/` pattern to exclude generated test artifacts

## E2E Results
- 14 files generated in `url-shortener-ops-agent/`
- `python -m guard check` — All checks passed
- 8 Python files — ast.parse OK
- config/agent.yaml — yaml.safe_load OK
- ruff check (with project config) — All checks passed
- 24 project tests — All passed

## Verification
- All 24 tests pass
- ruff lint clean
