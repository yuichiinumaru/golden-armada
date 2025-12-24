# old-codeswarm Manifest

This file categorizes the contents of the `old-codeswarm` directory and identifies assets for recycling or archiving.

## 1. High-Value Assets (Recycle Candidates)

### 1.1. Agent Prompts
- [ ] `old-codeswarm/codeswarm/prompts/admin_prompt.json`: Core logic for PM agent.
- [ ] `old-codeswarm/codeswarm/prompts/dev_prompt.json`: Core logic for coding agent.
- [ ] `old-codeswarm/codeswarm/prompts/revisor_prompt.json`: Logic for specialized review.
- [ ] `old-codeswarm/codeswarm/prompts/mcp_master_prompt.json`: MCP interaction logic.

### 1.2. Knowledge Base & Research
- [ ] `old-codeswarm/docs/research/metodo cientifico de prompting.txt`: Advanced prompting strategies.
- [ ] `old-codeswarm/docs/research/MCP Techniques Use Cases.txt`: Real-world MCP patterns.
- [ ] `old-codeswarm/docs/RAG/`: Various RAG techniques (HYDE, Citation generation).

### 1.3. Core Logic & Tools (Batch 2)
- [x] `old-codeswarm/codeswarm/adk_tools/advanced_analysis_tools.py`:
    - **Harvested**: `PythonASTAnalyzer`, `UnitTestGeneratorTool`, `TestRunnerTool`.
- [x] `old-codeswarm/codeswarm/adk_core/tool_logic.py`:
    - **Harvested**: `docker_pull`/`docker_build`, `read_config`, `fetch_web_text`.
- [x] `old-codeswarm/codeswarm/adk_agents/enhanced_agents.py`:
    - **Harvested**: `LoopAgent` and `ParallelAgent` strategies.

## 2. Architectural References (Reference only)
- `old-codeswarm/codeswarm-v2/`: Docker-based agent architecture.
- `old-codeswarm/ollama-mem0/`: Memories integration logic.
    - *Architectural Harvest*:
        - **Flexible Transports**: SSE vs. stdio support for MCP servers.
        - **Contextual Memory Retrieval**: Patterns for gathering memories for agent injection.
        - **Semantic-First Management**: Using search-based deletion/retrieval rather than key-based.
- `old-codeswarm/docs/project.md`: historical vision and specifications.

## 3. Archive Candidates (Obsolete)
- `old-codeswarm/.git/`: To be removed or compressed.
- `old-codeswarm/.agent/`, `old-codeswarm/.gemini/`: Old agent settings.
- `old-codeswarm/test_project/`: Sample data.
