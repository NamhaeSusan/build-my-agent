# Pytest Collection Scope Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restrict default root-level pytest discovery to the repository's official `tests/` directory so generated agent projects do not break the plugin test suite.

**Architecture:** Add a focused regression test that shells out to `pytest --collect-only` from the repository root and asserts only the maintained test suite is collected. Then add root pytest configuration in `pyproject.toml` using `testpaths = ["tests"]` so the default discovery contract is explicit and deterministic.

**Tech Stack:** Python 3.10+, pytest, subprocess

---

## File Map

### Files to Create

- `tests/test_pytest_collection.py` — regression test for root pytest discovery behavior

### Files to Modify

- `pyproject.toml` — add root pytest discovery configuration

### Files to Create During Execution

- `claude_history/2026-03-29-pytest-collection-scope-impl.md` — implementation record required before commit

---

### Task 1: Add a Regression Test for Root Pytest Discovery

**Files:**
- Create: `tests/test_pytest_collection.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_pytest_collection.py`:

```python
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_root_pytest_collects_only_repo_tests():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    output = f"{result.stdout}\n{result.stderr}"

    assert result.returncode == 0, output
    assert "tests/test_checker.py::TestStructureRules::test_valid_project_passes" in result.stdout
    assert "url-shortener-ops-agent/tests/test_agent.py" not in output
    assert "url-shortener-ops-agent/tests/test_tools.py" not in output
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python3 -m pytest tests/test_pytest_collection.py -q`
Expected: FAIL because root-level collection currently descends into `url-shortener-ops-agent/tests/` and exits non-zero during collection.

---

### Task 2: Restrict Default Pytest Discovery to `tests/`

**Files:**
- Modify: `pyproject.toml`
- Test: `tests/test_pytest_collection.py`

- [ ] **Step 1: Add pytest configuration to `pyproject.toml`**

Append:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Run the targeted regression test**

Run: `python3 -m pytest tests/test_pytest_collection.py -q`
Expected: PASS

- [ ] **Step 3: Run the root pytest command**

Run: `python3 -m pytest -q`
Expected: PASS, with only repository tests collected

- [ ] **Step 4: Run the explicit maintained suite command**

Run: `python3 -m pytest tests -q`
Expected: PASS, unchanged from current maintained workflow

---

### Task 3: Record the Work and Commit

**Files:**
- Create: `claude_history/2026-03-29-pytest-collection-scope-impl.md`
- Modify: `pyproject.toml`
- Create: `tests/test_pytest_collection.py`

- [ ] **Step 1: Write the implementation history file**

Create `claude_history/2026-03-29-pytest-collection-scope-impl.md`:

```markdown
# Pytest Collection Scope Fix

## Date
2026-03-29

## Summary
Restricted root pytest discovery to `tests/` and added a regression test for collection scope.

## Changes
- Added a regression test covering root `pytest --collect-only` behavior
- Added `[tool.pytest.ini_options]` with `testpaths = ["tests"]` to `pyproject.toml`
- Verified both `python3 -m pytest -q` and `python3 -m pytest tests -q`
```

- [ ] **Step 2: Commit**

```bash
git add pyproject.toml tests/test_pytest_collection.py claude_history/2026-03-29-pytest-collection-scope-impl.md
git commit -m "fix: restrict pytest collection to repo tests" -m "Prevent root pytest discovery from collecting generated agent projects.\n\nHistory: claude_history/2026-03-29-pytest-collection-scope-impl.md"
```
