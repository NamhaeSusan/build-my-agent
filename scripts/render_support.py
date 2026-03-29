"""Shared render metadata and helpers."""

import re
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

FILE_MAP = {
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
    "skills/troubleshooting/SKILL.md.tmpl": "skills/troubleshooting/SKILL.md",
    "skills/troubleshooting/runbooks/triage.md.tmpl": "skills/troubleshooting/runbooks/triage.md",
    "skills/troubleshooting/runbooks/common-issues.md.tmpl": "skills/troubleshooting/runbooks/common-issues.md",
}

SAMPLE_VALUES = {
    "component_name": "url-shortener",
    "component_description": "URL shortening and redirect service backed by Redis and PostgreSQL",
    "opensearch_endpoint": "https://opensearch.internal:9200",
    "opensearch_index_pattern": "url-shortener-*",
    "prometheus_endpoint": "https://prometheus.internal:9090",
    "prometheus_namespace": "url_shortener",
    "self_endpoint": "http://url-shortener:8080",
    "log_fields": "short_code, original_url, trace_id, user_id",
    "http_endpoints": "self (http://url-shortener:8080)",
    "additional_capabilities": (
        "- Check redirect latency and error rates\n"
        "- Verify Redis connectivity via health endpoint\n"
        "- Query short URL creation and expiration stats"
    ),
    "domain_knowledge": (
        "URL shortener flow: user POSTs long URL -> service generates short_code -> "
        "stores mapping in Redis (fast lookup) + PostgreSQL (persistence).\n"
        "Redirect flow: GET /:short_code -> Redis lookup -> 302 redirect to original URL.\n"
        "Short codes expire based on TTL set at creation time.\n"
        "Redis is the primary read path; PostgreSQL is the source of truth for recovery."
    ),
    "failure_patterns": (
        "- Redis connection failure: redirects return 503, creation still works (writes to PG)\n"
        "- High 404 rate: often caused by expired short URLs or bot traffic\n"
        "- Slow redirects: check Redis latency and connection pool exhaustion\n"
        "- PG replication lag: new URLs created but not yet available for analytics queries"
    ),
    "tool_imports": "http_request, query_metrics, search_logs",
    "tool_list": "http_request, query_metrics, search_logs",
    "tool_imports_block": (
        "from tools.http_client import http_request\n"
        "from tools.log_search import search_logs\n"
        "from tools.metric_query import query_metrics"
    ),
    "tool_all_list": '"http_request", "search_logs", "query_metrics"',
    "test_imports": (
        "from tools.log_search import search_logs\n"
        "from tools.metric_query import query_metrics\n"
        "\n"
        "from tools.http_client import http_request"
    ),
    "test_cases": (
        'def test_search_logs_callable():\n'
        '    """Verify search_logs is a callable tool."""\n'
        '    assert callable(search_logs)\n'
        '\n'
        '\n'
        'def test_query_metrics_callable():\n'
        '    """Verify query_metrics is a callable tool."""\n'
        '    assert callable(query_metrics)\n'
        '\n'
        '\n'
        'def test_http_request_callable():\n'
        '    """Verify http_request is a callable tool."""\n'
        '    assert callable(http_request)\n'
    ),
    "dependency_checks": (
        "- Redis health: `http_request('self/health/redis')`\n"
        "- PostgreSQL health: `http_request('self/health/db')`"
    ),
    "common_issues": (
        "- Redis down: redirects fail with 503, check `url_shortener_redis_connection_errors_total`\n"
        "- High 404s: search logs for `level:WARN AND short_code` to find missing codes\n"
        "- Slow creation: check PG connection pool with `url_shortener_pg_pool_active`"
    ),
}


def render(template_text: str, values: dict) -> str:
    """Replace {{placeholder}} with values. Raises on unknown keys."""

    def replacer(match: re.Match) -> str:
        key = match.group(1)
        if key not in values:
            raise KeyError(f"Unknown placeholder: {{{{{key}}}}}")
        return values[key]

    return re.sub(r"\{\{(\w+)\}\}", replacer, template_text)


def render_project(dest: Path, values: dict) -> None:
    """Render all templates into a complete agent project."""
    for tmpl_rel, out_rel in FILE_MAP.items():
        tmpl_path = TEMPLATES_DIR / tmpl_rel
        out_path = dest / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        rendered = render(tmpl_path.read_text(), values)
        out_path.write_text(rendered)
    print(f"Generated {len(FILE_MAP)} files in {dest}")
