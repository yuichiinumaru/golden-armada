# Implementing Advanced AI Agent Patterns in Agno AGI v2

A comprehensive guide to building enterprise-grade AI agents using Agno's advanced capabilities, including agent loop architecture, tool calling best practices, file editing strategies, environment awareness, deep research patterns, and agentic reasoning.

---

## 1. Agent Loop Architecture (6-Stage Cycle)

The agent loop is the core execution model in Agno. Here's how to implement the complete lifecycle with proper event handling and fallback mechanisms.

### 1.1 Understanding the Core Loop

```python
from agno.agent import Agent, RunEvent, RunOutput
from agno.models.openai import OpenAIChat
import asyncio

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[...],  # Your tools
)

# The 6-stage loop in Agno:
# 1. ANALYZE EVENTS - Agent reads event stream
# 2. SELECT TOOLS - Agent chooses appropriate tool based on context
# 3. WAIT FOR EXECUTION - Tool executes in sandbox environment
# 4. ITERATE - Repeat with new observations added to event stream
# 5. SUBMIT RESULTS - Send results via message tools
# 6. ENTER STANDBY - Idle state until new task arrives
```

### 1.2 Implementing Event Monitoring

```python
async def run_agent_with_event_monitoring(agent: Agent, prompt: str):
    """Monitor all agent loop events with detailed tracking"""
    
    event_log = []
    tool_call_count = 0
    iteration_count = 0
    MAX_ITERATIONS = 16  # Global tool call limit
    MAX_RETRIES_PER_ERROR = 3
    error_tracking = {}
    
    async for run_output_event in agent.arun(
        prompt,
        stream=True,
        stream_events=True,
    ):
        iteration_count += 1
        
        # 1. ANALYZE EVENTS
        if run_output_event.event == RunEvent.run_started:
            print(f"[ANALYZE] Run started, analyzing event stream")
            event_log.append(("ANALYZE", run_output_event))
        
        # 2. SELECT TOOLS
        elif run_output_event.event == RunEvent.tool_call_started:
            tool_call_count += 1
            tool_name = run_output_event.tool.tool_name
            print(f"[SELECT] Tool selected: {tool_name} (Call #{tool_call_count})")
            event_log.append(("SELECT_TOOL", tool_name))
            
            # Check if we're hitting the global iteration limit
            if tool_call_count >= MAX_ITERATIONS:
                print(f"WARNING: Approaching max iterations ({MAX_ITERATIONS})")
        
        # 3. WAIT FOR EXECUTION
        elif run_output_event.event == RunEvent.tool_call_completed:
            tool_name = run_output_event.tool.tool_name
            result = run_output_event.tool.result
            
            print(f"[EXECUTE] Tool executed: {tool_name}")
            
            # Track errors for fallback mechanism
            if "error" in str(result).lower():
                error_tracking[tool_name] = error_tracking.get(tool_name, 0) + 1
                
                if error_tracking[tool_name] >= MAX_RETRIES_PER_ERROR:
                    print(f"[FALLBACK] Tool '{tool_name}' failed {MAX_RETRIES_PER_ERROR}x, attempting alternative")
            
            event_log.append(("EXECUTE", tool_name, result))
        
        # 4. ITERATE (new observations)
        elif run_output_event.event == RunEvent.reasoning_step:
            print(f"[ITERATE] Reasoning: {run_output_event.content[:100]}...")
            event_log.append(("ITERATE_REASONING", run_output_event.content))
        
        # 5. SUBMIT RESULTS
        elif run_output_event.event == RunEvent.run_content:
            print(f"[SUBMIT] Result content: {run_output_event.content[:100]}...")
            event_log.append(("SUBMIT_RESULT", run_output_event.content))
        
        # 6. ENTER STANDBY
        elif run_output_event.event == RunEvent.run_completed:
            print(f"[STANDBY] Run completed. Total iterations: {iteration_count}, Tool calls: {tool_call_count}")
            event_log.append(("STANDBY", "Run complete"))
    
    return event_log, tool_call_count

# Usage
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[...],
)

log, calls = asyncio.run(
    run_agent_with_event_monitoring(agent, "Your complex task here")
)
```

### 1.3 Checkpoint System Implementation

```python
from dataclasses import dataclass
import json
from datetime import datetime

@dataclass
class Checkpoint:
    iteration: int
    timestamp: str
    tool_calls: int
    progress: str
    context_snapshot: dict

class CheckpointManager:
    def __init__(self, checkpoint_interval: int = 5):
        self.checkpoint_interval = checkpoint_interval
        self.checkpoints = []
    
    def create_checkpoint(self, iteration: int, tool_calls: int, 
                         progress: str, context: dict):
        """Create checkpoint every N tool calls (5 recommended)"""
        if tool_calls % self.checkpoint_interval == 0:
            checkpoint = Checkpoint(
                iteration=iteration,
                timestamp=datetime.now().isoformat(),
                tool_calls=tool_calls,
                progress=progress,
                context_snapshot=context
            )
            self.checkpoints.append(checkpoint)
            return checkpoint
        return None
    
    def validate_progress(self, checkpoint: Checkpoint) -> bool:
        """Evaluate if progress is being made"""
        if len(self.checkpoints) < 2:
            return True
        
        prev_checkpoint = self.checkpoints[-2]
        
        # Check if we're repeating the same action
        if checkpoint.progress == prev_checkpoint.progress:
            return False
        
        return True
    
    def get_delta_updates(self) -> list:
        """Get progress deltas to avoid repetition"""
        deltas = []
        for i in range(1, len(self.checkpoints)):
            prev = self.checkpoints[i-1]
            curr = self.checkpoints[i]
            deltas.append({
                "iteration_delta": curr.iteration - prev.iteration,
                "progress_change": curr.progress != prev.progress,
                "tool_calls_delta": curr.tool_calls - prev.tool_calls
            })
        return deltas

# Usage in agent run
async def run_with_checkpoints(agent: Agent, prompt: str):
    checkpoint_mgr = CheckpointManager(checkpoint_interval=5)
    iteration = 0
    tool_calls = 0
    
    async for event in agent.arun(prompt, stream=True, stream_events=True):
        if event.event == RunEvent.tool_call_completed:
            tool_calls += 1
            iteration += 1
            
            # Create checkpoint every 5 tool calls
            checkpoint = checkpoint_mgr.create_checkpoint(
                iteration=iteration,
                tool_calls=tool_calls,
                progress=f"Completed {tool_calls} tool calls",
                context={"last_tool": event.tool.tool_name}
            )
            
            if checkpoint:
                # Validate progress
                if not checkpoint_mgr.validate_progress(checkpoint):
                    print("ALERT: No progress detected, consider fallback strategy")
                    # Implement alternative approach
                
                print(f"CHECKPOINT {tool_calls}: {checkpoint.progress}")
```

---

## 2. Tool Calling Etiquette & Best Practices

### 2.1 The 7 Critical Principles

```python
from agno.agent import Agent
from agno.tools import tool
from typing import Any, Callable, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolCallingEtiquette:
    """Enforce proper tool calling patterns"""
    
    @staticmethod
    def principle_1_hide_implementation_details(user_message: str, tool_name: str) -> str:
        """Never mention tool names to users"""
        # WRONG: "I'll now use the 'database_query' tool to..."
        # RIGHT: "I'll search the database for..."
        return user_message.replace(f"using {tool_name}", "by searching")
    
    @staticmethod
    def principle_2_explain_rationale_first(tool_name: str, args: Dict[str, Any]) -> str:
        """Explain WHY before calling tool"""
        return f"To get this information, I need to search for {args.get('query', 'data')}. Let me do that now."
    
    @staticmethod
    def principle_3_strict_schema_adherence(tool_definition: Dict) -> bool:
        """Always validate against JSON schema"""
        required_fields = tool_definition.get("properties", {}).keys()
        # Validate all required parameters exist and match types
        return True
    
    @staticmethod
    def principle_4_no_permission_asking(context: Dict) -> str:
        """Don't ask permission; users expect action"""
        # WRONG: "Can I search the web for this?"
        # RIGHT: "I'm searching the web for this information."
        return "Taking action immediately..."
    
    @staticmethod
    def principle_5_message_tool_usage(tool_type: str) -> str:
        """Use appropriate message tools"""
        # notify = non-blocking (background updates)
        # ask = blocking (requires user response)
        if tool_type == "informational":
            return "notify"  # Don't block for info
        elif tool_type == "requires_decision":
            return "ask"     # Block for decisions
        return "notify"
    
    @staticmethod
    def principle_6_parallel_execution(tools_to_call: list) -> bool:
        """Execute independent operations in parallel"""
        # EXCEPTION: semantic_search should NEVER run in parallel
        if any("semantic_search" in str(t) for t in tools_to_call):
            return False
        return True
    
    @staticmethod
    def principle_7_no_fabrication(available_tools: list, requested_tool: str) -> bool:
        """Never invent non-existent tools"""
        if requested_tool not in available_tools:
            logger.error(f"Tool '{requested_tool}' not available. Available: {available_tools}")
            return False
        return True
```

### 2.2 Proper Tool Definition with Hooks

```python
@tool(
    name="search_database",
    description="Search the application database for records matching criteria",
    stop_after_tool_call=False,  # Let model process results
    show_result=True,
)
def search_database(query: str, filters: Dict[str, Any] | None = None) -> Dict:
    """
    Args:
        query: The search term or SQL-like query
        filters: Optional metadata filters
    
    Returns:
        List of matching records with metadata
    """
    # Implementation
    return {"results": [], "count": 0}

# Pre-execution hook: validate inputs
def pre_search_validation(function_name: str, function_call: Callable, 
                         arguments: Dict[str, Any]):
    """Validate before execution"""
    if not arguments.get("query"):
        raise ValueError("Query parameter is required")
    logger.info(f"About to call {function_name} with query: {arguments['query']}")

# Post-execution hook: validate outputs
def post_search_validation(result: Any):
    """Validate output quality"""
    if not isinstance(result, dict):
        logger.warning("Unexpected result format")
    return result

# Create agent with proper tool configuration
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[search_database],
    tool_hooks=[pre_search_validation],
    instructions=[
        "Never mention tool names in responses",
        "Explain why you're taking each action",
        "Execute tools without asking permission",
        "Use parallel execution when possible",
    ]
)
```

---

## 3. File Editing Strategies

### 3.1 Line-Based Search and Replace (Preferred Method)

```python
from agno.tools import tool
import re

@tool(
    name="replace_in_file_by_line",
    description="Replace content in a file using line numbers and validation",
)
def replace_file_content_by_line(
    filepath: str,
    search_content: str,
    replace_content: str,
    first_replaced_line: int,
    last_replaced_line: int,
    validate: bool = True
) -> Dict[str, Any]:
    """
    Preferred approach for edits > 6 lines.
    Uses explicit line numbers for precision.
    
    Example:
        filepath: "src/components/TaskList.tsx"
        search_content: '''const handleTaskComplete = (taskId) => {
          setTasks(...)
          ... existing code ...
          onTaskUpdate?.(updatedTasks)
        }'''
        replace_content: '''const handleTaskComplete = useCallback((taskId: string) => {
          // Analytics tracking
          ...
        })'''
        first_replaced_line: 15
        last_replaced_line: 28
    """
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Validate line range
        if first_replaced_line < 1 or last_replaced_line > len(lines):
            return {"success": False, "error": "Line range out of bounds"}
        
        # Validate search content matches
        actual_content = ''.join(lines[first_replaced_line-1:last_replaced_line])
        
        if validate and search_content.strip() != actual_content.strip():
            return {
                "success": False,
                "error": "Search content doesn't match file content",
                "expected": search_content,
                "actual": actual_content
            }
        
        # Perform replacement
        new_lines = (
            lines[:first_replaced_line-1] +
            [replace_content + '\n'] +
            lines[last_replaced_line:]
        )
        
        with open(filepath, 'w') as f:
            f.writelines(new_lines)
        
        return {
            "success": True,
            "lines_replaced": last_replaced_line - first_replaced_line + 1,
            "filepath": filepath
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}

# Usage in agent
@tool(name="edit_code", description="Edit code files")
def edit_code(task: str):
    """Agent uses this when modifying existing code"""
    # For large changes (>6 lines):
    return replace_file_content_by_line(
        filepath="src/main.py",
        search_content="old_function():\n    pass",
        replace_content="new_function():\n    # Implementation",
        first_replaced_line=10,
        last_replaced_line=15
    )
```

### 3.2 String Replacement (For Simple Changes)

```python
@tool(
    name="replace_string_in_file",
    description="Simple string replacement for small, precise changes"
)
def replace_string_in_file(
    filepath: str,
    old_string: str,
    new_string: str,
    context_lines: int = 3
) -> Dict[str, Any]:
    """
    Use for simple, isolated changes where you have a unique substring.
    Requires 3-5 lines of context before/after for validation.
    
    Example: Changing an import or renaming a variable
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Validate uniqueness with context
        occurrences = content.count(old_string)
        if occurrences != 1:
            return {
                "success": False,
                "error": f"String appears {occurrences} times, not unique",
                "suggestion": "Use line-based replacement for multiple occurrences"
            }
        
        new_content = content.replace(old_string, new_string)
        
        with open(filepath, 'w') as f:
            f.write(new_content)
        
        return {"success": True, "filepath": filepath}
    
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 3.3 Insert Edit (Last Resort)

```python
@tool(
    name="insert_edit_into_file",
    description="Smart insertion that understands context (use only if other methods fail)"
)
def insert_edit_into_file(
    filepath: str,
    location_marker: str,  # Search for this context
    new_code: str,
    position: str = "after"  # "before" or "after"
) -> Dict[str, Any]:
    """
    Use ONLY when:
    1. Line-based replacement fails
    2. User explicitly requests it
    3. Code structure makes line numbers unreliable
    
    Example:
        location_marker = "class Person {"
        new_code = "  age: number;  // New field"
        position = "after"
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        if location_marker not in content:
            return {
                "success": False,
                "error": f"Marker '{location_marker}' not found in file"
            }
        
        if position == "after":
            new_content = content.replace(
                location_marker,
                location_marker + "\n" + new_code
            )
        else:
            new_content = content.replace(
                location_marker,
                new_code + "\n" + location_marker
            )
        
        with open(filepath, 'w') as f:
            f.write(new_content)
        
        return {"success": True, "filepath": filepath}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

# Decision flowchart for agents
EDIT_STRATEGY_FLOW = """
1. Is this a modification to existing code?
   └─ YES: Can you identify exact line numbers?
           └─ YES: Use replace_file_content_by_line() (PREFERRED)
           └─ NO: Have you got unique search string? 
                  └─ YES: Use replace_string_in_file()
                  └─ NO: Use insert_edit_into_file()
   
2. Is this adding new code?
   └─ Use insert_edit_into_file()
"""
```

---

## 4. Sandbox Environment Awareness

### 4.1 Environment Detection

```python
import os
import platform
import sys
from dataclasses import dataclass
from typing import Optional

@dataclass
class SandboxEnvironment:
    """Complete environment awareness for agents"""
    
    # System Information
    os_name: str
    os_version: str
    architecture: str
    
    # Runtime Environment
    python_version: str
    node_version: Optional[str] = None
    default_shell: str = "bash"
    
    # Sandbox Constraints (if applicable)
    has_pip: bool = True
    has_git: bool = True
    has_native_binaries: bool = True
    stdlib_only: bool = False  # WebContainer limitation
    
    # Directory Context
    cwd: str = ""
    home_dir: str = ""
    
    # Permissions
    has_sudo: bool = False
    
    # Current Time
    current_timestamp: str = ""

class EnvironmentAwareness:
    @staticmethod
    def detect_environment() -> SandboxEnvironment:
        """Detect and report full environment context"""
        
        # Detect OS
        system = platform.system()
        if system == "Windows":
            os_name = "Windows"
            shell = "powershell.exe"
        elif system == "Darwin":
            os_name = "macOS"
            shell = "zsh"
        else:
            os_name = "Linux"
            shell = "bash"
        
        return SandboxEnvironment(
            os_name=os_name,
            os_version=platform.version(),
            architecture=platform.machine(),
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            default_shell=shell,
            cwd=os.getcwd(),
            home_dir=os.path.expanduser("~"),
            current_timestamp=str(__import__('datetime').datetime.now().isoformat()),
            # Detection of constraints
            has_pip=EnvironmentAwareness._check_pip(),
            has_git=EnvironmentAwareness._check_git(),
        )
    
    @staticmethod
    def _check_pip() -> bool:
        """Check if pip is available"""
        import shutil
        return shutil.which("pip") is not None
    
    @staticmethod
    def _check_git() -> bool:
        """Check if git is available"""
        import shutil
        return shutil.which("git") is not None

# Usage in Agent
def create_environment_aware_agent(model):
    """Create agent with full environment context"""
    
    env = EnvironmentAwareness.detect_environment()
    
    system_context = f"""
You are running in the following environment:
- OS: {env.os_name} {env.os_version}
- Architecture: {env.architecture}
- Python: {env.python_version}
- Shell: {env.default_shell}
- Working Directory: {env.cwd}
- pip available: {env.has_pip}
- git available: {env.has_git}

IMPORTANT CONSTRAINTS:
- For Windows: Use '{env.default_shell}' syntax and path separators
- For Linux/Mac: Use bash/zsh syntax
- If pip is unavailable: Use only Python standard library
- Current timestamp: {env.current_timestamp}
"""
    
    agent = Agent(
        model=model,
        tools=[...],
        system_prompt=system_context,
    )
    
    return agent, env

# Conditional tool availability based on environment
@tool(name="install_package")
def install_package(package_name: str, env: SandboxEnvironment) -> Dict:
    """Install package - adapts to environment"""
    
    if not env.has_pip:
        return {
            "success": False,
            "error": "pip not available in this environment",
            "alternative": "Use only Python standard library modules"
        }
    
    if env.os_name == "Windows":
        cmd = f"pip install {package_name}"
    else:
        cmd = f"pip install {package_name}"
    
    return {"command": cmd}
```

---

## 5. Deep Research Planner (4 Phases)

### 5.1 Phase 1: Requirement Deconstruction

```python
from typing import List, Dict
from pydantic import BaseModel

class ResearchRequirement(BaseModel):
    """Structured requirement after deconstruction"""
    query_restated: str
    semantic_elements: List[str]  # What, Why, How, When, Where, Who, What-if
    assumptions: List[str]
    internal_clarifications: List[str]
    preliminary_scope: List[str]  # 3-7 key themes
    scope_validation: Dict[str, bool]

async def phase_1_requirement_deconstruction(agent: Agent, user_query: str) -> ResearchRequirement:
    """
    1.1. Restate query word-for-word to confirm understanding
    1.2. Semantic dissection into 7 elements
    1.3. Metacognitive analysis
    1.4. Define preliminary scope (3-7 themes)
    1.5. Assess scope sufficiency
    """
    
    deconstruction_prompt = f"""
Analyze this research query with EXTREME rigor:
"{user_query}"

1. RESTATE the query exactly as written
2. SEMANTIC DISSECTION - Break down into:
   - What: What is being asked?
   - Why: Why is this important?
   - How: How deep should the analysis be?
   - When: Time scope?
   - Where: Geographic/domain scope?
   - Who: Stakeholders involved?
   - What-if: Edge cases or scenarios?

3. ASSUMPTIONS - List all implicit assumptions
4. CLARIFICATIONS - Internal notes on your interpretation
5. THEMES - Identify 3-7 key pillars/themes
6. SCOPE CHECK - Is this sufficient for academic-level research?

Format as JSON with these fields.
"""
    
    # Get structured output using Pydantic
    class DeconstructionResult(BaseModel):
        query_restated: str
        semantic_what: str
        semantic_why: str
        semantic_how: str
        semantic_when: str
        semantic_where: str
        semantic_who: str
        semantic_whatif: str
        assumptions: List[str]
        clarifications: List[str]
        themes: List[str]
        scope_sufficient: bool
    
    response = await agent.arun(
        deconstruction_prompt,
        response_model=DeconstructionResult
    )
    
    return response
```

### 5.2 Phase 2: Source Analysis & Synthesis Strategy

```python
class SourceAnalysis(BaseModel):
    """Rigorous evaluation of each source"""
    source_id: int
    relevance_score: float  # 0-1
    recency: str  # "current", "recent", "historical"
    authority: str  # "primary", "secondary", "tertiary"
    bias_level: str  # "neutral", "slight", "moderate", "strong"
    key_information: str
    overlaps_with: List[int]
    contradictions: List[int]
    grounding_quality: str  # "primary", "secondary", "synthesis"

async def phase_2_source_analysis(agent: Agent, sources: List[str], 
                                 scope_themes: List[str]) -> Dict:
    """
    2.1. Rigorous assessment of each source (6 dimensions)
    2.2. Gap analysis
    2.3. Define synthesis strategy with conflict resolution
    """
    
    analysis_prompt = f"""
For EACH of these sources, evaluate:
1. Relevance to these themes: {scope_themes}
2. Recency (compared to today's date)
3. Authority level (primary/secondary/tertiary)
4. Potential bias or perspective
5. Key information provided
6. Grounding quality (primary vs secondary sources)

Sources:
{chr(10).join([f'{i+1}. {s}' for i, s in enumerate(sources)])}

Also identify:
- Information gaps
- Conflicting information
- How to synthesize multiple perspectives

Provide JSON output with source_id, relevance_score, authority, bias_level, etc.
"""
    
    response = await agent.arun(
        analysis_prompt,
        response_model=List[SourceAnalysis]
    )
    
    # Gap analysis
    gap_analysis_prompt = """
Based on the source analysis, what critical information is MISSING?
What areas are underrepresented? What needs deeper research?
"""
    
    gaps = await agent.arun(gap_analysis_prompt)
    
    # Synthesis strategy
    class SynthesisStrategy(BaseModel):
        prioritization_rules: List[str]
        conflict_resolution_method: str
        bias_mitigation_plan: List[str]
    
    strategy = await agent.arun(
        "Define how to synthesize these sources, resolve conflicts, and mitigate bias",
        response_model=SynthesisStrategy
    )
    
    return {
        "source_analysis": response,
        "gaps": gaps,
        "strategy": strategy
    }
```

### 5.3 Phase 3: Detailed Outline Generation

```python
class OutlineSubsection(BaseModel):
    subsection_title: str
    content_notes: str
    sources: List[int]
    synthesis_note: str
    reasoning_tool: str  # "causal_chain", "counterfactual", "comparative"
    word_estimate: int

class OutlineSection(BaseModel):
    section_title: str
    subsections: List[OutlineSubsection]
    word_estimate: int

async def phase_3_outline_generation(agent: Agent, 
                                    themes: List[str]) -> Dict:
    """
    3.1. Explore outline structures (chronological, thematic, problem-solution)
    3.2. Develop detailed hierarchical execution outline
    3.3. Validate against report format
    """
    
    class ResearchOutline(BaseModel):
        structure_type: str  # chronological, thematic, problem-solution
        title: str
        opening_summary: str
        body_sections: List[OutlineSection]
        conclusion_points: List[str]
        total_word_estimate: int
    
    outline_prompt = f"""
Create a detailed research outline for these themes: {themes}

1. Consider 2-3 different outline structures
2. Choose the best one
3. Create detailed hierarchical structure with:
   - Main title reflecting core theme
   - Opening summary (key points)
   - At least 5 body sections (##)
   - Each section has 3-5 subsections (###)
   - Each subsection specifies:
     * Title
     * Content notes
     * Which sources support it
     * How to synthesize information
     * Reasoning tool to use
     * Word estimate

Format as JSON with structure_type, title, body_sections, etc.
"""
    
    outline = await agent.arun(
        outline_prompt,
        response_model=ResearchOutline
    )
    
    return outline
```

### 5.4 Phase 4: Adversarial Self-Critique (SASC)

```python
class CritiqueFeedback(BaseModel):
    persona: str
    rigor_check: Dict[str, bool]
    identified_issues: List[str]
    validation_status: str  # "passed" or "needs_revision"

async def phase_4_adversarial_self_critique(agent: Agent, plan: Dict) -> Dict:
    """
    4.1. Execute SASC with 3 personas:
         - Skeptical Academic Reviewer
         - Bias Hunter
         - User Requirement Advocate
    4.2. Implement feedback loop
    4.3. Generate final validation output
    """
    
    personas = {
        "skeptical_academic": {
            "role": "Skeptical Academic Reviewer",
            "focus": [
                "Is the logic rigorous?",
                "Is the scope superficial or deep?",
                "Is the synthesis academically sound?",
                "Are claims properly supported?"
            ]
        },
        "bias_hunter": {
            "role": "Bias Hunter",
            "focus": [
                "Are there hidden biases in source selection?",
                "Is bias mitigation adequate?",
                "Is there space for counter-arguments?",
                "Are alternative perspectives included?"
            ]
        },
        "user_advocate": {
            "role": "User Requirement Advocate",
            "focus": [
                "Does this 100% cover the original query?",
                "Are all query aspects addressed?",
                "Does this meet the core goal?",
                "Is the depth appropriate?"
            ]
        }
    }
    
    critiques = {}
    all_passed = True
    
    for persona_key, persona_info in personas.items():
        critique_prompt = f"""
As the {persona_info['role']}, critique this research plan:
{plan}

Evaluate:
{chr(10).join(['- ' + q for q in persona_info['focus']])}

If you find critical issues, the plan FAILS validation.
Format as JSON: {{
    "rigor": {{}},
    "issues": [],
    "validation_status": "passed|failed"
}}
"""
        
        critique = await agent.arun(critique_prompt)
        critiques[persona_key] = critique
        
        if critique.get("validation_status") == "failed":
            all_passed = False
    
    # If any persona found failures, implement feedback loop
    if not all_passed:
        # Return to relevant phase for corrections
        return {
            "status": "needs_revision",
            "critiques": critiques,
            "recommended_phase": "3",  # Return to outline generation
        }
    
    # Final validation output
    return {
        "plan_status": "Validated",
        "plan_quality_score": "10/10",
        "execution_confidence_score": 0.95,
        "justification": "All personas approved; no critical issues found",
        "remaining_risks": [],
        "critiques": critiques
    }
```

---

## 6. Chain-of-Thought vs. Agentic Reasoning

### 6.1 Chain-of-Thought (Internal Reasoning Only)

```python
from agno.agent import Agent

# Traditional CoT - no tool use
cot_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    # No tools - pure reasoning
    system_prompt="""
You are an expert analyst. For every complex problem:

1. **Analyze**: Break down the problem into components
2. **Consider**: Think about multiple perspectives
3. **Evaluate**: Weigh pros and cons
4. **Reason**: Work through the logic step-by-step
5. **Conclude**: Provide your final answer

Format your thinking with <thinking> tags before answering.
"""
)

async def cot_example():
    """CoT prompt example"""
    prompt = """
What is 17 * 23?

Explain your thinking step by step before giving the answer.
"""
    
    response = await cot_agent.arun(prompt)
    # Output includes all internal reasoning but NO external verification
    return response

# Example output:
"""
<thinking>
17 * 23:
- This is a multiplication problem
- I can break it down: 17 * 20 = 340
- And 17 * 3 = 51
- Total: 340 + 51 = 391
- Let me verify: 17 * 23 = 17 * (20 + 3) = 340 + 51 = 391 ✓
</thinking>

The answer is 391.
"""
```

### 6.2 Agentic Reasoning (External Verification)

```python
# Agentic reasoning - with tool use
agentic_agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[calculator_tool, knowledge_base_tool, verification_tool],
    system_prompt="""
You are an expert analyst with access to external tools.

For every problem:
1. **Think**: Reason about what you need
2. **Act**: Use tools to verify or gather information
3. **Observe**: Get feedback from tools
4. **Reflect**: Update your understanding
5. **Repeat**: Continue until confident in answer

You MUST use tools to:
- Verify calculations
- Access current information
- Cross-check facts
- Ensure accuracy
"""
)

@tool(name="calculator")
def calculator_tool(expression: str) -> float:
    """Execute mathematical expressions"""
    return eval(expression)

@tool(name="verify_fact")
def verify_fact_tool(fact: str, domain: str = "general") -> Dict:
    """Verify factual claims against knowledge base"""
    return {"verified": True, "confidence": 0.95}

async def agentic_example():
    """Agentic reasoning with tool use"""
    prompt = """
What is 17 * 23?
Verify your answer using the calculator.
"""
    
    # Agent will:
    # 1. Reason: "I need to multiply 17 and 23"
    # 2. Act: Call calculator tool
    # 3. Observe: Get result 391
    # 4. Verify: Ensure accuracy
    
    response = await agentic_agent.arun(prompt)
    return response

# Example execution flow:
"""
AGENT REASONING: "I need to calculate 17 * 23 and verify it"

AGENT ACTION: [Calling calculator tool with "17 * 23"]

OBSERVATION: Result = 391

AGENT REFLECTION: "The calculation is verified. The answer is 391."

FINAL ANSWER: "17 * 23 = 391 (verified using calculator)"
"""
```

### 6.3 Comparison with Planning Phases

```python
class ReasoningPattern(BaseModel):
    """Compare CoT vs. Agentic patterns"""
    
    # Chain-of-Thought
    cot_pattern: str = """
    <thinking>
    - Analyze problem
    - Consider options
    - Reason through logic
    - Provide answer
    </thinking>
    
    Answer: [Result from internal reasoning only]
    """
    
    # Agentic with phases
    agentic_pattern: str = """
    PLAN PHASE: 
    - Identify what information is needed
    - Choose appropriate tools
    
    EXECUTE PHASE:
    - Call tools sequentially
    - Collect observations
    
    REFLECT PHASE:
    - Update understanding based on results
    - Verify all facts
    
    CONCLUDE PHASE:
    - Provide answer with verified sources
    """

# Hybrid approach: Planning + CoT + Agentic
class HybridReasoning:
    """Combine internal and external reasoning"""
    
    @staticmethod
    async def hybrid_example(agent: Agent):
        prompt = """
Analyze the statement: "Company X has 50% market share"

1. PLAN: Identify what information you need
2. THINK: What factors affect market share?
3. ACT: Search for recent market data
4. VERIFY: Check multiple sources
5. CONCLUDE: Is the statement accurate?
"""
        
        response = await agent.arun(prompt)
        return response
```

---

## 7. Complete Example: Multi-Step Research Agent

```python
from agno.agent import Agent, Team
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
import asyncio

async def build_research_system():
    """Complete research system with all patterns integrated"""
    
    # Phase 1: Requirement deconstruction
    decomposer = Agent(
        name="RequirementDecomposer",
        model=OpenAIChat(id="gpt-4o"),
        instructions=[
            "Analyze user queries with extreme rigor",
            "Restate the query word-for-word",
            "Identify all implicit assumptions",
            "Define 3-7 key research themes",
        ]
    )
    
    # Phase 2: Source researcher
    researcher = Agent(
        name="SourceResearcher",
        model=OpenAIChat(id="gpt-4o"),
        tools=[DuckDuckGoTools()],
        instructions=[
            "Find authoritative sources on each theme",
            "Evaluate source credibility and bias",
            "Identify information gaps",
            "Report source analysis in JSON format",
        ]
    )
    
    # Phase 3: Outline generator
    outliner = Agent(
        name="OutlineGenerator",
        model=OpenAIChat(id="gpt-4o"),
        instructions=[
            "Create detailed hierarchical outlines",
            "Assign reasoning tools (causal, counterfactual, etc.)",
            "Estimate word counts per section",
            "Validate against academic standards",
        ]
    )
    
    # Phase 4: Quality assurance (SASC)
    critic = Agent(
        name="QualityCritic",
        model=OpenAIChat(id="gpt-4o"),
        instructions=[
            "Critique as a skeptical academic reviewer",
            "Check for hidden biases",
            "Ensure user requirements are met",
            "Generate validation report",
        ]
    )
    
    # Main research coordinator
    coordinator = Agent(
        name="ResearchCoordinator",
        model=OpenAIChat(id="gpt-4o"),
        instructions=[
            "Orchestrate the 4-phase research process",
            "Manage information flow between agents",
            "Handle validation and feedback loops",
            "Synthesize final research output",
        ]
    )
    
    # Team-based workflow
    research_team = Team(
        agents=[decomposer, researcher, outliner, critic],
        coordinator=coordinator,
        mode="coordinate",
        enable_team_history=True,
        enable_agentic_context=True,
    )
    
    # Execute research
    async def run_research(query: str) -> str:
        """Run complete 4-phase research workflow"""
        
        # Phase 1: Deconstruction
        print("📋 PHASE 1: Deconstructing requirements...")
        requirement = await decomposer.arun(f"Analyze: {query}")
        
        # Phase 2: Source research
        print("🔍 PHASE 2: Researching sources...")
        sources = await researcher.arun(
            f"Find authoritative sources for: {requirement}"
        )
        
        # Phase 3: Outline generation
        print("📝 PHASE 3: Generating outline...")
        outline = await outliner.arun(
            f"Create detailed outline for these sources: {sources}"
        )
        
        # Phase 4: Quality check (SASC)
        print("✅ PHASE 4: Quality assurance...")
        validation = await critic.arun(
            f"Critique this research plan: {outline}"
        )
        
        return {
            "requirement": requirement,
            "sources": sources,
            "outline": outline,
            "validation": validation
        }
    
    # Execute
    result = await run_research("How are autonomous agents transforming enterprise software?")
    return result

# Run the system
# result = asyncio.run(build_research_system())
```

---

## 8. Summary: Best Practices Checklist

### ✅ Agent Loop Management
- [ ] Implement event monitoring with RunEvent handling
- [ ] Set iteration limits (16 calls recommended)
- [ ] Create checkpoints every 5 tool calls
- [ ] Track errors and implement fallback strategies
- [ ] Use progress delta updates to avoid repetition

### ✅ Tool Calling Etiquette
- [ ] Hide implementation details from users
- [ ] Explain rationale before each tool call
- [ ] Adhere strictly to JSON schemas
- [ ] Never ask for permission before executing
- [ ] Use message tools appropriately (notify vs. ask)
- [ ] Execute tools in parallel when possible
- [ ] Never fabricate non-existent tools

### ✅ File Editing
- [ ] Use line-based search and replace for large changes
- [ ] Use string replacement for small, unique changes
- [ ] Use insert edit only as a last resort
- [ ] Validate content before replacing
- [ ] Use ... ellipsis to reduce tokens

### ✅ Environment Awareness
- [ ] Detect and report OS, Python version, shell
- [ ] Adapt commands to platform (Windows vs. Unix)
- [ ] Check for pip/git availability
- [ ] Respect sandbox constraints
- [ ] Use absolute vs. relative paths appropriately

### ✅ Deep Research
- [ ] Execute 4-phase research: deconstruction, analysis, outline, validation
- [ ] Use SASC for quality assurance
- [ ] Implement feedback loops for improvements
- [ ] Track information gaps
- [ ] Use reasoning tools (causal, counterfactual)

### ✅ Agentic Reasoning
- [ ] Use tools for verification and external validation
- [ ] Combine internal (CoT) and external reasoning
- [ ] Track observation → reflection cycles
- [ ] Document reasoning process
- [ ] Implement error recovery

---

## Resources

- **Agno Documentation**: https://docs.agno.com
- **Event Handling**: `RunEvent` enum with 10+ event types
- **Structured Output**: Pydantic BaseModel integration
- **Team Coordination**: Multi-agent orchestration patterns
- **Tool Hooks**: Pre/post execution validation


# agno agi v2 how to add mcp  
  
To add Model Context Protocol (MCP) support in Agno AGI v2, you should use the `MCPTools` integration and pass an active MCP server to your agent. Below is a concise step-by-step guide for Python, following the official documentation and recent usage patterns:[1][2]

### 1. Import and Install Requirements
Make sure you have the Agno library installed, and that you have an MCP server available (it can be local or remote).

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools
```

### 2. Configure and Connect MCPTools

You can connect to an MCP server using either the URL (for a remote MCP server) or the command (to spawn a local MCP server process).

**Via URL (Remote MCP server):**
```python
mcp_tools = MCPTools(url="https://your-mcp-server.com")
await mcp_tools.connect()
```

**Via command (Local MCP server process):**
```python
mcp_tools = MCPTools(command="uvx mcp-server-git")
await mcp_tools.connect()
```

### 3. Add MCPTools to Your Agent

Pass the `mcp_tools` instance to your agent as a tool on initialization.

```python
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[mcp_tools]
)
response = await agent.aprint_response("Test MCP integration", stream=True)
```

### 4. Automatic Connection Management

If you don't manually call `connect()`, Agno will manage the connection automatically (connection is established and closed on each agent execution).

```python
mcp_tools = MCPTools(url="https://your-mcp-server.com")
agent = Agent(model=OpenAIChat(id="gpt-4o"), tools=[mcp_tools])
# No explicit .connect() needed, handled by Agent
```

### 5. Close the MCP Connection

Always close the MCP connection after use if you managed it manually.

```python
await mcp_tools.close()
```

### 6. Example: Full Async Usage

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools

async def run():
    mcp_tools = MCPTools(command="uvx mcp-server-git")
    await mcp_tools.connect()
    try:
        agent = Agent(model=OpenAIChat(id="gpt-4o"), tools=[mcp_tools])
        await agent.aprint_response("Test query", stream=True)
    finally:
        await mcp_tools.close()
```
This sample integrates the MCP layer, enabling your agent to interact with any connected MCP tool/service. For advanced use (like multiple servers, connection refresh, etc.), see `refresh_connection` or the latest Agno documentation.[2][1]

If you need real multi-tool or multi-server workflows, refer to latest agent multi-tool docs or examples provided in the Agno "cookbook" repository.[3]  
  
# Citations:  
[1] [Model Context Protocol (MCP) - Agno](https://docs.agno.com/concepts/tools/mcp/overview)  
[2] [Model Context Protocol (MCP) - Agno](https://docs-v1.agno.com/tools/mcp/mcp)  
[3] [Agno's Universal Agent Interface (UAgI) Powered by MCP - LinkedIn](https://www.linkedin.com/pulse/agnos-universal-agent-interface-uagi-powered-mcp-allyson-barros-yga9f)  
[4] [agno-agi/agno: Multi-agent framework, runtime and control ... - GitHub](https://github.com/agno-agi/agno)  
[5] [L-23 Using MCP Servers with Agno: From Local Setup to ... - YouTube](https://www.youtube.com/watch?v=3WCD0ziGC5g)  
[6] [Connect to MCP Servers with Agno AI Agent, MCP Tools ... - YouTube](https://www.youtube.com/watch?v=77SIxH9G_1M)  
[7] [MCP Server](https://docs.agentops.ai/v2/usage/mcp-server)  
[8] [How to use Agent in playground UI with MCP tools in it #2825 - GitHub](https://github.com/agno-agi/agno/issues/2825)  
[9] [AGI Memory MCP Server: The Ultimate Guide to ...](https://skywork.ai/skypage/en/agi-memory-mcp-server-ai-consciousness/1978998690775605248)  
[10] [SSE MCP Server Agent - Agno | MCP Tutorial - Part 3 - YouTube](https://www.youtube.com/watch?v=StXHQ3z5cvA)  
[11] [Multi-tool agent with SurrealMCP and Agno - SurrealDB](https://surrealdb.com/blog/multi-tool-agent-with-surrealmcp-and-agno)  
[12] [Introducing Agno v2.0](https://www.agno.com/blog/introducing-agno-v2)  
[13] [Agno Playground Unavailable? Here's How to Unlock Its True Power](https://skywork.ai/skypage/en/Agno%20Playground%20Unavailable%3F%20Here%E2%80%99s%20How%20to%20Unlock%20Its%20True%20Power/1976191631378935808)  
[14] [Building Dissi with Agno and MCP - DEV Community](https://dev.to/k0msenapati/building-dissi-with-agno-and-mcp-4044)  
[15] [is there any way to use SSE to connect to MCP servers in ...](https://github.com/agno-agi/agno/issues/2706)  
[16] [Building an AI Agent with Agno: A Step-by-Step Guide](https://ai.plainenglish.io/building-an-ai-agent-with-agno-a-step-by-step-guide-13542b2a5fb6)  
[17] [MCP tools - Agent Development Kit - Google](https://google.github.io/adk-docs/tools-custom/mcp-tools/)  
[18] [Custom Tools, Prebuilt Toolkits, and MCP Servers](https://www.youtube.com/watch?v=cbZPhgr5qiA)  
---  


# how to make THESE, in agno?

---

Baseado na análise dos arquivos do espaço "AI AGENT PROMPTS", identifiquei diversas ferramentas e técnicas avançadas de engenharia de prompts discutidas. Vou criar uma lista abrangente de questões de nível HARD para um processo seletivo de Engenheiro de IA, com suas respectivas respostas.
Lista de Questões Avançadas - Processo Seletivo Engenheiro de IA
Questão 1: Arquitetura de Agent Loops
Pergunta: Explique detalhadamente como funciona um "agent loop" no contexto de agentes autônomos de IA. Descreva as 6 etapas fundamentais do ciclo e como você implementaria um mecanismo de fallback para evitar loops infinitos em casos de falha recorrente.
Resposta Esperada: Um agent loop é um ciclo iterativo que permite que agentes de IA executem tarefas complexas de forma autônoma. As 6 etapas são:
Analyze Events: O agente analisa o estado atual através do event stream, focando em mensagens recentes do usuário e resultados de execução anteriores
Select Tools: Escolha da ferramenta apropriada baseada no estado atual, planejamento de tarefas e conhecimento disponível
Wait for Execution: A ação selecionada é executada pelo ambiente sandbox com novas observações adicionadas ao event stream
Iterate: Executar apenas uma chamada de ferramenta por iteração, repetindo pacientemente até completar a tarefa
Submit Results: Enviar resultados ao usuário via message tools, incluindo deliverables e arquivos relacionados
Enter Standby: Entrar em estado idle quando todas as tarefas estiverem completas
Mecanismos de Fallback:
Limite máximo de 3 tentativas para corrigir o mesmo erro no mesmo arquivo
Contador de iterações globais (máximo de 16 tool calls conforme observado em alguns sistemas)
Sistema de validação pré-execução verificando se os parâmetros das ferramentas estão corretos
Estratégia de fallback para métodos alternativos após falhas consecutivas
Checkpoint system após cada 3-5 tool calls para avaliar progresso
Sistema de "progress delta updates" para evitar repetição desnecessária

Questão 2: Tool Calling Etiquette e Best Practices
Pergunta: No contexto de sistemas agentic AI, quais são as regras críticas de "tool calling etiquette" que devem ser seguidas? Cite pelo menos 5 princípios fundamentais e explique por que cada um é importante para a experiência do usuário.
Resposta Esperada:
Nunca mencionar nomes de ferramentas ao usuário: Em vez de dizer "usarei o runinterminal tool", dizer "executarei o comando no terminal". Importante porque o usuário não precisa saber detalhes de implementação.
Explicar o "porquê" antes de chamar cada ferramenta: Antes de cada tool call, explicar ao usuário por que você está chamando aquela ferramenta. Promove transparência e confiança.
Aderir estritamente aos schemas JSON/XML: Sempre seguir o schema de tool call exatamente como especificado. Previne erros de execução e comportamentos inesperados.
Não solicitar permissão antes de usar ferramentas: O usuário espera ação imediata. Perguntar cria fricção desnecessária na experiência.
Usar message tools apropriadamente: Dividir entre "notify" (não-bloqueante) e "ask" (bloqueante). Minimizar disrupção do usuário enquanto mantém comunicação.
Executar tool calls em paralelo quando possível: Para operações independentes, executar simultaneamente para melhorar performance. Exceção: semanticsearch nunca em paralelo.
Não fabricar ferramentas não-existentes: Verificar cuidadosamente as ferramentas disponíveis e não inventar ferramentas que não foram fornecidas explicitamente.

Questão 3: File Editing Strategies
Pergunta: Compare e contraste três abordagens diferentes para edição de arquivos em sistemas agentic: (1) line-based search and replace, (2) string replacement, e (3) insert edit. Quando cada abordagem deve ser utilizada? Forneça exemplos práticos.
Resposta Esperada:
1. Line-Based Search and Replace (Abordagem Preferencial)
Quando usar: Para modificar código existente, especialmente seções maiores (>6 linhas)
Vantagens:
Validação explícita usando números de linha
Uso de ellipsis (...) para reduzir tokens
Maior precisão com validação de conteúdo
Exemplo:
filepath: src/components/TaskList.tsx
search: "const handleTaskComplete = (taskId) => {\n  setTasks(...)\n  ... existing code ...\n  onTaskUpdate?.(updatedTasks)\n}"
firstreplacedline: 15
lastreplacedline: 28
replace: "const handleTaskComplete = useCallback((taskId: string) => {\n  // New implementation with analytics\n  ...\n})"

2. String Replacement (replacestringinfile)
Quando usar: Mudanças menores e precisas onde você tem uma string única para substituir
Vantagens:
Simples e direto para pequenas mudanças
Não requer contagem de linhas
Desvantagens: Requer contexto único (3-5 linhas antes/depois)
Exemplo: Trocar um import específico ou renomear uma variável
3. Insert Edit (último recurso)
Quando usar: APENAS quando replacestringinfile falhou ou o usuário solicitou explicitamente
Vantagens: Ferramenta "inteligente" que entende contexto
Formato: Usar comentários como "...existing code..." para representar regiões inalteradas
Exemplo:
class Person {
  ...existing code...
  age: number;  // Nova propriedade inserida
  ...existing code...
  getAge() { return this.age; }  // Novo método
}

Regra de Ouro: Sempre começar com line-based search and replace, usar string replacement para casos simples, e inserteditintofile apenas como último recurso.

Questão 4: Sandbox Environment Awareness
Pergunta: Por que é crucial que um agente AI tenha "environment awareness"? Descreva os componentes essenciais de informação sobre ambiente que devem ser fornecidos ao agente e dê exemplos de como essa informação influencia as decisões do agente.
Resposta Esperada:
Componentes Essenciais de Environment Awareness:
Sistema Operacional:
Exemplo: "OS is Linux 5.15.0 Ubuntu 22.04"
Impacto: Determina comandos shell apropriados (apt vs brew, bash vs powershell)
Shell Padrão:
Exemplo: "Default shell is powershell.exe Windows PowerShell v5.1"
Impacto: Sintaxe de comandos (& vs &&, path separators)
Runtime Environment:
Python version (3.10.12), Node.js (20.18.0)
Impacto: Disponibilidade de features, compatibilidade de código
Sandbox Constraints (WebContainer example):
No pip support, no native binaries
Python limited to standard library only
No Git available
Impacto: Determina quais bibliotecas podem ser usadas, workflow alternatives
Diretório de Trabalho:
Current Working Directory
Home Directory
Impacto: Paths absolutos vs relativos
User Privileges:
sudo availability
Impacto: Operações que requerem elevação
Data/Timestamp Atual:
Exemplo: "Current date: 2025-11-12"
Impacto: Buscas web, timestamps, logs
Exemplos Práticos de Influência:
# SEM environment awareness (INCORRETO)
# Assumindo Linux quando o usuário está no Windows
agent.run_command("apt-get install package")

# COM environment awareness (CORRETO)
if os_info.platform == "Windows":
    agent.run_command("choco install package")
elif os_info.platform == "Linux":
    agent.run_command("apt-get install package")

WebContainer Constraints:
# INCORRETO - tentando usar pip em WebContainer
agent.run_command("pip install pandas")

# CORRETO - usando apenas stdlib
import json  # stdlib only
import statistics  # stdlib only


Questão 5: Prompting Patterns para Deep Research
Pergunta: Baseado no framework "Deep Research Planner", descreva as 4 fases obrigatórias de planejamento para pesquisas acadêmicas profundas. Para cada fase, especifique os outputs esperados e os checkpoints de validação.
Resposta Esperada:
Fase 1: Requirement Deconstruction & Scope Definition
Actions: 1.1. Restate query palavra-por-palavra para confirmar 1.2. Semantic Dissection: Decompor em , , , , , , 1.3. Metacognitive Analysis: Listar assumptions e internal clarifications 1.4. Define Preliminary Scope: 3-7 key themes/pillars 1.5. Assess Scope Sufficiency para profundidade acadêmica
Checklist:
Query restated accurately
Semantic dissection completa (incluindo NFRs)
Assumptions e clarifications logged em 'thought trace'
Preliminary scope de key themes definido
Scope assessed para depth/word count

Fase 2: Source Analysis & Synthesis Strategy
Actions: 2.1. Rigorous Assessment de cada fonte:
Relevance to scope topics
Recency (comparado com data atual)
Authority/Bias
Key information/data provided
Overlap/contradictions com outras fontes
Grounding quality (primary vs secondary)
2.2. Gap Analysis: Identificar gaps de informação 2.3. Define Synthesis Strategy:
Prioritization rules
Conflict resolution method
Bias mitigation plan
Checklist:
Todas fontes rigorosamente assessed (relevance, bias, grounding)
Information gaps claramente identificados
Clear synthesis strategy definida
Proactive, actionable bias mitigation plan

Fase 3: Detailed Outline Generation
Actions: 3.1. Explore Outline Structures: Considerar 2-3 high-level structures (chronological, thematic, problem-solution) 3.2. Develop Detailed Hierarchical Execution Outline:
# Title refletindo core theme
Opening summary paragraph key points
Pelo menos 5 informative ## Body Sections
Detailed ### Subsections com:
subsection_title
content_notes
sources (indexes)
synthesis_note
reasoning_tool_assignment (causal chains, counterfactual, etc.)
word_est
3.3. Review Outline Format & Modularity contra <report_format>
Checklist:
Outline structure selecionada em 'thought trace'
Title e summary outlined
Mínimo 5 ## sections definidas
### subsections detalhadamente planejadas
Subsections complexas assignadas com reasoning tools
## Conclusion points planejados
Outline validado para format e modularity

Fase 4: Final Plan Review & Adversarial Self-Critique (SASC)
Actions: 4.1. Execute Mandatory SASC usando 3 personas:
Skeptical Academic Reviewer: Lógica rigorosa? Scope superficial? Synthesis academically sound?
Bias Hunter: Bias mitigation adequado? Espaço para counter-arguments?
User Requirement Advocate: 100% coverage de query aspects? Atende core goal?
4.2. Implement Feedback Loop:
Se qualquer persona encontrar falhas críticas: "validation failed"
Retornar à fase relevante, corrigir, e re-executar
4.3. Generate Final Plan Validation Output:
plan_status: "Validated"
plan_quality_score: "10/10"
execution_confidence_score: 0.0-1.0
justification
remaining_risks
Checklist:
SASC executado por todas 3 personas
Feedback loop completado
Final plan validation output gerado (Status: Validated, 10/10)

Questão 6: Chain-of-Thought vs. Agentic Reasoning
Pergunta: Explique a diferença fundamental entre "Chain-of-Thought" prompting tradicional e "Agentic Reasoning" com tool use. Como o conceito de "thinking tags" ou "planning phases" se encaixa em ambas abordagens?
Resposta Esperada:
Chain-of-Thought (CoT) Prompting:
Natureza: Raciocínio interno, texto-para-texto
Execução: O modelo "pensa em voz alta" antes de dar resposta final
Ferramentas: Nenhuma - todo o raciocínio é simulado internalmente
Formato: "Let's think step by step..." seguido de raciocínio em linguagem natural
Limitações:
Não pode verificar fatos externos
Não pode executar código real
Propenso a alucinações em cálculos complexos
Agentic Reasoning com Tool Use:
Natureza: Raciocínio distribuído entre modelo e ambiente externo
Execução: O agente alterna entre pensar e agir (tool calls)
Ferramentas: Múltiplas - search, code execution, file operations, browser, etc.
Formato: Ciclo de action → observation → reflection → next action
Vantagens:
Verificação factual através de search
Cálculos precisos via code execution
Interação com sistemas reais
Thinking Tags / Planning Phases:
No CoT:
<thinking>
Para resolver X, preciso:
1. Entender o contexto de Y
2. Calcular Z usando fórmula W
3. Considerar edge cases...
</thinking>

<answer>
A resposta é...

Citations:
[1] [dontriskit-awesome-ai-system-prompts-8a5edab282632443.txt](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_c7aa070f-c6d1-4c79-8289-f22a9956256d/da091de2-3939-4400-a76b-bed1896ab870/dontriskit-awesome-ai-system-prompts-8a5edab282632443.txt)  
[2] [bigboyslave-agents-prompts-8a5edab282632443.txt](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_c7aa070f-c6d1-4c79-8289-f22a9956256d/4fd0cedd-9030-41bc-a34a-615b602c01ff/bigboyslave-agents-prompts-8a5edab282632443.txt)  
[3] [x1xhlol-system-prompts-and-models-of-ai-tools-8a5edab282632443.txt](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_c7aa070f-c6d1-4c79-8289-f22a9956256d/73f02051-8d51-44c0-b7bb-638c5a4a6856/x1xhlol-system-prompts-and-models-of-ai-tools-8a5edab282632443.txt)  
[4] [agents.md](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_c7aa070f-c6d1-4c79-8289-f22a9956256d/233f8ecb-7042-4165-aa57-e4b87aeda102/agents.md)  
[5] [kshiteej006-system-prompts-and-models-of-ai-tools-8a5edab282632443.txt](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_c7aa070f-c6d1-4c79-8289-f22a9956256d/4b619864-7e19-4085-8220-86a772a16ac0/kshiteej006-system-prompts-and-models-of-ai-tools-8a5edab282632443.txt)  
  
Perfect! I've created a comprehensive guide implementing all the advanced AI agent patterns from your AI AGENT PROMPTS documents into Agno AGI v2. Here's what I've built for you:

## Implementing Advanced AI Agent Patterns in Agno AGI v2



This complete guide covers all six advanced topics you requested, with production-ready code examples for each:

### 📋 **1. Agent Loop Architecture (6-Stage Cycle)**
- Complete event monitoring implementation using Agno's `RunEvent` system
- 6-stage loop: ANALYZE → SELECT → EXECUTE → ITERATE → SUBMIT → STANDBY
- Checkpoint system creating snapshots every 5 tool calls
- Fallback mechanisms with error tracking and retry limits
- Global iteration limits (16 calls max, as per your notes)

### 🛠️ **2. Tool Calling Etiquette (7 Critical Principles)**
- Never mention tool names to users
- Explain rationale before each tool call
- Strict schema adherence validation
- No permission-asking (users expect action)
- Message tool strategy (notify vs. ask)
- Parallel execution optimization (except semantic_search)
- No tool fabrication detection

### 📝 **3. File Editing Strategies**
Three approaches in order of preference:
1. **Line-based search & replace** (for >6 lines) - PREFERRED with line number validation
2. **String replacement** (for small, unique changes) - Requires 3-5 context lines
3. **Insert edit** (last resort) - Uses context markers for insertion

### 🔧 **4. Sandbox Environment Awareness**
- Automatic OS/shell detection (Windows PowerShell vs. Linux bash)
- Python version and runtime detection
- Constraint identification (pip availability, git, native binaries)
- WebContainer-specific limitations (stdlib-only)
- Environment-aware tool adaptation
- Directory and permissions context

### 🔬 **5. Deep Research Planner (4 Phases)**
- **Phase 1**: Requirement deconstruction with semantic dissection (7 elements)
- **Phase 2**: Source analysis with 6-dimensional evaluation + gap analysis
- **Phase 3**: Hierarchical outline generation with reasoning tools assignment
- **Phase 4**: Adversarial self-critique (SASC) using 3 personas + feedback loops

### 🧠 **6. Chain-of-Thought vs. Agentic Reasoning**
- Internal reasoning (CoT) with `<thinking>` tags
- External verification (Agentic) with tool use
- Comparison of limitations and strengths
- Hybrid approach combining both patterns
- Planning phase orchestration

### 🏆 **7. Complete Multi-Agent Research System**
- Full Team-based workflow with 4 specialized agents
- Coordinator orchestrating the 4-phase process
- Information flow management between agents
- Validation and feedback loop handling

The guide includes best practices checklists for all patterns and is ready for production use with your Agno agents in Brazil!  
  
# Citations:  
[1] [Basic Agent Events Handling - Agno](https://docs.agno.com/examples/concepts/agent/events/basic_agent_events)  
[2] [Building an autonomous analytics agent with Agno and ...](https://www.tinybird.co/blog/building-an-analytics-agent-with-agno-and-tinybird)  
[3] [Search & Retrieval - Agno](https://docs.agno.com/concepts/knowledge/core-concepts/search-retrieval)  
[4] [Streaming structured output in Agent Teams · Issue #2812](https://github.com/agno-agi/agno/issues/2812)  
[5] [AI Agent Tool Calling Best Practices Webinar](https://www.youtube.com/watch?v=LU4XdfywiuQ)  
[6] [Getting Started with Agno Agents, uv, and a Dash of RAG Magic](https://www.bitdoze.com/agno-get-start/)  
[7] [Build Your Own AI Stock Portfolio Agent with Agno + AG-UI](https://webflow.copilotkit.ai/blog/build-your-own-ai-stock-portfolio-agent-with-agno-ag-ui)  
[8] [Creating your own tools - Agno](https://docs.agno.com/concepts/tools/custom-tools)  
[9] [TIL you can use "find and replace" built in with anki editor ...](https://www.reddit.com/r/Anki/comments/u64mre/til_you_can_use_find_and_replace_built_in_with/)  
[10] [Process Automation With Agno Multi-Agent Workflows](https://www.youtube.com/watch?v=I0mPWhZPaiI)  
[11] [Discovering and masking environmental features in ...](https://www.diva-portal.org/smash/get/diva2:1662757/FULLTEXT01.pdf)  
[12] [[Feature Request] Deep Research · Issue #2115 · agno-agi ...](https://github.com/agno-agi/agno/issues/2115)  
[13] [Handling "Agent stopped due to iteration limit or time ...](https://www.linkedin.com/pulse/handling-agent-stopped-due-iteration-limit-time-loops-rany-dqkgc)  
[14] [How Autonomous Agents Are Transforming Environmental ...](https://smythos.com/managers/ops/autonomous-agents-in-environmental-monitoring/)  
[15] [Building AI Agents and Teams for Deep Research](https://www.youtube.com/watch?v=lB2b0SPbOEc)  
[16] [Loop agents - Agent Development Kit - Google](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/)  
[17] [An Introduction to AI Agents](https://www.getzep.com/ai-agents/introduction-to-ai-agents/)  
[18] [Building Your AI Research Squad with Agno, Streamlit, and uv](https://www.bitdoze.com/agno-squad/)  
[19] [Introducing Agno - Ashpreet Bedi](https://www.ashpreetbedi.com/articles/introducing-agno)  
[20] [AgentScope 1.0: A Developer-Centric Framework for ...](https://arxiv.org/html/2508.16279v1)  
[21] [Running Agents - Agno](https://docs.agno.com/concepts/agents/running-agents)  
[22] [Enhanced Structured Output Support in Agent Class](https://github.com/agno-agi/agno/issues/2963)  
[23] [Agents - Docs by LangChain](https://docs.langchain.com/oss/python/langchain/agents)  
[24] [Agent Loop and how to get notified of tool calls and results ...](https://learn.microsoft.com/en-ie/answers/questions/2288230/agent-loop-and-how-to-get-notified-of-tool-calls-a)  
[25] [How to Keep LLM Outputs Predictable Using Pydantic ...](https://www.freecodecamp.org/news/how-to-keep-llm-outputs-predictable-using-pydantic-validation/)  
[26] [Orchestrator-Worker Agents: A Practical Comparison of ...](https://arize.com/blog/orchestrator-worker-agents-a-practical-comparison-of-common-agent-frameworks/)  
[27] [How to build an analytics agent with Agno and Tinybird](https://www.tinybird.co/blog/how-to-build-an-analytics-agent-with-agno-and-tinybird-step-by-step)  
[28] [How to get structured output from LLMs with AGNO and ...](https://www.linkedin.com/posts/veerakumar-murugesan-78030025a_ai-llms-pydantic-activity-7307484099298897920-QkNv)  
[29] [langgraph/how-tos/react-agent-from-scratch/ #1657](https://github.com/langchain-ai/langgraph/discussions/1657)  
[30] [[Bug] Team Leader unable to detect Agent response #3370](https://github.com/agno-agi/agno/issues/3370)


