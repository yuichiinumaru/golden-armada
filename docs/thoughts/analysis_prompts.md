# Incremental Analysis: `codeswarm/prompts`
**Date:** 2025-12-21

## Overview
The `prompts` directory contains the "instructional DNA" of the agents. Instead of simple text files, it uses structured JSON templates that allow for precise control over agent behavior, input context, and output schemas.

## Key Components

### 1. Root Role Prompts (`admin_prompt.json`, `dev_prompt.json`, etc.)
- **Structure:** each prompt defines an `agentProfile`, `inputContext`, `coreDirectives`, and `responseSchema`.
- **Dynamic Behavior:** the `AdminAgent` prompt shows a sophisticated "directive matching" system where the agent selects its action based on the `current_phase` metadata provided in the input JSON. This ensures high reliability in stateful multi-round conversations.

### 2. Knowledge Base (`kb/` subfolder)
- **Modularity:** the KB is broken down into thematic modules (e.g., `kb_framework_problem_solving`, `kb_agent_orchestration_core`).
- **Standardization:** these modules provide standardized definitions and strategies that are injected into multiple agents. For example, `kb_agent_orchestration_core` covers communication protocols (REST, gRPC, P2P) and discovery mechanisms, ensuring all agents understand how to find and talk to each other.

## Completeness Assessment
- **Sophistication:** the use of JSON for prompts, combined with conditional directives, is much more advanced than typical "system message" approaches. It reduces parser errors and improves instruction following.
- **Shared Knowledge:** the presence of extensive KB modules confirms the "Swarm" aspect of the project—agents don't just act in isolation; they share a common knowledge framework.
- **Systematic Planning:** the `planner_prompt` and `revisor_prompt` designs indicate a robust feedback loop is implemented at the core of the agentic workflows.
