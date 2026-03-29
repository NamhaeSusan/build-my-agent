import tempfile
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_root_pytest_collects_only_repo_tests():
    with tempfile.TemporaryDirectory(dir=REPO_ROOT, prefix="transient-", suffix="-ops-agent") as temp_dir:
        generated_project = Path(temp_dir)
        generated_tests = generated_project / "tests"
        generated_tests.mkdir(parents=True)
        (generated_tests / "test_should_not_collect.py").write_text(
            "raise RuntimeError('generated project was collected')\n"
        )

        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

    output = f"{result.stdout}\n{result.stderr}"

    assert result.returncode == 0, output
    assert "tests/test_checker.py::TestStructureRules::test_valid_project_passes" in result.stdout
    assert "test_should_not_collect.py" not in output
