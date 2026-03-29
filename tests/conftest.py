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
    (project / "skills").mkdir()

    # agent.py
    (project / "agent.py").write_text(textwrap.dedent("""\
        from deepagents import create_deep_agent

        from tools import query_metrics, search_logs


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

    # models.py
    (project / "models.py").write_text(textwrap.dedent("""\
        from pydantic import BaseModel


        class DiagnosisReport(BaseModel):
            summary: str
    """))

    # skills/troubleshooting/SKILL.md
    (project / "skills" / "troubleshooting").mkdir()
    (project / "skills" / "troubleshooting" / "SKILL.md").write_text(
        "# Test Service Troubleshooting"
    )

    # tools/__init__.py
    (project / "tools" / "__init__.py").write_text(textwrap.dedent("""\
        from tools.log_search import search_logs
        from tools.metric_query import query_metrics

        __all__ = ["search_logs", "query_metrics"]
    """))

    # tools/log_search.py — valid tool (ruff-clean)
    (project / "tools" / "log_search.py").write_text(
        'import yaml\n'
        '\n'
        '\n'
        'def _load_config():\n'
        '    with open("config/agent.yaml") as f:\n'
        '        return yaml.safe_load(f)\n'
        '\n'
        '\n'
        'def search_logs(query: str, time_range: str = "1h") -> list[dict]:\n'
        '    """Search OpenSearch logs for the component."""\n'
        '    config = _load_config()\n'
        '    return [{"endpoint": config["opensearch"]["endpoint"], "query": query}]\n'
    )

    # tools/metric_query.py — valid tool (ruff-clean)
    (project / "tools" / "metric_query.py").write_text(
        'import yaml\n'
        '\n'
        '\n'
        'def _load_config():\n'
        '    with open("config/agent.yaml") as f:\n'
        '        return yaml.safe_load(f)\n'
        '\n'
        '\n'
        'def query_metrics(promql: str, duration: str = "5m") -> dict:\n'
        '    """Query Prometheus metrics for the component."""\n'
        '    config = _load_config()\n'
        '    return {"endpoint": config["prometheus"]["endpoint"], "promql": promql}\n'
    )

    return project


@pytest.fixture
def rules_path() -> Path:
    """Path to the guard rules file."""
    return Path(__file__).parent.parent / "guard" / "rules.yaml"
