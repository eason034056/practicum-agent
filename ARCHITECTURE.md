# Architecture Document: Utility Identification AI Agent

## Executive Summary

This document describes the architecture of the Utility Identification AI Agent, built using LangGraph to collect utility provider and regulatory information for land development projects.

**Key Design Decisions:**
- **Framework**: LangGraph (not Google Cloud ADK)
- **Pattern**: ReAct (Reason + Act + Observe)
- **LLM**: OpenAI GPT-4 Turbo
- **Grounding**: RAG with Tavily Search API
- **State Management**: Explicit state graph

## Why LangGraph?

### Decision Rationale

We chose LangGraph over Google Cloud's Agent Development Kit (ADK) for the following reasons:

| Criterion | LangGraph | Google ADK | Winner |
|-----------|-----------|------------|--------|
| Platform Independence | ✅ | ❌ (Google Cloud only) | LangGraph |
| Control & Flexibility | ✅ | ⚠️ (Opinionated) | LangGraph |
| State Management | ✅ Explicit | ✅ Implicit | Tie |
| Debugging | ✅ LangSmith | ✅ Cloud Trace | Tie |
| Cost | $ (OpenAI + Search) | $$ (Vertex AI + Search) | LangGraph |
| Open Source | ✅ | ⚠️ Partial | LangGraph |
| Learning Curve | Medium | Medium-High | LangGraph |

### Key Advantages

1. **Graph-Based Control Flow**
   - Explicit state transitions
   - Visual workflow representation
   - Easy to modify and extend

2. **Platform Independence**
   - Runs anywhere (local, cloud, containers)
   - Not locked into Google Cloud
   - Can deploy to AWS, Azure, GCP, or on-premises

3. **Debugging & Observability**
   - LangSmith provides complete trace visualization
   - Can inspect state at every step
   - Easy to replay and debug executions

4. **Flexibility**
   - Complete control over agent behavior
   - Can implement custom routing logic
   - Easy to add new nodes and edges

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                           USER LAYER                            │
│  - CLI Interface (main.py)                                      │
│  - Interactive Mode                                             │
│  - Python API                                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       AGENT LAYER (LangGraph)                   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    State Graph                          │    │
│  │                                                         │    │
│  │   START → agent_node ⟷ tool_executor_node → END        │    │
│  │             ↑              ↓                            │    │
│  │             └──────────────┘                            │    │
│  │           (ReAct Loop)                                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  State Schema (AgentState):                                     │
│  - input, output                                                │
│  - messages (conversation history)                              │
│  - intermediate_steps (reasoning trace)                         │
│  - identified_ahj, *_provider (gathered info)                   │
│  - next_action, iterations, error (control flow)                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        TOOL LAYER                               │
│                                                                 │
│  AHJ Tools:                                                     │
│  ├─ identify_ahj(location)                                      │
│  └─ get_development_regulations(ahj_name)                       │
│                                                                 │
│  Utility Provider Tools:                                        │
│  ├─ search_gas_provider(location)                               │
│  ├─ search_electric_provider(location)                          │
│  ├─ search_water_provider(location)                             │
│  ├─ search_sewer_provider(location)                             │
│  └─ search_stormwater_authority(location)                       │
│                                                                 │
│  Detail Tools:                                                  │
│  ├─ get_utility_contact_info(provider, type)                    │
│  └─ get_connection_requirements(provider)                       │
│                                                                 │
│  Search Tools:                                                  │
│  ├─ web_search(query)                                           │
│  └─ search_with_context(query, context)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                            │
│                                                                 │
│  ├─ OpenAI GPT-4 (LLM for reasoning)                            │
│  ├─ Tavily Search API (Web search for RAG)                      │
│  └─ LangSmith (Monitoring & tracing)                            │
└─────────────────────────────────────────────────────────────────┘
```

### Component Layers

#### 1. User Layer
- **CLI Interface**: Command-line interface for single queries
- **Interactive Mode**: REPL for multiple queries
- **Python API**: Programmatic access for integration

#### 2. Agent Layer (LangGraph)
- **State Graph**: Manages workflow and state transitions
- **Agent Node**: LLM-powered reasoning and decision-making
- **Tool Executor Node**: Executes tools and returns results
- **Router**: Decides whether to continue or end

#### 3. Tool Layer
- **10 specialized tools** for different information types
- **Structured returns** with status, data, and sources
- **Error handling** for reliability

#### 4. External Services
- **OpenAI**: LLM for reasoning
- **Tavily**: Search API for real-time information
- **LangSmith**: Monitoring and debugging

## ReAct Pattern Implementation

### What is ReAct?

ReAct (Reason + Act + Observe) is a prompting pattern that interleaves reasoning, action, and observation:

1. **Reason**: LLM thinks about what to do next
2. **Act**: LLM chooses and executes a tool
3. **Observe**: LLM sees the result
4. **Loop**: Repeat until task is complete

### Implementation in LangGraph

```python
# Simplified pseudocode

def react_loop(initial_state):
    state = initial_state
    
    while state.next_action != "end":
        # REASON + ACT
        state = agent_node(state)
        # Agent decides: "I need to call tool X"
        
        if state.next_action == "end":
            break
        
        # OBSERVE
        state = tool_executor_node(state)
        # Execute tool X and see results
        
        # Loop back to REASON
    
    return state.output
```

### Example Execution Trace

```
User: "Find utilities for Johnson City, TN"

Iteration 1:
├─ REASON: "I need to identify the AHJ first"
├─ ACT: Call identify_ahj("Johnson City, TN")
└─ OBSERVE: "City of Johnson City is the AHJ"

Iteration 2:
├─ REASON: "Now I should search for gas provider"
├─ ACT: Call search_gas_provider("Johnson City, TN")
└─ OBSERVE: "Dominion Energy serves this area"

Iteration 3:
├─ REASON: "Let me get contact info for Dominion"
├─ ACT: Call get_utility_contact_info("Dominion Energy", "gas")
└─ OBSERVE: "Phone: 555-1234, Website: ..."

... (continues for all utilities) ...

Final Iteration:
├─ REASON: "I have all the information"
└─ ACT: Provide final answer (no more tools)
```

## State Management

### State Schema (AgentState)

```python
class AgentState(TypedDict):
    # Core I/O
    input: str                          # User's query
    output: str                         # Final answer
    
    # Conversation
    messages: Annotated[Sequence[BaseMessage], operator.add]
    intermediate_steps: Annotated[list, operator.add]
    
    # Gathered Information
    identified_ahj: str
    gas_provider: dict
    electric_provider: dict
    water_provider: dict
    sewer_provider: dict
    stormwater_authority: dict
    
    # Control Flow
    next_action: str                    # "continue" or "end"
    iterations: int                     # Iteration counter
    error: str                          # Error message
```

### Why This Structure?

1. **Complete Context**: All information in one place
2. **History Tracking**: Messages preserve full conversation
3. **Explicit Control**: `next_action` makes routing clear
4. **Safety**: `iterations` prevents infinite loops
5. **Modularity**: Each utility has its own field

### State Update Pattern

```python
# Node returns partial state update
def agent_node(state: AgentState) -> dict:
    # ... reasoning ...
    return {
        "messages": [new_message],      # Appended (operator.add)
        "iterations": state["iterations"] + 1,  # Replaced
        "next_action": "continue"       # Replaced
    }

# LangGraph merges update into state
# - messages: Appended to existing list
# - iterations: Replaces old value
# - other fields: Unchanged
```

## Tool Design

### Design Principles

1. **Descriptive Names**: `search_gas_provider`, not `find_gas`
2. **Consistent Signatures**: All take strings, return dicts
3. **Structured Returns**: Always include status, data, sources
4. **Error Handling**: Graceful failures with clear messages
5. **Docstrings**: Detailed descriptions for LLM understanding

### Tool Return Format

```python
{
    "status": "success" | "error",
    "location": "...",              # Echo input
    "provider_type": "gas",         # What type
    "information": "...",           # Actual data
    "sources": [                    # Source URLs
        {"title": "...", "url": "..."}
    ],
    "error": "..."                  # If status == "error"
}
```

### Why This Format?

- **Status Field**: Agent can check success/failure
- **Echo Inputs**: Traceability and debugging
- **Structured Data**: Easy parsing and extraction
- **Sources**: Enables grounding and verification
- **Consistency**: Same pattern across all tools

## RAG (Retrieval-Augmented Generation)

### Implementation

```
User Query → Tool Call → Web Search → Retrieved Context → LLM → Grounded Answer
```

1. **No Pre-existing Documents**: All information from web
2. **Real-time Search**: Uses Tavily API for current data
3. **Context Injection**: Search results provided to LLM
4. **Source Citation**: URLs included in responses

### Why Tavily?

- **LLM-Optimized**: Designed for AI applications
- **Clean Results**: Filters noise, returns relevant content
- **Structured Output**: Easy to parse and use
- **Fast**: Optimized for real-time applications

## Accuracy & Grounding

### Strategies for Accuracy

1. **Web Search**: Real-time, current information
2. **Multiple Sources**: Cross-validation from multiple results
3. **Source Citations**: All claims traceable to sources
4. **Structured Tools**: Specific tools reduce ambiguity
5. **Low Temperature**: `temperature=0.0` for consistency

### Grounding Mechanisms

- **Tool Returns Include Sources**: Every search result has URLs
- **LLM Prompted to Cite**: System prompt asks for sources
- **Evaluation**: `evaluate_grounding()` checks for citations

## Error Handling

### Multi-Level Error Handling

1. **Tool Level**: Try/except in tool implementations
2. **Execution Level**: Try/except in tool executor node
3. **Application Level**: Try/except in main.py
4. **Graceful Degradation**: Partial results on error

### Example

```python
# Tool level
def web_search(query):
    try:
        result = api.search(query)
        return {"status": "success", "results": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# Executor level
def tool_executor_node(state):
    try:
        result = tool_function(**args)
        return {"messages": [ToolMessage(str(result))]}
    except Exception as e:
        return {"messages": [ToolMessage(f"Error: {e}")]}
```

## Monitoring & Evaluation (AgentOps)

### LangSmith Integration

Every execution is traced with:
- All messages (user, AI, tool)
- State at each step
- Tool calls and results
- Execution timeline
- Error stack traces

### Evaluation Metrics

1. **Trajectory Evaluation**
   - Tool selection quality
   - Reasoning coherence
   - Efficiency

2. **Outcome Evaluation**
   - Completeness (all utilities found?)
   - Accuracy (correct information?)
   - Quality (well-structured answer?)

3. **Efficiency Metrics**
   - Iteration count
   - Tool call count
   - Execution time

4. **Grounding Check**
   - Sources cited?
   - Claims traceable?

## Scalability Considerations

### Current Implementation
- **Single-threaded**: One query at a time
- **Synchronous**: Blocking tool calls
- **In-memory State**: No persistence

### Production Enhancements

1. **Async Execution**
   ```python
   # Use async/await for parallel tool calls
   async def tool_executor_node(state):
       tasks = [call_tool_async(tc) for tc in tool_calls]
       results = await asyncio.gather(*tasks)
   ```

2. **State Persistence**
   ```python
   # Use LangGraph checkpointing
   from langgraph.checkpoint import MemorySaver
   memory = MemorySaver()
   agent = graph.compile(checkpointer=memory)
   ```

3. **Caching**
   ```python
   # Cache search results
   @lru_cache(maxsize=100)
   def web_search(query):
       # ...
   ```

4. **Rate Limiting**
   ```python
   # Throttle API calls
   from ratelimit import limits
   @limits(calls=10, period=60)
   def web_search(query):
       # ...
   ```

## Security Considerations

1. **API Key Management**: Never commit `.env`
2. **Input Validation**: Validate location inputs
3. **Output Sanitization**: Escape HTML/JavaScript in responses
4. **Rate Limiting**: Prevent abuse
5. **Error Messages**: Don't expose internals

## Deployment Options

### Option 1: Local/Development
```bash
python main.py --location "Johnson City, TN"
```

### Option 2: Docker Container
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py", "--interactive"]
```

### Option 3: Cloud Run (Google Cloud)
```bash
gcloud run deploy utility-agent --source .
```

### Option 4: Lambda (AWS)
Package as Lambda function with API Gateway

### Option 5: Kubernetes
Deploy as microservice with HPA (Horizontal Pod Autoscaling)

## Future Enhancements

1. **Streaming Responses**: Real-time output as agent works
2. **Multi-Language Support**: Internationalization
3. **Batch Processing**: Process multiple locations
4. **API Mode**: RESTful API with FastAPI
5. **Caching Layer**: Redis for search result caching
6. **Advanced Routing**: More sophisticated decision logic
7. **Human-in-the-Loop**: Approval workflows
8. **Fine-tuned Models**: Custom models for utility domain

## Conclusion

This architecture provides:
- ✅ **Flexibility**: LangGraph enables custom workflows
- ✅ **Accuracy**: RAG ensures grounded information
- ✅ **Observability**: Complete tracing with LangSmith
- ✅ **Scalability**: Can be enhanced for production
- ✅ **Maintainability**: Clear structure, well-documented code

The choice of LangGraph over Google ADK provides platform independence and maximum control while maintaining production-quality features through LangSmith integration and comprehensive error handling.

