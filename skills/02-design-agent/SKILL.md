---
name: design-agent
description: Design an operational agent based on codebase analysis, determining tools, config, and system prompt content
---

# Design Operational Agent

You are designing an operational agent based on the codebase analysis from the previous step.

## Prerequisites
- The `<component>-analysis.md` file exists from the analyze step
- The component owner is available for Q&A

## Process

### Step 1: Load Analysis

Read the `<component>-analysis.md` file. Summarize the key findings to the owner:
> "Based on the analysis, here's what I'm planning for your ops agent:
> - **Tools:** [tool list]
> - **Key monitoring areas:** [what the agent will watch]
> - **Domain knowledge:** [what the agent will know about your component]"

### Step 2: Determine Tool List

**Always included:**
- `log_search` — OpenSearch log querying
- `metric_query` — Prometheus metric querying

**Add based on analysis:**
- If Kafka dependencies found → suggest `kafka_consumer` tool (check lag, read messages)
- If database found → suggest `db_query` tool (health check, slow query analysis)
- If external APIs found → suggest `api_health` tool (endpoint health checks)

For each additional tool, ask:
> "I'm suggesting a `<tool_name>` tool for <reason>. Should I include it? If yes, what endpoint/credentials does it need?"

### Step 3: Define Config Values

Compile all config values needed for `agent.yaml`:

```yaml
component: <from analysis>
description: <from analysis>

opensearch:
  endpoint: <ask if not in analysis>
  index_pattern: <from analysis>
  verify_certs: true

prometheus:
  endpoint: <ask if not in analysis>
  namespace: <from analysis>
```

Present to owner for confirmation.

### Step 4: Draft System Prompt Content

Based on the analysis, prepare:
1. **Component overview** — what it does, in operational context
2. **Domain knowledge** — key error codes, business logic the agent should understand
3. **Failure patterns** — from analysis, formatted as agent instructions
4. **Monitoring guidelines** — what to check first, correlation patterns

Ask the owner:
> "Here's the domain knowledge I'll give the agent:
> [draft content]
>
> Is there anything to add or correct?"

### Step 5: Present Design Summary

Present the complete design:

```
Agent Design for <component_name>
===================================

Tools:
  - log_search (OpenSearch)
  - metric_query (Prometheus)
  - <additional tools>

Config:
  <agent.yaml content>

System Prompt Sections:
  - Component: <summary>
  - Domain Knowledge: <summary>
  - Failure Patterns: <count> patterns documented
  - Guidelines: <summary>
```

> "Does this design look good? If yes, I'll generate the agent project. Run: **03-generate-agent**"

### Output

Save the design as `<component>-design.md` with all the above details, structured so the generation skill can reference it directly.
