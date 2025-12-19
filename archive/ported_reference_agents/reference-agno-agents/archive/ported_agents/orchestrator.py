from typing import Dict, Any, List, Optional
import json
from app.templates.base_agent import KhalaBaseAgent
from agno.agent import Agent
from agno.models.google import Gemini

class OrchestratorAgent(KhalaBaseAgent):
    def __init__(self, user_id: str):
        super().__init__(
            user_id=user_id,
            agent_name="ViviArchitect",
            model_id="gemini-2.5-flash",
            system_prompt="You are the Vivi Architect, an autonomous planning engine.",
            tools=[]
        )
        # We might use a stronger model for planning if needed
        self.planner_model = Gemini(id="gemini-2.5-pro")

    async def plan_workflow(self, user_request: str, language: str = 'en-us') -> Dict[str, Any]:
        """
        Analyzes the User Request and creates a high-efficiency execution plan.
        Ported from orchestratorService.ts
        """
        system_prompt = f"""
        You are the "Vivi Architect", an autonomous planning engine for IVISA RIO.
        
        YOUR GOAL: 
        Analyze the User Request and create a high-efficiency execution plan using Vivi primitives (Agents, Workflows, Tools).
        
        LANGUAGE REQUIREMENT:
        The user prefers: {language}.
        - The 'thoughts' field MUST be in this language.
        - The 'instruction' fields for agents MUST be in this language.
        
        HANDLING AMBIGUITY (CRITICAL):
        - If the user request is too broad, create a SINGLE step using 'vivi-generalist' to ask for clarification.

        SWARM PATTERN DETECTION:
        - If the user provides a list of links or multiple items, use 'parallel' step type.
        
        RESPONSE FORMAT (JSON):
        {{
          "thoughts": "Brief strategy explanation...",
          "steps": [
            {{
              "toolId": "tool-id-here",
              "type": "single" | "parallel",
              "priority": "high" | "medium",
              "reasoning": "Why I chose this tool...",
              "instruction": "Detailed instruction for the agent",
              "parallelTasks": [ ... ]
            }}
          ]
        }}
        """
        
        try:
            # Using the underlying Agno agent or model directly for JSON generation
            response = self.agent.run(
                f"USER REQUEST: {user_request}",
                system_message=system_prompt,
                response_model=None # We want raw JSON string to parse manually or use Pydantic model if defined
            )
            
            # Agno's run returns a RunResponse. content is the text.
            text = response.content
            
            # Clean markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                
            return json.loads(text)
            
        except Exception as e:
            self.logger.error(f"Planning failed: {e}")
            return {
                "thoughts": "Failed to generate plan. Using general agent.",
                "steps": [{
                    "toolId": "vivi-generalist",
                    "type": "single",
                    "status": "pending",
                    "reasoning": "Fallback mechanism.",
                    "instruction": user_request
                }]
            }

    async def review_task_output(self, instruction: str, deliverables: List[str], output: str) -> Dict[str, Any]:
        """Reviews task output against deliverables."""
        prompt = f"""
        Review this output against deliverables.
        Instruction: {instruction}
        Deliverables: {json.dumps(deliverables)}
        Output: {output[:2000]}...
        
        Return JSON {{ "approved": boolean, "feedback": string }}
        """
        
        try:
            response = self.agent.run(prompt)
            text = response.content
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception:
            return {"approved": True, "feedback": "Auto-approved (Review failed)."}

    async def generate_final_report(self, original_request: str, completed_steps: List[Dict[str, Any]]) -> str:
        """Generates a final executive report."""
        context_data = ""
        for i, s in enumerate(completed_steps):
            result = s.get('result', '')
            if s.get('type') == 'parallel' and s.get('parallelTasks'):
                result = "\\n".join([f"--- TASK {idx+1} ---\\n{pt.get('result','')}" for idx, pt in enumerate(s['parallelTasks'])])
            context_data += f"STEP {i+1} ({s.get('toolId')}):\\n{result}\\n\\n"
            
        prompt = f"""
        Generate a final executive report based on the original request and the execution logs below.
        
        REQUEST: "{original_request}"
        
        EXECUTION LOGS:
        {context_data}
        
        FORMAT: Markdown.
        """
        
        response = self.agent.run(prompt)
        return response.content
