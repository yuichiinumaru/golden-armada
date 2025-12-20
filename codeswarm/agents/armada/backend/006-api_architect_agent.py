#!/usr/bin/env python3
"""
Refactored ApiArchitectAgent using SwarmAgent base and shared utilities.
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Ensure core packages are in path if run standalone
_CURRENT_FILE = Path(__file__).resolve()
for parent in _CURRENT_FILE.parents:
    if (parent / "codeswarm").exists():
        if str(parent) not in sys.path:
            sys.path.insert(0, str(parent))
        break

from codeswarm.core.base_agent import SwarmAgent
from codeswarm.core.agent_utils import load_system_prompt, setup_logging
from codeswarm.core.api_keys import get_api_key

load_dotenv()

SYSTEM_PROMPT_FILE = Path(__file__).with_name("api_architect_sysp.json")
logger = logging.getLogger("ApiArchitect")

class ApiArchitectAgent(SwarmAgent):
    def __init__(self, user_id: str = "cli-user"):
        self.context = load_system_prompt(SYSTEM_PROMPT_FILE)
        
        # Extract instructions and append extras
        instructions = list(self.context.get("instructions", []))
        if self.context.get("additional_context"):
            instructions.append(self.context.get("additional_context"))
        if self.context.get("supplemental_sections"):
            instructions.extend(self.context.get("supplemental_sections"))

        description = self.context.get("description", "Expert API Architect")
        
        # Initialize SwarmAgent
        super().__init__(
            user_id=user_id,
            agent_name="ApiArchitect",
            role="Architect",
            model_id=os.environ.get("GEMINI_MODEL", "gemini-2.5-pro"),
            instructions=instructions,
            use_memory=True
        )
        self.agent.description = description

    async def run_cli_task(self, task: str):
        """Run a task from CLI with formatted output."""
        print(f"🚀 Starting task for {self.agent_name}...")
        print(f"📝 Task: {task}")
        print("-" * 70 + "\n")

        # Use the chat/run_task method from SwarmAgent
        result = await self.chat(task)
        response_content = result["response"]

        print(response_content, end="", flush=True)
        return response_content

async def main():
    parser = argparse.ArgumentParser(description="ApiArchitect Agent CLI")
    parser.add_argument("--task", required=True, help="The task for the agent to perform.")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout in seconds.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging.")
    args = parser.parse_args()

    log_file = setup_logging("ApiArchitect", verbose=args.verbose)
    print(f"🗒️  Log saved to: {log_file}")

    agent = ApiArchitectAgent(user_id="cli-user")
    await agent.setup_agent()

    try:
        await asyncio.wait_for(agent.run_cli_task(args.task), timeout=args.timeout)
    except asyncio.TimeoutError:
        print(f"\n\n⏱️  Timeout after {args.timeout}s")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main())