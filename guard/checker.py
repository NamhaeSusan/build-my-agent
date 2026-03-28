"""AST-based structure validator for generated agent projects."""

import ast
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Violation:
    """A single rule violation."""
    rule: str       # e.g. "structure.required_files"
    message: str    # human-readable description
    path: str       # file or directory that caused the violation


def validate(project_path: Path, rules_path: Path) -> list[Violation]:
    """Validate a generated agent project against the guard rules.

    Args:
        project_path: Root directory of the generated agent project.
        rules_path: Path to the rules.yaml file.

    Returns:
        List of Violation objects. Empty list means the project is valid.
    """
    with open(rules_path) as f:
        rules = yaml.safe_load(f)

    violations: list[Violation] = []
    violations.extend(_check_structure(project_path, rules.get("structure", {})))
    violations.extend(_check_naming(project_path, rules.get("naming", {}), rules.get("structure", {})))
    violations.extend(_check_patterns(project_path, rules.get("patterns", {}), rules.get("structure", {})))
    violations.extend(_check_lint(project_path, rules.get("lint", {}), rules.get("structure", {})))
    return violations


def _check_structure(project: Path, rules: dict) -> list[Violation]:
    violations = []
    for f in rules.get("required_files", []):
        if not (project / f).is_file():
            violations.append(Violation(
                rule="structure.required_files",
                message=f"Required file missing: {f}",
                path=str(project / f),
            ))
    for d in rules.get("required_dirs", []):
        if not (project / d).is_dir():
            violations.append(Violation(
                rule="structure.required_dirs",
                message=f"Required directory missing: {d}",
                path=str(project / d),
            ))
    return violations


_SNAKE_CASE_RE = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")


def _is_snake_case(name: str) -> bool:
    return _SNAKE_CASE_RE.match(name) is not None


def _check_naming(project: Path, rules: dict, structure: dict) -> list[Violation]:
    violations = []
    tool_dir = project / structure.get("tool_dir", "tools")
    if not tool_dir.is_dir():
        return violations

    for py_file in tool_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        # Check file naming
        stem = py_file.stem
        if rules.get("tool_files") == "snake_case" and not _is_snake_case(stem):
            violations.append(Violation(
                rule="naming.tool_files",
                message=f"Tool file name is not snake_case: {py_file.name}",
                path=str(py_file),
            ))

        # Check function naming
        if rules.get("tool_functions") == "snake_case":
            try:
                tree = ast.parse(py_file.read_text())
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
                    if not _is_snake_case(node.name):
                        violations.append(Violation(
                            rule="naming.tool_functions",
                            message=f"Tool function name is not snake_case: {node.name} in {py_file.name}",
                            path=str(py_file),
                        ))

    return violations


_URL_RE = re.compile(r"""https?://[^\s"']+""")


def _check_patterns(project: Path, rules: dict, structure: dict) -> list[Violation]:
    violations = []
    tool_dir = project / structure.get("tool_dir", "tools")
    if not tool_dir.is_dir():
        return violations

    for py_file in tool_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        source = py_file.read_text()
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        public_functions = [
            node for node in ast.iter_child_nodes(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_")
        ]

        # One public function per tool
        if rules.get("one_public_function_per_tool") and len(public_functions) != 1:
            names = [f.name for f in public_functions]
            if len(public_functions) == 0:
                msg = f"Tool file must have exactly one public function, found none in {py_file.name}"
            else:
                msg = (
                    f"Tool file must have exactly one public function, "
                    f"found {len(public_functions)}: {names} in {py_file.name}"
                )
            violations.append(Violation(
                rule="patterns.one_public_function_per_tool",
                message=msg,
                path=str(py_file),
            ))

        # Docstring required
        if rules.get("tool_docstring_required"):
            for func in public_functions:
                if not ast.get_docstring(func):
                    violations.append(Violation(
                        rule="patterns.tool_docstring_required",
                        message=f"Tool function missing docstring: {func.name} in {py_file.name}",
                        path=str(py_file),
                    ))

        # No hardcoded endpoints (skip docstrings — they may contain example URLs)
        if rules.get("no_hardcoded_endpoints"):
            docstrings = {
                ast.get_docstring(node, clean=False)
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module))
                and ast.get_docstring(node, clean=False)
            }
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    if node.value in docstrings:
                        continue
                    if _URL_RE.search(node.value):
                        violations.append(Violation(
                            rule="patterns.no_hardcoded_endpoints",
                            message=f"Hardcoded URL found in {py_file.name}: {node.value}",
                            path=str(py_file),
                        ))

        # Config source must be referenced (as literal string or path components)
        config_source = rules.get("config_source")
        if config_source:
            # Check for literal string "config/agent.yaml" OR
            # path components like Path(...) / "config" / "agent.yaml"
            string_constants = [
                node.value for node in ast.walk(tree)
                if isinstance(node, ast.Constant) and isinstance(node.value, str)
            ]
            parts = config_source.split("/")  # ["config", "agent.yaml"]
            has_literal = config_source in string_constants
            has_path_parts = all(p in string_constants for p in parts)
            if not has_literal and not has_path_parts:
                violations.append(Violation(
                    rule="patterns.config_source",
                    message=f"Tool file must reference config source '{config_source}': {py_file.name}",
                    path=str(py_file),
                ))

    return violations


def _check_lint(project: Path, rules: dict, structure: dict) -> list[Violation]:
    """Run ruff on the project's Python files."""
    if not rules.get("ruff", False):
        return []

    select = rules.get("ruff_select", "E,F,I")
    ignore = rules.get("ruff_ignore", "")

    tool_dir = project / structure.get("tool_dir", "tools")
    py_files = [f for f in tool_dir.glob("*.py") if f.name != "__init__.py"] if tool_dir.is_dir() else []
    if not py_files:
        return []

    cmd = ["ruff", "check", "--select", select]
    if ignore:
        cmd.extend(["--ignore", ignore])
    cmd.extend(str(f) for f in py_files)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)  # noqa: S603
    except FileNotFoundError:
        return [Violation(
            rule="lint.ruff",
            message="ruff not installed — install with: pip install ruff",
            path=str(project),
        )]

    if result.returncode == 0:
        return []

    violations = []
    for line in result.stdout.strip().splitlines():
        # ruff output: path/file.py:10:5: E302 expected 2 blank lines
        violations.append(Violation(
            rule="lint.ruff",
            message=line,
            path=str(project),
        ))
    return violations
