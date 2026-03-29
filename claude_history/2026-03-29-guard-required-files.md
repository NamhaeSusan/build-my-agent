# Guard Required Files Expansion

## Date
2026-03-29

## Summary
Expanded the generated-project guard contract to require `models.py` and `skills/troubleshooting/SKILL.md`.

## Changes
- Added `models.py` and `skills/troubleshooting/SKILL.md` to `guard/rules.yaml`
- Updated the valid-project fixture to create both required files
- Added guard regression tests covering both missing-file cases
- Kept troubleshooting runbook files out of the required set
