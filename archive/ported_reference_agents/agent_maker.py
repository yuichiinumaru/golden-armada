import os
import re
import yaml
import json
from pathlib import Path
from typing import List, Dict, Any

from app.services.agent_factory import create_agent_file
from app.agents.agent_engineer import ToolsSpecialistAgent, PromptEngineerAgent

# Load tools library
BASE_LIB_DIR = Path(__file__).resolve().parent.parent / "lib"
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
        # We assume environmental auth (Gemini keys) are set
        try:
            self.tools_agent = ToolsSpecialistAgent()
            self.prompt_agent = PromptEngineerAgent()
        except Exception:
            # Fallback if agents fail to init (e.g. missing API keys in test env)
            self.tools_agent = None
            self.prompt_agent = None

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
        Runs the AI pipeline: Tools Specialist -> Prompt Engineer.
        """
        if "error" in draft:
            raise ValueError(f"Invalid draft: {draft['error']}")

        selected_tools_info = []
        selected_mcp_names = []
        optimized_prompt = draft['prompt']

        # Prepare MCP Context
        mcp_context = "\n".join([f"- {m['name']}: {m['description']}" for m in MCP_LIBRARY])

        # 1. Tools Selection
        if self.tools_agent:
            try:
                # Ask agent
                response = await self.tools_agent.chat(
                    f"""
                    Agent: {draft['name']}
                    Description: {draft['description']}
                    Prompt: {draft['prompt']}

                    AVAILABLE MCP SERVERS (Check for relevance):
                    {mcp_context}
                    """
                )

                # Parse JSON output (assuming agent returns Markdown-wrapped JSON)
                text = response.get("response", "")
                if "```json" in text:
                    json_str = text.split("```json")[1].split("```")[0].strip()
                    try:
                        data = json.loads(json_str)

                        # Native Tools
                        native_tools = data.get("native_tools", [])
                        for tool_name in native_tools:
                            if tool_name in TOOLS_LIBRARY:
                                selected_tools_info.append(TOOLS_LIBRARY[tool_name])

                        # MCP Tools
                        selected_mcp_names = data.get("mcp_servers", [])

                    except json.JSONDecodeError:
                        print("Failed to decode JSON from Tools Specialist")

            except Exception as e:
                print(f"Tools Specialist failed: {e}")
                # Fallback heuristic
                self._apply_heuristics(draft, selected_tools_info)
        else:
            self._apply_heuristics(draft, selected_tools_info)

        # 2. Prompt Optimization
        if self.prompt_agent:
            try:
                native_names = [t['class_name'] for t in selected_tools_info]
                tools_context = f"Native Tools: {native_names}\nMCP Servers: {selected_mcp_names}"

                response = await self.prompt_agent.chat(
                    f"Draft Prompt: {draft['prompt']}\nTools Available: {tools_context}"
                )
                optimized_prompt = response.get("response", draft['prompt'])
            except Exception as e:
                print(f"Prompt Engineer failed: {e}")

        return {
            "name": draft['name'],
            "prompt": optimized_prompt,
            "tools": selected_tools_info,
            "mcp_servers": selected_mcp_names
        }

    def _apply_heuristics(self, draft, selected_tools_info):
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
