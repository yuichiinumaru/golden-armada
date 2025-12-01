from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
import uuid

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    APPROVED = "approved"
    REJECTED = "rejected"

class TaskNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    status: TaskStatus = TaskStatus.PENDING
    assigned_dev_id: Optional[int] = None
    assigned_revisor_id: Optional[int] = None
    file_path: Optional[str] = None

    # Results
    dev_output: Optional[Dict[str, Any]] = None
    revisor_output: Optional[Dict[str, Any]] = None

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Hierarchy
    children: List['TaskNode'] = Field(default_factory=list)
    parent_id: Optional[str] = None

    def add_child(self, child: 'TaskNode'):
        child.parent_id = self.id
        self.children.append(child)

    def is_leaf(self) -> bool:
        return len(self.children) == 0

class TaskTree(BaseModel):
    root: TaskNode

    def get_node(self, node_id: str) -> Optional[TaskNode]:
        return self._find_node(self.root, node_id)

    def _find_node(self, current: TaskNode, node_id: str) -> Optional[TaskNode]:
        if current.id == node_id:
            return current
        for child in current.children:
            found = self._find_node(child, node_id)
            if found:
                return found
        return None

    def get_leaves(self) -> List[TaskNode]:
        leaves = []
        self._collect_leaves(self.root, leaves)
        return leaves

    def _collect_leaves(self, current: TaskNode, leaves: List[TaskNode]):
        if current.is_leaf():
            leaves.append(current)
        else:
            for child in current.children:
                self._collect_leaves(child, leaves)
