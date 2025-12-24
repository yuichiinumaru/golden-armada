# Incremental Analysis: `codeswarm/agents`
**Date:** 2025-12-21

## Overview
The `agents` directory is the "brains" of the Golden Armada. It contains the logic for the orchestrator, the safety gatekeeper, and the various specialized agents that perform the actual work.

## Key Files & Responsibilities

### 1. `orchestrator_agent.py`
- **Role:** central planning engine.
- **Workflow:** takes a user request, uses the `AgentRegistry` to find capable agents, and returns a JSON-formatted multi-step execution plan.
- **Reporting:** includes logic to generate a final executive report after the execution phase.
- **Intelligence:** defaults to the `gemini-2.5-pro` (reasoning) model.

### 2. `gatekeeper_agent.py` (`SecurityAboyeur`)
- **Role:** strictly monitors input/output for security risks (prompt injection, PII leaks).
- **Strategy:** typically initialized with `use_memory=False` to prevent the agent itself from being poisoned by malformed memory entries.

### 3. `armada/` (Subfolders)
- **Categorization:** agents are organized by domain (backend, frontend, qa, security, etc.).
- **Consistency:** most agents inherit from `SwarmAgent` and load their instructions from designated prompt locations.

### 4. `specialists/`
- **Role:** contains agents for very specific or high-level cognitive tasks (e.g., `DeepReasoner`, `Poet`, `FiscalJudge`).
- **Niche Expertise:** these agents are called by the orchestrator for tasks that fall outside standard development cycles (e.g., legal analysis, advanced pattern matching).

## Completeness Assessment
- **Hierarchical Depth:** the structure supports a complex chain of command, from the orchestrator down to specialized specialists.
- **Diversity:** the wide range of specialists found in `specialists/` and the categorizations in `armada/` confirm the project's ambition for a comprehensive 222+ agent fleet.
- **Architecture:** the clear separation of the "Orchestrator" from the "Specialists" is a hallmark of a scalable multi-agent system.
