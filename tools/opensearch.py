"""OpenSearch log search tool for deepagents.

This is the reference implementation. Generated agents get a copy
customized with their component's index pattern and fields.
"""

from pathlib import Path

import yaml
from opensearchpy import OpenSearch

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "agent.yaml"
_config: dict = {}


def _get_os_config() -> dict:
    global _config
    if not _config:
        _config = yaml.safe_load(_CONFIG_PATH.read_text())
    if "opensearch" not in _config:
        raise KeyError(f"'opensearch' section missing from {_CONFIG_PATH}")
    return _config["opensearch"]


def search_logs(
    query: str,
    time_range: str = "1h",
    level: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """Search OpenSearch logs for the component.

    Args:
        query: Search keyword or Lucene query string.
        time_range: How far back to search (e.g. "1h", "30m", "7d").
        level: Filter by log level (e.g. "ERROR", "WARN"). None means all levels.
        limit: Maximum number of results to return.

    Returns:
        List of log entries, each as a dict with timestamp, level, message, and fields.
    """
    os_config = _get_os_config()

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
