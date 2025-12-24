# Incremental Analysis: `codeswarm/core`
**Date:** 2025-12-21

## Overview
The `core` directory contains the fundamental building blocks of the Golden Armada system. It bridges the generic Agno framework with the specific needs of the swarm, particularly in terms of memory and agent lifecycle.

## Key Files & Responsibilities

### 1. `base_agent.py`
- defines the `SwarmAgent` class.
- **Role:** acts as a wrapper around `Agno.Agent`.
- **Memory Integration:** automatically initializes `KhalaClient` and handles memory initialization/cleanup.
- **Model Routing:** includes logic to select between "fast" (Flash) and "reasoning" (Pro) models based on the agent's role (e.g., orchestrator/admin gets Pro).

### 2. `khala_client.py`
- **Role:** provides a singleton interface to the `Khala` memory system (SurrealDB).
- **Resilience:** includes fallback/mock implementations if the `khala` library is missing, ensuring the system can still run in a degraded state.

### 3. `registry.py` & `mcp_registry.json`
- **Role:** manages agent metadata and tool registration.
- **UI Metadata:** defines mapping for agent icons (e.g., "Scale" for legal, "BrainCircuit" for reasoning) and animation profiles.
- **Discovery:** provides methods to list and categorize agents for the frontend.

### 4. `agent_utils.py`
- **Role:** utility functions for system prompt manipulation and standardized logging setup.

## Completeness Assessment
- **Integration Layer:** the core integration with Agno and Khala seems robust and well-structured.
- **Scalability:** the registry-based approach for agent and tool management supports the "222+ agents" goal by allowing dynamic discovery and metadata-driven UI rendering.
- **Observation:** the move from ADK to Agno is clearly reflected in the `SwarmAgent` implementation.
