import subprocess
import sys
from pathlib import Path


def test_cli_valid_project(tmp_agent_project: Path, rules_path: Path):
    result = subprocess.run(
        [sys.executable, "-m", "guard", "check", str(tmp_agent_project)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "passed" in result.stdout.lower()


def test_cli_invalid_project(tmp_agent_project: Path, rules_path: Path):
    (tmp_agent_project / "agent.py").unlink()
    result = subprocess.run(
        [sys.executable, "-m", "guard", "check", str(tmp_agent_project)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "agent.py" in result.stdout


def test_cli_no_path_shows_usage():
    result = subprocess.run(
        [sys.executable, "-m", "guard"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
