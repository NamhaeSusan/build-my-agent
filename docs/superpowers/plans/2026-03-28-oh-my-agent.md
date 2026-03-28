# build-my-agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude Code plugin that generates standardized deepagents-based operational agents for any component through conversational Q&A.

**Architecture:** Skills-heavy Claude Code plugin. Four sequential skills guide Claude through codebase analysis, agent design, code generation, and structure validation. An AST guard enforces uniform project structure across all generated agents. Reference tool implementations (OpenSearch, Prometheus) serve as both templates and working code.

**Tech Stack:** Python 3.11+, deepagents, opensearch-py, prometheus-api-client, PyYAML, pytest

---

## File Map

### New Files to Create

```
build-my-agent/
├── pyproject.toml                              # Plugin package config + guard deps
├── README.md                                   # (will not create unless asked)
│
├── guard/                                      # AST structure validator
│   ├── __init__.py                             # Package init, exports validate()
│   ├── rules.yaml                              # Declarative rule definitions
│   ├── checker.py                              # Core validation logic using ast module
│   └── cli.py                                  # CLI: python -m guard check <path>
│
├── tools/                                      # Reference tool implementations
│   ├── __init__.py                             # Package init
│   ├── opensearch.py                           # OpenSearch log query tool
│   └── prometheus.py                           # Prometheus metric query tool
│
├── templates/                                  # Boilerplate for generated agents
│   ├── pyproject.toml.tmpl                     # Agent package config
│   ├── agent.py.tmpl                           # Agent entry point
│   ├── config/
│   │   └── agent.yaml.tmpl                     # Agent config
│   ├── tools/
│   │   ├── __init__.py.tmpl                    # Tool exports
│   │   ├── log_search.py.tmpl                  # OpenSearch tool
│   │   └── metric_query.py.tmpl                # Prometheus tool
│   ├── prompts/
│   │   └── system.md.tmpl                      # System prompt
│   └── tests/
│       ├── test_tools.py.tmpl                  # Tool unit tests
│       └── test_agent.py.tmpl                  # Agent integration test
│
├── skills/                                     # Claude Code skills
│   ├── 01-analyze-codebase/
│   │   └── SKILL.md
│   ├── 02-design-agent/
│   │   └── SKILL.md
│   ├── 03-generate-agent/
│   │   └── SKILL.md
│   └── 04-validate-structure/
│       └── SKILL.md
│
└── tests/                                      # Guard tests
    ├── __init__.py
    ├── conftest.py                             # Shared fixtures (temp project dirs)
    ├── test_checker.py                         # Guard checker unit tests
    └── test_cli.py                             # Guard CLI integration tests
```

---

## Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `guard/__init__.py`
- Create: `tools/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Initialize git repository**

```bash
cd /Users/kimtaeyun/build-my-agent
git init
```

- [ ] **Step 2: Create pyproject.toml**

```toml
[project]
name = "build-my-agent"
version = "0.1.0"
description = "Claude Code plugin for generating standardized operational agents"
requires-python = ">=3.11"
dependencies = [
    "deepagents>=0.1.0",
    "opensearch-py>=2.4.0",
    "prometheus-api-client>=0.5.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
]

[project.scripts]
build-my-agent-guard = "guard.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

- [ ] **Step 3: Create package init files**

`guard/__init__.py`:
```python
from guard.checker import validate

__all__ = ["validate"]
```

`tools/__init__.py`:
```python
from tools.opensearch import search_logs
from tools.prometheus import query_metrics

__all__ = ["search_logs", "query_metrics"]
```

`tests/__init__.py`:
```python
```

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml guard/__init__.py tools/__init__.py tests/__init__.py
git commit -m "chore: initialize build-my-agent project structure"
```

---

## Task 2: Guard — Rule Definitions

**Files:**
- Create: `guard/rules.yaml`
- Create: `tests/conftest.py`
- Create: `tests/test_checker.py` (first batch of tests)

- [ ] **Step 1: Create guard/rules.yaml**

```yaml
# build-my-agent AST Guard Rules
# These rules enforce structural consistency across all generated agent projects.

structure:
  required_files:
    - "agent.py"
    - "config/agent.yaml"
    - "tools/__init__.py"
    - "prompts/system.md"
  required_dirs:
    - "tools"
    - "config"
    - "prompts"
    - "tests"
  tool_dir: "tools"  # tool files must live here

naming:
  tool_files: "snake_case"       # e.g. log_search.py, metric_query.py
  tool_functions: "snake_case"   # e.g. search_logs, query_metrics

patterns:
  one_public_function_per_tool: true    # each tool file exports exactly one public function
  tool_docstring_required: true         # tool functions must have docstrings
  no_hardcoded_endpoints: true          # no http:// or https:// literals in tool files
  config_source: "config/agent.yaml"    # config must be loaded from this file
```

- [ ] **Step 2: Create tests/conftest.py with fixtures**

```python
import os
import shutil
import textwrap
from pathlib import Path

import pytest


@pytest.fixture
def tmp_agent_project(tmp_path: Path) -> Path:
    """Create a minimal valid agent project structure."""
    project = tmp_path / "test-ops-agent"
    project.mkdir()

    # Required directories
    (project / "tools").mkdir()
    (project / "config").mkdir()
    (project / "prompts").mkdir()
    (project / "tests").mkdir()

    # agent.py
    (project / "agent.py").write_text(textwrap.dedent("""\
        from deepagents import create_deep_agent
        from tools import search_logs, query_metrics

        def create_agent():
            return create_deep_agent(
                tools=[search_logs, query_metrics],
            )
    """))

    # config/agent.yaml
    (project / "config" / "agent.yaml").write_text(textwrap.dedent("""\
        component: test-service
        description: "Test service"
        opensearch:
          endpoint: https://opensearch.internal:9200
          index_pattern: test-*
        prometheus:
          endpoint: https://prometheus.internal:9090
          namespace: test
    """))

    # prompts/system.md
    (project / "prompts" / "system.md").write_text(
        "You are an operational agent for test-service."
    )

    # tools/__init__.py
    (project / "tools" / "__init__.py").write_text(textwrap.dedent("""\
        from tools.log_search import search_logs
        from tools.metric_query import query_metrics

        __all__ = ["search_logs", "query_metrics"]
    """))

    # tools/log_search.py — valid tool
    (project / "tools" / "log_search.py").write_text(textwrap.dedent("""\
        import yaml

        def _load_config():
            with open("config/agent.yaml") as f:
                return yaml.safe_load(f)

        def search_logs(query: str, time_range: str = "1h") -> list[dict]:
            \"\"\"Search OpenSearch logs for the component.\"\"\"
            config = _load_config()
            endpoint = config["opensearch"]["endpoint"]
            return []
    """))

    # tools/metric_query.py — valid tool
    (project / "tools" / "metric_query.py").write_text(textwrap.dedent("""\
        import yaml

        def _load_config():
            with open("config/agent.yaml") as f:
                return yaml.safe_load(f)

        def query_metrics(promql: str, duration: str = "5m") -> dict:
            \"\"\"Query Prometheus metrics for the component.\"\"\"
            config = _load_config()
            endpoint = config["prometheus"]["endpoint"]
            return {}
    """))

    return project


@pytest.fixture
def rules_path() -> Path:
    """Path to the guard rules file."""
    return Path(__file__).parent.parent / "guard" / "rules.yaml"
```

- [ ] **Step 3: Write failing tests for structure validation**

`tests/test_checker.py`:
```python
from pathlib import Path

from guard.checker import validate


class TestStructureRules:
    def test_valid_project_passes(self, tmp_agent_project: Path, rules_path: Path):
        errors = validate(tmp_agent_project, rules_path)
        assert errors == []

    def test_missing_agent_py(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "agent.py").unlink()
        errors = validate(tmp_agent_project, rules_path)
        assert any("agent.py" in e.message for e in errors)

    def test_missing_config_dir(self, tmp_agent_project: Path, rules_path: Path):
        import shutil
        shutil.rmtree(tmp_agent_project / "config")
        errors = validate(tmp_agent_project, rules_path)
        assert any("config" in e.message for e in errors)

    def test_missing_tools_init(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "__init__.py").unlink()
        errors = validate(tmp_agent_project, rules_path)
        assert any("tools/__init__.py" in e.message for e in errors)


class TestNamingRules:
    def test_camel_case_tool_file_rejected(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "LogSearch.py").write_text(
            'def log_search():\n    """Search logs."""\n    pass\n'
        )
        errors = validate(tmp_agent_project, rules_path)
        assert any("LogSearch.py" in e.message for e in errors)

    def test_camel_case_function_rejected(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "bad_tool.py").write_text(
            'def SearchLogs():\n    """Search logs."""\n    pass\n'
        )
        errors = validate(tmp_agent_project, rules_path)
        assert any("SearchLogs" in e.message for e in errors)

    def test_snake_case_tool_file_accepted(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "kafka_consumer.py").write_text(
            'def consume_messages():\n    """Consume Kafka messages."""\n    pass\n'
        )
        errors = validate(tmp_agent_project, rules_path)
        assert errors == []


class TestPatternRules:
    def test_multiple_public_functions_rejected(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "bad_tool.py").write_text(
            'def func_a():\n    """A."""\n    pass\n\ndef func_b():\n    """B."""\n    pass\n'
        )
        errors = validate(tmp_agent_project, rules_path)
        assert any("one public function" in e.message.lower() for e in errors)

    def test_missing_docstring_rejected(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "no_doc.py").write_text(
            "def no_docs():\n    pass\n"
        )
        errors = validate(tmp_agent_project, rules_path)
        assert any("docstring" in e.message.lower() for e in errors)

    def test_hardcoded_url_rejected(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "hardcoded.py").write_text(
            'def bad_tool():\n    """Bad."""\n    url = "https://opensearch.internal:9200"\n    return url\n'
        )
        errors = validate(tmp_agent_project, rules_path)
        assert any("hardcoded" in e.message.lower() for e in errors)

    def test_config_loaded_from_yaml_accepted(self, tmp_agent_project: Path, rules_path: Path):
        """The default fixture tools load config properly — should pass."""
        errors = validate(tmp_agent_project, rules_path)
        assert errors == []
```

- [ ] **Step 4: Run tests to verify they fail**

```bash
cd /Users/kimtaeyun/build-my-agent
python -m pytest tests/test_checker.py -v
```

Expected: FAIL — `guard.checker` module does not exist yet / `validate` not importable.

- [ ] **Step 5: Commit test files**

```bash
git add guard/rules.yaml tests/conftest.py tests/test_checker.py
git commit -m "test: add guard checker tests and rule definitions"
```

---

## Task 3: Guard — Checker Implementation

**Files:**
- Create: `guard/checker.py`

- [ ] **Step 1: Implement guard/checker.py**

```python
"""AST-based structure validator for generated agent projects."""

import ast
import re
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Violation:
    """A single rule violation."""
    rule: str       # e.g. "structure.required_files"
    message: str    # human-readable description
    path: str       # file or directory that caused the violation


def validate(project_path: Path, rules_path: Path) -> list[Violation]:
    """Validate a generated agent project against the guard rules.

    Args:
        project_path: Root directory of the generated agent project.
        rules_path: Path to the rules.yaml file.

    Returns:
        List of Violation objects. Empty list means the project is valid.
    """
    with open(rules_path) as f:
        rules = yaml.safe_load(f)

    violations: list[Violation] = []
    violations.extend(_check_structure(project_path, rules.get("structure", {})))
    violations.extend(_check_naming(project_path, rules.get("naming", {}), rules.get("structure", {})))
    violations.extend(_check_patterns(project_path, rules.get("patterns", {}), rules.get("structure", {})))
    return violations


def _check_structure(project: Path, rules: dict) -> list[Violation]:
    violations = []
    for f in rules.get("required_files", []):
        if not (project / f).is_file():
            violations.append(Violation(
                rule="structure.required_files",
                message=f"Required file missing: {f}",
                path=str(project / f),
            ))
    for d in rules.get("required_dirs", []):
        if not (project / d).is_dir():
            violations.append(Violation(
                rule="structure.required_dirs",
                message=f"Required directory missing: {d}",
                path=str(project / d),
            ))
    return violations


_SNAKE_CASE_RE = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")


def _is_snake_case(name: str) -> bool:
    return _SNAKE_CASE_RE.match(name) is not None


def _check_naming(project: Path, rules: dict, structure: dict) -> list[Violation]:
    violations = []
    tool_dir = project / structure.get("tool_dir", "tools")
    if not tool_dir.is_dir():
        return violations

    for py_file in tool_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        # Check file naming
        stem = py_file.stem
        if rules.get("tool_files") == "snake_case" and not _is_snake_case(stem):
            violations.append(Violation(
                rule="naming.tool_files",
                message=f"Tool file name is not snake_case: {py_file.name}",
                path=str(py_file),
            ))

        # Check function naming
        if rules.get("tool_functions") == "snake_case":
            try:
                tree = ast.parse(py_file.read_text())
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                    if not _is_snake_case(node.name):
                        violations.append(Violation(
                            rule="naming.tool_functions",
                            message=f"Tool function name is not snake_case: {node.name} in {py_file.name}",
                            path=str(py_file),
                        ))

    return violations


_URL_RE = re.compile(r"""https?://[^\s"']+""")


def _check_patterns(project: Path, rules: dict, structure: dict) -> list[Violation]:
    violations = []
    tool_dir = project / structure.get("tool_dir", "tools")
    if not tool_dir.is_dir():
        return violations

    for py_file in tool_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        source = py_file.read_text()
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        public_functions = [
            node for node in ast.iter_child_nodes(tree)
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
        ]

        # One public function per tool
        if rules.get("one_public_function_per_tool") and len(public_functions) > 1:
            names = [f.name for f in public_functions]
            violations.append(Violation(
                rule="patterns.one_public_function_per_tool",
                message=f"Tool file must have exactly one public function, found {len(public_functions)}: {names} in {py_file.name}",
                path=str(py_file),
            ))

        # Docstring required
        if rules.get("tool_docstring_required"):
            for func in public_functions:
                if not ast.get_docstring(func):
                    violations.append(Violation(
                        rule="patterns.tool_docstring_required",
                        message=f"Tool function missing docstring: {func.name} in {py_file.name}",
                        path=str(py_file),
                    ))

        # No hardcoded endpoints
        if rules.get("no_hardcoded_endpoints"):
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    if _URL_RE.search(node.value):
                        # Check this isn't inside a config file path string
                        violations.append(Violation(
                            rule="patterns.no_hardcoded_endpoints",
                            message=f"Hardcoded URL found in {py_file.name}: {node.value}",
                            path=str(py_file),
                        ))

    return violations
```

- [ ] **Step 2: Run tests to verify they pass**

```bash
cd /Users/kimtaeyun/build-my-agent
python -m pytest tests/test_checker.py -v
```

Expected: All tests PASS.

- [ ] **Step 3: Commit**

```bash
git add guard/checker.py guard/__init__.py
git commit -m "feat: implement AST guard checker with structure, naming, and pattern validation"
```

---

## Task 4: Guard — CLI

**Files:**
- Create: `guard/cli.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing test for CLI**

`tests/test_cli.py`:
```python
import subprocess
import sys
from pathlib import Path


def test_cli_valid_project(tmp_agent_project: Path, rules_path: Path):
    result = subprocess.run(
        [sys.executable, "-m", "guard", "check", str(tmp_agent_project)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "passed" in result.stdout.lower()


def test_cli_invalid_project(tmp_agent_project: Path, rules_path: Path):
    (tmp_agent_project / "agent.py").unlink()
    result = subprocess.run(
        [sys.executable, "-m", "guard", "check", str(tmp_agent_project)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "agent.py" in result.stdout


def test_cli_no_path_shows_usage():
    result = subprocess.run(
        [sys.executable, "-m", "guard"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_cli.py -v
```

Expected: FAIL — `guard/__main__.py` doesn't exist.

- [ ] **Step 3: Implement guard/cli.py and guard/__main__.py**

`guard/cli.py`:
```python
"""CLI entry point for the build-my-agent AST guard."""

import argparse
import sys
from pathlib import Path

from guard.checker import validate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="build-my-agent-guard",
        description="Validate generated agent project structure",
    )
    subparsers = parser.add_subparsers(dest="command")

    check_parser = subparsers.add_parser("check", help="Check project structure")
    check_parser.add_argument("path", type=Path, help="Path to agent project")
    check_parser.add_argument(
        "--rules",
        type=Path,
        default=Path(__file__).parent / "rules.yaml",
        help="Path to rules.yaml (default: built-in rules)",
    )

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_usage()
        return 2

    violations = validate(args.path, args.rules)

    if violations:
        print(f"Found {len(violations)} violation(s):\n")
        for v in violations:
            print(f"  [{v.rule}] {v.message}")
            print(f"    -> {v.path}\n")
        return 1

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`guard/__main__.py`:
```python
"""Allow running guard as: python -m guard check <path>."""

import sys

from guard.cli import main

sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_cli.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add guard/cli.py guard/__main__.py tests/test_cli.py
git commit -m "feat: add guard CLI for project structure validation"
```

---

## Task 5: Reference Tool — OpenSearch

**Files:**
- Create: `tools/opensearch.py`

- [ ] **Step 1: Implement tools/opensearch.py**

```python
"""OpenSearch log search tool for deepagents.

This is the reference implementation. Generated agents get a copy
customized with their component's index pattern and fields.
"""

import yaml
from opensearchpy import OpenSearch


def _load_config(config_path: str = "config/agent.yaml") -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def search_logs(
    query: str,
    time_range: str = "1h",
    level: str | None = None,
    limit: int = 50,
    config_path: str = "config/agent.yaml",
) -> list[dict]:
    """Search OpenSearch logs for the component.

    Args:
        query: Search keyword or Lucene query string.
        time_range: How far back to search (e.g. "1h", "30m", "7d").
        level: Filter by log level (e.g. "ERROR", "WARN"). None means all levels.
        limit: Maximum number of results to return.
        config_path: Path to agent config file.

    Returns:
        List of log entries, each as a dict with timestamp, level, message, and fields.
    """
    config = _load_config(config_path)
    os_config = config["opensearch"]

    client = OpenSearch(
        hosts=[os_config["endpoint"]],
        use_ssl=os_config["endpoint"].startswith("https"),
        verify_certs=os_config.get("verify_certs", True),
    )

    must_clauses: list[dict] = [
        {"query_string": {"query": query}},
        {"range": {"@timestamp": {"gte": f"now-{time_range}", "lte": "now"}}},
    ]
    if level:
        must_clauses.append({"term": {"level": level.upper()}})

    body = {
        "query": {"bool": {"must": must_clauses}},
        "sort": [{"@timestamp": {"order": "desc"}}],
        "size": limit,
    }

    response = client.search(
        index=os_config["index_pattern"],
        body=body,
    )

    return [
        {
            "timestamp": hit["_source"].get("@timestamp"),
            "level": hit["_source"].get("level"),
            "message": hit["_source"].get("message"),
            "fields": {
                k: v
                for k, v in hit["_source"].items()
                if k not in ("@timestamp", "level", "message")
            },
        }
        for hit in response["hits"]["hits"]
    ]
```

- [ ] **Step 2: Commit**

```bash
git add tools/opensearch.py
git commit -m "feat: add OpenSearch log search reference tool"
```

---

## Task 6: Reference Tool — Prometheus

**Files:**
- Create: `tools/prometheus.py`

- [ ] **Step 1: Implement tools/prometheus.py**

```python
"""Prometheus metric query tool for deepagents.

This is the reference implementation. Generated agents get a copy
customized with their component's namespace and common queries.
"""

import yaml
from prometheus_api_client import PrometheusConnect


def _load_config(config_path: str = "config/agent.yaml") -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def query_metrics(
    promql: str,
    duration: str = "5m",
    step: str = "15s",
    config_path: str = "config/agent.yaml",
) -> dict:
    """Query Prometheus metrics for the component.

    Args:
        promql: PromQL query string.
        duration: Time range for range queries (e.g. "5m", "1h").
        step: Query resolution step (e.g. "15s", "1m").
        config_path: Path to agent config file.

    Returns:
        Dict with 'result_type' ("vector" or "matrix") and 'data' (list of series).
        Each series has 'metric' (label dict) and 'values' (list of [timestamp, value]).
    """
    config = _load_config(config_path)
    prom_config = config["prometheus"]

    prom = PrometheusConnect(
        url=prom_config["endpoint"],
        disable_ssl=not prom_config["endpoint"].startswith("https"),
    )

    # Try range query first, fall back to instant
    result = prom.custom_query_range(
        query=promql,
        start_time=f"now-{duration}",
        end_time="now",
        step=step,
    )

    if not result:
        # Fallback to instant query
        result = prom.custom_query(query=promql)
        return {
            "result_type": "vector",
            "data": [
                {
                    "metric": item.get("metric", {}),
                    "value": item.get("value", []),
                }
                for item in result
            ],
        }

    return {
        "result_type": "matrix",
        "data": [
            {
                "metric": item.get("metric", {}),
                "values": item.get("values", []),
            }
            for item in result
        ],
    }
```

- [ ] **Step 2: Commit**

```bash
git add tools/prometheus.py tools/__init__.py
git commit -m "feat: add Prometheus metric query reference tool"
```

---

## Task 7: Templates — Agent Project Boilerplate

**Files:**
- Create: `templates/pyproject.toml.tmpl`
- Create: `templates/agent.py.tmpl`
- Create: `templates/config/agent.yaml.tmpl`
- Create: `templates/tools/__init__.py.tmpl`
- Create: `templates/tools/log_search.py.tmpl`
- Create: `templates/tools/metric_query.py.tmpl`
- Create: `templates/prompts/system.md.tmpl`
- Create: `templates/tests/test_tools.py.tmpl`
- Create: `templates/tests/test_agent.py.tmpl`

- [ ] **Step 1: Create templates/pyproject.toml.tmpl**

```toml
[project]
name = "{{component_name}}-ops-agent"
version = "0.1.0"
description = "Operational agent for {{component_name}}"
requires-python = ">=3.11"
dependencies = [
    "deepagents>=0.1.0",
    "opensearch-py>=2.4.0",
    "prometheus-api-client>=0.5.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
]
```

- [ ] **Step 2: Create templates/agent.py.tmpl**

```python
"""{{component_name}} operational agent entry point."""

from deepagents import create_deep_agent
from pathlib import Path

from tools import {{tool_imports}}


def create_agent():
    """Create the operational agent for {{component_name}}."""
    system_prompt = Path("prompts/system.md").read_text()

    return create_deep_agent(
        system_prompt=system_prompt,
        tools=[{{tool_list}}],
    )


if __name__ == "__main__":
    agent = create_agent()
    agent.invoke({"messages": [("user", "What is the current status of {{component_name}}?")]})
```

- [ ] **Step 3: Create templates/config/agent.yaml.tmpl**

```yaml
component: {{component_name}}
description: "{{component_description}}"

opensearch:
  endpoint: {{opensearch_endpoint}}
  index_pattern: {{opensearch_index_pattern}}
  verify_certs: true

prometheus:
  endpoint: {{prometheus_endpoint}}
  namespace: {{prometheus_namespace}}
```

- [ ] **Step 4: Create templates/tools/ files**

`templates/tools/__init__.py.tmpl`:
```python
{{tool_imports_block}}

__all__ = [{{tool_all_list}}]
```

`templates/tools/log_search.py.tmpl`:
```python
"""OpenSearch log search tool for {{component_name}}."""

import yaml
from opensearchpy import OpenSearch


def _load_config(config_path: str = "config/agent.yaml") -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def search_logs(
    query: str,
    time_range: str = "1h",
    level: str | None = None,
    limit: int = 50,
    config_path: str = "config/agent.yaml",
) -> list[dict]:
    """Search logs for {{component_name}}.

    Available fields: {{log_fields}}

    Args:
        query: Search keyword or Lucene query string.
        time_range: How far back to search (e.g. "1h", "30m", "7d").
        level: Filter by log level (e.g. "ERROR", "WARN"). None means all levels.
        limit: Maximum number of results to return.
        config_path: Path to agent config file.

    Returns:
        List of log entries with timestamp, level, message, and fields.
    """
    config = _load_config(config_path)
    os_config = config["opensearch"]

    client = OpenSearch(
        hosts=[os_config["endpoint"]],
        use_ssl=os_config["endpoint"].startswith("https"),
        verify_certs=os_config.get("verify_certs", True),
    )

    must_clauses: list[dict] = [
        {"query_string": {"query": query}},
        {"range": {"@timestamp": {"gte": f"now-{time_range}", "lte": "now"}}},
    ]
    if level:
        must_clauses.append({"term": {"level": level.upper()}})

    body = {
        "query": {"bool": {"must": must_clauses}},
        "sort": [{"@timestamp": {"order": "desc"}}],
        "size": limit,
    }

    response = client.search(index=os_config["index_pattern"], body=body)

    return [
        {
            "timestamp": hit["_source"].get("@timestamp"),
            "level": hit["_source"].get("level"),
            "message": hit["_source"].get("message"),
            "fields": {
                k: v for k, v in hit["_source"].items()
                if k not in ("@timestamp", "level", "message")
            },
        }
        for hit in response["hits"]["hits"]
    ]
```

`templates/tools/metric_query.py.tmpl`:
```python
"""Prometheus metric query tool for {{component_name}}."""

import yaml
from prometheus_api_client import PrometheusConnect


def _load_config(config_path: str = "config/agent.yaml") -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def query_metrics(
    promql: str,
    duration: str = "5m",
    step: str = "15s",
    config_path: str = "config/agent.yaml",
) -> dict:
    """Query Prometheus metrics for {{component_name}}.

    Common metrics namespace: {{prometheus_namespace}}

    Args:
        promql: PromQL query string.
        duration: Time range for range queries (e.g. "5m", "1h").
        step: Query resolution step (e.g. "15s", "1m").
        config_path: Path to agent config file.

    Returns:
        Dict with result_type and data (list of metric series).
    """
    config = _load_config(config_path)
    prom_config = config["prometheus"]

    prom = PrometheusConnect(
        url=prom_config["endpoint"],
        disable_ssl=not prom_config["endpoint"].startswith("https"),
    )

    result = prom.custom_query_range(
        query=promql,
        start_time=f"now-{duration}",
        end_time="now",
        step=step,
    )

    if not result:
        result = prom.custom_query(query=promql)
        return {
            "result_type": "vector",
            "data": [
                {"metric": item.get("metric", {}), "value": item.get("value", [])}
                for item in result
            ],
        }

    return {
        "result_type": "matrix",
        "data": [
            {"metric": item.get("metric", {}), "values": item.get("values", [])}
            for item in result
        ],
    }
```

- [ ] **Step 5: Create templates/prompts/system.md.tmpl**

```markdown
# {{component_name}} Operational Agent

You are an operational agent for **{{component_name}}**.

## Component Overview
{{component_description}}

## Your Capabilities
- Search logs via OpenSearch (index: `{{opensearch_index_pattern}}`)
- Query metrics via Prometheus (namespace: `{{prometheus_namespace}}`)
{{additional_capabilities}}

## Domain Knowledge
{{domain_knowledge}}

## Common Failure Patterns
{{failure_patterns}}

## Guidelines
- Always check both logs and metrics when diagnosing issues
- Present timestamps in the component's timezone
- When reporting errors, include the relevant log entries and metric trends
- If you cannot determine the root cause, clearly state what you found and what is still unclear
```

- [ ] **Step 6: Create templates/tests/ files**

`templates/tests/test_tools.py.tmpl`:
```python
"""Unit tests for {{component_name}} ops agent tools."""

from unittest.mock import MagicMock, patch

{{test_imports}}


{{test_cases}}
```

`templates/tests/test_agent.py.tmpl`:
```python
"""Integration test for {{component_name}} ops agent."""

from pathlib import Path

from agent import create_agent


def test_agent_creation():
    """Verify the agent can be created without errors."""
    agent = create_agent()
    assert agent is not None
```

- [ ] **Step 7: Commit**

```bash
git add templates/
git commit -m "feat: add agent project templates"
```

---

## Task 8: Skill — 01-analyze-codebase

**Files:**
- Create: `skills/01-analyze-codebase/SKILL.md`

- [ ] **Step 1: Write skills/01-analyze-codebase/SKILL.md**

```markdown
---
name: analyze-codebase
description: Analyze a component's codebase to understand its logging, metrics, and infrastructure for ops agent creation
---

# Analyze Component Codebase

You are helping a component owner create an operational agent. This skill guides you through analyzing their codebase.

## Prerequisites
- The component owner has a repository you can access
- You have the build-my-agent plugin loaded

## Process

### Step 1: Identify the Component

Ask the owner:
> "Which component repository should I analyze? Please provide the path or let me know which directory to look at."

Read the repository's README, main entry point, and project config (go.mod, pom.xml, package.json, etc.) to understand what the component does.

### Step 2: Analyze Logging

Search the codebase for logging patterns:

**For Go:** Look for `log.`, `zap.`, `logrus.`, `slog.`, `zerolog` imports and usage
**For Java:** Look for `slf4j`, `log4j`, `logback`, `java.util.logging` imports
**For Python:** Look for `logging`, `structlog`, `loguru` imports
**For any language:** Look for log configuration files, structured logging patterns

Ask the owner to confirm:
> "I found that your component uses [logger library] with [format]. Logs appear to be sent to [destination]. Is this correct? Also:
> 1. What OpenSearch index pattern do your logs end up in? (e.g., `component-name-*`)
> 2. Are there any custom fields in your logs that are important for debugging? (e.g., `trace_id`, `user_id`, `order_id`)"

### Step 3: Analyze Metrics

Search for metrics/monitoring patterns:

**For Go:** Look for `prometheus` package, `promhttp`, metric registration (`NewCounter`, `NewGauge`, `NewHistogram`)
**For Java:** Look for `micrometer`, `prometheus` client, `@Timed`, `@Counted` annotations
**For any language:** Look for `/metrics` endpoint, Prometheus scrape config

Ask the owner to confirm:
> "I found these metrics being exported:
> - [list of metrics found]
>
> 1. What Prometheus namespace/prefix do these use?
> 2. What's the Prometheus endpoint URL your team uses?
> 3. Are there specific metric queries you regularly check when debugging?"

### Step 4: Analyze Infrastructure Dependencies

Search for:
- **Database:** connection strings, ORM configs, migration files, SQL queries
- **Message queues:** Kafka producer/consumer configs, topic names, RabbitMQ connections
- **External APIs:** HTTP client calls, gRPC stubs, service discovery configs
- **Cache:** Redis, Memcached connections

Ask the owner:
> "I found these infrastructure dependencies:
> - [list of dependencies]
>
> 1. Which of these are critical for operations monitoring?
> 2. Are there any dependencies I missed?
> 3. For each critical dependency, what would you want the ops agent to be able to check?"

### Step 5: Understand Failure Patterns

Ask the owner:
> "What are the most common incidents or issues you deal with for this component?
> 1. What's the first thing you check when something goes wrong?
> 2. Are there specific log queries or metric dashboards you always look at?
> 3. What are the typical root causes you've seen?"

### Step 6: Produce Analysis Document

Create a structured analysis document at `<component>-analysis.md` in the working directory:

```markdown
# {{component_name}} Analysis

## Component Overview
- **Name:** {{name}}
- **Language:** {{language}}
- **Purpose:** {{what it does}}

## Logging
- **Library:** {{logger}}
- **Format:** {{structured/text}}
- **Transport:** {{how logs get to OpenSearch}}
- **OpenSearch Index:** {{index_pattern}}
- **Key Fields:** {{important fields for debugging}}

## Metrics
- **Library:** {{metrics library}}
- **Namespace:** {{prometheus namespace}}
- **Endpoint:** {{prometheus URL}}
- **Key Metrics:**
  - {{metric 1}}: {{what it measures}}
  - {{metric 2}}: {{what it measures}}

## Infrastructure Dependencies
- {{dependency 1}}: {{what, why it matters}}
- {{dependency 2}}: {{what, why it matters}}

## Failure Patterns
- {{pattern 1}}: {{symptoms, usual cause, what to check}}
- {{pattern 2}}: {{symptoms, usual cause, what to check}}

## Recommended Tools
- `log_search` (OpenSearch) — required
- `metric_query` (Prometheus) — required
- {{additional tools based on dependencies}}
```

After creating the document, tell the owner:
> "Analysis complete. I've documented the findings in `{{component}}-analysis.md`. Please review it, then we'll move on to designing the agent. Run the next skill with: **02-design-agent**"
```

- [ ] **Step 2: Commit**

```bash
git add skills/01-analyze-codebase/SKILL.md
git commit -m "feat: add 01-analyze-codebase skill"
```

---

## Task 9: Skill — 02-design-agent

**Files:**
- Create: `skills/02-design-agent/SKILL.md`

- [ ] **Step 1: Write skills/02-design-agent/SKILL.md**

```markdown
---
name: design-agent
description: Design an operational agent based on codebase analysis, determining tools, config, and system prompt content
---

# Design Operational Agent

You are designing an operational agent based on the codebase analysis from the previous step.

## Prerequisites
- The `{{component}}-analysis.md` file exists from the analyze step
- The component owner is available for Q&A

## Process

### Step 1: Load Analysis

Read the `{{component}}-analysis.md` file. Summarize the key findings to the owner:
> "Based on the analysis, here's what I'm planning for your ops agent:
> - **Tools:** [tool list]
> - **Key monitoring areas:** [what the agent will watch]
> - **Domain knowledge:** [what the agent will know about your component]"

### Step 2: Determine Tool List

**Always included:**
- `log_search` — OpenSearch log querying
- `metric_query` — Prometheus metric querying

**Add based on analysis:**
- If Kafka dependencies found → suggest `kafka_consumer` tool (check lag, read messages)
- If database found → suggest `db_query` tool (health check, slow query analysis)
- If external APIs found → suggest `api_health` tool (endpoint health checks)

For each additional tool, ask:
> "I'm suggesting a `{{tool_name}}` tool for {{reason}}. Should I include it? If yes, what endpoint/credentials does it need?"

### Step 3: Define Config Values

Compile all config values needed for `agent.yaml`:

```yaml
component: {{from analysis}}
description: {{from analysis}}

opensearch:
  endpoint: {{ask if not in analysis}}
  index_pattern: {{from analysis}}
  verify_certs: true

prometheus:
  endpoint: {{ask if not in analysis}}
  namespace: {{from analysis}}

# Additional sections per tool
```

Present to owner for confirmation.

### Step 4: Draft System Prompt Content

Based on the analysis, prepare:
1. **Component overview** — what it does, in operational context
2. **Domain knowledge** — key error codes, business logic the agent should understand
3. **Failure patterns** — from analysis, formatted as agent instructions
4. **Monitoring guidelines** — what to check first, correlation patterns

Ask the owner:
> "Here's the domain knowledge I'll give the agent:
> [draft content]
>
> Is there anything to add or correct?"

### Step 5: Present Design Summary

Present the complete design:

```
Agent Design for {{component_name}}
===================================

Tools:
  - log_search (OpenSearch)
  - metric_query (Prometheus)
  - {{additional tools}}

Config:
  {{agent.yaml content}}

System Prompt Sections:
  - Component: {{summary}}
  - Domain Knowledge: {{summary}}
  - Failure Patterns: {{count}} patterns documented
  - Guidelines: {{summary}}
```

> "Does this design look good? If yes, I'll generate the agent project. Run: **03-generate-agent**"

### Output

Save the design as `{{component}}-design.md` with all the above details, structured so the generation skill can reference it directly.
```

- [ ] **Step 2: Commit**

```bash
git add skills/02-design-agent/SKILL.md
git commit -m "feat: add 02-design-agent skill"
```

---

## Task 10: Skill — 03-generate-agent

**Files:**
- Create: `skills/03-generate-agent/SKILL.md`

- [ ] **Step 1: Write skills/03-generate-agent/SKILL.md**

```markdown
---
name: generate-agent
description: Generate a deepagents-based operational agent project from templates and design document
---

# Generate Operational Agent

You are generating a complete operational agent project based on the design from the previous step.

## Prerequisites
- The `{{component}}-design.md` file exists from the design step
- Templates are available in the build-my-agent `templates/` directory
- Reference tool implementations are in build-my-agent `tools/` directory

## Process

### Step 1: Load Design and Templates

1. Read `{{component}}-design.md`
2. Read all files in the build-my-agent `templates/` directory
3. Read the reference implementations in build-my-agent `tools/`

### Step 2: Create Project Directory

Create `{{component_name}}-ops-agent/` in the working directory with the standard structure:

```
{{component_name}}-ops-agent/
├── pyproject.toml
├── config/
│   └── agent.yaml
├── agent.py
├── tools/
│   ├── __init__.py
│   ├── log_search.py
│   ├── metric_query.py
│   └── {{additional_tools}}.py
├── prompts/
│   └── system.md
└── tests/
    ├── test_tools.py
    └── test_agent.py
```

### Step 3: Generate Each File

For each file, use the corresponding template from `templates/` as your base. Fill in the `{{placeholders}}` with values from the design document.

**Important rules:**
- Follow the template structure exactly
- Use the reference implementations in `tools/` as examples for how tools should work
- Each tool file must have exactly ONE public function
- All public functions must have docstrings
- No hardcoded URLs — everything comes from config/agent.yaml
- Tool function names must be snake_case

**For additional tools** (Kafka, DB, etc.) that don't have templates:
- Follow the same pattern as log_search.py and metric_query.py
- Load config with `_load_config()` private helper
- One public function with docstring
- Return structured data (dicts/lists, not raw client responses)

### Step 4: Write System Prompt

Using `templates/prompts/system.md.tmpl` as the base, create a rich system prompt that includes:
- Component overview from the design
- All domain knowledge
- All failure patterns
- Monitoring guidelines
- List of available tools and when to use each one

### Step 5: Write Tests

**Tool unit tests** (`tests/test_tools.py`):
- For each tool, write at least one test that mocks the external client
- Verify the tool returns the expected structure
- Verify config is loaded (not hardcoded)

**Agent integration test** (`tests/test_agent.py`):
- Verify `create_agent()` returns a valid agent
- Verify all tools are registered

### Step 6: Verify with Guard

Run the AST guard to verify the generated project:

```bash
python -m guard check {{component_name}}-ops-agent/
```

If there are violations, fix them and re-run until all checks pass.

### Step 7: Handoff

> "Agent project generated at `{{component_name}}-ops-agent/`. All guard checks pass.
>
> To run: `cd {{component_name}}-ops-agent && pip install -e '.[dev]' && python agent.py`
>
> To validate structure: `python -m guard check {{component_name}}-ops-agent/`
>
> Want me to run the final structure validation? Run: **04-validate-structure**"
```

- [ ] **Step 2: Commit**

```bash
git add skills/03-generate-agent/SKILL.md
git commit -m "feat: add 03-generate-agent skill"
```

---

## Task 11: Skill — 04-validate-structure

**Files:**
- Create: `skills/04-validate-structure/SKILL.md`

- [ ] **Step 1: Write skills/04-validate-structure/SKILL.md**

```markdown
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
> cd {{component_name}}-ops-agent
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
> - Tests: {{pass/fail status}}
>
> Your `{{component_name}}-ops-agent` is ready for use."
```

- [ ] **Step 2: Commit**

```bash
git add skills/04-validate-structure/SKILL.md
git commit -m "feat: add 04-validate-structure skill"
```

---

## Task 12: Final Integration Verification

- [ ] **Step 1: Verify complete project structure**

```bash
find . -type f | head -50
```

Verify all expected files exist per the file map.

- [ ] **Step 2: Run guard tests**

```bash
pip install -e '.[dev]'
python -m pytest tests/ -v
```

All tests should pass.

- [ ] **Step 3: Test guard CLI on a mock project**

```bash
python -m guard check tests/  # Should fail (not an agent project)
```

Verify it reports violations correctly.

- [ ] **Step 4: Commit any remaining changes**

```bash
git add -A
git commit -m "chore: final integration verification"
```
