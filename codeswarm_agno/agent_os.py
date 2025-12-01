import json
import os
import concurrent.futures
from typing import List, Dict, Any, Optional
from datetime import datetime

from . import config
from . import agents
from .structures import TaskTree, TaskNode, TaskStatus
from .models import TaskAssignment

class AgentOS:
    def __init__(self, goal: str, project_path: str, pairs: int, rounds: int):
        self.goal = goal
        self.project_path = project_path
        self.pairs = pairs
        self.rounds = rounds

        self.admin_agent = agents.get_admin_agent()
        self.logger_agent = agents.get_admin_logger_agent()

        # Initialize the tree with the root goal
        self.tree = TaskTree(root=TaskNode(description=goal, status=TaskStatus.IN_PROGRESS))
        self.session_state = {
            "overall_project_goal": goal,
            "target_project_path": project_path,
            "previous_summaries": []
        }

    def run(self):
        print(f"AgentOS: Starting CodeSwarm for goal: {self.goal}")

        for r in range(1, self.rounds + 1):
            print(f"\n=== Round {r} ===")
            self.session_state["round"] = r

            # 1. Planning Phase (Admin expands the tree)
            self._planning_phase(r)

            # 2. Execution Phase (Dev/Revisor work on leaves)
            self._execution_phase(r)

            # 3. Logging Phase
            self._logging_phase(r)

        print("\nAgentOS: Workflow Finished.")

    def _planning_phase(self, round_num: int):
        print("AgentOS: Planning Phase...")
        self.session_state["current_phase"] = "task_assignment"

        # Admin Agent decides what tasks are needed based on current state
        # In a more complex tree, we might pass specific sub-nodes.
        # Here we pass the global context to generate the next batch of tasks (leaves).

        try:
            admin_response = self.admin_agent.run(json.dumps(self.session_state))
            tasks_output = admin_response.content
            new_tasks: List[TaskAssignment] = tasks_output.tasks

            if not new_tasks:
                print("AgentOS: No new tasks generated.")
                return

            print(f"AgentOS: Generated {len(new_tasks)} new tasks.")

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
                # We attach the 'raw' task data for the execution phase to use easily
                # Store extra context if needed, or rely on node fields.
                # For the execution function, we need the specific Revisor instructions too.
                # We'll attach them to the node or reconstruct them.
                # Let's attach them to the node's 'revisor_output' temporarily or a custom field?
                # TaskNode is Pydantic, so we can't easily add dynamic fields unless we allowed extra.
                # But we have 'revisor_focus_areas' in TaskAssignment.
                # Let's store the full TaskAssignment in the node's description or a separate lookup?
                # Actually, let's just use the node fields we have.
                # We might need to extend TaskNode or just pass the 'revisor_focus_areas' differently.
                # Let's add 'metadata' to TaskNode? Or just keep it simple.

                # I'll modify TaskNode to allow generic metadata if I could, but I already defined it.
                # I'll just use the fact that I have the list of tasks here.
                # Actually, I should probably add them to the tree, and then collect them for execution.
                # But I need the 'revisor_focus_areas' which isn't in TaskNode fields explicitly.
                # Let's assume description contains it or I'll just use a local mapping for execution this round.

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
            print(f"AgentOS: Error in planning phase: {e}")

    def _execution_phase(self, round_num: int):
        print("AgentOS: Execution Phase...")
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
                    print(f"AgentOS: Error executing task {i}: {e}")
                    node.status = TaskStatus.FAILED

        # Store results for logging phase
        self.last_round_results = round_results

    def _run_single_task(self, task: TaskAssignment, round_num: int):
        """Runs the Dev -> Revisor cycle for a task."""
        # This logic is moved from main.py's run_dev_revisor_pair

        # Dev Agent
        dev_agent = agents.get_dev_agent(task.dev_id)
        dev_input = {
            "dev_task_description": task.dev_task_description,
            "file_to_edit_or_create": task.file_to_edit_or_create,
            "dev_id": task.dev_id,
            "round": round_num
        }

        print(f"  [Dev {task.dev_id}] {task.file_to_edit_or_create}...")
        dev_response = dev_agent.run(json.dumps(dev_input))
        dev_output = dev_response.content

        # Revisor Agent
        revisor_agent = agents.get_revisor_agent(task.revisor_id)
        revisor_input = {
            "file_to_edit_or_create": task.file_to_edit_or_create,
            "dev_task_description": task.dev_task_description,
            "revisor_focus_areas": task.revisor_focus_areas,
            "revisor_id": task.revisor_id,
            "round": round_num
        }

        print(f"  [Revisor {task.revisor_id}] Reviewing...")
        revisor_response = revisor_agent.run(json.dumps(revisor_input))
        revisor_output = revisor_response.content

        return {
            "task": task.model_dump(),
            "dev_output": dev_output.model_dump(),
            "revisor_output": revisor_output.model_dump()
        }

    def _logging_phase(self, round_num: int):
        print("AgentOS: Logging Phase...")
        if not hasattr(self, 'last_round_results') or not self.last_round_results:
            return

        self.session_state["current_phase"] = "logging_and_updates"
        self.session_state["dev_outputs"] = [res["dev_output"] for res in self.last_round_results]
        self.session_state["revisor_feedback"] = [res["revisor_output"] for res in self.last_round_results]

        try:
            logger_response = self.logger_agent.run(json.dumps(self.session_state))
            logger_output = logger_response.content
            print(f"AgentOS: Logger Status: {logger_output.status}. Message: {logger_output.message}")
        except Exception as e:
            print(f"AgentOS: Logger Error: {e}")

        # Summary for memory
        summary = f"Round {round_num} completed. {len(self.last_round_results)} tasks executed."
        self.session_state["previous_summaries"].append(summary)

        # Cleanup
        del self.session_state["dev_outputs"]
        del self.session_state["revisor_feedback"]
