import argparse
import asyncio
import sys
import os
from pathlib import Path

# Fix path to allow importing app
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Ensure env vars are loaded
from dotenv import load_dotenv
load_dotenv()

from app.services.agent_maker import agent_maker
from app.services.agent_factory import create_agent_file

async def main():
    parser = argparse.ArgumentParser(description="AgentMaker v2 CLI")
    parser.add_argument("name", help="Name of the agent")
    parser.add_argument("--prompt", "-p", help="System prompt")
    parser.add_argument("--file", "-f", help="Path to MD file with prompt")
    
    args = parser.parse_args()
    
    prompt = args.prompt
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                prompt = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return

    if not prompt:
        print("Error: Must provide --prompt or --file")
        return

    print(f"🤖 Engineering Agent: {args.name}...")
    print("   Analyzing requirements and selecting tools...")
    
    draft = {
        "name": args.name,
        "description": "Created via CLI",
        "prompt": prompt
    }
    
    try:
        final_spec = await agent_maker.engineer_agent(draft)

        print("   Generating code...")
        success, msg = create_agent_file(
            name=final_spec['name'],
            prompt=final_spec['prompt'],
            model="gemini-2.5-flash",
            tools=final_spec['tools'],
            mcp_tools=final_spec.get('mcp_servers', [])
        )

        if success:
            print(f"✅ Success: {msg}")
            if final_spec['tools']:
                print(f"   🛠️  Tools Injected: {[t['class_name'] for t in final_spec['tools']]}")
            else:
                print(f"   ℹ️  No tools selected (Heuristics/AI decision).")
        else:
            print(f"❌ Failed: {msg}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
