import argparse
import os
from . import config
from .agent_os import AgentOS

def parse_args():
    parser = argparse.ArgumentParser(description="CodeSwarm Agno Controller")
    parser.add_argument("--path", type=str, default=config.DEFAULT_PROJECT_PATH, help="Project path")
    parser.add_argument("--goal", type=str, default=config.DEFAULT_GOAL, help="Project goal")
    parser.add_argument("--pairs", type=int, default=int(config.DEFAULT_PAIRS), help="Number of Dev/Revisor pairs")
    parser.add_argument("--rounds", type=int, default=int(config.DEFAULT_ROUNDS), help="Number of rounds")
    return parser.parse_args()

def main():
    args = parse_args()

    target_project_path = os.path.abspath(args.path)
    os.makedirs(target_project_path, exist_ok=True)

    # Initialize AgentOS with the project parameters
    # The 'hierarchical task tree conformation' is managed internally by AgentOS.
    agent_os = AgentOS(
        goal=args.goal,
        project_path=target_project_path,
        pairs=args.pairs,
        rounds=args.rounds
    )

    # Execute the workflow
    agent_os.run()

if __name__ == "__main__":
    main()
