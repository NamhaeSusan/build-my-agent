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
