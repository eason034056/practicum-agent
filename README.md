# Utility Identification AI Agent

An intelligent agent built with LangGraph for identifying utility providers and regulatory information for land development projects.

## Overview

This AI agent helps developers and planners quickly identify:
- **Authority Having Jurisdiction (AHJ)** - The local government with regulatory authority
- **Utility Providers** - Gas, Electric, Water, Sewer services
- **Stormwater Authority** - Stormwater management requirements
- **Contact Information** - Phone numbers, addresses, websites
- **Connection Requirements** - Application processes, fees, technical requirements

### Key Features

- ✅ **Accurate Information** - Uses RAG (Retrieval-Augmented Generation) with web search
- 🔄 **Multi-Step Reasoning** - ReAct pattern (Reason + Act + Observe)
- 🛠️ **Specialized Tools** - Dedicated functions for each utility type
- 📊 **Full Traceability** - Every step is logged and traceable
- 🔍 **Source Grounding** - All information includes source URLs
- 💬 **Interactive Mode** - REPL for multiple queries
- 🎯 **Production Ready** - Error handling, monitoring, evaluation

## Architecture

### Why LangGraph?

This project uses **LangGraph** instead of Google Cloud ADK because:

1. **Platform Independence** - Works anywhere, not tied to Google Cloud
2. **Graph-Based Control** - Explicit, visual workflow management
3. **State Management** - Built-in state tracking across steps
4. **Flexibility** - Complete control over agent behavior
5. **Debugging** - LangSmith integration for trajectory visualization
6. **Open Source** - Fully open source framework

### System Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────┐
│    LangGraph Agent State            │
│  - Input location                   │
│  - Message history                  │
│  - Gathered information             │
│  - Reasoning steps                  │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│      ReAct Loop (Graph Nodes)       │
│                                     │
│  ┌────────┐    ┌──────┐    ┌────┐ │
│  │ Agent  │───▶│Tools │───▶│Back│ │
│  │(Reason)│    │(Act) │    │Loop│ │
│  └────────┘    └──────┘    └────┘ │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│     Tools (10 specialized tools)    │
│  - identify_ahj                     │
│  - search_gas_provider              │
│  - search_electric_provider         │
│  - search_water_provider            │
│  - search_sewer_provider            │
│  - search_stormwater_authority      │
│  - get_utility_contact_info         │
│  - get_connection_requirements      │
│  - web_search                       │
│  - search_with_context              │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│      External Data Sources          │
│  - Tavily Search API                │
│  - Municipal websites               │
│  - Utility company sites            │
└─────────────────────────────────────┘
```

### LangGraph State Graph

```
        START
          │
          ▼
    ┌──────────┐
    │  Agent   │◄─────┐
    │(Reason)  │      │
    └────┬─────┘      │
         │            │
         ▼            │
    Should use       │
      tools?         │
         │            │
    Yes  │  No        │
         │   │        │
         ▼   │        │
    ┌────────┴─┐     │
    │  Tools   │     │
    │ (Action) │     │
    └────┬─────┘     │
         │           │
         └───────────┘
                │
                ▼ No more tools needed
              END
           (Final Answer)
```

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd ai-agent
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
LANGCHAIN_API_KEY=your_langsmith_api_key_here  # Optional
```

**Getting API Keys:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Tavily**: https://tavily.com
- **LangSmith** (optional): https://smith.langchain.com

## Usage

### Single Query Mode

Search for utilities in a specific location:

```bash
python main.py --location "Johnson City, TN"
```

With verbose output (shows all steps):

```bash
python main.py --location "Raleigh, NC" --verbose
```

### Interactive Mode

Run in REPL mode for multiple queries:

```bash
python main.py --interactive
```

Example session:
```
Enter location (or 'quit'): Johnson City, TN
Searching for utilities in Johnson City, TN...
[Results displayed]

Enter location (or 'quit'): Durham, NC
Searching for utilities in Durham, NC...
[Results displayed]

Enter location (or 'quit'): quit
Goodbye!
```

### As a Python Module

```python
from agent.graph import run_agent

# Run agent
result = run_agent("Find utilities for Raleigh, NC")

# Access results
print(result["output"])  # Final answer
print(result["identified_ahj"])  # AHJ name
print(result["gas_provider"])  # Gas provider info
print(result["iterations"])  # Number of reasoning steps
```

## Project Structure

```
ai-agent/
├── README.md                   # This file
├── TUTORIAL.md                 # Complete tutorial with explanations
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment file
├── .env                        # Your environment file (not in git)
│
├── config/                     # Configuration management
│   ├── __init__.py
│   └── settings.py             # Settings from environment
│
├── tools/                      # Tool implementations
│   ├── __init__.py
│   ├── ahj_tools.py           # AHJ identification tools
│   ├── utility_tools.py       # Utility provider tools
│   └── search_tools.py        # Web search and RAG
│
├── agent/                      # LangGraph agent implementation
│   ├── __init__.py
│   ├── state.py               # State schema definition
│   ├── nodes.py               # Graph node implementations
│   └── graph.py               # Graph construction
│
├── evaluation/                 # Evaluation and monitoring
│   ├── __init__.py
│   └── evaluators.py          # AgentOps evaluation
│
├── main.py                     # Entry point
│
└── tests/                      # Unit tests
    └── test_agent.py
```

## How It Works

### ReAct Pattern Implementation

The agent uses the **ReAct** (Reason + Act + Observe) pattern:

1. **Reason**: Agent analyzes the current situation
   - "I need to identify the AHJ first"
   - "Now I should search for the gas provider"

2. **Act**: Agent calls appropriate tools
   - Calls `identify_ahj(location="Johnson City, TN")`
   - Calls `search_gas_provider(location="Johnson City, TN")`

3. **Observe**: Agent sees tool results
   - Tool returns: "City of Johnson City is the AHJ"
   - Agent incorporates this into reasoning

4. **Loop**: Repeat until task is complete
   - Continue gathering information
   - Stop when all utilities identified

### Example Execution Flow

```
User: "Find utilities for Johnson City, TN"

Iteration 1:
  Reason: "I need to identify the AHJ first"
  Act: identify_ahj("Johnson City, TN")
  Observe: "AHJ is City of Johnson City"

Iteration 2:
  Reason: "Now search for gas provider"
  Act: search_gas_provider("Johnson City, TN")
  Observe: "Dominion Energy provides gas service"

Iteration 3:
  Reason: "Get contact information for Dominion Energy"
  Act: get_utility_contact_info("Dominion Energy", "gas")
  Observe: "Phone: 555-1234, Website: ..."

... (continues for all utilities) ...

Final Iteration:
  Reason: "I have all required information"
  Act: None (provide final answer)
  Output: "Here are the utilities for Johnson City, TN..."
```

## Tools Available

### AHJ Tools

1. **identify_ahj(location)** - Identifies the Authority Having Jurisdiction
2. **get_development_regulations(ahj_name)** - Gets regulations and requirements

### Utility Provider Tools

3. **search_gas_provider(location)** - Finds gas utility provider
4. **search_electric_provider(location)** - Finds electric utility provider
5. **search_water_provider(location)** - Finds water utility provider
6. **search_sewer_provider(location)** - Finds sewer utility provider
7. **search_stormwater_authority(location)** - Finds stormwater authority

### Detail Tools

8. **get_utility_contact_info(provider_name, utility_type)** - Gets contact details
9. **get_connection_requirements(provider_name)** - Gets connection process

### Search Tools

10. **web_search(query)** - General web search for any information

Each tool:
- Has a clear, descriptive name
- Returns structured data (dictionaries)
- Includes source URLs for grounding
- Handles errors gracefully

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key settings:

- `LLM_MODEL` - Which OpenAI model to use (default: gpt-4-turbo-preview)
- `LLM_TEMPERATURE` - Response randomness (0.0 = deterministic)
- `MAX_ITERATIONS` - Maximum reasoning loops (prevents runaway)
- `LANGCHAIN_TRACING_V2` - Enable LangSmith monitoring

### Model Selection

**GPT-4 Turbo** (Recommended):
- Best reasoning capabilities
- Handles complex multi-step tasks
- Higher cost but better accuracy

**GPT-3.5 Turbo** (Budget option):
- Faster and cheaper
- May require more iterations
- Good for testing

## Monitoring and Debugging

### LangSmith Integration

If LangSmith is configured, every agent run is traced:

1. Go to https://smith.langchain.com
2. Select your project: "utility-identification-agent"
3. View traces with:
   - Every reasoning step
   - Every tool call
   - All messages and state changes
   - Execution timeline

### Evaluation

The agent can be evaluated on:

1. **Trajectory Evaluation** - Did it choose the right tools?
2. **Outcome Evaluation** - Is the final answer correct?
3. **Efficiency** - How many iterations were needed?
4. **Grounding** - Are sources cited correctly?

See `evaluation/evaluators.py` for implementation.

## Deployment Options

### Local Development

```bash
python main.py --location "Your Location"
```

### Cloud Deployment

#### Option 1: Docker Container

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py", "--interactive"]
```

#### Option 2: Google Cloud Run

```bash
gcloud run deploy utility-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY,TAVILY_API_KEY=$TAVILY_API_KEY
```

#### Option 3: AWS Lambda

Package the agent as a Lambda function with API Gateway.

## Testing

Run tests:

```bash
pytest tests/
```

Test individual components:

```bash
# Test tools
pytest tests/test_tools.py

# Test agent
pytest tests/test_agent.py

# Test with coverage
pytest --cov=agent --cov=tools tests/
```

## Performance

Typical execution metrics:

- **Time**: 30-60 seconds per query
- **Iterations**: 5-15 reasoning steps
- **API Calls**: 10-20 web searches
- **Cost**: ~$0.10-0.20 per query (GPT-4 Turbo)

Optimization tips:

1. Use GPT-3.5 for lower cost
2. Cache search results
3. Reduce max_results in searches
4. Implement parallel tool execution

## Troubleshooting

### "OPENAI_API_KEY not set"

- Check `.env` file exists
- Verify API key is correct
- Ensure `.env` is in project root

### "TAVILY_API_KEY not set"

- Get API key from https://tavily.com
- Add to `.env` file
- Restart application

### Agent takes too long

- Check network connection
- Reduce `max_results` in tool calls
- Use faster model (gpt-3.5-turbo)

### Agent reaches max iterations

- Increase `MAX_ITERATIONS` in `.env`
- Check if query is too complex
- Review LangSmith traces to see where it's stuck

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

[Your License Here]

## Contact

[Your Contact Information]

## Acknowledgments

- **LangChain** - Framework for LLM applications
- **LangGraph** - Graph-based agent orchestration
- **OpenAI** - GPT models
- **Tavily** - Search API optimized for LLMs

