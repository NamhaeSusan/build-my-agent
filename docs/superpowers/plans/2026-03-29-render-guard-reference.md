# Render Metadata + Guard Contract + Reference Tool Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove render metadata duplication, expand the guard contract to match stable generated outputs, and align reference tools with the template config path convention.

**Architecture:** Introduce a shared render support module under `scripts/` so the renderer script and E2E render test consume the same file map, sample values, and render helpers. Then expand `guard/rules.yaml` narrowly to require `models.py` and `skills/troubleshooting/SKILL.md`, updating fixtures and guard tests to keep the contract explicit. Finally, align reference tool config paths with the generated template convention and add runtime tests that load the reference modules from temporary project layouts without relying on external service libraries being installed.

**Tech Stack:** Python 3.10+, pytest, importlib, subprocess, PyYAML

---

## File Map

### Files to Create

- `scripts/render_support.py` — shared render metadata, sample values, and render helpers
- `tests/test_reference_tools.py` — regression tests for reference tool config path behavior
- `claude_history/2026-03-29-render-guard-reference-impl.md` — implementation record for the batch commit

### Files to Modify

- `scripts/render_agent.py` — import shared render metadata instead of defining local copies
- `tests/test_e2e_render.py` — load shared render metadata instead of defining local copies
- `guard/rules.yaml` — require `models.py` and `skills/troubleshooting/SKILL.md`
- `tests/conftest.py` — update the valid-project fixture to include newly required files
- `tests/test_checker.py` — add guard regression tests for the new required files
- `tools/opensearch.py` — align config path resolution with generated templates
- `tools/prometheus.py` — align config path resolution with generated templates
- `tools/http_client.py` — align config path resolution with generated templates

---

### Task 1: Single-Source Render Metadata

**Files:**
- Create: `scripts/render_support.py`
- Modify: `scripts/render_agent.py`
- Modify: `tests/test_e2e_render.py`

- [ ] **Step 1: Write the failing render support test**

Add a new test to `tests/test_e2e_render.py` that loads `scripts/render_support.py` via `importlib.util.spec_from_file_location()` and asserts the shared metadata exposes the expected standard files:

```python
def _load_render_support():
    module_path = Path(__file__).parent.parent / "scripts" / "render_support.py"
    spec = importlib.util.spec_from_file_location("render_support", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_render_support_has_expected_standard_files():
    render_support = _load_render_support()
    assert render_support.FILE_MAP["models.py.tmpl"] == "models.py"
    assert (
        render_support.FILE_MAP["skills/troubleshooting/SKILL.md.tmpl"]
        == "skills/troubleshooting/SKILL.md"
    )
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python3 -m pytest tests/test_e2e_render.py::test_render_support_has_expected_standard_files -q`

Expected: FAIL because `scripts/render_support.py` does not exist yet.

- [ ] **Step 3: Implement the shared render support module**

Create `scripts/render_support.py` with:

- `TEMPLATES_DIR`
- `FILE_MAP`
- `SAMPLE_VALUES`
- `render(template_text: str, values: dict) -> str`
- `render_project(dest: Path, values: dict) -> None`

Keep the existing template/output mapping and sample values exactly aligned with current behavior.

- [ ] **Step 4: Refactor both consumers to use the shared source**

Update `scripts/render_agent.py` to import:

```python
from render_support import SAMPLE_VALUES, render_project
```

and keep only the CLI wrapper / destination handling in the script.

Update `tests/test_e2e_render.py` to load `scripts/render_support.py` with `importlib.util.spec_from_file_location()` and reuse:

- `FILE_MAP`
- `SAMPLE_VALUES`
- `render_project`

Remove the duplicated local `FILE_MAP`, `SAMPLE_VALUES`, `_render()`, and `_render_project()` definitions from the test.

- [ ] **Step 5: Run render-focused tests**

Run: `python3 -m pytest tests/test_e2e_render.py -q`

Expected: PASS

---

### Task 2: Narrow Guard Contract Expansion

**Files:**
- Modify: `guard/rules.yaml`
- Modify: `tests/conftest.py`
- Modify: `tests/test_checker.py`

- [ ] **Step 1: Write the failing guard tests**

Add two tests to `tests/test_checker.py` inside `TestStructureRules`:

```python
def test_missing_models_py(self, tmp_agent_project: Path, rules_path: Path):
    (tmp_agent_project / "models.py").write_text(
        "from pydantic import BaseModel\n\n\nclass DiagnosisReport(BaseModel):\n    summary: str\n"
    )
    (tmp_agent_project / "skills" / "troubleshooting").mkdir(parents=True)
    (tmp_agent_project / "skills" / "troubleshooting" / "SKILL.md").write_text(
        "# Test Service Troubleshooting\n"
    )
    (tmp_agent_project / "models.py").unlink()
    errors = validate(tmp_agent_project, rules_path)
    assert any("models.py" in e.message for e in errors)


def test_missing_troubleshooting_skill(self, tmp_agent_project: Path, rules_path: Path):
    (tmp_agent_project / "models.py").write_text(
        "from pydantic import BaseModel\n\n\nclass DiagnosisReport(BaseModel):\n    summary: str\n"
    )
    (tmp_agent_project / "skills" / "troubleshooting").mkdir(parents=True)
    skill_path = tmp_agent_project / "skills" / "troubleshooting" / "SKILL.md"
    skill_path.write_text("# Test Service Troubleshooting\n")
    skill_path.unlink()
    errors = validate(tmp_agent_project, rules_path)
    assert any("skills/troubleshooting/SKILL.md" in e.message for e in errors)
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python3 -m pytest tests/test_checker.py::TestStructureRules::test_missing_models_py tests/test_checker.py::TestStructureRules::test_missing_troubleshooting_skill -q`

Expected: FAIL because the guard does not require those files yet.

- [ ] **Step 3: Update the guard contract**

Modify `guard/rules.yaml`:

```yaml
structure:
  required_files:
    - "agent.py"
    - "models.py"
    - "config/agent.yaml"
    - "tools/__init__.py"
    - "prompts/system.md"
    - "skills/troubleshooting/SKILL.md"
```

Do not add troubleshooting runbook files to the required set.

- [ ] **Step 4: Update the valid-project fixture**

Modify `tests/conftest.py` so `tmp_agent_project` creates:

- `models.py`
- `skills/troubleshooting/SKILL.md`
- the nested directory `skills/troubleshooting/`

Use minimal valid file contents, for example:

```python
(project / "models.py").write_text(
    "from pydantic import BaseModel\n\n\nclass DiagnosisReport(BaseModel):\n    summary: str\n"
)

(project / "skills" / "troubleshooting").mkdir()
(project / "skills" / "troubleshooting" / "SKILL.md").write_text(
    "# Test Service Troubleshooting\n"
)
```

- [ ] **Step 5: Run guard-focused tests**

Run: `python3 -m pytest tests/test_checker.py -q`

Expected: PASS

---

### Task 3: Align and Verify Reference Tool Config Paths

**Files:**
- Modify: `tools/opensearch.py`
- Modify: `tools/prometheus.py`
- Modify: `tools/http_client.py`
- Create: `tests/test_reference_tools.py`

- [ ] **Step 1: Write the failing reference tool tests**

Create `tests/test_reference_tools.py` with helpers that:

1. Create a temporary project layout:
   - `tmp/project/tools/<tool_file>.py`
   - `tmp/project/config/agent.yaml`
2. Copy the current reference tool source into the temp `tools/` directory
3. Stub external imports with `monkeypatch.setitem(sys.modules, ...)`
4. Load the copied tool module via `importlib.util.spec_from_file_location()`
5. Assert `_CONFIG_PATH` resolves to `project / "config" / "agent.yaml"`
6. Assert `_get_*_config()` reads the correct section

Representative test shape:

```python
def test_opensearch_reference_tool_reads_project_root_config(tmp_path: Path, monkeypatch):
    project = _prepare_tool_project(tmp_path, "opensearch.py")
    stub = types.ModuleType("opensearchpy")
    stub.OpenSearch = object
    monkeypatch.setitem(sys.modules, "opensearchpy", stub)

    module = _load_tool_module(project / "tools" / "opensearch.py", "reference_opensearch")

    assert module._CONFIG_PATH == project / "config" / "agent.yaml"
    assert module._get_os_config()["endpoint"] == "https://opensearch.internal:9200"
```

Mirror the same pattern for `prometheus.py` and `http_client.py`.

- [ ] **Step 2: Run the new tests to verify they fail**

Run: `python3 -m pytest tests/test_reference_tools.py -q`

Expected: FAIL because the current reference tools still resolve config from `tools/config/agent.yaml`.

- [ ] **Step 3: Align the reference tool paths**

Update each reference tool to use the generated-template convention:

```python
# tools/ -> project root -> config/
_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "agent.yaml"
```

Apply this to:

- `tools/opensearch.py`
- `tools/prometheus.py`
- `tools/http_client.py`

Do not change public tool behavior in this task beyond config path alignment.

- [ ] **Step 4: Run reference tool tests**

Run: `python3 -m pytest tests/test_reference_tools.py -q`

Expected: PASS

- [ ] **Step 5: Run the maintained suite**

Run: `python3 -m pytest tests -q`

Expected: PASS

---

### Task 4: Record the Work and Commit

**Files:**
- Create: `claude_history/2026-03-29-render-guard-reference-impl.md`
- Modify: all files from Tasks 1-3

- [ ] **Step 1: Write the implementation history file**

Create `claude_history/2026-03-29-render-guard-reference-impl.md`:

```markdown
# Render Metadata + Guard Contract + Reference Tool Alignment

## Date
2026-03-29

## Summary
Deduplicated render metadata, expanded the guard contract to require stable generated outputs, and aligned reference tools with the template config convention.

## Changes
- Added a shared render support module and updated the renderer script and E2E render test to use it
- Expanded guard required files to include `models.py` and `skills/troubleshooting/SKILL.md`
- Updated the valid project fixture and guard tests for the new required files
- Aligned reference tool config paths with generated templates
- Added regression tests for reference tool config resolution
```

- [ ] **Step 2: Run final verification**

Run: `python3 -m pytest tests -q`

Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add \
  scripts/render_support.py \
  scripts/render_agent.py \
  tests/test_e2e_render.py \
  guard/rules.yaml \
  tests/conftest.py \
  tests/test_checker.py \
  tools/opensearch.py \
  tools/prometheus.py \
  tools/http_client.py \
  tests/test_reference_tools.py \
  claude_history/2026-03-29-render-guard-reference-impl.md

git commit -m "refactor: align render metadata and guard contract" -m "Deduplicate render metadata, require stable generated outputs, and align reference tools with the template config convention.\n\nHistory: claude_history/2026-03-29-render-guard-reference-impl.md"
```
