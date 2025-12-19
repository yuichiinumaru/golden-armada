from agent_os.templates.base_agent import KhalaBaseAgent
#!/usr/bin/env python3
"""
TEMPLATE FOR AGNO AGENTS - AUTOMATION READY
"""

import os
import sys
import asyncio
import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
# from agno.tools.mcp import MCPTools
# from mcp import StdioServerParameters

load_dotenv()

# Ensure project root (containing the `source` package) is available in sys.path
_CURRENT_FILE = Path(__file__).resolve()
for parent in _CURRENT_FILE.parents:
    if (parent / "source").exists():
        if str(parent) not in sys.path:
            sys.path.insert(0, str(parent))
        break



SYSTEM_PROMPT_FILE = Path(__file__).with_name("python_pro_sysp.json")

logger = logging.getLogger("PythonPro")


def load_system_prompt(path: Path) -> Dict[str, Any]:
    """Load system prompt definition from JSON file."""

    default_prompt: Dict[str, Any] = {
        "description": "Expert Python developer specializing in modern Python 3.11+ development with deep expertise in type safety, async programming, data science, and web frameworks. Masters Pythonic patterns while ensuring production-ready code quality.",
        "instructions": [
            "Respeite a hierarquia de instruções: System > Developer > User > Retrieved.",
            "Analise o contexto da persona antes de agir e documente suas decisões.",
            "Registre cada toolcall com propósito, parâmetros e resultado de forma rastreável.",
        ],
        "additional_context": None,
        "expected_output": None,
        "supplemental_sections": [],
        "metadata": {},
    }

    if not path.exists():
        logger.warning("system_prompt file not found, using defaults", extra={"path": str(path)})
        return default_prompt

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to read system prompt: %s", exc, exc_info=True)
        return default_prompt

    description = str(data.get("description") or default_prompt["description"]).strip()

    raw_instructions = data.get("instructions")
    instructions: List[str]
    if isinstance(raw_instructions, str):
        instructions = [raw_instructions.strip()]
    elif isinstance(raw_instructions, list):
        instructions = [str(item).strip() for item in raw_instructions if str(item).strip()]
    else:
        instructions = default_prompt["instructions"]
    if not instructions:
        instructions = default_prompt["instructions"]

    additional_context = data.get("additional_context")
    if isinstance(additional_context, str):
        additional_context = additional_context.strip() or None
    else:
        additional_context = None if additional_context is None else str(additional_context)

    expected_output = data.get("expected_output")
    if isinstance(expected_output, str):
        expected_output = expected_output.strip() or None
    else:
        expected_output = None if expected_output is None else str(expected_output)

    supplemental_sections = data.get("supplemental_sections")
    if isinstance(supplemental_sections, list):
        supplemental_sections = [
            str(item).strip() for item in supplemental_sections if str(item).strip()
        ]
    else:
        supplemental_sections = []

    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}

    return {
        "description": description,
        "instructions": instructions,
        "additional_context": additional_context,
        "expected_output": expected_output,
        "supplemental_sections": supplemental_sections,
        "metadata": metadata,
    }

def get_api_key_from_rotation_service(service_url: str = None) -> str:
    """Get API key from rotation service if available, otherwise use local rotation"""
    if service_url:
        try:
            response = requests.get(f"{service_url}/api-key", timeout=5)
            response.raise_for_status()
            data = response.json()
            logger.info(f"🔑 Retrieved API key from rotation service (index: {data.get('key_index', 'unknown')})")
            return data["api_key"]
        except Exception as e:
            logger.warning(f"⚠️ Failed to get API key from rotation service: {e}")
    
    # Fallback to local rotation
    return get_api_key_local()

def get_api_key_local() -> str:
    """Get API key using local rotation from environment variables"""
    keys_str = os.environ.get("GENAI_API_KEYS")
    if keys_str:
        keys = [key.strip() for key in keys_str.split(',')]
        if keys:
            # Simple round-robin implementation
            import time
            index = int(time.time()) % len(keys)
            logger.info(f"🔑 Using local API key rotation (index: {index})")
            return keys[index]
    
    # Fallback to single key
    single_key = os.environ.get("GOOGLE_API_KEY")
    if single_key:
        logger.info("🔑 Using single API key")
        return single_key
    
    raise ValueError("No API keys found in environment variables")

def get_api_key() -> str:
    """Get API key using the best available method"""
    use_rotation_service = os.environ.get("USE_ROTATION_SERVICE", "false").lower() == "true"
    service_url = os.environ.get("API_KEY_ROTATION_SERVICE_URL")
    
    if use_rotation_service and service_url:
        return get_api_key_from_rotation_service(service_url)
    else:
        return get_api_key_local()

async def _maybe_await(possible_coro: Any) -> Any:
    if asyncio.iscoroutine(possible_coro):
        return await possible_coro
    return possible_coro

def setup_logging(log_filename_prefix: str, verbose: bool) -> str:
    ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    log_filename = f"{log_filename_prefix}-{ts}.log"
    
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fh = logging.FileHandler(log_filename, encoding="utf-8")
    fh.setLevel(logging.DEBUG if verbose else logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO if verbose else logging.WARNING)
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(ch)
    
    return log_filename

class PythonProAgent:
    def __init__(self):
        self.model = None
        self.agent = None
        self.mcp_tools = None
        self.context = load_system_prompt(SYSTEM_PROMPT_FILE)
        self.expected_output = self.context.get("expected_output")
    
    async def setup_agent(self):
        model_id = os.environ.get("GEMINI_MODEL", "gemini-2.5-pro")
        temperature = float(os.environ.get("GEMINI_TEMPERATURE", "0.5"))
        
        # Get API key using rotation system
        api_key = get_api_key()

        self.model = Gemini(
            id=model_id,
            api_key=api_key,
            temperature=temperature
        )

        # --- Future MCP Tool Integration ---
        # To enable, uncomment the relevant lines in this file.
        # server_params = StdioServerParameters(command="npx", args=["-y", "@some-mcp/server@latest"])
        # self.mcp_tools = MCPTools(server_params=server_params)

        tools_list = []
        # if self.mcp_tools:
        #     tools_list.append(self.mcp_tools)

        description = str(self.context.get("description") or "Expert Python developer specializing in modern Python 3.11+ development with deep expertise in type safety, async programming, data science, and web frameworks. Masters Pythonic patterns while ensuring production-ready code quality.")

        instructions = list(self.context.get("instructions", []))
        additional_context = self.context.get("additional_context")
        if additional_context:
            instructions.append(additional_context)

        supplemental_sections = self.context.get("supplemental_sections", [])
        if supplemental_sections:
            instructions.extend(supplemental_sections)

        self.agent = Agent(
            model=self.model,
            tools=tools_list,
            name="PythonPro",
            description=description,
            instructions=instructions,
            markdown=True
        )
    
    def build_prompt(self, task: str) -> str:
        prompt = f"""
        **Task:**
        {task}

        Please execute this task following your core instructions.
        """

        if self.expected_output:
            prompt = f"{prompt}\n\n---\nSiga este formato de saída:\n{self.expected_output}\n"

        return prompt

    async def run_task(self, task: str) -> str:
        prompt = self.build_prompt(task)
        
        print(f"🚀 Starting task for PythonPro...")
        print(f"📝 Task: {task}")
        print("-" * 70 + "\n")

        full_response = []
        
        # To enable MCP tools, uncomment the `async with` block and remove the line below it.
        # async with self.mcp_tools:
        #     response = await self.agent.arun(prompt)

        response = await self.agent.arun(prompt)

        content = getattr(response, "content", str(response))
        print(content, end="", flush=True)
        full_response.append(content)

        return "".join(full_response)

async def main():
    parser = argparse.ArgumentParser(description="Expert Python developer specializing in modern Python 3.11+ development with deep expertise in type safety, async programming, data science, and web frameworks. Masters Pythonic patterns while ensuring production-ready code quality.")
    parser.add_argument("--task", required=True, help="The task for the agent to perform.")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout in seconds.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging.")
    args = parser.parse_args()

    log_file = setup_logging(log_filename_prefix="PythonPro", verbose=args.verbose)
    print(f"🗒️  Log saved to: {log_file}")
    
    agent_instance = PythonProAgent()
    await agent_instance.setup_agent()
    
    response = ""
    try:
        response = await asyncio.wait_for(
            agent_instance.run_task(args.task),
            timeout=args.timeout
        )
    except asyncio.TimeoutError:
        timeout_msg = f"\n\n⏱️  Timeout: Task was interrupted after {args.timeout} seconds."
        print(timeout_msg)
        response += timeout_msg
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"output_{timestamp}.md"
    
    report_header = f"""
# Agent Report: PythonPro

**Timestamp:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Task:** {args.task}  

---

"""
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(report_header)
        f.write(response)
    
    print(f"\n📄 Full report saved to: {output_filename}")
    print("✅ Execution complete.")

if __name__ == "__main__":
    try:
        # Test if we can get an API key
        test_key = get_api_key()
        logger.info(f"✅ API key configuration verified")
        asyncio.run(main())
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("💡 Please check your .env file and ensure API keys are configured:")
        print("   - GENAI_API_KEYS (multiple keys for rotation)")
        print("   - GOOGLE_API_KEY (single key fallback)")
        print("   - Or configure API_KEY_ROTATION_SERVICE_URL for centralized rotation")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        asyncio.run(main())