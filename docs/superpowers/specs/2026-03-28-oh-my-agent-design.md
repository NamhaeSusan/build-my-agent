# build-my-agent Design Spec

## Overview

build-my-agent is a Claude Code plugin that helps component owners create standardized operational agents for their services. It leverages `langchain-ai/deepagents` to generate agents that can query logs (OpenSearch), metrics (Prometheus), and optionally interact with other infrastructure (Kafka, DB, APIs).

The plugin provides skills (markdown guides) that walk Claude through analyzing a component's codebase, designing an agent with the component owner via Q&A, generating the agent code, and validating its structure.

## Goals

- Any component owner can create an ops agent through conversational Q&A with Claude
- Generated agents have a **unified structure** regardless of which component they serve
- Default tools: OpenSearch (logs), Prometheus (metrics)
- Extensible: users can add custom tools (Kafka, DB, response APIs, etc.)
- Runs locally; designed for future orchestration integration

## Non-Goals (for now)

- Alert system integration (company-specific, deferred)
- Centralized orchestration platform
- Multi-agent coordination between components

---

## Architecture

### Plugin Structure

```
build-my-agent/
├── skills/                        # Claude Code skills (core of the plugin)
│   ├── 01-analyze-codebase/
│   │   └── SKILL.md
│   ├── 02-design-agent/
│   │   └── SKILL.md
│   ├── 03-generate-agent/
│   │   └── SKILL.md
│   └── 04-validate-structure/
│       └── SKILL.md
│
├── templates/                     # Boilerplate for generated agent projects
│   ├── pyproject.toml.tmpl
│   ├── agent.py.tmpl
│   ├── tools/
│   │   ├── __init__.py.tmpl
│   │   ├── opensearch.py.tmpl
│   │   └── prometheus.py.tmpl
│   └── config/
│       └── agent.yaml.tmpl
│
├── guard/                         # AST structure validator
│   ├── __init__.py
│   ├── rules.yaml                 # Declarative rule definitions
│   ├── checker.py                 # Python AST-based validation
│   └── cli.py                     # CLI entry: python -m guard check <path>
│
└── tools/                         # Reference tool implementations
    ├── opensearch.py
    └── prometheus.py
```

### Usage Flow

```
Component owner activates plugin in Claude Code
        |
        v
[01-analyze]  Claude reads component repo
              Asks owner about logging, metrics, infra dependencies, failure patterns
              Produces structured analysis document
        |
        v
[02-design]   Based on analysis, determines:
              - Required tools (default + custom)
              - System prompt domain knowledge
              - Config values (endpoints, index patterns, namespaces)
              Owner approves design
        |
        v
[03-generate] Generates agent project from templates/
              Writes tool code referencing tools/ implementations
              Applies config, system prompt, tests
        |
        v
[04-validate] Runs AST guard: python -m guard check <path>
              Auto-fixes violations, re-validates
        |
        v
    Complete ops agent project
```

---

## Generated Agent Project Structure (Standard)

Every generated agent follows this exact structure, enforced by the AST guard:

```
<component-name>-ops-agent/
├── pyproject.toml
├── config/
│   └── agent.yaml                # Component-specific config
├── agent.py                      # Entry point: create_deep_agent()
├── tools/
│   ├── __init__.py               # Exports all tools
│   ├── log_search.py             # OpenSearch log query
│   ├── metric_query.py           # Prometheus metric query
│   └── ...                       # Additional tools as needed
├── prompts/
│   └── system.md                 # System prompt with domain knowledge
└── tests/
    ├── test_tools.py
    └── test_agent.py
```

### agent.yaml Example

```yaml
component: payment-service
description: "Handles payment processing and billing"

opensearch:
  endpoint: https://opensearch.internal:9200
  index_pattern: payment-*

prometheus:
  endpoint: https://prometheus.internal:9090
  namespace: payment
```

---

## AST Guard Rules

Defined declaratively in `guard/rules.yaml`:

| Category | Rule |
|----------|------|
| Structure | `agent.py`, `config/agent.yaml`, `tools/__init__.py` must exist |
| Structure | Tool files only in `tools/` directory |
| Naming | Tool file names: `snake_case.py` |
| Naming | Tool function names: `snake_case` (no classes, function-based tools) |
| Pattern | Each tool file exports exactly one public function |
| Pattern | Tool functions must have docstrings (used by deepagents as description) |
| Pattern | Config loading only from `config/agent.yaml` |
| Pattern | No hardcoded endpoints (must reference config) |

---

## Skills Detail

### 01-analyze-codebase

Instructs Claude to:
1. Explore the component repository
2. Identify and confirm with the owner:
   - **Logging**: logger library, log format, transport (stdout -> fluentd -> OpenSearch? direct?)
   - **Metrics**: Prometheus exporter presence, custom metrics, namespace
   - **Infra dependencies**: Kafka topics, DB connections, external API calls
   - **Failure patterns**: common incidents, dashboards/queries the owner checks
3. Produce a structured analysis document

### 02-design-agent

Based on analysis:
1. Determine tool list (default: log_search, metric_query + additions)
2. Compile domain knowledge for system prompt
3. Finalize agent.yaml config values
4. Present design summary to owner for approval

### 03-generate-agent

1. Scaffold project from templates/
2. Write tool implementations referencing tools/ examples
3. Apply config values from design
4. Write system prompt
5. Write basic tests

### 04-validate-structure

1. Run `python -m guard check <generated-project-path>`
2. Auto-fix violations
3. Re-validate until clean

---

## Default Tools

### OpenSearch Log Search (`tools/opensearch.py`)

- Query logs by time range, level, keyword, component fields
- Return structured results with timestamps
- Support common patterns: error log search, trace correlation, log tailing

### Prometheus Metric Query (`tools/prometheus.py`)

- Execute PromQL queries
- Support instant and range queries
- Common patterns: error rate, latency percentiles, resource usage, alerting threshold checks

### Extension Pattern

Users add tools by:
1. Creating a new file in `tools/` following the function-based pattern
2. Adding config section in `agent.yaml`
3. Exporting from `tools/__init__.py`
4. Running the guard to validate

---

## Tech Stack

- **Plugin runtime**: Claude Code plugin (skills + tools)
- **Generated agents**: Python, deepagents (`create_deep_agent()`)
- **AST guard**: Python `ast` module
- **Config format**: YAML
- **Templates**: Plain files with `.tmpl` extension (Claude fills in, not Jinja)
