"""Render an agent project from templates with given values."""

import importlib.util
import sys
from pathlib import Path


def _load_render_support():
    module_path = Path(__file__).with_name("render_support.py")
    spec = importlib.util.spec_from_file_location("render_support", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_render_support = _load_render_support()
SAMPLE_VALUES = _render_support.SAMPLE_VALUES
render_project = _render_support.render_project


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python render_agent.py <output-dir>")
        sys.exit(1)

    dest = Path(sys.argv[1])
    dest.mkdir(parents=True, exist_ok=True)
    render_project(dest, SAMPLE_VALUES)
