# Agent Integration Strategy

## Overview
This strategy outlines how CodeSwarm incorporates external agent definitions ("Personas" or "Droids") and orchestration patterns from reference repositories like `pew-pew-workspace` and `droid-factory-template`.

## Core Concept: Dynamic Personas
Instead of hardcoding agent classes (e.g., `DevAgent`, `RevisorAgent`), CodeSwarm will support a **Dynamic Persona System**.
*   **Base Agents:** We retain `Admin`, `Planner`, `Logger` as the stable core.
*   **Worker Agents:** The `DevAgent` and `RevisorAgent` can assume specific *Personas* based on the task.

## Sources & Harvested Concepts

### 1. Droid Factory (Role Definitions)
*   **Source:** `droid-factory-template/droids/`
*   **Concept:** Highly specialized system instructions (e.g., `security-auditor`, `api-documenter`).
*   **Integration:**
    *   Store these as Markdown templates in `codeswarm/personas/`.
    *   Load them at runtime to configure the `Agent.instructions`.

### 2. PewPew Workspace (Team Structure)
*   **Source:** `pew-pew-workspace` (Discovery, Context, Requirements teams).
*   **Concept:** Organizing agents into functional "Teams" with distinct lifecycle phases.
*   **Integration:**
    *   Implement `Discovery Phase` in `AgentOS`.
    *   Use `DiscoveryAgent` persona for the initial phase.

## Orchestration Logic
1.  **Planner Decision:** The `PlannerAgent` analyzes the goal.
2.  **Persona Selection:** The Planner selects the best personas for the job (e.g., "We need a `backend-architect` and a `security-auditor`").
3.  **Instantiation:** `AgentOS` instantiates generic worker agents but injects the specific Persona instructions.
4.  **Execution:** The agents perform the task using their specialized knowledge/behavior.

## Roadmap
1.  **Library Creation:** Populate `codeswarm/personas/` with harvested droids.
2.  **Loader Implementation:** Write `codeswarm/utils/persona_loader.py`.
3.  **Planner Update:** Teach Planner to use the library.
