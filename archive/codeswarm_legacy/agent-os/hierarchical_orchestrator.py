#!/usr/bin/env python3
"""Hierarchical task delegation orchestrator for Agno agents."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import textwrap
import uuid
from dataclasses import dataclass, field
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
from typing import Any, Dict, List


logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("HierarchicalOrchestrator")


REPO_ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = REPO_ROOT / "01-agents"


@dataclass(frozen=True)
class AgentSpec:
    key: str
    filename: str
    class_name: str
    display_name: str

    @property
    def path(self) -> Path:
        return AGENT_DIR / self.filename

    @property
    def module_name(self) -> str:
        sanitized = self.filename.replace("-", "_").replace(".", "_")
        return f"orchestrator.dynamic.{sanitized}"


AGENT_REGISTRY: Dict[str, AgentSpec] = {
    "agent_organizer": AgentSpec(
        key="agent_organizer",
        filename="002-agent_organizer_agent.py",
        class_name="AgentOrganizerAgent",
        display_name="Agent Organizer",
    ),
    "multi_agent_coordinator": AgentSpec(
        key="multi_agent_coordinator",
        filename="114-multi_agent_coordinator_agent.py",
        class_name="MultiAgentCoordinatorAgent",
        display_name="Multi-Agent Coordinator",
    ),
    "task_distributor": AgentSpec(
        key="task_distributor",
        filename="189-task_distributor_agent.py",
        class_name="TaskDistributorAgent",
        display_name="Task Distributor",
    ),
    "context_manager": AgentSpec(
        key="context_manager",
        filename="030-context_manager_agent.py",
        class_name="ContextManagerAgent",
        display_name="Context Manager",
    ),
    "agent_accessibility": AgentSpec(
        key="agent_accessibility",
        filename="001-accessibility_tester_agent.py",
        class_name="AccessibilityTesterAgent",
        display_name="Accessibility Tester",
    ),
    "agent_backend": AgentSpec(
        key="agent_backend",
        filename="014-backend_developer_agent.py",
        class_name="BackendDeveloperAgent",
        display_name="Backend Developer",
    ),
    "agent_frontend": AgentSpec(
        key="agent_frontend",
        filename="072-frontend_developer_agent.py",
        class_name="FrontendDeveloperAgent",
        display_name="Frontend Developer",
    ),
    "agent_quality": AgentSpec(
        key="agent_quality",
        filename="134-qa_expert_agent.py",
        class_name="QAExpertAgent",
        display_name="QA Expert",
    ),
}


@dataclass
class TaskNode:
    title: str
    instruction: str
    agent_key: str
    mode: str = "sequential"
    children: List["TaskNode"] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskNode":
        children = [cls.from_dict(child) for child in data.get("children", [])]
        return cls(
            title=data.get("title") or data.get("task") or "Task",
            instruction=data.get("instruction") or data.get("description") or "",
            agent_key=data.get("agent_key") or data.get("agent") or "multi_agent_coordinator",
            mode=data.get("mode") or "sequential",
            children=children,
        )


@dataclass
class TaskExecutionResult:
    node: TaskNode
    output: str
    summary: Dict[str, Any]
    children: List["TaskExecutionResult"] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.node.id,
            "title": self.node.title,
            "agent_key": self.node.agent_key,
            "mode": self.node.mode,
            "summary": self.summary,
            "output": self.output,
            "children": [child.to_dict() for child in self.children],
        }


class AgentManager:
    def __init__(self, registry: Dict[str, AgentSpec]):
        self.registry = registry
        self._instances: Dict[str, Any] = {}
        self._locks: Dict[str, asyncio.Lock] = {}

    def get_spec(self, agent_key: str) -> AgentSpec:
        if agent_key not in self.registry:
            raise KeyError(f"Unknown agent key: {agent_key}")
        return self.registry[agent_key]

    async def get_agent(self, agent_key: str) -> Any:
        if agent_key in self._instances:
            return self._instances[agent_key]
        lock = self._locks.setdefault(agent_key, asyncio.Lock())
        async with lock:
            if agent_key in self._instances:
                return self._instances[agent_key]
            spec = self.get_spec(agent_key)
            module = self._load_module(spec)
            agent_cls = getattr(module, spec.class_name)
            instance = agent_cls()
            await instance.setup_agent()
            self._instances[agent_key] = instance
            return instance

    def _load_module(self, spec: AgentSpec):
        if not spec.path.exists():
            raise FileNotFoundError(f"Agent file not found: {spec.path}")
        loader = SourceFileLoader(spec.module_name, str(spec.path))
        module_spec = spec_from_loader(spec.module_name, loader)
        module = module_from_spec(module_spec)
        loader.exec_module(module)  # type: ignore[attr-defined]
        return module


class HierarchicalTaskOrchestrator:
    def __init__(self, agent_manager: AgentManager, max_parallel: int = 4):
        self.agent_manager = agent_manager
        self.max_parallel = max_parallel
        self.context_log: List[Dict[str, Any]] = []

    async def generate_plan(self, objective: str, max_depth: int = 3) -> TaskNode:
        organizer = await self.agent_manager.get_agent("agent_organizer")
        objective_block = textwrap.indent(objective.strip(), "  ") if objective else "  (none provided)"
        prompt = textwrap.dedent(
            f"""
            Plan a hierarchical execution strategy for the following objective:
            {objective_block}

            Output strict JSON with the schema:
            {{
              "title": str,
              "instruction": str,
              "agent_key": str,
              "mode": "sequential" | "parallel",
              "children": [ ... recursive ... ]
            }}

            Use only agent keys from this list: {sorted(self.agent_manager.registry.keys())}.
            Depth must not exceed {max_depth}. Do not include any text outside JSON.
            """
        ).strip()
        response = await organizer.run_task(prompt)
        data = self._extract_json(response)
        if not isinstance(data, dict):
            raise ValueError("Agent organizer returned an invalid plan")
        return TaskNode.from_dict(data)

    async def execute(self, root: TaskNode) -> TaskExecutionResult:
        semaphore = asyncio.Semaphore(self.max_parallel)
        return await self._execute_node(root, lineage=[], semaphore=semaphore)

    async def _execute_node(
        self,
        node: TaskNode,
        lineage: List[str],
        semaphore: asyncio.Semaphore,
    ) -> TaskExecutionResult:
        spec = self.agent_manager.get_spec(node.agent_key)
        prompt = self._format_prompt(node, lineage, spec.display_name)
        agent = await self.agent_manager.get_agent(node.agent_key)
        async with semaphore:
            output = await agent.run_task(prompt)
        summary = await self._summarize(node, output)
        path = " > ".join(lineage + [node.title])
        self.context_log.append({"path": path, "summary": summary})
        children: List[TaskExecutionResult] = []
        if node.children:
            child_lineage = lineage + [node.title]
            if node.mode == "parallel":
                coroutines = [self._execute_node(child, child_lineage, semaphore) for child in node.children]
                children = list(await asyncio.gather(*coroutines))
            else:
                for child in node.children:
                    children.append(await self._execute_node(child, child_lineage, semaphore))
        return TaskExecutionResult(node=node, output=output, summary=summary, children=children)

    def build_report(self, result: TaskExecutionResult) -> Dict[str, Any]:
        return {
            "objective": result.node.title,
            "execution_tree": result.to_dict(),
            "context_log": self.context_log,
        }

    def _format_prompt(self, node: TaskNode, lineage: List[str], display_name: str) -> str:
        context = self._latest_context(limit=5)
        lineage_path = " > ".join(lineage + [node.title])
        prompt = textwrap.dedent(
            f"""
            You are {display_name} operating within a hierarchical delegation workflow.
            Current task lineage: {lineage_path}

            Primary objective:
            {node.instruction or node.title}

            Recent shared context:
            {context or "No prior context available."}

            Expectations:
            - Execute according to your core instructions.
            - Provide a concise progress summary and explicit next actions.
            - Note dependencies, risks, and hand-offs for downstream agents.
            - If producing artifacts, list the file paths or locations.
            """
        ).strip()
        return prompt

    async def _summarize(self, node: TaskNode, output: str) -> Dict[str, Any]:
        try:
            context_agent = await self.agent_manager.get_agent("context_manager")
        except KeyError:
            return {"summary": output[:1024]}
        summary_prompt = textwrap.dedent(
            f"""
            Summarize the following agent output for shared context.
            Respond strictly in JSON with keys: summary, key_points, follow_ups.
            Output must be valid JSON without markdown fences.

            Agent output:
            {output}
            """
        ).strip()
        response = await context_agent.run_task(summary_prompt)
        data = self._extract_json(response)
        if isinstance(data, dict):
            return data
        return {"summary": output[:1024]}

    def _latest_context(self, limit: int = 5) -> str:
        if not self.context_log:
            return ""
        recent = self.context_log[-limit:]
        lines = [f"- {entry['path']}: {self._truncate(entry['summary'])}" for entry in recent]
        return "\n".join(lines)

    @staticmethod
    def _truncate(summary: Any, length: int = 200) -> str:
        text = summary if isinstance(summary, str) else json.dumps(summary, ensure_ascii=False)
        text = text.strip()
        return text if len(text) <= length else text[: length - 3] + "..."

    @staticmethod
    def _extract_json(text: str) -> Any:
        if not text:
            return None
        fenced = re.search(r"```json\s*(.*?)```", text, re.DOTALL)
        if fenced:
            snippet = fenced.group(1).strip()
            try:
                return json.loads(snippet)
            except json.JSONDecodeError:
                pass
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            snippet = match.group(0)
            try:
                return json.loads(snippet)
            except json.JSONDecodeError:
                return None
        return None


def load_plan_from_file(path: Path) -> TaskNode:
    data = json.loads(path.read_text(encoding="utf-8"))
    return TaskNode.from_dict(data)


async def run_orchestrator(args: argparse.Namespace) -> Dict[str, Any]:
    manager = AgentManager(AGENT_REGISTRY)
    orchestrator = HierarchicalTaskOrchestrator(manager, max_parallel=args.max_parallel)
    if args.plan_file:
        plan = load_plan_from_file(Path(args.plan_file))
    elif args.auto_plan:
        plan = await orchestrator.generate_plan(args.task, max_depth=args.max_depth)
    else:
        plan = TaskNode(
            title=args.task,
            instruction=args.task,
            agent_key="multi_agent_coordinator",
            mode="sequential",
            children=[
                TaskNode(
                    title="Organize team",
                    instruction="Analyse the objective and design a delegation plan.",
                    agent_key="agent_organizer",
                ),
                TaskNode(
                    title="Distribute tasks",
                    instruction="Assign work units to the appropriate agents with priorities.",
                    agent_key="task_distributor",
                ),
                TaskNode(
                    title="Execute specialized work",
                    instruction="Coordinate specialized agents to complete deliverables.",
                    agent_key="multi_agent_coordinator",
                    mode="parallel",
                    children=[
                        TaskNode(
                            title="Frontend stream",
                            instruction="Handle user-facing implementation tasks for the objective.",
                            agent_key="agent_frontend",
                        ),
                        TaskNode(
                            title="Backend stream",
                            instruction="Handle server-side implementation tasks for the objective.",
                            agent_key="agent_backend",
                        ),
                        TaskNode(
                            title="Quality validation",
                            instruction="Design and execute validation strategies for the deliverables.",
                            agent_key="agent_quality",
                        ),
                    ],
                ),
            ],
        )
    result = await orchestrator.execute(plan)
    report = orchestrator.build_report(result)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Saved workflow report to %s", output_path)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Hierarchical task tree delegation orchestrator for Agno agents.",
    )
    parser.add_argument("--task", required=True, help="Top-level objective description.")
    parser.add_argument("--auto-plan", action="store_true", help="Generate plan using agent organizer.")
    parser.add_argument("--plan-file", help="Path to JSON file describing the task tree.")
    parser.add_argument("--max-depth", type=int, default=3, help="Maximum depth for auto-generated plans.")
    parser.add_argument(
        "--output",
        default=str(REPO_ROOT / "04-workflow" / "workflow_report.json"),
        help="Path to persist workflow execution report.",
    )
    parser.add_argument("--max-parallel", type=int, default=4, help="Concurrency limit for agent tasks.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        asyncio.run(run_orchestrator(args))
    except KeyboardInterrupt:
        logger.warning("Execution interrupted by user.")


if __name__ == "__main__":
    main()
