"""E2E test: render templates with sample values and verify guard passes."""

import importlib.util
from pathlib import Path

import pytest

from guard.checker import validate

RULES_PATH = Path(__file__).parent.parent / "guard" / "rules.yaml"


def _load_render_support():
    module_path = Path(__file__).parent.parent / "scripts" / "render_support.py"
    spec = importlib.util.spec_from_file_location("render_support", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def render_support():
    module_path = Path(__file__).parent.parent / "scripts" / "render_support.py"
    if not module_path.exists():
        pytest.skip("scripts/render_support.py is missing")
    return _load_render_support()


def test_render_support_has_expected_standard_files():
    render_support = _load_render_support()
    assert render_support.FILE_MAP["models.py.tmpl"] == "models.py"
    assert (
        render_support.FILE_MAP["skills/troubleshooting/SKILL.md.tmpl"]
        == "skills/troubleshooting/SKILL.md"
    )


class TestE2ERender:
    def test_rendered_project_passes_guard(self, tmp_path: Path, render_support):
        """The core guarantee: templates + sample values -> guard passes."""
        project = tmp_path / "order-service-ops-agent"
        project.mkdir()
        render_support.render_project(project, render_support.SAMPLE_VALUES)
        errors = validate(project, RULES_PATH)
        assert errors == [], f"Guard violations: {[e.message for e in errors]}"

    def test_rendered_tool_files_have_one_public_function(self, tmp_path: Path, render_support):
        """Each rendered tool file has exactly one public function."""
        project = tmp_path / "order-service-ops-agent"
        project.mkdir()
        render_support.render_project(project, render_support.SAMPLE_VALUES)

        import ast

        tool_dir = project / "tools"
        for py_file in tool_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            tree = ast.parse(py_file.read_text())
            public_funcs = [
                node.name
                for node in ast.iter_child_nodes(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and not node.name.startswith("_")
            ]
            assert len(public_funcs) == 1, (
                f"{py_file.name} has {len(public_funcs)} public functions: {public_funcs}"
            )

    def test_rendered_config_has_all_sections(self, tmp_path: Path, render_support):
        """Rendered agent.yaml has opensearch, prometheus, and http sections."""
        import yaml

        project = tmp_path / "order-service-ops-agent"
        project.mkdir()
        render_support.render_project(project, render_support.SAMPLE_VALUES)

        config = yaml.safe_load((project / "config" / "agent.yaml").read_text())
        assert "opensearch" in config
        assert "prometheus" in config
        assert "http" in config
        assert config["opensearch"]["endpoint"] == "https://opensearch.internal:9200"
        assert config["http"]["base_urls"]["self"] == render_support.SAMPLE_VALUES["self_endpoint"]

    def test_rendered_agent_py_is_valid_python(self, tmp_path: Path, render_support):
        """Rendered agent.py parses as valid Python."""
        import ast

        project = tmp_path / "order-service-ops-agent"
        project.mkdir()
        render_support.render_project(project, render_support.SAMPLE_VALUES)

        # Should not raise SyntaxError
        ast.parse((project / "agent.py").read_text())
