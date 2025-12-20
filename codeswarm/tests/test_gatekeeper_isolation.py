import asyncio
import os
from dotenv import load_dotenv
from codeswarm.agents.gatekeeper_agent import SecurityAboyeur

load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = "dummy"

async def test_gatekeeper_isolation():
    print("Testing Gatekeeper Isolation...")
    gk = SecurityAboyeur()
    
    print(f"Gatekeeper Initialized. use_memory={gk.use_memory}")
    
    if gk.use_memory:
        print("FAIL: Gatekeeper memory should be disabled.")
    else:
        print("PASS: Gatekeeper memory is disabled locally.")
        
    try:
        # Accessing khala should raise RuntimeError
        _ = gk.khala
        print("FAIL: Accessing gk.khala should have raised RuntimeError")
    except RuntimeError as e:
        print(f"PASS: Accessing khala raised expected error: {e}")
    except Exception as e:
        print(f"FAIL: Unexpected error accessing khala: {e}")

    try:
        await gk.remember("Secret content that shouldn't be stored")
        # Remember should silently return if disabled, checking logs/execution flow
        print("PASS: executed remember() without crashing (should be no-op)")
    except Exception as e:
        print(f"FAIL: remember() crashed: {e}")

if __name__ == "__main__":
    asyncio.run(test_gatekeeper_isolation())
