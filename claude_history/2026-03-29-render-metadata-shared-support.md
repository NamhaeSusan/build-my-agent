# Render Metadata Shared Support

## Date
2026-03-29

## Summary
Moved render metadata and helpers into a shared support module and updated the renderer and E2E test to consume it.

## Changes
- Added `scripts/render_support.py` with the shared template map, sample values, and render helpers
- Refactored `scripts/render_agent.py` to import `SAMPLE_VALUES` and `render_project`
- Updated `tests/test_e2e_render.py` to load the shared module via `importlib.util.spec_from_file_location()`
- Added a regression test for the expected standard template outputs
