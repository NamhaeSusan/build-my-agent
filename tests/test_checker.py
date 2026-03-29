from pathlib import Path

from guard.checker import validate


class TestStructureRules:
    def test_valid_project_passes(self, tmp_agent_project: Path, rules_path: Path):
        errors = validate(tmp_agent_project, rules_path)
        assert errors == []

    def test_missing_agent_py(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "agent.py").unlink()
        errors = validate(tmp_agent_project, rules_path)
        assert any("agent.py" in e.message for e in errors)

    def test_missing_config_dir(self, tmp_agent_project: Path, rules_path: Path):
        import shutil
        shutil.rmtree(tmp_agent_project / "config")
        errors = validate(tmp_agent_project, rules_path)
        assert any("config" in e.message for e in errors)

    def test_missing_tools_init(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "__init__.py").unlink()
        errors = validate(tmp_agent_project, rules_path)
        assert any("tools/__init__.py" in e.message for e in errors)


class TestNamingRules:
    def test_camel_case_tool_file_rejected(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "LogSearch.py").write_text(
            'def log_search():\n    """Search logs."""\n    pass\n'
        )
        errors = validate(tmp_agent_project, rules_path)
        assert any("LogSearch.py" in e.message for e in errors)

    def test_camel_case_function_rejected(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "bad_tool.py").write_text(
            'def SearchLogs():\n    """Search logs."""\n    pass\n'
        )
        errors = validate(tmp_agent_project, rules_path)
        assert any("SearchLogs" in e.message for e in errors)

    def test_snake_case_tool_file_accepted(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "kafka_consumer.py").write_text(
            'def consume_messages():\n    """Consume Kafka messages."""\n    return {"config": "config/agent.yaml"}\n'
        )
        errors = validate(tmp_agent_project, rules_path)
        assert errors == []


class TestPatternRules:
    def test_multiple_public_functions_rejected(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "bad_tool.py").write_text(
            'def func_a():\n    """A."""\n    pass\n\ndef func_b():\n    """B."""\n    pass\n'
        )
        errors = validate(tmp_agent_project, rules_path)
        assert any("one public function" in e.message.lower() for e in errors)

    def test_missing_docstring_rejected(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "no_doc.py").write_text(
            "def no_docs():\n    pass\n"
        )
        errors = validate(tmp_agent_project, rules_path)
        assert any("docstring" in e.message.lower() for e in errors)

    def test_hardcoded_url_rejected(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "hardcoded.py").write_text(
            'def bad_tool():\n    """Bad."""\n    url = "https://opensearch.internal:9200"\n    return url\n'
        )
        errors = validate(tmp_agent_project, rules_path)
        assert any("hardcoded" in e.message.lower() for e in errors)

    def test_zero_public_functions_rejected(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "empty_tool.py").write_text(
            'def _helper():\n    pass\n'
        )
        errors = validate(tmp_agent_project, rules_path)
        assert any("one public function" in e.message.lower() for e in errors)

    def test_async_public_function_counted(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "async_tool.py").write_text(
            'async def fetch_data():\n    """Fetch data."""\n    return {"config": "config/agent.yaml"}\n'
        )
        errors = validate(tmp_agent_project, rules_path)
        assert errors == []

    def test_missing_config_source_rejected(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "no_config.py").write_text(
            'def do_stuff():\n    """Do stuff."""\n    pass\n'
        )
        errors = validate(tmp_agent_project, rules_path)
        assert any("config source" in e.message.lower() for e in errors)

    def test_config_loaded_from_yaml_accepted(self, tmp_agent_project: Path, rules_path: Path):
        """The default fixture tools load config properly — should pass."""
        errors = validate(tmp_agent_project, rules_path)
        assert errors == []

    def test_http_client_tool_accepted(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "http_client.py").write_text(
            'def http_request(url: str, method: str = "GET") -> dict:\n'
            '    """Send an HTTP request."""\n'
            '    return {"config": "config/agent.yaml", "url": url}\n'
        )
        errors = validate(tmp_agent_project, rules_path)
        assert errors == []


class TestLintRules:
    def test_valid_project_passes_ruff(self, tmp_agent_project: Path, rules_path: Path):
        errors = validate(tmp_agent_project, rules_path)
        ruff_errors = [e for e in errors if e.rule == "lint.ruff"]
        assert ruff_errors == []

    def test_unused_import_caught_by_ruff(self, tmp_agent_project: Path, rules_path: Path):
        (tmp_agent_project / "tools" / "bad_lint.py").write_text(
            'import os\n\n\n'
            'def do_thing():\n'
            '    """Do thing."""\n'
            '    config = "config/agent.yaml"\n'
            '    return {}\n'
        )
        errors = validate(tmp_agent_project, rules_path)
        ruff_errors = [e for e in errors if e.rule == "lint.ruff"]
        assert any("F401" in e.message for e in ruff_errors)


class TestLintScopeRules:
    def test_project_scope_catches_agent_py_lint_error(
        self, tmp_agent_project: Path, rules_path: Path
    ):
        """Lint with project scope should catch errors in agent.py (outside tools/)."""
        (tmp_agent_project / "agent.py").write_text(
            'import os\n\n\n'
            'def create_agent():\n'
            '    """Create agent."""\n'
            '    return {}\n'
        )
        errors = validate(tmp_agent_project, rules_path)
        ruff_errors = [e for e in errors if e.rule == "lint.ruff"]
        assert any("F401" in e.message and "agent.py" in e.message for e in ruff_errors)

    def test_project_scope_skips_init_files(
        self, tmp_agent_project: Path, rules_path: Path
    ):
        """__init__.py files should be skipped from lint even with project scope."""
        errors = validate(tmp_agent_project, rules_path)
        ruff_errors = [e for e in errors if e.rule == "lint.ruff"]
        assert ruff_errors == []

    def test_tools_scope_ignores_agent_py(
        self, tmp_agent_project: Path, rules_path: Path
    ):
        """With lint.scope set to 'tools', agent.py lint errors should be ignored."""
        import yaml

        (tmp_agent_project / "agent.py").write_text(
            'import os\n\n\n'
            'def create_agent():\n'
            '    """Create agent."""\n'
            '    return {}\n'
        )

        with open(rules_path) as f:
            rules = yaml.safe_load(f)
        rules["lint"]["scope"] = "tools"

        scoped_rules = tmp_agent_project / "scoped_rules.yaml"
        scoped_rules.write_text(yaml.dump(rules))

        errors = validate(tmp_agent_project, scoped_rules)
        ruff_errors = [e for e in errors if e.rule == "lint.ruff"]
        assert not any("agent.py" in e.message for e in ruff_errors)
