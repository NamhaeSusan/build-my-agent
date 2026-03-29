"""Render an agent project from templates with given values."""

import sys

from render_support import SAMPLE_VALUES, render_project


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python render_agent.py <output-dir>")
        sys.exit(1)

    dest = Path(sys.argv[1])
    dest.mkdir(parents=True, exist_ok=True)
    render_project(dest, SAMPLE_VALUES)
