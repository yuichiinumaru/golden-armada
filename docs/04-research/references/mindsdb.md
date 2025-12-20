# Reference Analysis: MindsDB

**Source:** `gitingest-mindsdb-mindsdb.txt`
**Repo:** mindsdb/mindsdb
**Date:** 2025-03-31

---

## 1. Synthesis: What is MindsDB?

MindsDB is a "Serverless AI Database" that abstracts AI models as "AI Tables". It allows users to train, deploy, and query machine learning models using standard SQL.

### Core Concepts

1.  **AI Tables**:
    *   Models are treated as virtual tables in the database.
    *   Querying an AI table with `SELECT` triggers inference.
    *   Creating a model is done via `CREATE MODEL` statements.

2.  **Handlers & Integrations**:
    *   MindsDB connects to *data sources* (Postgres, MongoDB, S3) and *AI Engines* (OpenAI, HuggingFace, Anthropic).
    *   It acts as a middleware that pipes data from sources to models and writes predictions back.

3.  **Agents & Skills**:
    *   Recent versions introduce "Agents" that can be defined via SQL.
    *   Agents have "Skills" (access to specific datasets or tools).

4.  **SQL-First API**:
    *   Everything is an SQL query. `INSERT INTO mindsdb.models ...` trains a model. `SELECT * FROM mindsdb.models WHERE ...` runs it.

---

## 2. Strategic Ideas for CodeSwarm (Golden Armada)

MindsDB's "Model-as-a-Table" abstraction is incredibly powerful for our **SurrealDB** integration. Since SurrealDB supports SQL-like queries and custom functions, we can emulate this pattern.

### A. The "AI Table" Pattern in SurrealDB
Instead of calling Python functions to run agents, we can treat Agents as "Live Tables" or "Views" in SurrealDB.
*   **Concept**: To ask the Planner a question, we `INSERT` a record into the `planner_requests` table.
*   **Mechanism**: A Live Query listener (the Agent) picks up the record, processes it, and `UPDATE`s the record with the `response`.
*   **Benefit**: This decouples the Agent execution from the API. The frontend just writes to the DB and waits for the change.

### B. "Virtual Tables" for External Tools
MindsDB presents GitHub, Slack, etc., as tables (`SELECT * FROM github.issues`).
*   **Idea**: We can map `codeswarm/tools` to SurrealDB "Virtual Tables" (or just pre-filled tables).
*   **Implementation**: A `GitHubSyncer` agent periodically (or on demand) syncs PRs into a `github_prs` table. Agents query this table instead of calling the GitHub API directly. This provides **caching** and **memory**.

### C. SQL-Based Agent Definition
MindsDB defines agents via SQL:
```sql
CREATE AGENT support_bot
USING
   model = 'gpt-4',
   skills = ['knowledge_base'];
```
*   **CodeSwarm Adaptation**: We can store Agent Definitions in a `agents` table in SurrealDB. The `Orchestrator` reads this table to spawn the actual Python processes/threads.

---

## 3. Integration Plan (Agno + SurrealDB)

We will not use MindsDB directly (it's too heavy/separate), but we will **steal its architecture**.

### Phase 1: The "Live Table" Communication Protocol

**File:** `codeswarm/agno-agents/transports/surreal_live.py`

```python
class SurrealLiveTransport:
    """
    Enables Agno agents to communicate via SurrealDB tables.
    """
    def __init__(self, db, agent_id):
        self.db = db
        self.agent_id = agent_id

    async def listen(self):
        """
        Subscribes to 'INSERT' events on the 'mailbox' table for this agent.
        """
        async with self.db.live(f"live select * from mailbox where recipient = '{self.agent_id}'") as stream:
            async for task in stream:
                yield task

    async def respond(self, task_id, response):
        """
        Writes the response back to the task record.
        """
        await self.db.update(task_id, {"status": "completed", "response": response})
```

### Phase 2: Virtualizing External State

We will create a `Syncer` role (similar to MindsDB Handlers).

**File:** `codeswarm/agno-agents/squads/sync_squad.py`

```python
class GitHubSyncer(Agent):
    """
    Periodically syncs GitHub issues to SurrealDB so other agents
    can query them with SQL instead of API calls.
    """
    def run(self):
        issues = self.github.get_issues()
        for issue in issues:
            self.db.upsert("github_issues", issue)
```

### Phase 3: The "Model" Table Schema

We will define a schema that looks like MindsDB's system tables.

```sql
DEFINE TABLE models SCHEMAFULL;
DEFINE FIELD name ON TABLE models TYPE string;
DEFINE FIELD provider ON TABLE models TYPE string; -- 'openai', 'anthropic'
DEFINE FIELD parameters ON TABLE models TYPE object;

DEFINE TABLE agents SCHEMAFULL;
DEFINE FIELD name ON TABLE agents TYPE string;
DEFINE FIELD model ON TABLE agents TYPE record<models>;
DEFINE FIELD skills ON TABLE agents TYPE array<string>;
```

### Conclusion
MindsDB validates the "Database as the OS" philosophy. By implementing **Live Table Communication**, we make our agents asynchronous, decoupled, and persistent by default. The Planner doesn't need to know *where* the Coder is running; it just drops a ticket in the `coder_inbox` table.
