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
        uses Category Routing to scale to hundreds of agents.
        """
        # 1. Security Check
        logger.info(f"Orchestrator invoking Gatekeeper for request: {user_request[:50]}...")
        security_response = await self.gatekeeper.chat(user_request)
        response_text = security_response.get("response", "").lower()
        if "rejected" in response_text or "violation" in response_text:
            logger.warning("Request blocked by Gatekeeper.")
            return {
                "thoughts": "Security Violation Detected. Request blocked.",
                "steps": [],
                "error": "Security Violation"
            }

        # 2. Category Routing (Step 1)
        all_categories = self.registry.get_categories()
        # Ensure 'general' and 'specialists' are always considered if available
        default_cats = [c for c in ['general', 'specialists'] if c in all_categories]
        
        classification_prompt = f"""
        USER REQUEST: "{user_request}"
        
        AVAILABLE CATEGORIES: {all_categories}
        
        Task: Identify the most relevant categories for this request.
        Always include 'general' for broad tasks.
        
        Return JSON ONLY: {{ "categories": ["cat1", "cat2"] }}
        """
        
        selected_categories = default_cats
        try:
            # Use the agent to classify. 
            # Note: Ideally we'd use a faster model here, but using the reasoning model is safer for accuracy.
            class_response = await self.a_run(classification_prompt)
            text = class_response.content if hasattr(class_response, 'content') else str(class_response)
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            data = json.loads(text)
            selected_categories = list(set(data.get("categories", []) + default_cats))
            logger.info(f"Routing Request to Categories: {selected_categories}")
        except Exception as e:
            logger.warning(f"Category routing failed, defaulting to all: {e}")
            selected_categories = all_categories

        # 3. Dynamic Agent Discovery (Step 2)
        candidate_agents = []
        for cat in selected_categories:
            candidate_agents.extend(self.registry.get_agents_by_category(cat))
        
        # Remove duplicates
        candidate_agents = list(set(candidate_agents))
        agents_list_str = ", ".join(candidate_agents)

        # 4. Planning (Step 3)
        prompt = f"""
        USER REQUEST: {user_request}
        
        Analyze the request and generate a JSON plan.
        
        AVAILABLE AGENTS (Filtered by category):
        [{agents_list_str}]
        
        Note:
        - Use 'DeepReasoner' (if available) for complex logic.
        - Use 'BIAnalystAgent', 'FiscalAccuserAgent', etc. for domain specific tasks.
        - Use 'PerformanceOptimizer' for optimization tasks.
        - Use 'AgentMakerService' (via a wrapper or direct call if implemented as agent) for creating new agents.
        
        Generate the plan now.
        """
        
        try:
            response = await self.a_run(prompt)
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
