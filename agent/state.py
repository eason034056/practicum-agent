"""
Agent State Definition

This module defines the state schema for the Utility Identification Agent.

What is State:
- State is the data structure that holds ALL information during agent execution
- It persists across all reasoning steps and tool calls
- LangGraph automatically manages state updates

Why State is Critical:
- Memory: Agent remembers what it has done
- Context: Each step has access to previous steps
- Traceability: Complete record of agent's reasoning
- Resumability: Can pause and resume execution

State Design Principles:
1. Include all information needed for decision-making
2. Track both inputs and outputs
3. Maintain history for context
4. Keep structure flat for simplicity
"""

# typing: For type hints
from typing import TypedDict, Annotated, Sequence
# TypedDict: Define dictionary structure with type hints
# Annotated: Add metadata to types (used by LangGraph)
# Sequence: Immutable list type

# operator: For list concatenation in state updates
import operator
# operator.add: Used to append to lists in state

# LangChain message types for chat history
from langchain_core.messages import BaseMessage
# BaseMessage: Base class for all message types (AI, Human, System, Tool)
# Why messages: Agent's conversation history is stored as messages


# ==============================================================================
# Agent State Schema
# ==============================================================================
class AgentState(TypedDict):
    """
    State schema for the Utility Identification Agent.
    
    This defines what information the agent tracks throughout its execution.
    Each field in this class represents a piece of state that persists
    across reasoning steps.
    
    Why TypedDict:
    - Type Safety: Fields have defined types
    - IDE Support: Autocomplete and type checking
    - Documentation: Clear contract for state structure
    - Validation: Type hints help catch errors early
    
    LangGraph State Management:
    - When a node returns a dict, LangGraph updates the state
    - Fields not returned by a node remain unchanged
    - Annotated fields have special update behaviors (like append)
    """
    
    # --------------------------------------------------------------------------
    # Core Input/Output
    # --------------------------------------------------------------------------
    input: str
    """
    The original user input (location/query).
    
    Field Name: "input"
    - Why "input": Standard term for user's request
    - Type: str (string)
    - Example: "Find utilities for Johnson City, TN"
    
    When Set: At the very beginning, before any reasoning
    When Used: Throughout execution as reference point
    """
    
    output: str
    """
    The final answer/response to the user.
    
    Field Name: "output"
    - Why "output": Parallel to "input"
    - Type: str (string)
    - Example: "Gas provider: Dominion Energy (555-1234)..."
    
    When Set: At the end, when agent decides it has complete answer
    When Used: Returned to user as final response
    """
    
    # --------------------------------------------------------------------------
    # Conversation History
    # --------------------------------------------------------------------------
    messages: Annotated[Sequence[BaseMessage], operator.add]
    """
    Complete conversation history (messages between user, agent, and tools).
    
    Field Name: "messages"
    - Why "messages": Standard LangChain terminology
    - Type: Sequence[BaseMessage] - List of message objects
    - Annotated with operator.add: New messages APPEND to list (not replace)
    
    Why Annotated[Sequence[BaseMessage], operator.add]:
    - Annotated: Tells LangGraph this field has special behavior
    - operator.add: When node returns messages, ADD to existing (don't replace)
    - Without annotation: Node return would replace entire list
    - With annotation: Node return appends to existing list
    
    Message Types:
    - HumanMessage: From the user
    - AIMessage: From the LLM
    - ToolMessage: Results from tool execution
    - SystemMessage: System instructions
    
    Example Flow:
    1. Initial: [HumanMessage("Find gas provider for Johnson City")]
    2. After LLM: + [AIMessage(tool_call="search_gas_provider")]
    3. After tool: + [ToolMessage("Dominion Energy serves this area")]
    4. After LLM: + [AIMessage("The gas provider is Dominion Energy")]
    
    Why Track Messages:
    - Context: LLM sees entire conversation
    - History: Can reference previous findings
    - Debugging: Can replay entire conversation
    """
    
    # --------------------------------------------------------------------------
    # Reasoning and Intermediate Steps
    # --------------------------------------------------------------------------
    intermediate_steps: Annotated[list, operator.add]
    """
    List of intermediate reasoning steps and tool calls.
    
    Field Name: "intermediate_steps"
    - Why "intermediate_steps": Standard ReAct terminology
    - Type: list (can contain any elements)
    - Annotated with operator.add: Append new steps
    
    What Gets Stored:
    - Each (thought, action, observation) triplet
    - Tool calls and their results
    - Reasoning snapshots
    
    Example:
    [
        ("Need to identify AHJ first", "identify_ahj", {"ahj": "Johnson City"}),
        ("Now search for gas provider", "search_gas_provider", {"provider": "Dominion"}),
        ...
    ]
    
    Why Track:
    - Trajectory Evaluation: Can analyze reasoning quality
    - Debugging: See exactly what agent did
    - Learning: Can use as training data
    """
    
    # --------------------------------------------------------------------------
    # Gathered Information
    # --------------------------------------------------------------------------
    identified_ahj: str
    """
    The identified Authority Having Jurisdiction.
    
    Field Name: "identified_ahj"
    - Why "identified_ahj": Past tense indicates it's been determined
    - Type: str (string)
    - Example: "City of Johnson City"
    
    When Set: After identify_ahj tool is called
    When Used: For subsequent utility searches (provides context)
    
    Why Separate Field:
    - Quick Access: Don't need to parse tool results
    - Important: AHJ is fundamental to all subsequent searches
    - Clarity: Makes state structure explicit
    """
    
    gas_provider: dict
    """
    Information about the gas utility provider.
    
    Field Name: "gas_provider"
    - Type: dict (dictionary with provider details)
    - Example: {"name": "Dominion Energy", "phone": "555-1234", ...}
    
    Why dict Instead of str:
    - Structured: Can store multiple pieces of information
    - Accessible: Easy to extract specific fields
    - Extensible: Can add new fields without changing structure
    
    Typical Contents:
    - name: Provider name
    - contact: Contact information
    - sources: URLs where info was found
    """
    
    electric_provider: dict
    """Information about the electric utility provider."""
    # Same structure and reasoning as gas_provider
    
    water_provider: dict
    """Information about the water utility provider."""
    # Same structure and reasoning as gas_provider
    
    sewer_provider: dict
    """Information about the sewer utility provider."""
    # Same structure and reasoning as gas_provider
    
    stormwater_authority: dict
    """Information about the stormwater management authority."""
    # Same structure and reasoning as gas_provider
    
    # --------------------------------------------------------------------------
    # Control Flow
    # --------------------------------------------------------------------------
    next_action: str
    """
    What the agent should do next.
    
    Field Name: "next_action"
    - Why "next_action": Indicates future step
    - Type: str (string describing action)
    - Values: "continue", "end", "error"
    
    When Set: By the agent node after reasoning
    When Used: By the router to decide which node to execute next
    
    Example Values:
    - "continue": Agent wants to use more tools
    - "end": Agent has complete answer
    - "error": Something went wrong
    
    Why This Field:
    - Control Flow: Determines graph routing
    - Explicit: Makes agent's decision clear
    - Debuggable: Can see exactly what agent decided
    """
    
    iterations: int
    """
    Number of reasoning iterations so far.
    
    Field Name: "iterations"
    - Why "iterations": Standard term for counting loops
    - Type: int (integer/whole number)
    - Example: 5
    
    When Updated: Incremented each time agent node runs
    When Used: To prevent infinite loops (max iterations check)
    
    Why Track:
    - Safety: Prevents runaway agent
    - Metrics: Understand agent efficiency
    - Debugging: Know how many steps agent took
    """
    
    error: str
    """
    Error message if something went wrong.
    
    Field Name: "error"
    - Why "error": Standard terminology
    - Type: str (string describing error)
    - Default: Empty string or None
    
    When Set: If any step fails
    When Used: For error handling and user feedback
    
    Why Track:
    - User Feedback: Explain what went wrong
    - Debugging: Identify failure points
    - Recovery: Potentially retry or adjust strategy
    """


# ==============================================================================
# Initial State Factory
# ==============================================================================
def create_initial_state(user_input: str) -> AgentState:
    """
    Create initial state for the agent.
    
    This function creates a new state dictionary with default values
    for a fresh agent run.
    
    Function Name: "create_initial_state"
    - "create": Indicates this is a factory function
    - "initial_state": What it creates
    - Why function: Encapsulates initialization logic
    
    Args:
        user_input (str): The user's query/request
            - Example: "Find utilities for Johnson City, TN"
            - This becomes the "input" field in state
    
    Returns:
        AgentState: A fully initialized state dictionary
    
    Why This Function:
    - Consistency: All agents start with same structure
    - Default Values: Ensures all fields exist
    - Convenience: Single function call to initialize
    
    Usage:
        state = create_initial_state("Find gas provider in Raleigh")
        # state is now a complete AgentState dict ready for execution
    """
    
    # Import HumanMessage for initial message
    from langchain_core.messages import HumanMessage
    # HumanMessage: Represents a message from the user
    
    # Return initialized state dictionary
    # Why return dict: TypedDict is really a dict with type hints
    return {
        # Input/Output
        "input": user_input,
        # The original user query
        
        "output": "",
        # Empty initially, filled at the end
        
        # Messages
        "messages": [HumanMessage(content=user_input)],
        # Start with user's message
        # Why list: Will append more messages during execution
        # Why HumanMessage: Represents user input
        
        # Intermediate steps
        "intermediate_steps": [],
        # Empty list initially
        # Will be populated with (thought, action, observation) tuples
        
        # Gathered information (all start empty/None)
        "identified_ahj": "",
        # Will be filled by identify_ahj tool
        
        "gas_provider": {},
        # Will be filled by search_gas_provider tool
        
        "electric_provider": {},
        # Will be filled by search_electric_provider tool
        
        "water_provider": {},
        # Will be filled by search_water_provider tool
        
        "sewer_provider": {},
        # Will be filled by search_sewer_provider tool
        
        "stormwater_authority": {},
        # Will be filled by search_stormwater_authority tool
        
        # Control flow
        "next_action": "continue",
        # Start with "continue" so agent begins reasoning
        
        "iterations": 0,
        # Zero iterations initially
        # Will increment with each reasoning step
        
        "error": ""
        # No error initially
        # Will be set if something fails
    }
    # Return value is a complete AgentState dictionary
    # All fields are initialized with appropriate defaults


# ==============================================================================
# State Update Patterns
# ==============================================================================
# 
# How State Updates Work in LangGraph:
# 
# 1. Node Function Returns a Dict
#    def my_node(state: AgentState) -> dict:
#        return {"iterations": state["iterations"] + 1}
# 
# 2. LangGraph Merges Into State
#    - Fields in returned dict: Updated
#    - Fields not in returned dict: Unchanged
#    - Annotated fields: Special behavior (e.g., append)
# 
# 3. Next Node Receives Updated State
#    def next_node(state: AgentState):
#        print(state["iterations"])  # Now incremented
# 
# Example State Update Flow:
# 
# Initial State:
# {
#     "input": "Find utilities",
#     "iterations": 0,
#     "messages": [HumanMessage("Find utilities")]
# }
# 
# Agent Node Returns:
# {
#     "iterations": 1,
#     "messages": [AIMessage("I'll search for gas provider")]
# }
# 
# Updated State:
# {
#     "input": "Find utilities",  # Unchanged
#     "iterations": 1,  # Updated
#     "messages": [  # Appended (due to Annotated[..., operator.add])
#         HumanMessage("Find utilities"),
#         AIMessage("I'll search for gas provider")
#     ]
# }
# 
# Why This Design:
# - Selective Updates: Only change what you need
# - Immutability: Original state not mutated
# - Clarity: Explicit about what changed
# - Flexibility: Different update strategies per field

