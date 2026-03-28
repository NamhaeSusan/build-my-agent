---
name: validate-structure
description: Run AST guard validation on a generated agent project and auto-fix violations
---

# Validate Agent Structure

You are running the final structure validation on a generated agent project.

## Prerequisites
- A generated agent project exists (from the generate step)
- The build-my-agent guard is available

## Process

### Step 1: Run Guard

Execute the guard checker:

```bash
python -m guard check <agent-project-path>
```

### Step 2: Handle Results

**If all checks pass:**
> "All structure checks passed. Your agent is ready to use.
>
> Quick start:
> ```bash
> cd <component_name>-ops-agent
> pip install -e '.[dev]'
> python agent.py
> ```
>
> To add new tools later:
> 1. Create a new file in `tools/` with one public function and a docstring
> 2. Add its config section to `config/agent.yaml`
> 3. Import and export from `tools/__init__.py`
> 4. Register in `agent.py`
> 5. Run `python -m guard check .` to verify"

**If violations found:**

For each violation, fix it:

| Violation | Fix |
|-----------|-----|
| Missing required file | Create the file using the appropriate template |
| File name not snake_case | Rename the file to snake_case |
| Function name not snake_case | Rename the function |
| Multiple public functions | Split into separate tool files, or prefix helpers with `_` |
| Missing docstring | Add a descriptive docstring to the function |
| Hardcoded URL | Replace with config loading pattern |

After fixing, re-run the guard:

```bash
python -m guard check <agent-project-path>
```

Repeat until all checks pass.

### Step 3: Run Tests

After guard passes, run the project's tests:

```bash
cd <agent-project-path>
pip install -e '.[dev]'
python -m pytest tests/ -v
```

Fix any test failures.

### Step 4: Final Report

> "Validation complete:
> - Guard: all checks passed
> - Tests: [pass/fail status]
>
> Your `<component_name>-ops-agent` is ready for use."
