---
name: analyze-codebase
description: Analyze a component's codebase to understand its logging, metrics, and infrastructure for ops agent creation
---

# Analyze Component Codebase

You are helping a component owner create an operational agent. This skill guides you through analyzing their codebase.

## Prerequisites
- The component owner has a repository you can access
- You have the oh-my-agent plugin loaded

## Process

### Step 1: Identify the Component

Ask the owner:
> "Which component repository should I analyze? Please provide the path or let me know which directory to look at."

Read the repository's README, main entry point, and project config (go.mod, pom.xml, package.json, etc.) to understand what the component does.

### Step 2: Analyze Logging

Search the codebase for logging patterns:

**For Go:** Look for `log.`, `zap.`, `logrus.`, `slog.`, `zerolog` imports and usage
**For Java:** Look for `slf4j`, `log4j`, `logback`, `java.util.logging` imports
**For Python:** Look for `logging`, `structlog`, `loguru` imports
**For any language:** Look for log configuration files, structured logging patterns

Ask the owner to confirm:
> "I found that your component uses [logger library] with [format]. Logs appear to be sent to [destination]. Is this correct? Also:
> 1. What OpenSearch index pattern do your logs end up in? (e.g., `component-name-*`)
> 2. Are there any custom fields in your logs that are important for debugging? (e.g., `trace_id`, `user_id`, `order_id`)"

### Step 3: Analyze Metrics

Search for metrics/monitoring patterns:

**For Go:** Look for `prometheus` package, `promhttp`, metric registration (`NewCounter`, `NewGauge`, `NewHistogram`)
**For Java:** Look for `micrometer`, `prometheus` client, `@Timed`, `@Counted` annotations
**For any language:** Look for `/metrics` endpoint, Prometheus scrape config

Ask the owner to confirm:
> "I found these metrics being exported:
> - [list of metrics found]
>
> 1. What Prometheus namespace/prefix do these use?
> 2. What's the Prometheus endpoint URL your team uses?
> 3. Are there specific metric queries you regularly check when debugging?"

### Step 4: Analyze Infrastructure Dependencies

Search for:
- **Database:** connection strings, ORM configs, migration files, SQL queries
- **Message queues:** Kafka producer/consumer configs, topic names, RabbitMQ connections
- **External APIs:** HTTP client calls, gRPC stubs, service discovery configs
- **Cache:** Redis, Memcached connections

Ask the owner:
> "I found these infrastructure dependencies:
> - [list of dependencies]
>
> 1. Which of these are critical for operations monitoring?
> 2. Are there any dependencies I missed?
> 3. For each critical dependency, what would you want the ops agent to be able to check?"

### Step 5: Understand Failure Patterns

Ask the owner:
> "What are the most common incidents or issues you deal with for this component?
> 1. What's the first thing you check when something goes wrong?
> 2. Are there specific log queries or metric dashboards you always look at?
> 3. What are the typical root causes you've seen?"

### Step 6: Produce Analysis Document

Create a structured analysis document at `<component>-analysis.md` in the working directory:

    ```markdown
    # [component_name] Analysis

    ## Component Overview
    - **Name:** [name]
    - **Language:** [language]
    - **Purpose:** [what it does]

    ## Logging
    - **Library:** [logger]
    - **Format:** [structured/text]
    - **Transport:** [how logs get to OpenSearch]
    - **OpenSearch Index:** [index_pattern]
    - **Key Fields:** [important fields for debugging]

    ## Metrics
    - **Library:** [metrics library]
    - **Namespace:** [prometheus namespace]
    - **Endpoint:** [prometheus URL]
    - **Key Metrics:**
      - [metric 1]: [what it measures]
      - [metric 2]: [what it measures]

    ## Infrastructure Dependencies
    - [dependency 1]: [what, why it matters]
    - [dependency 2]: [what, why it matters]

    ## Failure Patterns
    - [pattern 1]: [symptoms, usual cause, what to check]
    - [pattern 2]: [symptoms, usual cause, what to check]

    ## Recommended Tools
    - `log_search` (OpenSearch) — required
    - `metric_query` (Prometheus) — required
    - [additional tools based on dependencies]
    ```

After creating the document, tell the owner:
> "Analysis complete. I've documented the findings in `[component]-analysis.md`. Please review it, then we'll move on to designing the agent. Run the next skill with: **02-design-agent**"
