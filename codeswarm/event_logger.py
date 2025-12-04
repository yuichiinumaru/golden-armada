import json
import os
import time
from typing import Any, Dict
from . import config

class EventLogger:
    def __init__(self, log_file: str = "codeswarm_events.jsonl"):
        self.log_file = log_file
        # Ensure log file path is absolute if relative to project
        if not os.path.isabs(self.log_file) and config.DEFAULT_PROJECT_PATH:
             self.log_file = os.path.join(config.DEFAULT_PROJECT_PATH, log_file)

    def log_event(self, event_type: str, agent_name: str, details: Dict[str, Any]):
        """
        Logs a structured event.

        Args:
            event_type: e.g., "action", "observation", "plan", "error".
            agent_name: Name of the agent generating the event.
            details: Dictionary containing event-specific data (inputs, outputs, etc.).
        """
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "agent_name": agent_name,
            "details": details
        }

        try:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            # Fallback to standard logger if file write fails, or just print if logger circular dep risk
            print(f"Failed to log event: {e}")

# Singleton instance
event_logger = EventLogger()
