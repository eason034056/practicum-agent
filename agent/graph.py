"""
LangGraph Construction

This module builds the agent graph by connecting nodes together.

What is LangGraph:
- A framework for building stateful, multi-step agents
- Uses a graph structure: nodes (functions) connected by edges (flow)
- Supports cyclical flows (loops) for iterative reasoning
- Provides state management and execution control

Graph Structure for This Agent:

                    START
                      │
                      ▼
                ┌──────────┐
                │  agent   │
                │  (LLM)   │
                └────┬─────┘
                      │
                      ▼
              ┌───────────────┐
              │ should_continue│
              │   (router)     │
              └───┬─────────┬─┘
                  │         │
         "continue"│         │"end"
                  │         │
                  ▼         ▼
            ┌─────────┐   END
            │  tools  │
            └────┬────┘
                  │
                  │ (loop back)
                  ▼
            ┌──────────┐
            │  agent   │
            │  (LLM)   │
            └──────────┘

This implements the ReAct (Reason + Act + Observe) pattern:
1. agent node: Reason and Act
2. tools node: Observe (execute and see results)
3. Loop until agent says "end"
"""

# LangGraph imports for building the graph
from langgraph.graph import StateGraph, END
# StateGraph: Class for building stateful graphs
# END: Special constant indicating graph termination

# Import our components
from agent.state import AgentState, create_initial_state
# AgentState: State schema definition
# create_initial_state: Factory function for initial state

from agent.nodes import agent_node, tool_executor_node, should_continue
# agent_node: LLM reasoning node
# tool_executor_node: Tool execution node
# should_continue: Router function

# Type hints
from typing import Dict, Any
# For type annotations


# ==============================================================================
# Graph Builder Function
# ==============================================================================
def create_utility_agent() -> StateGraph:
    """
    Create and configure the Utility Identification Agent graph.
    
    This function builds the LangGraph workflow by:
    1. Creating a StateGraph with our state schema
    2. Adding nodes (agent, tools)
    3. Connecting nodes with edges
    4. Setting up conditional routing
    5. Defining entry and exit points
    
    Function Name: "create_utility_agent"
    - "create": Factory function that builds something
    - "utility_agent": What it creates
    - Why function: Encapsulates graph construction
    - Why not class: Graph is stateless, function is simpler
    
    Returns:
        StateGraph: A compiled, ready-to-run graph
            - Can be invoked with initial state
            - Executes the agent workflow
            - Returns final state
    
    Why This Design:
    - Factory Pattern: Centralized graph creation
    - Testability: Can create multiple graphs for testing
    - Flexibility: Easy to modify graph structure
    - Reusability: Import and use anywhere
    
    Usage:
        agent = create_utility_agent()
        result = agent.invoke({"input": "Find utilities in Raleigh"})
        print(result["output"])
    """
    
    # Step 1: Create StateGraph with our state schema
    # StateGraph: Graph class that manages state
    # AgentState: Our state schema (TypedDict)
    graph = StateGraph(AgentState)
    # graph: StateGraph instance configured for our state
    # Why StateGraph: Handles state management automatically
    # What it does:
    # - Validates state structure
    # - Manages state updates between nodes
    # - Merges node returns into state
    # - Handles annotated fields (like operator.add)
    
    # Step 2: Add nodes to the graph
    # Nodes are the functions that do the work
    # Each node receives state and returns state updates
    
    # Add the agent node (LLM reasoning)
    graph.add_node(
        # First argument: Node name (string identifier)
        "agent",
        # Why "agent": Short, descriptive name for the reasoning node
        # This name is used in edges to reference the node
        
        # Second argument: Node function
        agent_node
        # agent_node: The function that implements reasoning
        # From agent.nodes import agent_node
    )
    # What this does:
    # - Registers "agent" as a node in the graph
    # - When graph reaches "agent" node, it calls agent_node(state)
    # - agent_node returns dict, which updates state
    
    # Add the tool executor node
    graph.add_node(
        # Node name
        "tools",
        # Why "tools": Indicates this node executes tools
        # Could also be "tool_executor" or "execute_tools"
        
        # Node function
        tool_executor_node
        # tool_executor_node: Function that runs tools
    )
    # What this does:
    # - Registers "tools" as a node
    # - When reached, calls tool_executor_node(state)
    # - Executes tools and returns results
    
    # Step 3: Set entry point (where graph starts)
    # Entry point: The first node to execute
    graph.set_entry_point("agent")
    # "agent": Start with the agent node
    # Why start with agent: Agent needs to analyze input and decide first action
    # Alternative: Could start with a preprocessing node
    # 
    # Execution flow:
    # 1. User calls graph.invoke(initial_state)
    # 2. Graph starts at entry point ("agent")
    # 3. Calls agent_node(initial_state)
    # 4. Continues based on edges
    
    # Step 4: Add conditional edge from agent node
    # Conditional edge: Route to different nodes based on state
    # Why conditional: Agent might continue or end
    graph.add_conditional_edges(
        # First argument: Source node
        "agent",
        # From "agent" node
        # After agent_node executes, check where to go next
        
        # Second argument: Router function
        should_continue,
        # should_continue: Function that decides next node
        # Takes state, returns string ("continue" or "end")
        
        # Third argument: Path mapping
        {
            "continue": "tools",
            # If should_continue returns "continue", go to "tools" node
            # Why: Agent wants to execute tools
            
            "end": END
            # If should_continue returns "end", stop execution
            # END: Special constant from langgraph.graph
            # Why: Agent has final answer
        }
    )
    # What this does:
    # - After "agent" node executes, call should_continue(state)
    # - If should_continue returns "continue": Route to "tools" node
    # - If should_continue returns "end": Stop execution
    # 
    # Example flow:
    # 1. agent_node runs, sets state["next_action"] = "continue"
    # 2. should_continue checks state["next_action"]
    # 3. Returns "continue"
    # 4. Graph routes to "tools" node
    
    # Step 5: Add normal edge from tools back to agent
    # Normal edge: Always goes to the same next node
    graph.add_edge(
        # First argument: From node
        "tools",
        # After "tools" node completes
        
        # Second argument: To node
        "agent"
        # Always go back to "agent" node
    )
    # What this does:
    # - After tool_executor_node executes, always go back to agent_node
    # - Why: Agent needs to see tool results and decide next step
    # - This creates the loop: agent → tools → agent → tools → ...
    # 
    # Example flow:
    # 1. tool_executor_node runs tools
    # 2. Returns tool results in messages
    # 3. Graph automatically routes back to "agent"
    # 4. agent_node sees tool results, decides next action
    
    # Step 6: Compile the graph
    # Compiling: Validates and optimizes the graph
    compiled_graph = graph.compile()
    # compiled_graph: Runnable graph object
    # What compile() does:
    # - Validates graph structure (all edges point to valid nodes)
    # - Checks for unreachable nodes
    # - Optimizes execution path
    # - Creates executable workflow
    # - Returns a "compiled" graph ready to run
    # 
    # Why compile: 
    # - Catches configuration errors early
    # - Optimizes performance
    # - Creates immutable execution plan
    
    # Return the compiled graph
    return compiled_graph
    # compiled_graph: Ready to invoke with state
    # 
    # Usage:
    # agent = create_utility_agent()
    # result = agent.invoke(initial_state)


# ==============================================================================
# Helper Function: Run Agent
# ==============================================================================
def run_agent(user_input: str) -> Dict[str, Any]:
    """
    Convenience function to run the agent with a user query.
    
    This function handles:
    1. Creating initial state
    2. Creating/getting agent graph
    3. Invoking graph
    4. Returning final state
    
    Function Name: "run_agent"
    - "run": Action verb indicating execution
    - "agent": What we're running
    - Why separate: Convenience wrapper for common use case
    
    Args:
        user_input (str): User's query or request
            - Example: "Find utilities for Johnson City, TN"
            - Type: Plain text string
    
    Returns:
        Dict[str, Any]: Final state after execution
            - Contains: output, messages, gathered info, etc.
            - Access final answer: result["output"]
    
    Why This Function:
    - Convenience: Single function call to run agent
    - Simple Interface: Just pass user input, get result
    - Encapsulation: Hides state management complexity
    
    Usage:
        result = run_agent("Find gas provider in Raleigh, NC")
        print(result["output"])
        # Output: "The gas provider for Raleigh, NC is..."
    """
    
    # Create initial state from user input
    # create_initial_state: From agent.state
    # Returns: AgentState dict with all fields initialized
    print("📝 Creating initial state...")
    print(f"   User query: '{user_input}'")
    initial_state = create_initial_state(user_input)
    # initial_state: Dict with:
    # - input: user_input
    # - messages: [HumanMessage(user_input)]
    # - All other fields initialized to defaults
    print(f"   ✓ Initial state created with {len(initial_state)} fields")
    print()
    
    # Create the agent graph
    # create_utility_agent: Function we defined above
    # Returns: Compiled StateGraph ready to run
    print("🏗️  Building agent graph...")
    print("   Creating StateGraph with AgentState schema...")
    print("   Adding nodes: 'agent' (reasoning), 'tools' (execution)...")
    print("   Setting entry point: 'agent'...")
    print("   Adding edges: agent → should_continue → tools → agent (loop)...")
    agent_graph = create_utility_agent()
    # agent_graph: Executable workflow
    # Why create here: Could also create once and reuse
    # For production: Create once at startup, reuse for all requests
    print("   ✓ Graph compiled successfully")
    print()
    
    # Run the graph with initial state
    # invoke: Synchronous execution method
    # initial_state: Starting state
    print("▶️  Invoking agent graph...")
    print("   Graph will now execute until completion (agent decides to stop)")
    print()
    
    final_state = agent_graph.invoke(initial_state)
    # final_state: State after graph execution completes
    # Contains:
    # - output: Final answer
    # - messages: Complete conversation history
    # - gas_provider, electric_provider, etc.: Gathered information
    # - iterations: How many reasoning steps taken
    # 
    # What happens during invoke:
    # 1. Graph starts at entry point ("agent")
    # 2. Calls agent_node(initial_state)
    # 3. Routes based on conditional edge
    # 4. Loops through tools and agent until done
    # 5. Returns final state when reaches END
    
    # Return the final state
    print("✅ Graph execution finished, returning final state")
    print()
    return final_state
    # final_state: Complete results
    # 
    # Caller can access:
    # - final_state["output"]: Final answer
    # - final_state["gas_provider"]: Gas provider info
    # - final_state["messages"]: Full conversation
    # - final_state["iterations"]: Performance metric


# ==============================================================================
# Graph Execution Flow Example
# ==============================================================================
#
# Let's trace a complete execution:
#
# 1. User calls:
#    result = run_agent("Find utilities for Johnson City, TN")
#
# 2. create_initial_state("Find utilities for Johnson City, TN")
#    Returns: {
#        "input": "Find utilities for Johnson City, TN",
#        "messages": [HumanMessage("Find utilities...")],
#        "iterations": 0,
#        "next_action": "continue",
#        ... (other fields)
#    }
#
# 3. agent_graph.invoke(initial_state)
#    Graph starts at entry point: "agent"
#
# 4. agent_node(state) - Iteration 1
#    LLM: "I need to identify the AHJ first"
#    Returns: {
#        "messages": [AIMessage(tool_call="identify_ahj")],
#        "next_action": "continue",
#        "iterations": 1
#    }
#    State updated with these fields
#
# 5. should_continue(state)
#    Checks state["next_action"] = "continue"
#    Returns: "continue"
#    Graph routes to: "tools" node
#
# 6. tool_executor_node(state)
#    Executes: identify_ahj(location="Johnson City, TN")
#    Result: {"status": "success", "information": "City of Johnson City..."}
#    Returns: {
#        "messages": [ToolMessage("City of Johnson City...")],
#        "next_action": "continue"
#    }
#
# 7. Graph automatically routes back to "agent" (normal edge)
#
# 8. agent_node(state) - Iteration 2
#    LLM sees tool result
#    LLM: "Good, now search for gas provider"
#    Returns: {
#        "messages": [AIMessage(tool_call="search_gas_provider")],
#        "next_action": "continue",
#        "iterations": 2
#    }
#
# 9. should_continue(state) → "continue" → tools node
#
# 10. tool_executor_node(state)
#     Executes: search_gas_provider(location="Johnson City, TN")
#     Returns tool results
#
# 11. Back to agent_node - Iteration 3
#     LLM: "I have the gas provider, let me search for electric..."
#     (Continues until all utilities found)
#
# 12. agent_node - Final Iteration
#     LLM: "I have all the information needed"
#     Returns: {
#         "messages": [AIMessage("Here are the utilities...")],
#         "next_action": "end",
#         "output": "Complete answer...",
#         "iterations": 10
#     }
#
# 13. should_continue(state)
#     Checks state["next_action"] = "end"
#     Returns: "end"
#     Graph routes to: END
#
# 14. Graph execution completes
#     Returns final_state with all gathered information
#
# 15. User receives:
#     {
#         "input": "Find utilities for Johnson City, TN",
#         "output": "Complete answer...",
#         "identified_ahj": "City of Johnson City",
#         "gas_provider": {...},
#         "electric_provider": {...},
#         ... (all gathered info)
#         "iterations": 10,
#         "messages": [... complete history ...]
#     }


# ==============================================================================
# Graph Visualization
# ==============================================================================
#
# The graph structure can be visualized as:
#
#   [START]
#      │
#      ▼
#  ┌────────┐
#  │ agent  │◄──────────┐
#  └───┬────┘           │
#      │                │
#      ▼                │
#  Conditional Edge     │
#      │                │
#      ├─"continue"──┐  │
#      │             │  │
#      │             ▼  │
#      │         ┌────────┐
#      │         │ tools  │
#      │         └───┬────┘
#      │             │
#      │             │ Normal Edge
#      │             └────┘
#      │
#      └─"end"──▶ [END]
#
# Key Features:
# - Cycle: agent → tools → agent (for iterative reasoning)
# - Conditional: Agent decides whether to continue or end
# - Entry: Starts at agent node
# - Exit: Ends when agent decides it's done
#
# This structure implements ReAct:
# - agent: Reason (analyze) + Act (choose tools)
# - tools: Observe (execute and see results)
# - Loop until complete


# ==============================================================================
# Why LangGraph for This Task
# ==============================================================================
#
# 1. State Management
#    - Explicit state structure (AgentState)
#    - Automatic state updates
#    - Persistence between steps
#
# 2. Cyclical Flows
#    - ReAct requires loops (reason → act → observe → repeat)
#    - Traditional chains are linear
#    - Graphs support cycles naturally
#
# 3. Conditional Routing
#    - Agent decides when to continue or stop
#    - Different paths based on state
#    - add_conditional_edges makes this simple
#
# 4. Debugging
#    - Can inspect state at each step
#    - Clear execution trace
#    - Integration with LangSmith
#
# 5. Flexibility
#    - Easy to add new nodes
#    - Easy to modify routing logic
#    - Easy to add parallel execution
#
# 6. Production Ready
#    - Checkpointing support (pause/resume)
#    - Error handling
#    - Scalability
#
# Comparison to Alternatives:
#
# LangChain Agents (AgentExecutor):
# - Pros: Simpler for basic agents
# - Cons: Less control, harder to customize, black box execution
#
# Custom Implementation:
# - Pros: Complete control
# - Cons: Must build state management, routing, etc. from scratch
#
# LangGraph:
# - Pros: Balance of control and convenience
# - Cons: Requires understanding graphs
# - Verdict: Best choice for complex, production agents

