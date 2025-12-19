import json
import logging
from typing import Dict, Any, List, Optional
from codeswarm.core.base_agent import SwarmAgent
from codeswarm.core.registry import AgentRegistry
from codeswarm.agents.gatekeeper_agent import SecurityAboyeur

logger = logging.getLogger(__name__)

class OrchestratorAgent(SwarmAgent):
    """
    Codeswarm Orchestrator - The Central Brain.
    Ported from reference ViviArchitect.
    Integrates with AgentRegistry for dynamic capability discovery and SecurityAboyeur for safety.
    """
    def __init__(self, user_id: str = "default_user"):
        super().__init__(
            user_id=user_id,
            agent_name="OrchestratorAgent",
            model_id="gemini-2.5-pro", # Strong model for planning
            instructions="""
            You are the "Orchestrator", the autonomous planning engine for Codeswarm.
            
            YOUR GOAL: 
            Analyze the User Request and create a high-efficiency execution plan.
            
            RESPONSE FORMAT (JSON):
            {
              "thoughts": "Brief strategy explanation...",
              "steps": [
                {
                  "agent_name": "AgentClassName",
                  "type": "single" | "parallel",
                  "priority": "high" | "medium",
                  "reasoning": "Why I chose this agent...",
                  "instruction": "Detailed instruction for the agent"
                }
              ]
            }
            """
        )
        self.registry = AgentRegistry()
        self.registry.load_agents()
        self.gatekeeper = SecurityAboyeur(user_id=user_id)

    async def plan_workflow(self, user_request: str) -> Dict[str, Any]:
        """
        Analyzes the User Request and creates an execution plan.
        Includes a Gatekeeper security check before planning.
        """
        # 1. Security Check
        logger.info(f"Orchestrator invoking Gatekeeper for request: {user_request[:50]}...")
        # Note: calling internal verify or chat. Using internal check for speed?
        # Let's use the chat method which encapsulates the logic.
        # But wait, chat returns a dict.
        security_response = await self.gatekeeper.chat(user_request)
        response_text = security_response.get("response", "").lower()
        if "rejected" in response_text or "violation" in response_text:
            logger.warning("Request blocked by Gatekeeper.")
            return {
                "thoughts": "Security Violation Detected. Request blocked.",
                "steps": [],
                "error": "Security Violation"
            }

        # 2. Dynamic Agent Discovery
        available_agents = self.registry.list_agents()
        agents_list_str = ", ".join(available_agents)

        # 3. Planning
        prompt = f"""
        USER REQUEST: {user_request}
        
        Analyze the request and generate a JSON plan.
        
        AVAILABLE AGENTS (Delegate to these specialists):
        [{agents_list_str}]
        
        Note:
        - Use 'DeepReasoner' (if available) for complex logic.
        - Use 'BIAnalystAgent', 'FiscalAccuserAgent', etc. for domain specific tasks.
        - Use 'PerformanceOptimizer' for optimization tasks.
        - Use 'AgentMakerService' (via a wrapper or direct call if implemented as agent) for creating new agents.
        
        Generate the plan now.
        """
        
        try:
            response = self.run(prompt)
            # Handle response content extraction similar to reference
            text = response.content if hasattr(response, 'content') else str(response)
            
            # Clean markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            return json.loads(text)
            
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return {
                "thoughts": "Failed to generate plan. Fallback mode.",
                "steps": [],
                "error": str(e)
            }

    async def generate_final_report(self, original_request: str, execution_logs: str) -> str:
        """Generates a final executive report."""
        prompt = f"""
        Generate a final executive report based on the original request and the execution logs.
        
        REQUEST: "{original_request}"
        
        EXECUTION LOGS:
        {execution_logs}
        
        FORMAT: Markdown.
        """
        
        response = self.run(prompt)
        return response.content if hasattr(response, 'content') else str(response)
