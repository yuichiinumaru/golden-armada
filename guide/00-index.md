# CodeSwarm Documentation Guide

Welcome to the comprehensive documentation for **CodeSwarm**, a multi-agent coding system orchestrated by the [Agno](https://agno.com) framework.

## Table of Contents

*   **[01. Getting Started](./01-getting-started.md)**
    *   Prerequisites & Installation
    *   Configuration Setup
    *   Running your first "Hello World"
*   **[02. Architecture Overview](./02-architecture-overview.md)**
    *   High-Level System Design
    *   The `AgentOS` Orchestrator
    *   Agent Roles & Interaction Flow
*   **[03. Core Concepts](./03-core-concepts.md)**
    *   Glossary (Agents, Tasks, Rounds)
    *   Data Models & Structures
*   **[04. Features & Capabilities](./04-features-and-capabilities.md)**
    *   Strategic Planning
    *   Dev-Revisor Feedback Loop
    *   Knowledge Retrieval
    *   State Persistence
*   **[05. Configuration Reference](./05-configuration-reference.md)**
    *   Environment Variables (`.env`)
    *   Model Settings
*   **[06. Developer Guide](./06-developer-guide.md)**
    *   Project Structure
    *   Adding New Agents & Tools
    *   Modifying Prompts
*   **[07. Troubleshooting](./07-troubleshooting.md)**
    *   Common Errors
    *   Debugging & Logging

## What is CodeSwarm?

CodeSwarm is an autonomous software development system that employs a hierarchy of AI agents to plan, code, and review software projects. It features a unique **Dev -> Revisor** feedback loop to ensure code quality before it is finalized.

*   **Entry Point**: `codeswarm/main.py`
*   **Core Logic**: `codeswarm/agent_os.py`
