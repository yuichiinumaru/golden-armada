from agno.tools import Toolkit
from codeswarm.services.agent_maker import AgentMakerService

# Initialize service singleton
agent_maker = AgentMakerService()

class AgentMakerTools(Toolkit):
    def __init__(self):
        super().__init__(name="agent_maker")
        self.register(self.bulk_create_agents)

    async def bulk_create_agents(self, folder_path: str) -> str:
        """
        Scans a folder for Markdown agent definitions and creates them as Python Agents in the system.

        Args:
            folder_path: Path to the folder containing .md files (e.g. 'packages/pew-pew-workspace/agents')

        Returns:
            A report of created agents.
        """
        results = await agent_maker.bulk_create_from_folder(folder_path)
        return "\n".join(results)
