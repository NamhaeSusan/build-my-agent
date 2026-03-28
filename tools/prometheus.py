"""Prometheus metric query tool for deepagents.

This is the reference implementation. Generated agents get a copy
customized with their component's namespace and common queries.
"""

import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml
from prometheus_api_client import PrometheusConnect

_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "agent.yaml"
_config: dict = {}


def _get_prom_config() -> dict:
    global _config
    if not _config:
        _config = yaml.safe_load(_CONFIG_PATH.read_text())
    if "prometheus" not in _config:
        raise KeyError(f"'prometheus' section missing from {_CONFIG_PATH}")
    return _config["prometheus"]


def _parse_duration(duration: str) -> timedelta:
    match = re.match(r"^(\d+)([smhd])$", duration)
    if not match:
        raise ValueError(f"Invalid duration: {duration}")
    value, unit = int(match.group(1)), match.group(2)
    units = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days"}
    return timedelta(**{units[unit]: value})


def query_metrics(
    promql: str,
    duration: str = "5m",
    step: str = "15s",
) -> dict:
    """Query Prometheus metrics for the component.

    Args:
        promql: PromQL query string.
        duration: Time range for range queries (e.g. "5m", "1h").
        step: Query resolution step (e.g. "15s", "1m").

    Returns:
        Dict with 'result_type' ("vector" or "matrix") and 'data' (list of series).
        Each series has 'metric' (label dict) and 'values' (list of [timestamp, value]).
    """
    prom_config = _get_prom_config()

    prom = PrometheusConnect(
        url=prom_config["endpoint"],
    )

    # Try range query first, fall back to instant
    end_time = datetime.now(tz=timezone.utc)
    start_time = end_time - _parse_duration(duration)
    result = prom.custom_query_range(
        query=promql,
        start_time=start_time,
        end_time=end_time,
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
