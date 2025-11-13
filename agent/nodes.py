"""
Agent Graph Nodes

This module implements the nodes (functions) that make up the agent's graph.

What is a Node:
- A node is a function that receives state and returns state updates
- Each node performs a specific role in the agent workflow
- Nodes are connected by edges to form the agent graph

Nodes in This Agent:
1. agent_node: LLM reasoning and decision-making (Reason + Act)
2. tool_executor_node: Execute tools chosen by agent (Observe)
3. should_continue: Router function (decides next node)

ReAct Pattern Implementation:
- agent_node: Reason (What should I do?) + Act (Call tool X)
- tool_executor_node: Execute action and Observe results
- should_continue: Check if done or continue loop
- Repeat until agent has final answer
"""

# Type hints
from typing import Dict, Any, List
# Dict, Any, List: Type hints for function signatures

# LangChain imports for LLM and messages
from langchain_openai import ChatOpenAI
# ChatOpenAI: OpenAI chat models (GPT-4, GPT-3.5, etc.)

from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
# AIMessage: Message from the AI/LLM
# ToolMessage: Result from a tool execution
# HumanMessage: Message from the user

# Import our state definition
from agent.state import AgentState
# AgentState: TypedDict defining state structure

# Import configuration
from config.settings import settings
# settings: Access to API keys and configuration

# Import all tools
from tools import (
    identify_ahj,
    get_development_regulations,
    search_gas_provider,
    search_electric_provider,
    search_water_provider,
    search_sewer_provider,
    search_stormwater_authority,
    get_utility_contact_info,
    get_connection_requirements,
    google_search_grounding
)
# These are all the tools the agent can use


# ==============================================================================
# Initialize LLM with Tools
# ==============================================================================
# Create the language model instance
# Why create here: Reused across all agent_node calls
llm = ChatOpenAI(
    # model: Which OpenAI model to use
    model=settings.llm_model,
    # Example: "gpt-4-turbo-preview"
    # Why from settings: Easy to change without modifying code
    
    # temperature: Controls randomness (0.0 = deterministic, 2.0 = creative)
    temperature=settings.llm_temperature,
    # 0.0 for factual tasks (our use case)
    # Higher values for creative tasks
    
    # openai_api_key: Authentication
    openai_api_key=settings.openai_api_key
    # Why from settings: Secure, not hardcoded
)
# llm: ChatOpenAI instance ready to generate responses

# Bind tools to the LLM
# What is "binding": Teaching LLM about available tools
# How it works: LLM system prompt includes tool descriptions
llm_with_tools = llm.bind_tools([
    # List of all tools the agent can use
    # Order doesn't matter; LLM chooses based on descriptions
    
    # AHJ tools
    identify_ahj,
    # Function: Identifies the Authority Having Jurisdiction
    # LLM will call this when it needs to know the AHJ
    
    get_development_regulations,
    # Function: Gets regulations for an AHJ
    # LLM will call this when asked about regulations
    
    # Utility provider tools
    search_gas_provider,
    # Function: Finds gas provider for a location
    # LLM will call this when it needs gas provider info
    
    search_electric_provider,
    # Function: Finds electric provider
    
    search_water_provider,
    # Function: Finds water provider
    
    search_sewer_provider,
    # Function: Finds sewer provider
    
    search_stormwater_authority,
    # Function: Finds stormwater authority
    
    # Detail tools
    get_utility_contact_info,
    # Function: Gets contact details for a provider
    # LLM will call this after identifying a provider
    
    get_connection_requirements,
    # Function: Gets connection requirements for a provider
    
    # Search tools
    google_search_grounding
    # Function: General web search
    # LLM will call this for any information not covered by specific tools
])
# llm_with_tools: LLM that can call these tools
# How binding works:
# 1. Each function's name, parameters, and docstring are analyzed
# 2. Converted to OpenAI function calling format
# 3. Included in LLM system prompt
# 4. LLM can output tool calls in special format
# 5. We parse tool calls and execute them


# ==============================================================================
# Node 1: Agent Node (Reason + Act)
# ==============================================================================
def agent_node(state: AgentState) -> Dict[str, Any]:
    """
    The main reasoning node - decides what to do next.
    
    This node implements the "Reason + Act" part of ReAct:
    1. Reason: Analyze current state and decide next action
    2. Act: Either call a tool or provide final answer
    
    Function Name: "agent_node"
    - "agent": This is the core agent logic
    - "node": It's a graph node in LangGraph
    - Why this name: Clear that this is the main decision-making node
    
    Args:
        state (AgentState): Current state of the agent
            - Contains: user input, message history, gathered info, etc.
            - Type: AgentState TypedDict
    
    Returns:
        Dict[str, Any]: State updates
            - Contains: new messages, updated iterations, next_action
            - LangGraph merges these updates into state
    
    Process:
    1. Check iteration limit (prevent infinite loops)
    2. Build system prompt with context
    3. Call LLM with conversation history
    4. Parse LLM response (tool calls or final answer)
    5. Return state updates
    
    Why This Design:
    - Centralized: All reasoning happens here
    - Stateless: Function doesn't maintain state (state passed in)
    - Pure: Same state input always gives same output
    - Testable: Easy to unit test with mock state
    """
    
    # ============ LOGGING START ============
    print("\n" + "="*80)
    print(f"🤖 AGENT NODE - REASONING ITERATION #{state['iterations'] + 1}")
    print("="*80)
    print("Function: agent_node()")
    print("Purpose: LLM analyzes current state and decides next action (Reason + Act)")
    print("-"*80)
    # ============ LOGGING END ============
    
    # Check iteration limit to prevent infinite loops
    # Why check: Agent might get stuck in reasoning loop
    if state["iterations"] >= settings.max_iterations:
        # Exceeded max iterations - force stop
        # Why force stop: Prevents runaway costs and time
        
        print(f"⚠️  WARNING: Reached maximum iterations ({settings.max_iterations})")
        print("Decision: Forcing agent to stop to prevent infinite loop")
        print("="*80 + "\n")
        
        return {
            # Return state updates to stop execution
            "next_action": "end",
            # Tell router to end execution
            
            "error": f"Reached maximum iterations ({settings.max_iterations})",
            # Explain why we stopped
            
            "output": "I apologize, but I reached my reasoning limit. "
                     "Please try breaking down your request or contact support."
            # Provide user-friendly error message
        }
        # Early return - no further processing
    
    # Build system prompt with current context
    # System prompt: Instructions to the LLM about its role and task
    # Why build dynamically: Include current gathered information as context
    system_prompt = f"""You are a helpful assistant that identifies utility providers and regulatory information for land development projects.

Your task is to help find:
1. Authority Having Jurisdiction (AHJ) for the location
2. Utility providers (gas, electric, water, sewer)
3. Stormwater management authority
4. Contact information and connection requirements

Current Progress:
- AHJ: {state.get('identified_ahj', 'Not yet identified')}
- Gas Provider: {'Found' if state.get('gas_provider') else 'Not yet found'}
- Electric Provider: {'Found' if state.get('electric_provider') else 'Not yet found'}
- Water Provider: {'Found' if state.get('water_provider') else 'Not yet found'}
- Sewer Provider: {'Found' if state.get('sewer_provider') else 'Not yet found'}
- Stormwater Authority: {'Found' if state.get('stormwater_authority') else 'Not yet found'}

Instructions:
1. If you don't have the AHJ yet, identify it first using identify_ahj()
2. Once you have the AHJ, search for each utility type
3. Use specific search tools for each utility type
4. Get contact information and requirements when needed
5. When you have gathered all requested information, provide a comprehensive final answer

Be thorough and ensure all information is grounded in search results.
"""
    
    # ============ LOGGING START ============
    print("📊 Current State Overview:")
    print(f"  • User Input: {state.get('input', 'N/A')}")
    print(f"  • AHJ Identified: {'✓ ' + state.get('identified_ahj', '') if state.get('identified_ahj') else '✗ Not yet'}")
    print(f"  • Gas Provider: {'✓ Found' if state.get('gas_provider') else '✗ Not found'}")
    print(f"  • Electric Provider: {'✓ Found' if state.get('electric_provider') else '✗ Not found'}")
    print(f"  • Water Provider: {'✓ Found' if state.get('water_provider') else '✗ Not found'}")
    print(f"  • Sewer Provider: {'✓ Found' if state.get('sewer_provider') else '✗ Not found'}")
    print(f"  • Stormwater Authority: {'✓ Found' if state.get('stormwater_authority') else '✗ Not found'}")
    print(f"  • Message History Length: {len(state.get('messages', []))}")
    print()
    print("💭 Sending context to LLM for reasoning...")
    print("   (LLM will analyze state and decide whether to call tools or provide final answer)")
    # ============ LOGGING END ============
    # system_prompt: Detailed instructions for the LLM
    # Why include current progress: LLM knows what's already done
    # Why include instructions: Guides LLM's decision-making
    # f-string: Embeds state information dynamically
    
    # Prepare messages for LLM
    # messages: Conversation history plus system prompt
    # Why messages: LLM needs full context to reason
    messages = [
        # System message with instructions
        {"role": "system", "content": system_prompt},
        # role="system": Special message type for instructions
        # content: The actual system prompt text
    ] + state["messages"]
    # + state["messages"]: Append conversation history
    # Result: [system_msg, human_msg, ai_msg, tool_msg, ...]
    # Why this order: System prompt first, then conversation
    
    # Call LLM to get next action
    # llm_with_tools: Our LLM instance with bound tools
    # invoke: Synchronous call to LLM
    # messages: The conversation to analyze
    print("⏳ Calling LLM (OpenAI GPT)...")
    response = llm_with_tools.invoke(messages)
    # response: AIMessage object from LLM
    # Contains either:
    # - tool_calls: List of tools to execute
    # - content: Final answer text
    # Why invoke: Synchronous call (simpler than async for this use case)
    print("✅ LLM response received")
    print()
    
    # Increment iteration counter
    # Why increment: Track how many reasoning steps taken
    new_iterations = state["iterations"] + 1
    # new_iterations: Current count + 1
    
    # Check if LLM wants to use tools
    # response.tool_calls: List of tool call requests from LLM
    # Why check: Determines if we continue or end
    if response.tool_calls:
        # LLM wants to use tools (continue reasoning loop)
        # Why: Agent needs more information before answering
        
        # ============ LOGGING START ============
        print("🔧 LLM Decision: CALL TOOLS (needs more information)")
        print(f"   Number of tools to call: {len(response.tool_calls)}")
        print()
        print("📋 Tool Calls Requested:")
        for idx, tool_call in enumerate(response.tool_calls, 1):
            print(f"   {idx}. Tool: {tool_call['name']}")
            print(f"      Purpose: This tool will {_get_tool_description(tool_call['name'])}")
            print(f"      Arguments: {tool_call['args']}")
            if idx < len(response.tool_calls):
                print()
        print()
        print("➡️  Next Action: Continue to tool_executor_node to execute these tools")
        print("="*80 + "\n")
        # ============ LOGGING END ============
        
        # Return state updates
        return {
            "messages": [response],
            # Add LLM's response to message history
            # Why list: Annotated field will append to existing messages
            # response: AIMessage with tool_calls
            
            "next_action": "continue",
            # Tell router to continue to tool execution
            # Why "continue": Agent is not done yet
            
            "iterations": new_iterations
            # Update iteration count
            # Why track: For max iteration check and metrics
        }
    else:
        # LLM provided final answer (no more tools needed)
        # Why: Agent has gathered enough information
        
        # ============ LOGGING START ============
        print("✅ LLM Decision: PROVIDE FINAL ANSWER (has enough information)")
        print()
        print("📝 Final Answer Preview:")
        preview = response.content[:200] + "..." if len(response.content) > 200 else response.content
        print(f"   {preview}")
        print()
        print("➡️  Next Action: End execution and return result to user")
        print("="*80 + "\n")
        # ============ LOGGING END ============
        
        # Return state updates
        return {
            "messages": [response],
            # Add LLM's final answer to history
            # response: AIMessage with content (no tool_calls)
            
            "next_action": "end",
            # Tell router to end execution
            # Why "end": Agent is done
            
            "output": response.content,
            # Extract final answer text
            # response.content: The actual answer string
            # This becomes the final output to user
            
            "iterations": new_iterations
            # Update iteration count
        }
    # Return value: Dict with state updates
    # LangGraph will merge these into state


# ==============================================================================
# Helper Function for Logging
# ==============================================================================
def _get_tool_description(tool_name: str) -> str:
    """
    Get a human-readable description of what a tool does.
    
    Function Name: "_get_tool_description"
    - Prefix "_": Indicates this is an internal helper function
    - "get_tool_description": Describes its purpose
    - Why: Makes logging more informative for users
    
    Args:
        tool_name (str): Name of the tool
    
    Returns:
        str: Description of what the tool does
    """
    descriptions = {
        "identify_ahj": "identify the Authority Having Jurisdiction (local government) for the location",
        "get_development_regulations": "retrieve development regulations and zoning information",
        "search_gas_provider": "find the natural gas utility provider",
        "search_electric_provider": "find the electric utility provider",
        "search_water_provider": "find the water utility provider",
        "search_sewer_provider": "find the sewer/wastewater utility provider",
        "search_stormwater_authority": "find the stormwater management authority",
        "get_utility_contact_info": "get contact information for a utility provider",
        "get_connection_requirements": "get utility connection requirements and procedures",
        "google_search_grounding": "perform a general web search for information"
    }
    return descriptions.get(tool_name, "perform its designated function")


# ==============================================================================
# Node 2: Tool Executor Node (Observe)
# ==============================================================================
def tool_executor_node(state: AgentState) -> Dict[str, Any]:
    """
    Execute tools requested by the agent.
    
    This node implements the "Observe" part of ReAct:
    1. Take tool calls from agent's message
    2. Execute each tool
    3. Collect results
    4. Return results as tool messages
    
    Function Name: "tool_executor_node"
    - "tool_executor": Describes what it does (executes tools)
    - "node": It's a graph node
    - Why this name: Clear that this node runs tools
    
    Args:
        state (AgentState): Current state
            - Must contain messages with tool_calls
    
    Returns:
        Dict[str, Any]: State updates
            - Contains: tool messages with results
            - next_action: Always "continue" (back to agent for reasoning)
    
    Process:
    1. Get last message from agent (contains tool calls)
    2. For each tool call:
        a. Get tool name and arguments
        b. Execute the tool
        c. Collect result
    3. Create ToolMessage for each result
    4. Return messages for state update
    
    Why Separate Node:
    - Separation of Concerns: Agent reasons, executor executes
    - Error Handling: Can catch and handle tool errors here
    - Logging: Easy to log all tool executions
    - Testing: Can test tool execution independently
    """
    
    # ============ LOGGING START ============
    print("\n" + "="*80)
    print("🔧 TOOL EXECUTOR NODE - EXECUTING TOOLS")
    print("="*80)
    print("Function: tool_executor_node()")
    print("Purpose: Execute tools requested by agent and observe results")
    print("-"*80)
    # ============ LOGGING END ============
    
    # Get the last message (should be from agent with tool calls)
    # state["messages"]: List of all messages
    # [-1]: Last element in list (most recent message)
    last_message = state["messages"][-1]
    # last_message: AIMessage with tool_calls
    # Why last message: Agent just decided which tools to use
    
    # Extract tool calls from message
    # last_message.tool_calls: List of tool call objects
    # Each tool call has: name, args, id
    tool_calls = last_message.tool_calls
    # tool_calls: List like [
    #     {"name": "search_gas_provider", "args": {"location": "Johnson City"}, "id": "call_123"}
    # ]
    
    # Create tool mapping (name -> function)
    # Why mapping: Easy lookup of tool function by name
    tool_map = {
        # AHJ tools
        "identify_ahj": identify_ahj,
        # Key: Tool name (string)
        # Value: Tool function (callable)
        
        "get_development_regulations": get_development_regulations,
        
        # Utility tools
        "search_gas_provider": search_gas_provider,
        "search_electric_provider": search_electric_provider,
        "search_water_provider": search_water_provider,
        "search_sewer_provider": search_sewer_provider,
        "search_stormwater_authority": search_stormwater_authority,
        
        # Detail tools
        "get_utility_contact_info": get_utility_contact_info,
        "get_connection_requirements": get_connection_requirements,
        
        # Search tools
        "google_search_grounding": google_search_grounding
    }
    # tool_map: Dictionary for tool lookup
    # Why dictionary: O(1) lookup by name
    # Alternative: Could use getattr or inspect, but explicit is clearer
    
    # Execute each tool and collect results
    # Why loop: Agent might request multiple tools at once
    tool_messages = []
    # tool_messages: List to store ToolMessage objects
    
    # Iterate through each tool call
    for idx, tool_call in enumerate(tool_calls, 1):
        # tool_call: One tool call object
        # Has: name (str), args (dict), id (str)
        
        # Extract tool information
        tool_name = tool_call["name"]
        # tool_name: Name of tool to execute (e.g., "search_gas_provider")
        
        tool_args = tool_call["args"]
        # tool_args: Arguments for tool (e.g., {"location": "Johnson City"})
        
        tool_call_id = tool_call["id"]
        # tool_call_id: Unique ID for this tool call
        # Why ID: Links tool message back to tool call
        
        # ============ LOGGING START ============
        print(f"\n🔨 Executing Tool {idx}/{len(tool_calls)}: {tool_name}")
        print(f"   Purpose: {_get_tool_description(tool_name)}")
        print(f"   Input Arguments: {tool_args}")
        # ============ LOGGING END ============
        
        # Get the tool function
        # tool_map.get(): Safe lookup (returns None if not found)
        tool_function = tool_map.get(tool_name)
        # tool_function: The actual Python function to call
        
        # Check if tool exists
        if tool_function is None:
            # Tool not found in our mapping
            # Why check: LLM might hallucinate a tool name
            
            # ============ LOGGING START ============
            print(f"   ❌ ERROR: Tool '{tool_name}' not found in tool_map")
            print(f"   This tool does not exist or is not registered")
            # ============ LOGGING END ============
            
            # Create error message
            tool_messages.append(
                ToolMessage(
                    content=f"Error: Tool '{tool_name}' not found",
                    # Error message explaining the issue
                    
                    tool_call_id=tool_call_id
                    # Link back to original tool call
                    # Why: LLM can see which call failed
                )
            )
            # Continue to next tool call
            continue
            # Why continue: Try to execute other tools even if one fails
        
        # Execute the tool with error handling
        try:
            # try block: Catch any errors during tool execution
            # Why needed: Tools might fail (network issues, invalid args, etc.)
            
            # ============ LOGGING START ============
            print(f"   ⏳ Calling tool function...")
            # ============ LOGGING END ============
            
            # Call the tool function with unpacked arguments
            # **tool_args: Unpacks dict to keyword arguments
            # Example: {"location": "X"} becomes location="X"
            result = tool_function(**tool_args)
            # result: Return value from tool (should be a dict)
            
            # ============ LOGGING START ============
            print(f"   ✅ Tool execution successful")
            print(f"   📊 Result summary:")
            # Show a preview of the result
            if isinstance(result, dict):
                status = result.get('status', 'N/A')
                print(f"      Status: {status}")
                
                # If status is error, show the error message prominently
                if status == 'error' and 'error' in result:
                    print(f"      ❌ ERROR DETAILS: {result.get('error')}")
                    print(f"      🔍 This means: The tool ran but couldn't find the information")
                
                # Show other relevant information
                if 'information' in result:
                    info_preview = str(result['information'])[:100]
                    print(f"      Information: {info_preview}...")
                if 'provider_name' in result:
                    print(f"      Provider: {result.get('provider_name')}")
                if 'ahj_name' in result:
                    print(f"      AHJ: {result.get('ahj_name')}")
                
                # Show any other useful fields
                if 'sources' in result and result['sources']:
                    print(f"      Sources found: {len(result['sources'])} URLs")
            else:
                result_str = str(result)[:100]
                print(f"      {result_str}...")
            # ============ LOGGING END ============
            
            # Create tool message with result
            tool_messages.append(
                ToolMessage(
                    # Convert result to string for LLM
                    # str(result): Converts dict to readable string
                    # Why convert: ToolMessage content must be string
                    content=str(result),
                    
                    tool_call_id=tool_call_id
                    # Link to original tool call
                )
            )
            # ToolMessage: Special message type for tool results
            # LLM will see this in next reasoning step
            
        except Exception as e:
            # Exception occurred during tool execution
            # e: Exception object with error details
            
            # ============ LOGGING START ============
            print(f"   ❌ ERROR during tool execution")
            print(f"      Error type: {type(e).__name__}")
            print(f"      Error message: {str(e)}")
            # ============ LOGGING END ============
            
            # Create error message
            tool_messages.append(
                ToolMessage(
                    content=f"Error executing {tool_name}: {str(e)}",
                    # Include tool name and error message
                    # str(e): Converts exception to string
                    
                    tool_call_id=tool_call_id
                    # Link to failed tool call
                )
            )
            # Why handle gracefully: Agent can see error and adapt strategy
            # Example: If one search fails, try alternative approach
    
    # Extract information from tool results and update state fields
    # Why: State fields track what's been found (for progress display)
    state_updates = {}
    # state_updates: Dictionary to collect all state field updates
    
    # Iterate through tool calls and their results together
    # zip: Pairs up tool_calls with tool_messages (1:1 correspondence)
    # Why zip: Each tool call has a corresponding result message
    for tool_call, tool_message in zip(tool_calls, tool_messages):
        # tool_call: The original request (has tool name)
        # tool_message: The result (has the data)
        
        tool_name = tool_call["name"]
        # tool_name: Which tool was called (e.g., "search_gas_provider")
        
        # Try to parse the result from the tool message
        # tool_message.content: String representation of result dict
        try:
            # Convert string back to dict
            # Why needed: ToolMessage stores content as string
            result_dict = eval(tool_message.content)
            # eval(): Evaluates the string as Python code
            # Warning: eval can be dangerous, but safe here (we control the input)
            
            # Check if the tool succeeded
            if isinstance(result_dict, dict) and result_dict.get("status") == "success":
                # Tool succeeded! Update the appropriate state field
                
                # Map tool names to state field names
                # Why: Different tools update different state fields
                if tool_name == "identify_ahj" and result_dict.get("ahj_name"):
                    state_updates["identified_ahj"] = result_dict.get("ahj_name")
                    # Update AHJ name in state
                    
                elif tool_name == "search_gas_provider":
                    state_updates["gas_provider"] = result_dict
                    # Store entire result dict for gas provider
                    
                elif tool_name == "search_electric_provider":
                    state_updates["electric_provider"] = result_dict
                    # Store entire result dict for electric provider
                    
                elif tool_name == "search_water_provider":
                    state_updates["water_provider"] = result_dict
                    # Store entire result dict for water provider
                    
                elif tool_name == "search_sewer_provider":
                    state_updates["sewer_provider"] = result_dict
                    # Store entire result dict for sewer provider
                    
                elif tool_name == "search_stormwater_authority":
                    state_updates["stormwater_authority"] = result_dict
                    # Store entire result dict for stormwater authority
                    
        except Exception as e:
            # If parsing fails, skip this update
            # Why: Don't crash if result format is unexpected
            pass
            # pass: Do nothing, continue to next iteration
    
    # Return state updates with tool results
    # ============ LOGGING START ============
    print()
    if state_updates:
        print(f"📝 State Updates:")
        for key, value in state_updates.items():
            if key == "identified_ahj":
                print(f"   • {key}: {value}")
            else:
                print(f"   • {key}: ✓ Updated")
    print(f"✅ All tools executed ({len(tool_messages)} results)")
    print("➡️  Next Action: Return to agent_node for reasoning with tool results")
    print("="*80 + "\n")
    # ============ LOGGING END ============
    
    # Combine messages with state field updates
    # Why: Need to update both messages (for LLM) and state fields (for tracking)
    return_dict = {
        "messages": tool_messages,
        # Add all tool messages to state
        # Why list: Will be appended to existing messages
        # Now messages history includes tool results
        
        "next_action": "continue"
        # Always continue back to agent
        # Why: Agent needs to see results and decide what to do next
        # Agent might: Call more tools, or provide final answer
    }
    
    # Merge in the state updates
    # Why separate: Cleaner code, only add updates if they exist
    return_dict.update(state_updates)
    # update(): Adds all key-value pairs from state_updates to return_dict
    
    return return_dict
    # Return value: State updates including messages AND provider fields
    # Flow: tool_executor_node → agent_node (with tool results)


# ==============================================================================
# Router Function: Should Continue?
# ==============================================================================
def should_continue(state: AgentState) -> str:
    """
    Determine which node to execute next (router function).
    
    This function examines the state and decides:
    - "continue": Go to tool_executor_node
    - "end": Stop execution (agent is done)
    
    Function Name: "should_continue"
    - Why: Descriptive of its purpose (deciding whether to continue)
    - Returns: String indicating next node
    
    Args:
        state (AgentState): Current state
    
    Returns:
        str: Either "continue" or "end"
            - "continue": Agent wants to use tools
            - "end": Agent is done or encountered error
    
    Why This Function:
    - Conditional Routing: Different paths based on state
    - LangGraph: Uses return value to choose next node
    - Flexibility: Easy to add more routing logic
    
    Routing Logic:
    1. Check next_action in state
    2. Return appropriate string
    3. LangGraph routes to corresponding node
    
    Graph Structure:
              agent_node
                  │
                  ▼
            should_continue
                  │
          ┌───────┴───────┐
          ▼               ▼
      "continue"       "end"
          │               │
          ▼               ▼
    tool_executor     END
          │
          └─────────────┐
                        │
                        ▼
                   agent_node
    """
    
    # ============ LOGGING START ============
    print("\n" + "="*80)
    print("🔀 ROUTER FUNCTION - DECIDING NEXT STEP")
    print("="*80)
    print("Function: should_continue()")
    print("Purpose: Examine state and route to next node (conditional routing)")
    print("-"*80)
    # ============ LOGGING END ============
    
    # Get next_action from state
    # state["next_action"]: Set by agent_node
    # Values: "continue", "end", "error"
    next_action = state["next_action"]
    # next_action: String indicating what to do
    
    # ============ LOGGING START ============
    print(f"📊 Checking state['next_action']: '{next_action}'")
    print()
    # ============ LOGGING END ============
    
    # Make routing decision
    # Why simple: Agent already decided, we just route
    if next_action == "continue":
        # Agent wants to use tools
        # ============ LOGGING START ============
        print("➡️  Routing Decision: 'continue'")
        print("   Explanation: Agent decided it needs to execute tools")
        print("   Next Node: tool_executor_node")
        print("   Flow: should_continue → tool_executor_node → agent_node")
        print("="*80 + "\n")
        # ============ LOGGING END ============
        
        return "continue"
        # Return "continue" to route to tool_executor_node
        # LangGraph will call tool_executor_node next
        
    else:
        # Agent is done (next_action == "end" or "error")
        # ============ LOGGING START ============
        print("🏁 Routing Decision: 'end'")
        print("   Explanation: Agent has final answer or encountered error")
        print("   Next Node: END (execution stops)")
        print("   The agent's reasoning process is complete!")
        print("="*80 + "\n")
        # ============ LOGGING END ============
        
        return "end"
        # Return "end" to stop execution
        # LangGraph will end the graph execution
    
    # Note: We could add more complex logic here:
    # - Check if we have all required information
    # - Force end if iteration limit reached
    # - Route to different nodes based on state
    # For now, we trust agent's decision (next_action)


# ==============================================================================
# Node Design Patterns
# ==============================================================================
#
# Pattern 1: Input/Output Contract
# - All nodes take AgentState as input
# - All nodes return Dict[str, Any] as output
# - Why: Consistent interface for LangGraph
#
# Pattern 2: Stateless Functions
# - Nodes don't maintain internal state
# - All state is in AgentState parameter
# - Why: Pure functions, easier to test and debug
#
# Pattern 3: Explicit Returns
# - Only return fields that changed
# - Unchanged fields are not returned
# - Why: LangGraph merges, not replaces
#
# Pattern 4: Error Handling
# - Try/except around external calls
# - Graceful degradation
# - Error messages in state
# - Why: Resilience and debugging
#
# Pattern 5: Single Responsibility
# - agent_node: Only reasoning
# - tool_executor_node: Only tool execution
# - should_continue: Only routing
# - Why: Modularity and clarity
#
# ReAct Loop Flow:
# 
# 1. START → agent_node
#    Agent: "I need to identify the AHJ first"
#    Output: {"messages": [AIMessage(tool_call="identify_ahj")], "next_action": "continue"}
# 
# 2. should_continue → "continue" → tool_executor_node
#    Executor: Runs identify_ahj("Johnson City")
#    Output: {"messages": [ToolMessage("AHJ is City of Johnson City")]}
# 
# 3. agent_node (with tool result)
#    Agent: "Good, now I'll search for gas provider"
#    Output: {"messages": [AIMessage(tool_call="search_gas_provider")], "next_action": "continue"}
# 
# 4. should_continue → "continue" → tool_executor_node
#    Executor: Runs search_gas_provider("Johnson City")
#    Output: {"messages": [ToolMessage("Gas: Dominion Energy")]}
# 
# 5. agent_node (with tool result)
#    Agent: "I have enough information now"
#    Output: {"messages": [AIMessage("The gas provider is...")], "next_action": "end", "output": "..."}
# 
# 6. should_continue → "end" → END
#    Execution stops, final output returned

