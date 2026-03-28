# Ruff Linter + Skills Folder

## Date
2026-03-28

## Summary
Added Ruff linter configuration and skills directory support to generated agents.

## Changes

### Ruff linter
- `pyproject.toml`: Added ruff config (E, F, I, S rules), S101 ignored, tests exempt from S, http_client exempt from S310
- Fixed: line-too-long in checker.py, unused pytest import in test_e2e_render.py

### Skills folder for generated agents
- `templates/agent.py.tmpl`: Added `FilesystemBackend` and `skills=` parameter to `create_deep_agent()`
- `templates/skills/troubleshooting/SKILL.md.tmpl`: Sample troubleshooting skill template
- `guard/rules.yaml`: Added `skills` to required_dirs
- `tests/conftest.py`: Added skills directory to test fixture
- `tests/test_e2e_render.py`: Added skills rendering + new sample values
- `skills/03-generate-agent/SKILL.md`: Added skills/ to project structure listing

## Tests
- 22 tests pass, ruff clean
