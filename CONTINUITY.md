## Continuity Ledger (compaction-safe)

- **Goal (incl. success criteria):**
  - Systematically recycle valuable components from `old-codeswarm` into the new Agno-based `golden-armada` architecture.
  - **Success:** Transform legacy `old-codeswarm` assets into clean, usable Agno modules in `codeswarm/recycled/` or `docs/recycled/`, then archive the rest.

- **Constraints/Assumptions:**
  - **Vital Asset Preservation:** Archive before delete.
  - **Framework:** Target architecture is Agno (not ADK 1.0) + SurrealDB (Khala).
  - **Legacy Compatibility:** Do not migrate `ollama-mem0` implementation directly (incompatible), but harvest its *patterns*.

- **Key decisions:**
  - **Batching Strategy:** Split recycling into 3 batches (1: Prompts/Docs, 2: Core Logic, 3: Infrastructure).
  - **Destinations:** 
    - Prompts/Docs -> `docs/recycled/`
    - Core Logic -> `codeswarm/recycled/`
  - **Cleanup:** Removed nested `.git` and `node_modules` from legacy folders to fix git hygiene.
  - **Governance:** Added "Continuity Ledger" protocol to `AGENTS.md`.

- **State:**
  - **Done:** 
    - **Batch 1:** Migrated prompts (`admin`, `dev`, `revisor`) and research docs.
    - **Batch 2:** Migrated `PythonASTAnalyzer` (Analysis), `UnitTestGenerator` (Testing), and DevOps utils to `codeswarm/recycled/`.
    - **Cleanup:** Removed nested git repos from `old-codeswarm`.
    - **Protocol:** Updated `AGENTS.md` and `.gitignore`.
  - **Now:** "Jules" is executing "Operation: Legacy Harvest" (Maximum Power) on `old-codeswarm`.
  - **Next:** **Architectural Design (CodeSwarm)** - Focusing on Orchestration Logic (Task 13) and Revisor Loops (Task 9-12).

- **Open questions (UNCONFIRMED if needed):**
  - None currently.

- **Working set (files/ids/commands):**
  - `task.md` (Tracking progress)
  - `docs/thoughts/old-codeswarm-manifest.md` (Recycling Strategy)
  - `codeswarm/recycled/` (Destination for code)
