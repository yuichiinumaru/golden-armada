"""Recycled agent orchestration strategies."""

from typing import List, Dict, Any, Callable

class OrchestrationPatterns:
    """Common patterns for agent coordination."""
    
    @staticmethod
    def loop_until(action: Callable, condition: Callable, max_iterations: int = 3) -> Dict[str, Any]:
        """Execute an action in a loop until a condition is met or max iterations reached."""
        results = []
        for i in range(max_iterations):
            result = action(i)
            results.append(result)
            if condition(result):
                return {"status": "success", "iterations": i + 1, "final_result": result, "history": results}
        return {"status": "max_iterations_reached", "iterations": max_iterations, "final_result": results[-1], "history": results}

    @staticmethod
    def parallel_map(action: Callable, items: List[Any]) -> List[Any]:
        """Execute an action for multiple items (can be extended to actual threading/async)."""
        # Current implementation is sequential but follows the parallel pattern
        return [action(item) for item in items]
