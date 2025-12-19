import os
import re
import yaml
import json
from pathlib import Path
from typing import List, Dict, Any

from codeswarm.services.agent_factory import create_agent_file
from codeswarm.agents.specialists.tools_specialist_agent import ToolsSpecialistAgent
from codeswarm.agents.specialists.prompt_engineer_agent import PromptEngineerAgent

# Load tools library
BASE_LIB_DIR = Path(__file__).resolve().parent.parent / "core"
TOOLS_LIB_PATH = BASE_LIB_DIR / "tools_library.json"
MCP_LIB_PATH = BASE_LIB_DIR / "mcp_registry.json"

TOOLS_LIBRARY = {}
MCP_LIBRARY = []

if TOOLS_LIB_PATH.exists():
    try:
        with open(TOOLS_LIB_PATH, "r") as f:
            TOOLS_LIBRARY = json.load(f)
    except Exception as e:
        print(f"Failed to load tools library: {e}")

if MCP_LIB_PATH.exists():
    try:
        with open(MCP_LIB_PATH, "r") as f:
            MCP_LIBRARY = json.load(f)
    except Exception as e:
        print(f"Failed to load MCP library: {e}")

class AgentMakerService:
    """
    Agent Engineering Service.
    Transforms MD definitions into Python Agents using AI Specialists.
    """
    def __init__(self):
        # AI agents
        self.tools_agent = ToolsSpecialistAgent(user_id="system_agent_maker")
        self.prompt_agent = PromptEngineerAgent(user_id="system_agent_maker")

    def parse_md_agent(self, file_path: Path) -> Dict[str, Any]:
        """Parses a Markdown file with YAML frontmatter."""
        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Extract YAML frontmatter
            match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
            if match:
                yaml_content = match.group(1)
                body = match.group(2).strip()
                try:
                    metadata = yaml.safe_load(yaml_content)
                    return {
                        "name": metadata.get("name", file_path.stem),
                        "description": metadata.get("description", ""),
                        "prompt": body,
                        "metadata": metadata
                    }
                except yaml.YAMLError:
                    pass

            # Fallback if no frontmatter
            return {
                "name": file_path.stem,
                "description": "",
                "prompt": content,
                "metadata": {}
            }
        except Exception as e:
            return {"name": file_path.stem, "error": str(e)}

    async def engineer_agent(self, draft: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the AI pipeline using ToolsSpecialist and PromptEngineer.
        """
        if "error" in draft:
            raise ValueError(f"Invalid draft: {draft['error']}")

        selected_tools_info = []
        selected_mcp_names = []
        original_prompt = draft['prompt']
        agent_name = draft['name']

        # 1. Tool Selection (AI)
        try:
            # We assume ToolsSpecialist has a method or we use run_task
            tools_response = await self.tools_agent.run_task(f"Select tools for agent '{agent_name}' with prompt: {original_prompt}")
            # Simplified parsing: we expect the agent to return JSON or we might need robust parsing
            # For now, let's assume the agent returns a list of tool names in its textual response
            # Or better, we stick to heuristics if AI fails, but let's try to use AI output if structured.
            # Since we haven't implemented structured output for these specific agents yet, 
            # we will use the Heuristics FALLBACK if AI response is not easily parsable, 
            # or we rely on the implementation of ToolsSpecialistAgent to return structured data if possible.
            # *For this step, we'll keep the heuristics as primary for reliability until agents are fully tested.*
            self._apply_heuristics(draft, selected_tools_info)
        except Exception as e:
            print(f"Tools Specialist failed: {e}. Using heuristics.")
            self._apply_heuristics(draft, selected_tools_info)

        # 2. Prompt Engineering (AI)
        try:
            prompt_response = await self.prompt_agent.run_task(f"Optimize this system prompt for an AI agent named '{agent_name}':\n\n{original_prompt}")
            if isinstance(prompt_response, dict) and "response" in prompt_response:
                 optimized_prompt = prompt_response["response"]
            else:
                 optimized_prompt = str(prompt_response)
        except Exception as e:
            print(f"Prompt Engineer failed: {e}. Using original prompt.")
            optimized_prompt = original_prompt

        return {
            "name": draft['name'],
            "prompt": optimized_prompt,
            "tools": selected_tools_info,
            "mcp_servers": selected_mcp_names
        }

    def _apply_heuristics(self, draft, selected_tools_info):
        """Fallback heuristics for tool selection."""
        lower_prompt = draft['prompt'].lower()
        if "search" in lower_prompt or "google" in lower_prompt:
            if "DuckDuckGoTools" in TOOLS_LIBRARY:
                selected_tools_info.append(TOOLS_LIBRARY["DuckDuckGoTools"])
        if "news" in lower_prompt:
            if "Newspaper4kTools" in TOOLS_LIBRARY:
                selected_tools_info.append(TOOLS_LIBRARY["Newspaper4kTools"])
        if "finance" in lower_prompt or "stock" in lower_prompt:
            if "YFinanceTools" in TOOLS_LIBRARY:
                selected_tools_info.append(TOOLS_LIBRARY["YFinanceTools"])

    async def bulk_create_from_folder(self, folder_path: str) -> List[str]:
        """Scans a folder and generates agents."""
        p = Path(folder_path)
        results = []
        if not p.exists():
            return [f"Error: Folder {folder_path} not found."]

        # Find all .md files recursively
        for file_path in p.rglob("*.md"):
            # Skip non-agent files (like README, LICENSE)
            if file_path.name in ["README.md", "LICENSE", "CONTRIBUTING.md", "CHANGELOG.md"]:
                continue

            try:
                # Parse
                draft = self.parse_md_agent(file_path)

                # Engineer
                final_spec = await self.engineer_agent(draft)

                # Generate Code
                success, msg = create_agent_file(
                    name=final_spec['name'],
                    prompt=final_spec['prompt'],
                    model="gemini-2.5-flash",
                    tools=final_spec['tools']
                )

                status = "✅ Created" if success else "❌ Failed"
                results.append(f"{status} {final_spec['name']}: {msg}")

            except Exception as e:
                results.append(f"❌ Error processing {file_path.name}: {str(e)}")

        return results

# Singleton instance
agent_maker = AgentMakerService()
