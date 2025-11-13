"""
Tools Package Initializer

This package contains all the tools (functions) that the AI agent can use
to interact with external systems and gather utility information.

Why separate tools into their own package:
- Modularity: Each tool category (AHJ, utilities, search) is in its own file
- Testability: Easy to test tools independently
- Reusability: Tools can be used by other agents or applications
- Maintainability: Clear organization makes updates easier

Tool Categories:
- ahj_tools: Functions for identifying Authority Having Jurisdiction
- utility_tools: Functions for finding utility providers (gas, electric, water, sewer)
- search_tools: Functions for web search and information retrieval (RAG)
"""

# Import all tool functions from their respective modules
# This allows convenient importing: from tools import identify_ahj, search_gas_provider

# AHJ (Authority Having Jurisdiction) tools
from tools.ahj_tools import (
    identify_ahj,                   # Identifies the AHJ for a location
    get_development_regulations     # Gets regulations and requirements for an AHJ
)

# Utility provider search tools
from tools.utility_tools import (
    search_gas_provider,       # Finds gas utility provider
    search_electric_provider,  # Finds electric utility provider
    search_water_provider,     # Finds water utility provider
    search_sewer_provider,     # Finds sewer utility provider
    search_stormwater_authority, # Finds stormwater management authority
    get_utility_contact_info,  # Gets contact details for a provider
    get_connection_requirements # Gets connection/setup requirements
)

# Web search and RAG tools
from tools.search_tools import (
    web_search,                # General web search
    search_with_context        # Web search with context from previous results
)

# __all__: List of all tools available for the agent
# Why this is important:
# - Documents all available tools in one place
# - The agent builder will use this list to bind tools to the LLM
# - Makes it clear what capabilities the agent has
__all__ = [
    # AHJ Tools
    "identify_ahj",
    "get_development_regulations",
    
    # Utility Tools
    "search_gas_provider",
    "search_electric_provider",
    "search_water_provider",
    "search_sewer_provider",
    "search_stormwater_authority",
    "get_utility_contact_info",
    "get_connection_requirements",
    
    # Search Tools
    "web_search",
    "search_with_context",
]

# Tool Naming Convention Explanation:
# 
# 1. Verbs describe actions: "identify", "search", "get"
#    - Why: Makes it clear what the tool does
#    - Example: "identify_ahj" tells the LLM this tool identifies something
#
# 2. Specific nouns describe targets: "gas_provider", "ahj", "stormwater"
#    - Why: LLM can match tool to intent based on keywords
#    - Example: If user asks about "gas", LLM knows to use "search_gas_provider"
#
# 3. Underscores separate words: snake_case
#    - Why: Python function naming convention
#    - Improves readability: "search_gas_provider" vs "searchgasprovider"
#
# 4. Descriptive but concise names
#    - Why: LLM has limited context, so names should be informative but not verbose
#    - Good: "get_connection_requirements"
#    - Bad: "get_all_connection_requirements_and_fees_for_utility_provider"

