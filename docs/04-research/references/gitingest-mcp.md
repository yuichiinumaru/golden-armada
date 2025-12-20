# Gitingest MCP: Repository Context Injection

## 1. Synthesis

**Repository:** `puravparab/gitingest-mcp`
**Language:** Python
**Core Purpose:** An MCP server wrapping the `gitingest` library. It turns any GitHub repository into a text-friendly format optimized for LLM consumption (summaries, directory trees, file contents).

### Key Capabilities
*   **`git_summary`:** Returns a high-level overview (Repo name, file count, token count, README content).
*   **`git_tree`:** Returns the file structure as a tree string, useful for the agent to "see" the project layout before diving in.
*   **`git_files`:** Fetches specific file contents concatenated into a single prompt-ready string with delimiters.
*   **Branch Support:** Can target specific branches.

### Architectural Highlights
*   **`GitIngester` Class:** Abstraction layer that fetches repo data asynchronously (running the sync `gitingest` lib in a thread pool).
*   **FastMCP:** Uses the `mcp[cli]` library for a clean, decorator-based server implementation.
*   **File Parsing:** Includes regex logic to parse the monolithic string returned by `gitingest` back into individual file contents if needed.

---

## 2. Strategic Ideas for Golden Armada

The Golden Armada needs to read codebases to understand them. This tool is the "Reader".

### A. The "Context Loader" Tool
Instead of manually cloning and reading files, an agent can just "digest" a remote repo.
*   **Idea:** When a user asks "How does the Vercel AI SDK work?", the `ResearchSquad` calls `git_summary("vercel", "ai")` followed by `git_tree` and `git_files` for relevant sections.
*   **Benefit:** Zero-setup context loading. The agent doesn't need a local clone.

### B. Dependency Analysis
The `git_tree` tool is perfect for understanding project structure.
*   **Idea:** Before writing any code, the `CodingSquad` should always call `git_tree` on the target repo to understand where new files should go.

### C. "Repo-to-Knowledge" Pipeline
We can use this to populate SurrealDB.
*   **Process:**
    1.  `git_files` -> Get all `.md` and `.py` files.
    2.  Chunking Agent -> Splits them.
    3.  Embedding -> Store in `repository_knowledge` table in SurrealDB.
    4.  Result: Instant RAG over any public GitHub repo.

---

## 3. Integration Plan (Agno + SurrealDB + Gemini 3)

We will use this logic to build the `RepositoryLoader` component.

### Component: `RepositoryLoader`

#### 1. Integration with Agno
We will create a native Agno tool that wraps this logic (or connects to the MCP server). Since the logic is simple (wrapper around `gitingest`), we might just import `gitingest` directly into our `ArmadaTools` to avoid the overhead of a separate server process, *unless* we want to run it remotely.

**Decision:** Wrap `gitingest` directly in a Python Tool class for Agno. It's cleaner for a monolithic Python app.

```python
# app/tools/repository.py
from agno.tools import Tool
from gitingest import ingest

class RepositoryTool(Tool):
    def read_repo(self, url: str) -> str:
        summary, tree, content = ingest(url)
        return f"{summary}\n\n{tree}\n\n{content}"
```

#### 2. The `Codebase` Graph Node
When we digest a repo, we store it structurally.
```sql
DEFINE TABLE repository SCHEMAFULL;
DEFINE FIELD url ON TABLE repository TYPE string;
DEFINE FIELD file_tree ON TABLE repository TYPE string;
DEFINE FIELD last_indexed ON TABLE repository TYPE datetime;
```

### Implementation Steps

1.  **Direct Integration:** Add `gitingest` to the Armada's `requirements.txt`.
2.  **Tool Creation:** Create `RepoIngestTool` in Agno.
3.  **Prompt Engineering:** Teach the `CodingSquad`: "When starting a task on an existing codebase, ALWAYS run `read_file_tree` first."

### Refined Workflow: "Onboarding"
1.  **User:** "Refactor `main.py` in this repo: github.com/user/repo."
2.  **Coding Agent:**
    *   Calls `repo_tool.get_tree("github.com/user/repo")`.
    *   Analyzes structure.
    *   Calls `repo_tool.get_content("github.com/user/repo", files=["main.py", "utils.py"])`.
    *   Writes refactored code.
