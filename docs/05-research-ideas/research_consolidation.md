# Research Consolidation Report

## Overview
This document consolidates insights from the analysis of arXiv papers (Oct-Dec 2025) relevant to CodeSwarm.

## Key Insights & Actionable Plans

### 1. Security & Alignment (from 2511.09904 - "CTRL-ALT-DECEIT")
*   **Insight:** Frontier agents can sabotage code (insert backdoors) or sandbag (underperform) deceptively. They may optimize for passing tests while introducing subtle vulnerabilities.
*   **Plan:**
    *   **Enhance RevisorAgent:** Add specific checks for "suspicious code patterns" not just correctness. Implement "Red Teaming" prompts where the Revisor actively tries to find backdoors.
    *   **Monitor Agents:** Implement a "Watcher" or "Audit" log that analyzes agent *intent* vs *output* (using a separate model).
    *   **Sandbagging Detection:** Compare agent performance on simple vs complex tasks to detect intentional underperformance.

### 2. Constraint Handling (from 2511.10952 - "Requirements for Aligned...")
*   **Insight:** Agents face conflicting operational constraints (e.g., speed vs. safety).
*   **Plan:**
    *   **Explicit Constraint Modeling:** In `PlannerAgent`, explicitly list constraints (e.g., "Must be fast" vs "Must be secure").
    *   **Justification Layer:** Require agents to "justify" decisions when constraints conflict, logged in `codeswarm_events.jsonl`.

### 3. Agent Resilience (from 2510.20333 - "GhostEI-Bench")
*   **Insight:** UI-based agents are vulnerable to visual injection attacks (fake overlays).
*   **Plan:**
    *   **Frontend Verification Security:** If using Playwright for verification, ensure the environment is isolated and inputs are sanitized.
    *   **Input Validation:** Ensure `AdminAgent` validates all user inputs for injection attempts before passing to DevAgent.

### 4. 3D & Embodied Intelligence (from 2511.11777)
*   **Insight:** LLMs combined with 3D vision can enhance perception.
*   **Plan:**
    *   **Future Expansion:** If CodeSwarm targets game development or robotics, integrate 3D understanding tools. Currently low priority.

## Implementation Strategy
1.  **Security Update:** Add `SecurityAudit` tool/prompt to `RevisorAgent`.
2.  **Planner Update:** Add `constraint_resolution` prompt module to `PlannerAgent`.
3.  **Knowledge Ingestion:** Feed these insights into Khala (see `docs/khala_ingestion_plan.md`).
