from codeswarm.core.base_agent import SwarmAgent
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

# # Ensure project root (containing the `source` package) is available in sys.path
_CURRENT_FILE = Path(__file__).resolve()
for parent in _CURRENT_FILE.parents:
    if (parent / "source").exists():
        if str(parent) not in sys.path:
            sys.path.insert(0, str(parent))
        break 
# (Commented out by migration script: codeswarm uses standard package structure)



SYSTEM_PROMPT_FILE = Path(__file__).with_name("spec_planner_sysp.json")

logger = logging.getLogger("SpecPlanner")


def load_system_prompt(path: Path) -> Dict[str, Any]:
    """Load system prompt definition from JSON file."""

    default_prompt: Dict[str, Any] = {
        "description": "Implementation planning specialist that breaks down architectural designs into actionable tasks. Creates detailed task lists, estimates complexity, defines implementation order, and plans comprehensive testing strategies. Bridges the gap between design and development.",
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


class SpecPlannerAgent(SwarmAgent):
    def __init__(self):
        self.context = load_system_prompt(SYSTEM_PROMPT_FILE)
        
        description = str(self.context.get("description") or "Implementation planning specialist...")
        instructions = list(self.context.get("instructions", []))
        additional_context = self.context.get("additional_context")
        if additional_context:
            instructions.append(additional_context)
        supplemental_sections = self.context.get("supplemental_sections", [])
        if supplemental_sections:
            instructions.extend(supplemental_sections)

        # Convert list of instructions to a single string for SwarmAgent/Agno
        instructions_str = "\n".join(instructions)

        super().__init__(
            agent_name="SpecPlanner",
            role="Planner", # Triggers Reasoning Model
            instructions=instructions_str
        )
        # SwarmAgent handles model init, api keys, and tools
    
    # SwarmAgent.run_task calls self.chat, but we can keep run_task wrapper if needed or rely on base.
    # The original had specific logging formatting. We can keep a thin wrapper.

    async def run_task(self, task: str) -> str:
        prompt = f"""
        **Task:**
        {task}

        Please execute this task following your core instructions.
        """
        expected_output = self.context.get("expected_output")
        if expected_output:
            prompt = f"{prompt}\n\n---\nSiga este formato de saída:\n{expected_output}\n"
            
        print(f"🚀 Starting task for SpecPlanner...")
        print(f"📝 Task: {task}")
        print("-" * 70 + "\n")

        # Use the base agent's chat method which uses the initialized self.agent
        response = await self.chat(prompt)
        
        # SwarmAgent.chat returns a dict with 'response' key, or we can use generic run if chat is too chatty.
        # Let's look at SwarmAgent.chat return type. It returns Dict[str, Any].
        # But here we want the stream or full string.
        # SwarmAgent.agent is the Agno agent. We can access it directly if we want the specific print behavior.
        
        # Actually, let's just delegate to self.agent.arun(prompt) like before but using the initialized agent
        
        response_obj = await self.agent.arun(prompt)
        content = getattr(response_obj, "content", str(response_obj))
        
        print(content, end="", flush=True)
        return content

async def main():
    parser = argparse.ArgumentParser(description="Implementation planning specialist.")
    parser.add_argument("--task", required=True, help="The task for the agent to perform.")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout in seconds.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging.")
    args = parser.parse_args()

    # SwarmAgent setup_logging is global usually, or we can use the one internal if we want specific file.
    # We'll use the one defined in this file for now or the base one.
    # The base agent uses codeswarm.core.agent_utils.setup_logging.
    # Let's use the local one for backward compatibility or switch to base.
    # Switching to base is cleaner but might change log file name format.
    # Let's keep existing main logic generally but use the new class.
    
    log_file = setup_logging(log_filename_prefix="SpecPlanner", verbose=args.verbose)
    print(f"🗒️  Log saved to: {log_file}")
    
    agent_instance = SpecPlannerAgent()
    # No setup_agent() needed, init does it.
    
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
# Agent Report: SpecPlanner

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
    asyncio.run(main())