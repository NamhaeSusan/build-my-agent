# Guard Lint Expansion + README Update

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand guard lint to cover the entire generated project (not just tools/) and update README to reflect current features.

**Architecture:** Add `lint.scope` option to `rules.yaml` (`"tools"` or `"project"`). When `"project"`, `_check_lint` collects all `.py` files recursively from the project root. Default to `"project"` for new agents. README gets updated sections for new features.

**Tech Stack:** Python, ruff, PyYAML, pytest

---

### Task 1: Test for project-wide lint scope

**Files:**
- Modify: `tests/test_checker.py` (append new tests)

- [ ] **Step 1: Write failing test for project-scope lint**

```python
class TestLintScopeRules:
    def test_project_scope_catches_agent_py_lint_error(self, tmp_agent_project: Path, rules_path: Path):
        """Lint with scope=project catches errors in agent.py, not just tools/."""
        (tmp_agent_project / "agent.py").write_text(
            'import os\n\n'
            'from deepagents import create_deep_agent\n'
            'from tools import search_logs, query_metrics\n\n\n'
            'def create_agent():\n'
            '    return create_deep_agent(tools=[search_logs, query_metrics])\n'
        )
        errors = validate(tmp_agent_project, rules_path)
        ruff_errors = [e for e in errors if e.rule == "lint.ruff"]
        assert any("F401" in e.message for e in ruff_errors), (
            "Expected unused import 'os' in agent.py to be caught"
        )

    def test_project_scope_skips_init_files(self, tmp_agent_project: Path, rules_path: Path):
        """__init__.py files should be skipped in all directories."""
        errors = validate(tmp_agent_project, rules_path)
        ruff_errors = [e for e in errors if e.rule == "lint.ruff"]
        assert ruff_errors == []

    def test_tools_scope_ignores_agent_py(self, tmp_agent_project: Path, rules_path: Path):
        """When scope is tools, agent.py lint errors are not reported."""
        import yaml
        rules = yaml.safe_load(rules_path.read_text())
        rules["lint"]["scope"] = "tools"
        scoped_rules = tmp_agent_project / "scoped_rules.yaml"
        scoped_rules.write_text(yaml.dump(rules))

        (tmp_agent_project / "agent.py").write_text(
            'import os\n\n'
            'from deepagents import create_deep_agent\n'
            'from tools import search_logs, query_metrics\n\n\n'
            'def create_agent():\n'
            '    return create_deep_agent(tools=[search_logs, query_metrics])\n'
        )
        errors = validate(tmp_agent_project, scoped_rules)
        ruff_errors = [e for e in errors if e.rule == "lint.ruff"]
        assert not any("agent.py" in e.message for e in ruff_errors)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_checker.py::TestLintScopeRules -v`
Expected: `test_project_scope_catches_agent_py_lint_error` FAILS (agent.py not linted currently)

- [ ] **Step 3: Commit failing tests**

```bash
git add tests/test_checker.py
git commit -m "test: add tests for project-wide lint scope"
```

### Task 2: Implement project-wide lint scope

**Files:**
- Modify: `guard/rules.yaml` (add `scope` field)
- Modify: `guard/checker.py:195-239` (`_check_lint` function)

- [ ] **Step 1: Add scope to rules.yaml**

Add `scope: "project"` to the `lint` section in `guard/rules.yaml`:

```yaml
lint:
  ruff: true
  scope: "project"                      # "project" (all .py files) or "tools" (only tools/)
  ruff_select: "E,F,I"
  ruff_ignore: ""
```

- [ ] **Step 2: Update `_check_lint` to support scope**

Replace the `_check_lint` function in `guard/checker.py`:

```python
def _check_lint(project: Path, rules: dict, structure: dict) -> list[Violation]:
    """Run ruff on the project's Python files."""
    if not rules.get("ruff", False):
        return []

    select = rules.get("ruff_select", "E,F,I")
    ignore = rules.get("ruff_ignore", "")
    scope = rules.get("scope", "project")

    if scope == "tools":
        tool_dir = project / structure.get("tool_dir", "tools")
        py_files = [f for f in tool_dir.glob("*.py") if f.name != "__init__.py"] if tool_dir.is_dir() else []
    else:
        py_files = [f for f in project.rglob("*.py") if f.name != "__init__.py"]

    if not py_files:
        return []

    cmd = ["ruff", "check", "--isolated", "--select", select]
    if ignore:
        cmd.extend(["--ignore", ignore])
    cmd.extend(str(f) for f in py_files)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)  # noqa: S603
    except FileNotFoundError:
        return [Violation(
            rule="lint.ruff",
            message="ruff not installed — install with: pip install ruff",
            path=str(project),
        )]

    if result.returncode == 0:
        return []

    violations = []
    for line in result.stdout.strip().splitlines():
        violations.append(Violation(
            rule="lint.ruff",
            message=line,
            path=str(project),
        ))
    if result.stderr.strip():
        violations.append(Violation(
            rule="lint.ruff",
            message=f"ruff stderr: {result.stderr.strip()}",
            path=str(project),
        ))
    return violations
```

- [ ] **Step 3: Run all tests**

Run: `python3 -m pytest tests/ -v`
Expected: All 27 tests PASS (24 existing + 3 new)

- [ ] **Step 4: Commit**

```bash
git add guard/checker.py guard/rules.yaml
git commit -m "feat: expand guard lint scope to entire project"
```

### Task 3: Fix conftest fixture for project-scope lint

**Files:**
- Modify: `tests/conftest.py` (ensure fixture files are ruff-clean)

The conftest `agent.py` fixture may trigger lint errors under project scope (unused imports, etc.). Verify and fix.

- [ ] **Step 1: Run tests and check for conftest-related failures**

Run: `python3 -m pytest tests/test_checker.py -v`

If `test_valid_project_passes` or `test_project_scope_skips_init_files` fails, the fixture agent.py has lint issues.

- [ ] **Step 2: Fix fixture agent.py if needed**

The current fixture `agent.py` has:
```python
from deepagents import create_deep_agent
from tools import search_logs, query_metrics

def create_agent():
    return create_deep_agent(
        tools=[search_logs, query_metrics],
    )
```

This should be ruff-clean. If it's not (e.g., isort issue), fix the indentation/ordering in `conftest.py`.

- [ ] **Step 3: Run all tests to confirm**

Run: `python3 -m pytest tests/ -v`
Expected: All PASS

- [ ] **Step 4: Commit if changes were made**

```bash
git add tests/conftest.py
git commit -m "fix: make conftest fixture ruff-clean for project-scope lint"
```

### Task 4: Update README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update Generated Agent Structure**

Add `models.py` and `skills/troubleshooting/runbooks/` to the tree:

```
<component>-ops-agent/
├── pyproject.toml
├── agent.py                  # Entry point: create_deep_agent()
├── models.py                 # DiagnosisReport for structured output
├── config/
│   └── agent.yaml            # Endpoints, index patterns, namespaces
├── tools/
│   ├── __init__.py
│   ├── log_search.py         # OpenSearch log query
│   ├── metric_query.py       # Prometheus metric query
│   ├── http_client.py        # HTTP requests (health checks, deploy triggers)
│   └── ...                   # Custom tools (Kafka, DB, etc.)
├── prompts/
│   └── system.md             # Domain knowledge for the agent
├── skills/
│   └── troubleshooting/
│       ├── SKILL.md           # Troubleshooting index
│       └── runbooks/          # Individual runbook files
│           ├── triage.md
│           └── common-issues.md
└── tests/
    ├── test_tools.py
    └── test_agent.py
```

- [ ] **Step 2: Add Run Modes section**

After "Run the generated agent", add:

```markdown
### Run modes

```bash
# Interactive chat (default)
python agent.py

# Single query
python agent.py --once "check error rate for the last hour"

# Structured diagnosis (returns JSON DiagnosisReport)
python agent.py --diagnose --once "why is latency high?"
```
```

- [ ] **Step 3: Update Guard Rules table**

Add lint row:

```markdown
| Rule | Description |
|------|-------------|
| Structure | Required files and directories must exist |
| Naming | Tool files and functions must be `snake_case` |
| Pattern | One public function per tool file |
| Pattern | All tool functions must have docstrings |
| Pattern | No hardcoded URLs (must use config) |
| Pattern | Config must be loaded from `config/agent.yaml` |
| Lint | ruff checks all Python files (E, F, I rules) |
```

- [ ] **Step 4: Add render script to Development section**

```markdown
## Development

```bash
# Run guard tests
python3 -m pytest tests/ -v

# Test guard on a project
python3 -m guard check <agent-project-path>

# Generate a sample agent from templates
python3 scripts/render_agent.py <output-dir>

# Lint
python3 -m ruff check .
```
```

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: update README with run modes, lint rule, render script"
```

### Task 5: Final verification

**Files:** None (verification only)

- [ ] **Step 1: Run full test suite**

Run: `python3 -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 2: Run lint**

Run: `python3 -m ruff check .`
Expected: All checks passed

- [ ] **Step 3: Run guard on url-shortener sample**

```bash
rm -rf url-shortener-ops-agent
python3 scripts/render_agent.py url-shortener-ops-agent
python3 -m guard check url-shortener-ops-agent/
```
Expected: All checks passed

- [ ] **Step 4: Write history file and commit**

Create `claude_history/2026-03-29-guard-expansion-readme.md` and commit.
