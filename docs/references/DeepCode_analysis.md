# DeepCode Analysis Report

## 1. Executive Summary

*   **Source**: [https://github.com/HKUDS/DeepCode](https://github.com/HKUDS/DeepCode)
*   **Core Value**: DeepCode is a SOTA multi-agent system for reproducing research papers into code. It features a sophisticated "Plan-First" architecture, rigorous plan validation, and an adaptive RAG system that indexes reference code based on the *intended* target structure.
*   **Recommendation**: Extract the **Planning & Validation Logic** and the **Structure-Aware RAG Strategy**.

## 2. Architecture Breakdown

### Entry Points
*   `deepcode.py`: CLI/UI entry point.
*   `workflows/agent_orchestration_engine.py`: The central nervous system. It orchestrates the entire pipeline from research analysis to code generation.

### Key Components
*   **Orchestration Engine**: Manages the state machine of the harvest (Research -> Plan -> Index -> Code).
*   **CodePlannerAgent**: Generates a massive, detailed YAML plan (~10k chars) before any code is written.
*   **CodebaseIndexWorkflow**: Indexes downloaded reference repositories. Crucially, it uses the *Target Plan* to guide the indexing of the *Source Code*, mapping reference features to the intended implementation.
*   **MCP Integration**: Uses the Model Context Protocol to standardize tool usage.

### Data Flow
1.  **Input**: PDF/URL/Text.
2.  **Analysis**: `ResearchAnalyzerAgent` extracts algorithms and requirements.
3.  **Planning**: `CodePlannerAgent` synthesizes a validatable YAML plan (`initial_plan.txt`).
4.  **Reference Mining**: `ReferenceAnalysisAgent` finds relevant GitHub repos.
5.  **Indexing**: `CodebaseIndexWorkflow` indexes these repos *contextualized by the plan*.
6.  **Implementation**: `CodeImplementationWorkflow` generates code, using the plan and the index.

## 3. The Gem List (Extractable Features)

### Feature A: Plan Validation Protocol (High Value)
*   **Description**: A strict validation function (`_assess_output_completeness`) that scores the LLM-generated plan. It checks for specific YAML sections, truncation, and length.
*   **Why**: Prevents "garbage in, garbage out". If the plan is weak, the code will be weak.
*   **Complexity**: Low. Single function port.

### Feature B: Structure-Aware RAG (Medium Value)
*   **Description**: The `CodebaseIndexWorkflow` doesn't just index code blindly. It extracts the *intended file tree* from the plan and uses it to "bucket" knowledge from reference repos.
*   **Why**: This is much smarter than generic RAG. It says "I plan to write `gcn.py`, show me GCN implementations from these 5 repos."
*   **Complexity**: High. Requires porting the Indexer and the Plan Parser.

### Feature C: Chat-Based Planning Pipeline (Medium Value)
*   **Description**: A streamlined pipeline (`execute_chat_based_planning_pipeline`) that skips paper analysis and goes straight to planning from user requirements.
*   **Why**: Perfect for "I have an idea, build it" scenarios, which matches CodeSwarm's use case.
*   **Complexity**: Medium. Requires adapting the orchestration logic.

## 4. Integration Strategy

We will focus on **Feature A (Plan Validation)** and **Feature C (Chat Planning)** first, as they directly improve CodeSwarm's reliability. Feature B is a longer-term goal.

1.  **Port `_assess_output_completeness`**: Add this to CodeSwarm's `AdminAgent` or a new `PlannerAgent`.
2.  **Adopt the YAML Plan Standard**: Move CodeSwarm from loose task lists to a structured YAML plan (`file_structure`, `implementation_steps`, etc.).
3.  **Implement `extract_file_tree_from_plan`**: Use this to scaffold the project structure automatically.
