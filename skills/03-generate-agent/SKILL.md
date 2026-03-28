---
name: generate-agent
description: Generate a deepagents-based operational agent project from templates and design document
---

# Generate Operational Agent

You are generating a complete operational agent project based on the design from the previous step.

## Prerequisites
- The `<component>-design.md` file exists from the design step
- Templates are available in the build-my-agent `templates/` directory
- Reference tool implementations are in build-my-agent `tools/` directory

## Process

### Step 1: Load Design and Templates

1. Read `<component>-design.md`
2. Read all files in the build-my-agent `templates/` directory
3. Read the reference implementations in build-my-agent `tools/`

### Step 2: Create Project Directory

Create `<component_name>-ops-agent/` in the working directory with the standard structure:

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
├── skills/
│   └── troubleshooting/
│       └── SKILL.md
└── tests/
    ├── test_tools.py
    └── test_agent.py
```

### Step 3: Generate Each File

For each file, use the corresponding template from `templates/` as your base. Fill in the placeholders with values from the design document.

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

**agent.py includes:**
- `SummarizationMiddleware` for compressing long conversations
- `MemorySaver` checkpointer for conversation persistence
- `--once "query"` flag for single invocation
- `--diagnose --once "query"` flag for structured DiagnosisReport output
- Interactive chat loop as default mode

### Step 3.5: Generate models.py

Using `templates/models.py.tmpl`, generate the DiagnosisReport model. This provides structured output when the agent is run with `--diagnose --once "query"`.

### Step 4: Write System Prompt

Using `templates/prompts/system.md.tmpl` as the base, create a rich system prompt that includes:
- Component overview from the design
- All domain knowledge
- All failure patterns
- Monitoring guidelines
- List of available tools and when to use each one

### Step 5: Write Tests

**Tool unit tests** (`tests/test_tools.py`):
- For each tool, write at least one test that mocks the external client
- Verify the tool returns the expected structure
- Verify config is loaded (not hardcoded)

**Agent integration test** (`tests/test_agent.py`):
- Verify `create_agent()` returns a valid agent
- Verify all tools are registered

### Step 6: Verify with Guard

Run the AST guard to verify the generated project:

```bash
python -m guard check <component_name>-ops-agent/
```

If there are violations, fix them and re-run until all checks pass.

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
