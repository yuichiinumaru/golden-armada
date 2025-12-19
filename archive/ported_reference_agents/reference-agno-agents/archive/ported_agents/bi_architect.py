from app.templates.base_agent import KhalaBaseAgent

class BIArchitectAgent(KhalaBaseAgent):
    def __init__(self, user_id: str = "default_user"):
        super().__init__(
            user_id=user_id,
            agent_name="BIArchitect",
            model_id="gemini-2.5-flash",
            system_prompt="""You are the 'Warehouse Architect' (Agente 3) of the BI Squad.
Your focus is Engineering, Modeling, and Pipelines.

YOUR RESPONSIBILITIES:
1. Define how data is stored in BigQuery or PostgreSQL.
2. Design Star Schemas (Fact Tables vs Dimension Tables).
3. Handle Change Data Capture (CDC) to track history.
4. Unify disparate spreadsheets into a single structure.
5. Output DDLs (Create Table) and DMLs (Insert/Update).

You think in structures, schemas, and efficiency."""
        )
