# build-my-agent

Claude Code plugin that generates standardized operational agents for any component using [deepagents](https://github.com/langchain-ai/deepagents).

## What It Does

Point it at any component's codebase, and it walks you through creating an ops agent that can:

- **Search logs** via OpenSearch
- **Query metrics** via Prometheus
- **Extend** with custom tools (Kafka, DB, APIs, etc.)

Every generated agent follows the same structure — enforced by an AST guard.

## Quick Start

### Install the plugin

```bash
# From Claude Code
/plugin install build-my-agent
```

### Create an ops agent

In Claude Code, invoke the skill:

```
> create-ops-agent
```

Claude will walk you through 4 phases:

1. **Analyze** — reads your component's code, identifies logging/metrics/infra patterns
2. **Design** — determines tools, config, and domain knowledge via Q&A with you
3. **Generate** — scaffolds a complete deepagents project from templates
4. **Validate** — runs AST guard to ensure structural consistency

### Run the generated agent

```bash
cd <component>-ops-agent
pip install -e '.[dev]'
python agent.py
```

### Run modes

```bash
# Interactive chat (default)
python agent.py

# Single query
python agent.py --once "check error rate for the last hour"

# Structured diagnosis (returns JSON DiagnosisReport)
python agent.py --diagnose --once "why is latency high?"
```

## Generated Agent Structure

Every agent follows this standard layout:

```
<component>-ops-agent/
├── pyproject.toml
├── agent.py                  # Entry point: create_deep_agent()
├── models.py                 # DiagnosisReport for structured output
├── config/
│   └── agent.yaml            # Endpoints, index patterns, namespaces
├── tools/
│   ├── __init__.py
│   ├── log_search.py         # OpenSearch log query
│   ├── metric_query.py       # Prometheus metric query
│   ├── http_client.py        # HTTP requests (health checks, deploy triggers)
│   └── ...                   # Custom tools (Kafka, DB, etc.)
├── prompts/
│   └── system.md             # Domain knowledge for the agent
├── skills/
│   └── troubleshooting/
│       ├── SKILL.md           # Troubleshooting index
│       └── runbooks/          # Individual runbook files
│           ├── triage.md
│           └── common-issues.md
└── tests/
    ├── test_tools.py
    └── test_agent.py
```

## Adding Custom Tools

1. Create a new file in `tools/` with **one public function** and a **docstring**
2. Add config section in `config/agent.yaml`
3. Export from `tools/__init__.py` and register in `agent.py`
4. Validate: `python -m guard check .`

### Guard Rules

The AST guard enforces:

| Rule | Description |
|------|-------------|
| Structure | Required files and directories must exist |
| Naming | Tool files and functions must be `snake_case` |
| Pattern | One public function per tool file |
| Pattern | All tool functions must have docstrings |
| Pattern | No hardcoded URLs (must use config) |
| Pattern | Config must be loaded from config/agent.yaml |
| Lint | ruff checks all Python files (E, F, I rules) |

## Plugin Structure

```
build-my-agent/
├── .claude-plugin/plugin.json   # Plugin manifest
├── skills/                      # Claude Code skills
│   ├── 00-create-ops-agent/     # Entry point (orchestration)
│   ├── 01-analyze-codebase/     # Phase 1: Analyze
│   ├── 02-design-agent/         # Phase 2: Design
│   ├── 03-generate-agent/       # Phase 3: Generate
│   └── 04-validate-structure/   # Phase 4: Validate
├── guard/                       # AST structure validator
├── tools/                       # Reference tool implementations
├── templates/                   # Agent project boilerplate
└── tests/                       # Guard tests
```

## Development

```bash
# Run guard tests
python3 -m pytest tests/ -v

# Test guard on a project
python3 -m guard check <agent-project-path>

# Generate a sample agent from templates
python3 scripts/render_agent.py <output-dir>

# Lint
python3 -m ruff check .
```

## License

MIT
