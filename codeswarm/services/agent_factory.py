import os
import re
from pathlib import Path
from typing import List, Dict

# Define paths relative to this file
BASE_DIR = Path(__file__).resolve().parent.parent
AGENTS_DIR = BASE_DIR / "agents" / "armada" # Targeting armada for generated agents? or just agents? Let's check AgentMaker usage.

# Use triple quotes for system_prompt to handle multi-line strings safely
TEMPLATE_CONTENT = """
from codeswarm.core.base_agent import SwarmAgent
{imports_section}

class {class_name}(SwarmAgent):
    def __init__(self, user_id: str = "system"):
        self.instructions = \"\"\"{system_prompt}\"\"\"
        
        super().__init__(
            user_id=user_id,
            agent_name="{agent_name}",
            model_id="{model_id}",
            instructions=self.instructions,
            tools=[{tools_instantiation}]
        )
        # Recommended MCP Servers (Requires explicit configuration in mcp-server):
        # {mcp_servers_list}

# Entry point for testing
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    load_dotenv()

    async def main():
        agent = {class_name}(user_id="test_user")
        
        print(f"--- {class_name} Initialized ---")
        response = await agent.run("Hello! Who are you?")
        print(f"Response: {response.content}")

    asyncio.run(main())
"""

def create_agent_file(name: str, prompt: str, model: str, tools: List[Dict[str, str]] = None, mcp_tools: List[str] = None) -> tuple[bool, str]:
    """
    Create a new agent file from template.

    Args:
        name: Name of the agent.
        prompt: System prompt.
        model: Model ID.
        tools: List of tool dicts, e.g. [{"import_path": "agno.tools.duckduckgo", "class_name": "DuckDuckGoTools"}]
        mcp_tools: List of MCP server names.
    """

    try:
        # 1. Validate Name (Security: Prevent Path Traversal & Invalid Chars)
        if not re.match(r'^[a-zA-Z0-9_\-\s]+$', name):
            return False, "Invalid agent name. Use alphanumeric characters, spaces, hyphens, and underscores only."

        # Normalize name
        clean_name = name.lower().replace(" ", "_").replace("-", "_")

        # Ensure it's a valid python identifier
        if not clean_name.isidentifier():
             # Basic cleanup if regex passed but still weird (e.g. starts with number)
             clean_name = "agent_" + clean_name

        class_name = "".join(x.title() for x in clean_name.split("_")) + "Agent"
        file_name = f"{clean_name}.py"
        
        # Ensure directory exists
        AGENTS_DIR.mkdir(parents=True, exist_ok=True)
        file_path = AGENTS_DIR / file_name

        if file_path.exists():
            return False, f"Agent '{clean_name}' already exists at {file_path}"

        # 2. Sanitize Prompt (Security: Escape triple quotes)
        safe_prompt = prompt.replace('"""', '\\"\\"\\"')

        # 3. Prepare Tools
        imports = []
        instantiations = []
        if tools:
            for tool in tools:
                imports.append(f"from {tool['import_path']} import {tool['class_name']}")
                instantiations.append(f"{tool['class_name']}()")

        imports_str = "\n".join(imports)
        tools_str = ", ".join(instantiations)
        mcp_str = ", ".join(mcp_tools) if mcp_tools else "None"

        # 4. Generate Content
        content = TEMPLATE_CONTENT.format(
            class_name=class_name,
            agent_name=name,
            model_id=model,
            system_prompt=safe_prompt,
            imports_section=imports_str,
            tools_instantiation=tools_str,
            mcp_servers_list=mcp_str
        )

        # Write file
        with open(file_path, "w") as f:
            f.write(content)

        return True, f"Agent created at {file_path}"

    except Exception as e:
        return False, str(e)
