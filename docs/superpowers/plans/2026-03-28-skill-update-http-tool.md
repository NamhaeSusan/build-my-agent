# Skill Update + HTTP Client Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a general-purpose HTTP client tool (reference + template) and update skills 03/04 to reflect the current template structure.

**Architecture:** New `http_client.py` follows the exact same lazy-config pattern as `opensearch.py` and `prometheus.py`. Skills get surgical text updates — no structural changes.

**Tech Stack:** Python stdlib `urllib.request`, PyYAML (already a dep)

---

### Task 1: HTTP Client Reference Implementation

**Files:**
- Create: `tools/http_client.py`
- Test: `tests/test_checker.py` (existing — add http_client to fixture)

- [ ] **Step 1: Write the failing guard test**

Add a test to `tests/test_checker.py` inside `TestPatternRules` that verifies an `http_client.py` tool file passes guard validation:

```python
def test_http_client_tool_accepted(self, tmp_agent_project: Path, rules_path: Path):
    (tmp_agent_project / "tools" / "http_client.py").write_text(
        'def http_request(url: str, method: str = "GET") -> dict:\n'
        '    """Send an HTTP request."""\n'
        '    config = "config/agent.yaml"\n'
        '    return {}\n'
    )
    errors = validate(tmp_agent_project, rules_path)
    assert errors == []
```

- [ ] **Step 2: Run test to verify it passes**

Run: `python3 -m pytest tests/test_checker.py::TestPatternRules::test_http_client_tool_accepted -v`
Expected: PASS (guard already supports any valid tool file)

- [ ] **Step 3: Write the reference implementation**

Create `tools/http_client.py`:

```python
"""General-purpose HTTP client tool for deepagents.

This is the reference implementation. Use this as a base when adding
HTTP-based actions to a generated agent (deploy triggers, health checks, etc.).
"""

import json
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import yaml

_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "agent.yaml"
_config: dict = {}


def _get_http_config() -> dict:
    global _config
    if not _config:
        _config = yaml.safe_load(_CONFIG_PATH.read_text())
    if "http" not in _config:
        raise KeyError(f"'http' section missing from {_CONFIG_PATH}")
    return _config["http"]


def http_request(
    url: str,
    method: str = "GET",
    headers: dict | None = None,
    body: str | None = None,
    timeout: int | None = None,
) -> dict:
    """Send an HTTP request and return the response.

    Use base_urls from config to reference endpoints by alias.
    For example, if config has base_urls.payment = "http://payment:8080",
    pass url="payment/health" to call http://payment:8080/health.

    Args:
        url: Full URL or "alias/path" using config base_urls.
        method: HTTP method (GET, POST, PUT, DELETE, PATCH).
        headers: Optional request headers.
        body: Optional request body (string).
        timeout: Request timeout in seconds. Uses config default if omitted.

    Returns:
        Dict with status_code, headers, body, and elapsed_ms.
    """
    http_config = _get_http_config()
    base_urls = http_config.get("base_urls", {})
    default_timeout = http_config.get("default_timeout", 10)

    # Resolve alias: "payment/health" -> "http://payment:8080/health"
    resolved_url = url
    if not url.startswith(("http://", "https://")):
        parts = url.split("/", 1)
        alias = parts[0]
        path = parts[1] if len(parts) > 1 else ""
        if alias in base_urls:
            base = base_urls[alias].rstrip("/")
            resolved_url = f"{base}/{path}" if path else base

    req = Request(
        resolved_url,
        method=method.upper(),
        headers=headers or {},
        data=body.encode() if body else None,
    )

    start = time.monotonic()
    try:
        with urlopen(req, timeout=timeout or default_timeout) as resp:
            resp_body = resp.read().decode()
            elapsed = (time.monotonic() - start) * 1000
            return {
                "status_code": resp.status,
                "headers": dict(resp.getheaders()),
                "body": resp_body,
                "elapsed_ms": round(elapsed, 1),
            }
    except HTTPError as e:
        elapsed = (time.monotonic() - start) * 1000
        return {
            "status_code": e.code,
            "headers": dict(e.headers),
            "body": e.read().decode(),
            "elapsed_ms": round(elapsed, 1),
        }
    except URLError as e:
        elapsed = (time.monotonic() - start) * 1000
        return {
            "status_code": 0,
            "headers": {},
            "body": str(e.reason),
            "elapsed_ms": round(elapsed, 1),
        }
```

- [ ] **Step 4: Run all guard tests**

Run: `python3 -m pytest tests/ -v`
Expected: 18 passed

- [ ] **Step 5: Commit**

```bash
git add tools/http_client.py tests/test_checker.py
git commit -m "feat: add HTTP client reference tool"
```

---

### Task 2: HTTP Client Template

**Files:**
- Create: `templates/tools/http_client.py.tmpl`
- Modify: `templates/config/agent.yaml.tmpl`

- [ ] **Step 1: Create the template**

Create `templates/tools/http_client.py.tmpl`:

```python
"""HTTP client tool for {{component_name}}."""

import json
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import yaml

# tools/ -> project root -> config/
_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "agent.yaml"
_config: dict = {}


def _get_http_config() -> dict:
    global _config
    if not _config:
        _config = yaml.safe_load(_CONFIG_PATH.read_text())
    if "http" not in _config:
        raise KeyError(f"'http' section missing from {_CONFIG_PATH}")
    return _config["http"]


def http_request(
    url: str,
    method: str = "GET",
    headers: dict | None = None,
    body: str | None = None,
    timeout: int | None = None,
) -> dict:
    """Send an HTTP request and return the response.

    Configured endpoints: {{http_endpoints}}

    Use base_urls from config to reference endpoints by alias.
    For example, if config has base_urls.payment = "http://payment:8080",
    pass url="payment/health" to call http://payment:8080/health.

    Args:
        url: Full URL or "alias/path" using config base_urls.
        method: HTTP method (GET, POST, PUT, DELETE, PATCH).
        headers: Optional request headers.
        body: Optional request body (string).
        timeout: Request timeout in seconds. Uses config default if omitted.

    Returns:
        Dict with status_code, headers, body, and elapsed_ms.
    """
    http_config = _get_http_config()
    base_urls = http_config.get("base_urls", {})
    default_timeout = http_config.get("default_timeout", 10)

    resolved_url = url
    if not url.startswith(("http://", "https://")):
        parts = url.split("/", 1)
        alias = parts[0]
        path = parts[1] if len(parts) > 1 else ""
        if alias in base_urls:
            base = base_urls[alias].rstrip("/")
            resolved_url = f"{base}/{path}" if path else base

    req = Request(
        resolved_url,
        method=method.upper(),
        headers=headers or {},
        data=body.encode() if body else None,
    )

    start = time.monotonic()
    try:
        with urlopen(req, timeout=timeout or default_timeout) as resp:
            resp_body = resp.read().decode()
            elapsed = (time.monotonic() - start) * 1000
            return {
                "status_code": resp.status,
                "headers": dict(resp.getheaders()),
                "body": resp_body,
                "elapsed_ms": round(elapsed, 1),
            }
    except HTTPError as e:
        elapsed = (time.monotonic() - start) * 1000
        return {
            "status_code": e.code,
            "headers": dict(e.headers),
            "body": e.read().decode(),
            "elapsed_ms": round(elapsed, 1),
        }
    except URLError as e:
        elapsed = (time.monotonic() - start) * 1000
        return {
            "status_code": 0,
            "headers": {},
            "body": str(e.reason),
            "elapsed_ms": round(elapsed, 1),
        }
```

- [ ] **Step 2: Add http section to config template**

Append to `templates/config/agent.yaml.tmpl` after the prometheus section:

```yaml

# Optional: include when http_client tool is added
http:
  base_urls:
    self: "{{self_endpoint}}"
  default_timeout: 10
```

- [ ] **Step 3: Commit**

```bash
git add templates/tools/http_client.py.tmpl templates/config/agent.yaml.tmpl
git commit -m "feat: add HTTP client tool template"
```

---

### Task 3: Update Skill 03-generate-agent

**Files:**
- Modify: `skills/03-generate-agent/SKILL.md`

- [ ] **Step 1: Update the project structure listing**

In Step 2 "Create Project Directory", update the tree to include `models.py`:

```
<component_name>-ops-agent/
├── pyproject.toml
├── config/
│   └── agent.yaml
├── agent.py
├── models.py
├── tools/
│   ├── __init__.py
│   ├── log_search.py
│   ├── metric_query.py
│   └── <additional_tools>.py
├── prompts/
│   └── system.md
└── tests/
    ├── test_tools.py
    └── test_agent.py
```

- [ ] **Step 2: Update the config loading guidance**

In Step 3 "Generate Each File", replace the "Important rules" section:

```markdown
**Important rules:**
- Follow the template structure exactly
- Use the reference implementations in `tools/` as examples for how tools should work
- Each tool file must have exactly ONE public function
- All public functions must have docstrings
- No hardcoded URLs — everything comes from config/agent.yaml
- Tool function names must be snake_case
- Config loading must use the lazy `_get_*_config()` pattern (not module-level loading)

**For additional tools** (Kafka, DB, etc.) that don't have templates:
- Follow the same pattern as log_search.py and metric_query.py
- For HTTP-based tools (deploy triggers, health checks, etc.), reference `tools/http_client.py`
- Use lazy config loading with `_get_*_config()` private helper
- One public function with docstring
- Return structured data (dicts/lists, not raw client responses)
```

- [ ] **Step 3: Add models.py generation step**

After Step 3 (Generate Each File), before Step 4 (Write System Prompt), add:

```markdown
### Step 3.5: Generate models.py

Using `templates/models.py.tmpl`, generate the DiagnosisReport model. This provides structured output when the agent is run with `--diagnose --once "query"`.
```

- [ ] **Step 4: Update the agent.py guidance in Step 3**

Add a note at the end of Step 3:

```markdown
**agent.py includes:**
- `SummarizationMiddleware` for compressing long conversations
- `MemorySaver` checkpointer for conversation persistence
- `--once "query"` flag for single invocation
- `--diagnose --once "query"` flag for structured DiagnosisReport output
- Interactive chat loop as default mode
```

- [ ] **Step 5: Update the handoff message in Step 7**

Replace the handoff with:

```markdown
### Step 7: Handoff

> "Agent project generated at `<component_name>-ops-agent/`. All guard checks pass.
>
> To run:
> ```bash
> cd <component_name>-ops-agent && pip install -e '.[dev]'
> python agent.py                              # interactive mode
> python agent.py --once "check error rate"    # single query
> python agent.py --diagnose --once "why is latency high?"  # structured report
> ```
>
> To validate structure: `python -m guard check <component_name>-ops-agent/`
>
> Want me to run the final structure validation? Run: **04-validate-structure**"
```

- [ ] **Step 6: Commit**

```bash
git add skills/03-generate-agent/SKILL.md
git commit -m "docs: update 03-generate-agent skill for new template structure"
```

---

### Task 4: Update Skill 04-validate-structure

**Files:**
- Modify: `skills/04-validate-structure/SKILL.md`

- [ ] **Step 1: Update the quick start in Step 2**

Replace the "If all checks pass" block:

```markdown
**If all checks pass:**
> "All structure checks passed. Your agent is ready to use.
>
> Quick start:
> ```bash
> cd <component_name>-ops-agent
> pip install -e '.[dev]'
> python agent.py                              # interactive mode
> python agent.py --once "check error rate"    # single query
> python agent.py --diagnose --once "why is latency high?"  # structured report
> ```
>
> To add new tools later:
> 1. Create a new file in `tools/` with one public function and a docstring
> 2. Use lazy config loading: `_get_*_config()` pattern (see existing tools for reference)
> 3. Add its config section to `config/agent.yaml`
> 4. Import and export from `tools/__init__.py`
> 5. Register in `agent.py` tools list
> 6. Run `python -m guard check .` to verify"
```

- [ ] **Step 2: Commit**

```bash
git add skills/04-validate-structure/SKILL.md
git commit -m "docs: update 04-validate-structure skill with new run modes"
```

---

### Task 5: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add http_client to Default Tools section**

Add after the Prometheus entry:

```markdown
- **HTTP Client** (`tools/http_client.py`) — 범용 HTTP 요청 (배포 트리거, 헬스체크 등)
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add HTTP client to default tools in CLAUDE.md"
```
