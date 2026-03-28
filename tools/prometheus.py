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
