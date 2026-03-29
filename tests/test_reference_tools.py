from __future__ import annotations

import importlib.util
import shutil
import sys
import types
from pathlib import Path


def _prepare_tool_project(tmp_path: Path, tool_name: str) -> Path:
    project = tmp_path / "project"
    tools_dir = project / "tools"
    config_dir = project / "config"
    tools_dir.mkdir(parents=True)
    config_dir.mkdir(parents=True)

    source = Path(__file__).resolve().parent.parent / "tools" / tool_name
    shutil.copy2(source, tools_dir / tool_name)

    config_dir.joinpath("agent.yaml").write_text(
        "\n".join(
            [
                "opensearch:",
                "  endpoint: https://opensearch.internal:9200",
                "  index_pattern: logs-*",
                "  verify_certs: true",
                "prometheus:",
                "  endpoint: https://prometheus.internal:9090",
                "http:",
                "  base_urls:",
                "    api: https://api.internal",
                "  default_timeout: 7",
                "",
            ]
        )
    )
    return project


def _load_tool_module(module_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_opensearch_reference_tool_reads_project_root_config(tmp_path: Path, monkeypatch):
    project = _prepare_tool_project(tmp_path, "opensearch.py")
    stub = types.ModuleType("opensearchpy")
    stub.OpenSearch = object
    monkeypatch.setitem(sys.modules, "opensearchpy", stub)

    module = _load_tool_module(project / "tools" / "opensearch.py", "reference_opensearch")

    assert module._CONFIG_PATH == project / "config" / "agent.yaml"
    assert module._get_os_config()["endpoint"] == "https://opensearch.internal:9200"


def test_prometheus_reference_tool_reads_project_root_config(tmp_path: Path, monkeypatch):
    project = _prepare_tool_project(tmp_path, "prometheus.py")
    stub = types.ModuleType("prometheus_api_client")
    stub.PrometheusConnect = object
    monkeypatch.setitem(sys.modules, "prometheus_api_client", stub)

    module = _load_tool_module(project / "tools" / "prometheus.py", "reference_prometheus")

    assert module._CONFIG_PATH == project / "config" / "agent.yaml"
    assert module._get_prom_config()["endpoint"] == "https://prometheus.internal:9090"


def test_http_client_reference_tool_reads_project_root_config(tmp_path: Path):
    project = _prepare_tool_project(tmp_path, "http_client.py")

    module = _load_tool_module(project / "tools" / "http_client.py", "reference_http_client")

    assert module._CONFIG_PATH == project / "config" / "agent.yaml"
    assert module._get_http_config()["default_timeout"] == 7
