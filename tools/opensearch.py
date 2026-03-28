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
