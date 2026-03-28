"""E2E test: render templates with sample values and verify guard passes."""

import re
from pathlib import Path

from guard.checker import validate

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
RULES_PATH = Path(__file__).parent.parent / "guard" / "rules.yaml"

# Sample values for all template placeholders.
SAMPLE_VALUES = {
    "component_name": "order-service",
    "component_description": "Handles order creation, payment, and fulfillment",
    "opensearch_endpoint": "https://opensearch.internal:9200",
    "opensearch_index_pattern": "order-service-*",
    "prometheus_endpoint": "https://prometheus.internal:9090",
    "prometheus_namespace": "order_service",
    "self_endpoint": "http://localhost:8080",
    "log_fields": "order_id, user_id, trace_id",
    "http_endpoints": "self (http://localhost:8080)",
    "additional_capabilities": "- Check order status via internal API",
    "domain_knowledge": "Order states: CREATED -> PAID -> SHIPPED -> DELIVERED",
    "failure_patterns": "- Payment timeout: check payment-gateway metrics first",
    "tool_imports": "search_logs, query_metrics, http_request",
    "tool_list": "search_logs, query_metrics, http_request",
    "tool_imports_block": (
        "from tools.log_search import search_logs\n"
        "from tools.metric_query import query_metrics\n"
        "from tools.http_client import http_request"
    ),
    "tool_all_list": '"search_logs", "query_metrics", "http_request"',
    "test_imports": (
        "from tools.log_search import search_logs\n"
        "from tools.metric_query import query_metrics\n"
        "from tools.http_client import http_request"
    ),
    "test_cases": (
        'def test_search_logs_returns_list():\n'
        '    """Verify search_logs returns a list."""\n'
        '    assert isinstance(search_logs, object)\n'
    ),
}


def _render(template_text: str) -> str:
    """Replace {{placeholder}} with sample values."""
    def replacer(match: re.Match) -> str:
        key = match.group(1)
        return SAMPLE_VALUES.get(key, match.group(0))

    # Handle escaped braces {{{{component_name}}}} -> literal {{component_name}}
    # These appear in f-string templates like agent.py.tmpl
    text = template_text.replace("{{{{component_name}}}}", "order-service")
    return re.sub(r"\{\{(\w+)\}\}", replacer, text)


def _render_project(dest: Path) -> None:
    """Render all templates into a complete agent project."""
    # Map template paths to output paths
    file_map = {
        "agent.py.tmpl": "agent.py",
        "models.py.tmpl": "models.py",
        "pyproject.toml.tmpl": "pyproject.toml",
        "config/agent.yaml.tmpl": "config/agent.yaml",
        "prompts/system.md.tmpl": "prompts/system.md",
        "tools/__init__.py.tmpl": "tools/__init__.py",
        "tools/log_search.py.tmpl": "tools/log_search.py",
        "tools/metric_query.py.tmpl": "tools/metric_query.py",
        "tools/http_client.py.tmpl": "tools/http_client.py",
        "tests/test_agent.py.tmpl": "tests/test_agent.py",
        "tests/test_tools.py.tmpl": "tests/test_tools.py",
    }

    for tmpl_rel, out_rel in file_map.items():
        tmpl_path = TEMPLATES_DIR / tmpl_rel
        out_path = dest / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        rendered = _render(tmpl_path.read_text())
        out_path.write_text(rendered)


class TestE2ERender:
    def test_rendered_project_passes_guard(self, tmp_path: Path):
        """The core guarantee: templates + sample values -> guard passes."""
        project = tmp_path / "order-service-ops-agent"
        project.mkdir()
        _render_project(project)
        errors = validate(project, RULES_PATH)
        assert errors == [], f"Guard violations: {[e.message for e in errors]}"

    def test_rendered_tool_files_have_one_public_function(self, tmp_path: Path):
        """Each rendered tool file has exactly one public function."""
        project = tmp_path / "order-service-ops-agent"
        project.mkdir()
        _render_project(project)

        import ast

        tool_dir = project / "tools"
        for py_file in tool_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            tree = ast.parse(py_file.read_text())
            public_funcs = [
                node.name
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and not node.name.startswith("_")
            ]
            assert len(public_funcs) == 1, (
                f"{py_file.name} has {len(public_funcs)} public functions: {public_funcs}"
            )

    def test_rendered_config_has_all_sections(self, tmp_path: Path):
        """Rendered agent.yaml has opensearch, prometheus, and http sections."""
        import yaml

        project = tmp_path / "order-service-ops-agent"
        project.mkdir()
        _render_project(project)

        config = yaml.safe_load((project / "config" / "agent.yaml").read_text())
        assert "opensearch" in config
        assert "prometheus" in config
        assert "http" in config
        assert config["opensearch"]["endpoint"] == "https://opensearch.internal:9200"
        assert config["http"]["base_urls"]["self"] == "http://localhost:8080"

    def test_rendered_agent_py_is_valid_python(self, tmp_path: Path):
        """Rendered agent.py parses as valid Python."""
        import ast

        project = tmp_path / "order-service-ops-agent"
        project.mkdir()
        _render_project(project)

        # Should not raise SyntaxError
        ast.parse((project / "agent.py").read_text())
