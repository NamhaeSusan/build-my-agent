# Render Metadata + Guard Contract + Reference Tool Alignment

## Date
2026-03-29

## Summary

Implement the next improvement batch with the fixed scope and order:

1. Single-source render metadata
2. Guard contract expansion
3. Reference tool alignment and verification

This batch explicitly excludes generated test template strengthening, config schema work, troubleshooting runbook schema work, and structured diagnosis verification.

## Scope

### Included

- Deduplicate render file metadata and sample placeholder values used by:
  - `scripts/render_agent.py`
  - `tests/test_e2e_render.py`
- Expand guard required files to include:
  - `models.py`
  - `skills/troubleshooting/SKILL.md`
- Align reference tool config path handling with the generated tool templates
- Add tests that verify reference tool implementations follow the expected config convention

### Excluded

- Strengthening generated test templates
- Config schema / runtime preflight validation
- Guard requirements for troubleshooting runbook files
- Structured diagnosis smoke tests

## Current Problems

### Render Metadata Drift

`scripts/render_agent.py` and `tests/test_e2e_render.py` each define their own file map and sample placeholder values. That creates a maintenance trap: template additions or placeholder changes must be applied in multiple places, and drift is easy.

### Guard Contract Lags Behind Actual Standard Output

The generated project structure includes `models.py` and `skills/troubleshooting/SKILL.md`, but `guard/rules.yaml` does not currently require them. That means the guard under-specifies the project's actual standard output.

### Reference Tools Are Not Canonical Enough

The reference tools under `tools/` still use a config path convention that differs from the generated templates. That weakens them as source-of-truth examples and makes future extension work less reliable.

## Chosen Design

### 1. Single-Source Render Metadata

Create a shared Python module that owns:

- the template-to-output file map
- sample placeholder values used for render validation
- the shared template rendering helper

Both `scripts/render_agent.py` and `tests/test_e2e_render.py` will import from this module instead of keeping their own copies.

This is intentionally small-scope. The module is a data/utility source, not a new abstraction layer.

### 2. Narrow Guard Expansion

Update `guard/rules.yaml` so the required file contract includes:

- `models.py`
- `skills/troubleshooting/SKILL.md`

Do not require troubleshooting runbook files in this batch. The guard should assert only the stable entrypoints that represent the current standard project shape, not the full runbook set.

### 3. Reference Tool Alignment

Update the reference tools in `tools/` to use the same config path convention as the generated templates:

- `tools/` reference files should resolve the project config via the project root, not via a `tools/config` path

Then add tests that validate the reference implementations against this expectation so the mismatch cannot regress.

## Alternatives Considered

### Guard-first

Expand the guard first, then clean up render duplication.

- Pros: contract locked early
- Cons: does not follow the requested execution order

### Render-first without contract awareness

Deduplicate render metadata first and defer contract implications until later.

- Pros: fastest initial cleanup
- Cons: likely to require follow-up changes once guard contract expands

### Chosen: Render-first but contract-aware

Deduplicate render metadata first, but design the shared source around the same standard output that guard will soon enforce.

- Pros: follows requested order `4 -> 2 -> 5`
- Pros: minimizes rework between steps
- Cons: requires slightly more care in the first change

## Verification

Success means:

1. `scripts/render_agent.py` and `tests/test_e2e_render.py` use shared render metadata rather than local duplicates
2. Guard reports violations when `models.py` or `skills/troubleshooting/SKILL.md` are missing from a generated project
3. Reference tool config resolution matches the generated template convention
4. New or updated tests verify the reference tool convention and pass

## Risks

- Low-to-moderate risk around test fixture expectations if guard contract expands without updating fixtures
- Low risk in render deduplication as long as file map and sample values are migrated mechanically
- Low risk in reference tool alignment, but tests must prevent silent path regressions
