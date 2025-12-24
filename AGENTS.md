## Continuity Ledger (compaction-safe)
Maintain a single Continuity Ledger for this workspace in `CONTINUITY.md`. The ledger is the canonical session briefing designed to survive context compaction; do not rely on earlier chat text unless it's reflected in the ledger.

### How it works
- At the start of every assistant turn: read `CONTINUITY.md`, update it to reflect the latest goal/constraints/decisions/state, then proceed with the work.
- Update `CONTINUITY.md` again whenever any of these change: goal, constraints/assumptions, key decisions, progress state (Done/Now/Next), or important tool outcomes.
- Keep it short and stable: facts only, no transcripts. Prefer bullets. Mark uncertainty as `UNCONFIRMED` (never guess).
- If you notice missing recall or a compaction/summary event: refresh/rebuild the ledger from visible context, mark gaps `UNCONFIRMED`, ask up to 1-3 targeted questions, then continue.

### `functions.update_plan` vs the Ledger
- `functions.update_plan` is for short-term execution scaffolding while you work (a small 3-7 step plan with pending/in_progress/completed).
- `CONTINUITY.md` is for long-running continuity across compaction (the "what/why/current state"), not a step-by-step task list.
- Keep them consistent: when the plan or state changes, update the ledger at the intent/progress level (not every micro-step).

### In replies
- Begin with a brief "Ledger Snapshot" (Goal + Now/Next + Open Questions). Print the full ledger only when it materially changes or when the user asks.

### `CONTINUITY.md` format (keep headings)
- Goal (incl. success criteria):
- Constraints/Assumptions:
- Key decisions:
- State:
  - Done:
  - Now:
  - Next:
- Open questions (UNCONFIRMED if needed):
- Working set (files/ids/commands):

---

{
  "file_metadata": {
    "filename": "AGENTS.json",
    "project": "Golden Armada",
    "type": "Agent Governance Protocol",
    "version": "1.0.0",
    "description": "Definitive rules, preservation policies, and operational workflows for agents working on the Golden Armada Project."
  },
  "vital_asset_preservation_policy": {
    "core_directive": "VITAL ASSET PRESERVATION",
    "immutable_rules": [
      {
        "rule_id": "PRESERVE_DOCS",
        "instruction": "NEVER DELETE documentation info. Always integrate new info. Only correct if data is objectively WRONG."
      },
      {
        "rule_id": "ARCHIVE_FIRST",
        "instruction": "Never delete files. Move them to 'docs/_archive/' before refactoring.",
        "protocol": "EXTRACTION PROTOCOL: Archive first, then extract information to new files."
      }
    ]
  },
  "separation_of_concerns": {
    "strategy_layer": {
      "file": "docs/01-plan.md",
      "content_type": "Why & How",
      "focus": ["Strategy", "Design", "Reasoning"]
    },
    "execution_layer": {
      "file": "docs/02-tasks.md",
      "content_type": "What & When",
      "focus": ["Granular implementation steps"]
    }
  },
  "operational_constraints": {
    "granularity": {
      "directive": "Write tasks as detailed as possible.",
      "tactics": [
        "Use subtasks and sub-subtasks.",
        "NO DETAIL LEFT BEHIND: Every technical detail counts.",
        "Use multi-step edits if necessary."
      ]
    },
    "hierarchical_scaling": {
      "threshold": "800 lines",
      "action": "Create a subdirectory (e.g., docs/01-plans/) and move details there.",
      "requirement": "Keep a synthetic version in the main file."
    }
  },
  "agent_workflow_lifecycle": [
    {
      "phase": "Session Initialization",
      "step_id": "1",
      "trigger": "When beginning a new session",
      "mandatory_actions": [
        "Read 'docs/tree.md'",
        "Read 'codeswarm/tree.md'"
      ],
      "objective": "Understand project goals, rules, plans, tasks, structure, and current state of development before proceeding."
    },
    {
      "phase": "Continuous Thought Processing",
      "step_id": "2",
      "trigger": "Progressive work / Scanning codebase",
      "target_folder": "docs/thoughts/",
      "actions": [
        "Write down a .md file to track thoughts and progress.",
        "Use as a space to remember, write notes to self, and act as a personal notebook.",
        "Read all existing thoughts before creating a new one to prevent duplication and clutter."
      ],
      "rationale": "Prevent forgetting important details and keep the folder organized."
    },
    {
      "phase": "Protocol Self-Evolution",
      "step_id": "3",
      "trigger": "Progress made or project structure changes",
      "target_file": "AGENTS.md",
      "actions": [
        "Update with new rules and instructions.",
        "NEVER remove any rules - only add or integrate details."
      ]
    },
    {
      "phase": "Change Logging & Error Prevention",
      "step_id": "4",
      "trigger": "Progress made or project structure changes",
      "target_file": "CHANGELOG.md",
      "formatting_rules": [
        "Add new changes to the top of the file.",
        "NEVER remove entries - only add or integrate."
      ],
      "core_purpose": "PREVENT repeating mistakes and making the same errors.",
      "content_requirement": "Write WHAT changed, WHY it changed, and HOW it changed (what worked vs what didn't)."
    },
    {
      "phase": "Task Management",
      "step_id": "5",
      "trigger": "Progress made or project structure changes",
      "target_file": "docs/02-tasks.md",
      "actions": [
        "Add new tasks to the top of the file.",
        "NEVER remove open tasks - only add or integrate details.",
        "Ensure docs/02-tasks.md reflects all open tasks in docs/02-tasks/ subfolder."
      ],
      "completion_protocol": {
        "action": "Move Completed Phases to 'docs/02-tasks/tasks-completed.md'.",
        "post_condition": "Update CHANGELOG.md immediately after moving tasks."
      }
    }
  ]
}