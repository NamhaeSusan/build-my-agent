# Pytest Collection Scope Fix

## Date
2026-03-29

## Summary

Restrict default pytest collection to this plugin's official test suite under `tests/`.

Today `python3 -m pytest -q` run from the repository root also collects generated agent projects that happen to exist in the workspace. That makes the plugin's own CI signal depend on local sample artifacts such as `url-shortener-ops-agent/`, which is not acceptable.

## Problem

- Root-level pytest collection currently walks beyond the plugin's maintained test suite.
- Generated agent directories are valid Python projects with their own `tests/`, so they are collected unintentionally.
- This creates false negatives that are unrelated to the plugin itself.

## Chosen Approach

Add pytest configuration to `pyproject.toml` so the default collection target is only `tests/`.

Recommended config:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

## Why This Approach

### Option A: `testpaths = ["tests"]` in `pyproject.toml`

- Most explicit expression of repository intent
- Keeps `python3 -m pytest -q` deterministic
- Avoids maintaining ignore lists for every generated artifact pattern

### Option B: Ignore generated directories with `norecursedirs` or `--ignore-glob`

- Works short-term
- Couples pytest behavior to artifact naming conventions
- Becomes harder to maintain as more example or generated directories appear

### Option C: Move generated examples elsewhere

- Clean long-term separation
- Larger scope than needed for this issue
- Not justified for the first fix

## Scope

### In Scope

- Update pytest configuration in the root project
- Preserve explicit test execution for generated agents when their path is provided directly

### Out of Scope

- Reorganizing generated examples
- Changing generated agent test layout
- Any guard or template changes

## Verification

Success means:

1. `python3 -m pytest -q` from the repository root collects only `tests/`
2. `python3 -m pytest tests -q` still passes unchanged
3. Generated agent tests remain runnable when explicitly targeted

## Risks

- Low risk. This only narrows default discovery and does not remove explicit test execution paths.
- The only behavior change is that root pytest no longer treats incidental generated projects as part of the plugin test suite.
