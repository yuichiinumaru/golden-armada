import json
import os
import concurrent.futures
from typing import List, Dict, Any, Optional
from datetime import datetime

from . import config
from . import agents
from . import khala_integration
from .logger import logger
from .event_logger import event_logger
from .structures import TaskTree, TaskNode, TaskStatus
from .models import TaskAssignment

class AgentOS:
    def __init__(self, goal: str, project_path: str, pairs: int, rounds: int):
        self.goal = goal
        self.project_path = project_path
        self.pairs = pairs
        self.rounds = rounds

        # Initialize Khala tools
        self.memory_tools = khala_integration.get_khala_tools()

        self.admin_agent = agents.get_admin_agent(extra_tools=self.memory_tools)
        self.logger_agent = agents.get_admin_logger_agent(extra_tools=self.memory_tools)
        self.planner_agent = agents.get_planner_agent(extra_tools=self.memory_tools)
        self.knowledge_agent = agents.get_knowledge_agent(extra_tools=self.memory_tools)

        # Initialize the tree with the root goal
        self.tree = TaskTree(root=TaskNode(description=goal, status=TaskStatus.IN_PROGRESS))
        self.session_state = {
            "overall_project_goal": goal,
            "target_project_path": project_path,
            "previous_summaries": []
        }

        # Load state if exists
        self.state_file_path = os.path.join(project_path, "codeswarm_state.json")
        self.load_state()

    def save_state(self):
        """Saves the current state (TaskTree and session_state) to a JSON file."""
        try:
            state_data = {
                "session_state": self.session_state,
                "task_tree": self.tree.model_dump()
            }
            with open(self.state_file_path, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=2, default=str)
            logger.info(f"AgentOS: State saved to {self.state_file_path}")
        except Exception as e:
            logger.error(f"AgentOS: Error saving state: {e}")

    def load_state(self):
        """Loads state from a JSON file if it exists."""
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, "r", encoding="utf-8") as f:
                    state_data = json.load(f)

                # Restore session state
                if "session_state" in state_data:
                    self.session_state = state_data["session_state"]

                # Restore Task Tree
                # Since TaskTree is a Pydantic model, we can reconstruct it
                if "task_tree" in state_data:
                    self.tree = TaskTree.model_validate(state_data["task_tree"])

                logger.info(f"AgentOS: State loaded from {self.state_file_path}")
            except Exception as e:
                logger.error(f"AgentOS: Error loading state: {e}")

    def run(self):
        # Start Khala System in background
        khala_integration.start_khala_background()

        try:
            logger.info(f"AgentOS: Starting CodeSwarm for goal: {self.goal}")

            start_round = self.session_state.get("round", 0) + 1
            # If we loaded a completed state, start_round might be rounds + 1
            if start_round > self.rounds:
                 logger.info(f"AgentOS: Workflow already completed up to round {self.rounds}. Continuing if you want more rounds or start new.")
                 # For now, we just respect the requested rounds if they are greater than current
                 if start_round > self.rounds:
                     logger.info("AgentOS: Requested rounds completed.")
                     return

            for r in range(start_round, self.rounds + 1):
                logger.info(f"=== Round {r} ===")
                self.session_state["round"] = r

                # 0. Strategic Planning (Planner updates todo.md and session_state)
                self._strategic_planning_phase(r)
                self.save_state()

                # 1. Planning Phase (Admin expands the tree)
                self._planning_phase(r)
                self.save_state()

                # 2. Execution Phase (Dev/Revisor work on leaves)
                self._execution_phase(r)
                self.save_state()

                # 3. Logging Phase
                self._logging_phase(r)
                self.save_state()

        finally:
            # Ensure Khala system is stopped
            khala_integration.stop_khala_background()
            logger.info("AgentOS: Workflow Finished.")

    def _strategic_planning_phase(self, round_num: int):
        logger.info("AgentOS: Strategic Planning Phase...")
        self.session_state["current_phase"] = "strategic_planning"

        try:
            # Planner Agent analyzes state and updates todo.md / session_state
            # We pass the full session state. Planner output is text (markdown plan).
            planner_response = self.planner_agent.run(json.dumps(self.session_state))
            strategic_plan = planner_response.content

            logger.info("AgentOS: Planner generated strategic update.")
            event_logger.log_event("planning", "PlannerAgent", {"plan": strategic_plan})

            # Store the plan in session state for Admin to see
            self.session_state["strategic_plan"] = strategic_plan

            # Optionally write to todo.md (Planner might do this via tool, but we can enforce it here if content is the plan)
            # For now, we assume Planner uses its tools (read_file, write_file) to update 'todo.md' directly.

        except Exception as e:
            logger.error(f"AgentOS: Error in strategic planning phase: {e}")

    def _planning_phase(self, round_num: int):
        logger.info("AgentOS: Planning Phase...")
        self.session_state["current_phase"] = "task_assignment"

        # Admin Agent decides what tasks are needed based on current state
        # In a more complex tree, we might pass specific sub-nodes.
        # Here we pass the global context to generate the next batch of tasks (leaves).

        try:
            admin_response = self.admin_agent.run(json.dumps(self.session_state))
            tasks_output = admin_response.content
            new_tasks: List[TaskAssignment] = tasks_output.tasks

            if not new_tasks:
                logger.info("AgentOS: No new tasks generated.")
                return

            logger.info(f"AgentOS: Generated {len(new_tasks)} new tasks.")

            # Add these tasks as children of the root (flattened list of active tasks for this round)
            # In a true recursive tree, Admin might target specific existing nodes to expand.
            # For now, we treat them as direct sub-tasks of the project goal.
            for task in new_tasks:
                node = TaskNode(
                    description=task.dev_task_description,
                    assigned_dev_id=task.dev_id,
                    assigned_revisor_id=task.revisor_id,
                    file_path=task.file_to_edit_or_create
                )

                self.tree.root.add_child(node)

            # We will use 'new_tasks' directly in execution phase for simplicity of mapping,
            # but we update the tree status.
            self.current_round_tasks = new_tasks
            # Note: The tree now has these nodes. We need to link them.
            # Since 'new_tasks' is a list of TaskAssignment, and we added TaskNodes,
            # we need to know which node corresponds to which task to update status.
            # Let's re-iterate:

            self.round_nodes_map = {} # Map task_index -> TaskNode
            # Wait, I just added them to root.children. They are the last N children.
            current_children_count = len(self.tree.root.children)
            added_count = len(new_tasks)
            start_index = current_children_count - added_count

            for i, task in enumerate(new_tasks):
                self.round_nodes_map[i] = self.tree.root.children[start_index + i]
                # Also store the extra info needed for execution that isn't in TaskNode
                self.round_nodes_map[i].metadata = {"revisor_focus_areas": task.revisor_focus_areas}

        except Exception as e:
            logger.error(f"AgentOS: Error in planning phase: {e}")

    def _execution_phase(self, round_num: int):
        logger.info("AgentOS: Execution Phase...")
        if not hasattr(self, 'current_round_tasks') or not self.current_round_tasks:
            return

        round_results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.pairs) as executor:
            # Map future to (task_index, task_assignment)
            future_to_task = {}
            for i, task in enumerate(self.current_round_tasks):
                node = self.round_nodes_map[i]
                node.status = TaskStatus.IN_PROGRESS
                future = executor.submit(self._run_single_task, task, round_num)
                future_to_task[future] = i

            for future in concurrent.futures.as_completed(future_to_task):
                i = future_to_task[future]
                node = self.round_nodes_map[i]
                try:
                    result = future.result()
                    round_results.append(result)

                    # Update Tree Node
                    node.dev_output = result["dev_output"]
                    node.revisor_output = result["revisor_output"]

                    if result["revisor_output"]["approved"]:
                        node.status = TaskStatus.APPROVED
                    else:
                        node.status = TaskStatus.REJECTED # or COMPLETED but needs work

                except Exception as e:
                    logger.error(f"AgentOS: Error executing task {i}: {e}")
                    node.status = TaskStatus.FAILED

        # Store results for logging phase
        self.last_round_results = round_results

    def _run_single_task(self, task: TaskAssignment, round_num: int):
        """Runs the Dev -> Revisor cycle for a task with retry loop."""

        # Use memory tools for Dev and Revisor
        dev_agent = agents.get_dev_agent(task.dev_id, extra_tools=self.memory_tools)
        revisor_agent = agents.get_revisor_agent(task.revisor_id, extra_tools=self.memory_tools)

        dev_input = {
            "dev_task_description": task.dev_task_description,
            "file_to_edit_or_create": task.file_to_edit_or_create,
            "dev_id": task.dev_id,
            "round": round_num
        }

        revisor_input = {
            "file_to_edit_or_create": task.file_to_edit_or_create,
            "dev_task_description": task.dev_task_description,
            "revisor_focus_areas": task.revisor_focus_areas,
            "revisor_id": task.revisor_id,
            "round": round_num
        }

        # Knowledge Retrieval Phase
        try:
            logger.info(f"  [Knowledge] Retrieving context for: {task.dev_task_description[:50]}...")
            knowledge_query = f"Task: {task.dev_task_description}\nFile: {task.file_to_edit_or_create}\nFind relevant code patterns, imports, or existing functions."
            knowledge_response = self.knowledge_agent.run(knowledge_query)
            context_snippet = knowledge_response.content

            # Inject context into Dev input
            dev_input["context_from_knowledge_agent"] = context_snippet
            event_logger.log_event("knowledge_retrieval", "KnowledgeAgent", {"query": knowledge_query, "context": context_snippet})
        except Exception as e:
            logger.error(f"  [Knowledge] Error retrieving context: {e}")

        max_retries = 3
        attempt = 0
        approved = False

        dev_output = None
        revisor_output = None

        while attempt < max_retries and not approved:
            attempt += 1
            logger.info(f"  [Dev {task.dev_id}] {task.file_to_edit_or_create} (Attempt {attempt}/{max_retries})...")
            event_logger.log_event("action_start", f"DevAgent_{task.dev_id}", {"attempt": attempt, "input": dev_input})

            dev_response = dev_agent.run(json.dumps(dev_input))
            dev_output = dev_response.content
            event_logger.log_event("action_complete", f"DevAgent_{task.dev_id}", {"output": dev_output.model_dump()})

            logger.info(f"  [Revisor {task.revisor_id}] Reviewing (Attempt {attempt}/{max_retries})...")
            event_logger.log_event("action_start", f"RevisorAgent_{task.revisor_id}", {"attempt": attempt, "input": revisor_input})

            revisor_response = revisor_agent.run(json.dumps(revisor_input))
            revisor_output = revisor_response.content
            event_logger.log_event("action_complete", f"RevisorAgent_{task.revisor_id}", {"output": revisor_output.model_dump()})

            if revisor_output.approved:
                approved = True
                logger.info(f"  [Revisor {task.revisor_id}] Approved!")
            else:
                logger.info(f"  [Revisor {task.revisor_id}] Rejected. Feedback: {revisor_output.review_comments}")
                # Feedback loop: Update dev input with rejection feedback
                dev_input["previous_feedback"] = f"Attempt {attempt} rejected. Revisor feedback: {revisor_output.review_comments}. Please fix."

        return {
            "task": task.model_dump(),
            "dev_output": dev_output.model_dump() if dev_output else None,
            "revisor_output": revisor_output.model_dump() if revisor_output else None
        }

    def _logging_phase(self, round_num: int):
        logger.info("AgentOS: Logging Phase...")
        if not hasattr(self, 'last_round_results') or not self.last_round_results:
            return

        self.session_state["current_phase"] = "logging_and_updates"
        self.session_state["dev_outputs"] = [res["dev_output"] for res in self.last_round_results]
        self.session_state["revisor_feedback"] = [res["revisor_output"] for res in self.last_round_results]

        try:
            logger_response = self.logger_agent.run(json.dumps(self.session_state))
            logger_output = logger_response.content
            logger.info(f"AgentOS: Logger Status: {logger_output.status}. Message: {logger_output.message}")
        except Exception as e:
            logger.error(f"AgentOS: Logger Error: {e}")

        # Summary for memory
        summary = f"Round {round_num} completed. {len(self.last_round_results)} tasks executed."
        self.session_state["previous_summaries"].append(summary)

        # Cleanup
        del self.session_state["dev_outputs"]
        del self.session_state["revisor_feedback"]
