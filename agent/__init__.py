"""
Agent Package Initializer

This package contains the core AI agent implementation using LangGraph.

Package Structure:
- state.py: Defines the agent's state schema (what data the agent tracks)
- nodes.py: Implements graph nodes (reasoning, tool execution)
- graph.py: Constructs the LangGraph workflow (how nodes connect)

Why LangGraph:
- State Management: Explicit state that persists across reasoning steps
- Graph-based Flow: Visual and controllable agent behavior
- ReAct Pattern: Built-in support for Reason-Act-Observe loops
- Debugging: Every step is traceable and inspectable

Import the main graph builder for easy access
"""

# Import the main function to create the agent graph
from agent.graph import create_utility_agent

# __all__: Public API of this package
__all__ = ["create_utility_agent"]
# Why: Makes it clear that create_utility_agent is the main entry point
# Usage: from agent import create_utility_agent

