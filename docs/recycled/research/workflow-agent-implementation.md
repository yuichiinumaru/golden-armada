# WorkflowAgent & LoopAgent Implementation

This document details the implementation of `WorkflowAgent` and `LoopAgent` based on ADK patterns.

## Core Components

### 1. LoopAgent
Designed for repetitive tasks, such as the Dev-Revisor cycle.
- **Max Iterations**: Configurable (default 3).
- **Termination Condition**: Success status or max iterations reached.

### 2. WorkflowAgent
Orchestrates the high-level sequence:
1. **Admin Phase**: Task decomposition.
2. **Execution Phase**: Dev-Revisor loops.
3. **Closing Phase**: Documentation updates.

## Strategic Insights
- **Agent Synergy**: Using a Revisor to check Dev output reduces hallucinations significantly.
- **State Persistence**: Using `session.state` to pass data between agents.
- **Granular Logging**: Tracking chaque iteration for easier debugging.
