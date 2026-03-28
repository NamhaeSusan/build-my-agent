---
name: create-ops-agent
description: Create a standardized operational agent for a component — orchestrates the full analyze → design → generate → validate workflow
---

# Create Operational Agent

You are helping a component owner create a standardized operational agent using deepagents. This skill orchestrates the entire process.

## Overview

You will walk the owner through 4 phases. Each phase has its own detailed skill — read and follow them in order. Do NOT skip phases or combine them.

```
Phase 1: Analyze    → Understand the component's codebase
Phase 2: Design     → Decide what the agent needs
Phase 3: Generate   → Create the agent project
Phase 4: Validate   → Verify structure and run tests
```

## Before You Start

1. Confirm the component repository path with the owner
2. Verify you have access to the build-my-agent plugin files:
   - `skills/` — the 4 phase skills
   - `templates/` — agent project boilerplate
   - `tools/` — reference tool implementations (OpenSearch, Prometheus)
   - `guard/` — AST structure validator

## Phase 1: Analyze Codebase

Read and follow `skills/01-analyze-codebase/SKILL.md`.

**Goal:** Understand the component's logging, metrics, infrastructure dependencies, and failure patterns.

**Output:** `<component>-analysis.md`

**Gate:** Confirm with the owner that the analysis is accurate before proceeding.

> "Analysis complete. Ready to move on to designing your agent?"

## Phase 2: Design Agent

Read and follow `skills/02-design-agent/SKILL.md`.

**Goal:** Determine tool list, config values, and system prompt content.

**Output:** `<component>-design.md`

**Gate:** Owner approves the design.

> "Design complete. Ready to generate the agent project?"

## Phase 3: Generate Agent

Read and follow `skills/03-generate-agent/SKILL.md`.

**Goal:** Create a complete, working agent project from templates.

**Output:** `<component>-ops-agent/` directory with all files

**Gate:** Guard validation passes.

> "Agent project generated. Running structure validation..."

## Phase 4: Validate Structure

Read and follow `skills/04-validate-structure/SKILL.md`.

**Goal:** Verify the generated project follows all structural rules and tests pass.

**Output:** Clean guard report + passing tests

**Gate:** All checks pass.

## Completion

After all 4 phases pass, present the final summary:

> "Your operational agent is ready!
>
> **Project:** `<component>-ops-agent/`
>
> **Quick start:**
> ```bash
> cd <component>-ops-agent
> pip install -e '.[dev]'
> python agent.py
> ```
>
> **What it can do:**
> - [tool list with descriptions]
>
> **To add tools later:**
> 1. Create a new file in `tools/` (one public function + docstring)
> 2. Add config section in `config/agent.yaml`
> 3. Export from `tools/__init__.py` and register in `agent.py`
> 4. Run `python -m guard check .` to verify
>
> **To re-validate:** `python -m guard check <component>-ops-agent/`"

## Rules

- **One phase at a time.** Complete each phase fully before starting the next.
- **Always confirm with the owner** at each gate before proceeding.
- **Don't guess.** If something is unclear about the component, ask the owner.
- **Follow the guard rules.** Every generated file must pass `python -m guard check`.
- **The owner drives.** You suggest, they decide. Especially for tool selection and config values.
