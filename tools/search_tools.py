"""
Web Search Tools for RAG (Retrieval-Augmented Generation)

This module provides web search capabilities for the agent to ground its responses
in real, up-to-date information from the internet.

Why these tools are critical:
- Accuracy: Real-time information prevents hallucinations
- Grounding: All answers are based on actual sources
- Currency: Gets latest information, not just training data
- Verification: Sources can be cited and verified

RAG (Retrieval-Augmented Generation) Process:
1. Agent identifies information need
2. Search tool retrieves relevant information
3. LLM generates answer based on retrieved context
4. Result is accurate and source-grounded
"""

# typing: Provides type hints for better code documentation and IDE support
from typing import Dict, List, Any, Optional
# Dict: Dictionary type {key: value}
# List: List type [item1, item2, ...]
# Any: Can be any type (use sparingly)
# Optional: Value can be None

# TavilySearchAPIWrapper: LangChain integration for Tavily search API
# Why Tavily: Specifically designed for LLM applications
# - Returns clean, structured results
# - Filters out irrelevant content
# - Provides answer summaries
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper

# Import settings to access API keys
from config.settings import settings


# ==============================================================================
# Initialize Tavily Search Client
# ==============================================================================
# _tavily_client: Private variable (underscore prefix = internal use only)
# Why initialize here: Reuse same client across all function calls
# Why conditional: Only create if API key is available
_tavily_client = None
if settings.tavily_api_key:
    # TavilySearchAPIWrapper: Creates a search client
    # tavily_api_key: Authentication for Tavily API
    _tavily_client = TavilySearchAPIWrapper(tavily_api_key=settings.tavily_api_key)
    # If API key is not set, _tavily_client stays None
    # Functions will handle this gracefully


# ==============================================================================
# Tool 1: General Web Search
# ==============================================================================
def web_search(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Perform a web search and return structured results.
    
    This is the primary tool for gathering real-time information from the internet.
    It's used when the agent needs to find facts, contact information, or
    verify information about utilities or authorities.
    
    Function Name Explanation:
    - "web_search": Clear, descriptive name that tells the LLM this tool searches the web
    - Not "search" alone: Too generic; could mean database search, file search, etc.
    - Not "google_search": Implementation-agnostic; we might switch search providers
    
    Args:
        query (str): The search query (e.g., "Johnson City TN gas utility provider")
        max_results (int): Maximum number of results to return (default: 5)
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - status: "success" or "error"
            - results: List of search results (if success)
            - error: Error message (if error)
            - query: The original query (for traceability)
        
        Why return a dict:
        - Structured: Agent can reliably parse the response
        - Flexible: Can add more fields without breaking existing code
        - Status indicator: Agent knows if search succeeded or failed
    
    Example Return Value:
        {
            "status": "success",
            "query": "Johnson City TN gas utility provider",
            "results": [
                {
                    "title": "Nicor Gas - Service Area",
                    "url": "https://nicorgas.com/service-area",
                    "content": "Nicor Gas serves Johnson City...",
                    "score": 0.95
                },
                ...
            ]
        }
    """
    
    # Validate input: Ensure query is not empty
    # Why validate: Prevents wasted API calls and gives clear error messages
    if not query or not query.strip():
        # not query: Checks if query is None, empty string, or False
        # not query.strip(): Checks if query is only whitespace
        # Why both: Catches different types of empty inputs
        
        # Return error response
        return {
            "status": "error",  # Status field tells agent the tool failed
            "error": "Search query cannot be empty",  # Descriptive error message
            "query": query,  # Echo back the query for debugging
            "results": []  # Empty results list
        }
        # Why return dict even on error: Consistent structure helps agent handle failures
    
    # Check if search client is available
    if not _tavily_client:
        # Why check: If API key wasn't set, client is None
        # This provides graceful degradation
        return {
            "status": "error",
            "error": "Search API not configured. Please set TAVILY_API_KEY.",
            "query": query,
            "results": []
        }
    
    # Perform the search
    try:
        # try block: Handles potential errors during API call
        # Why needed: Network issues, API limits, invalid responses can cause crashes
        
        # _tavily_client.results(): Calls Tavily API with our query
        # query=query: The search query to execute
        # max_results=max_results: How many results to return
        # search_depth="advanced": Use advanced search for better quality
        #   - "basic": Faster but less comprehensive
        #   - "advanced": Slower but more thorough and accurate
        #   Why "advanced": Accuracy is our top priority
        search_results = _tavily_client.results(
            query=query,
            max_results=max_results,
            search_depth="advanced"
        )
        # search_results: Raw response from Tavily API
        
        # Process and structure the results
        # Why process: Tavily returns extra metadata we don't need
        # We extract only relevant fields for the agent
        processed_results = []
        # processed_results: Empty list to store cleaned results
        
        # Handle different response formats from Tavily API
        # The API can return either a dict with "results" key, or a list directly
        # Why check: API behavior may vary by version or configuration
        if isinstance(search_results, list):
            # search_results is already a list of results
            results_to_process = search_results
        elif isinstance(search_results, dict):
            # search_results is a dict, extract "results" key
            results_to_process = search_results.get("results", [])
        else:
            # Unexpected format, return empty results
            results_to_process = []
        
        # Iterate through each result from the API
        for result in results_to_process:
            # result: One search result (a dictionary)
            
            # Extract relevant fields
            processed_results.append({
                # "title": The title of the webpage/article
                # result.get("title", "N/A"): Gets title, defaults to "N/A" if missing
                "title": result.get("title", "N/A"),
                
                # "url": The webpage URL
                # Why important: Agent can cite sources, users can verify
                "url": result.get("url", "N/A"),
                
                # "content": The relevant text snippet
                # Why important: Contains the actual information the agent needs
                "content": result.get("content", "N/A"),
                
                # "score": Relevance score (0.0 to 1.0)
                # Why important: Higher scores = more relevant results
                # Agent can prioritize high-scoring results
                "score": result.get("score", 0.0)
            })
        
        # Return successful response
        return {
            "status": "success",  # Indicates successful search
            "query": query,  # Echo back query for context
            "results": processed_results,  # List of search results
            "count": len(processed_results)  # How many results returned
            # Why include count: Agent can check if it got enough information
        }
    
    except Exception as e:
        # except: Catches any error that occurred during search
        # Exception: Base class for all exceptions (catches everything)
        # as e: Stores the exception object in variable 'e'
        
        # Return error response with exception details
        return {
            "status": "error",
            "error": f"Search failed: {str(e)}",  # Convert exception to string
            # f"...": f-string for string interpolation
            # str(e): Converts exception object to readable message
            "query": query,
            "results": []
        }
        # Why include error details: Helps debug issues in production


# ==============================================================================
# Tool 2: Context-Aware Web Search
# ==============================================================================
def search_with_context(
    query: str,
    context: str,
    max_results: int = 3
) -> Dict[str, Any]:
    """
    Perform a web search enhanced with context from previous findings.
    
    This tool is used when the agent needs to search for specific information
    based on what it already knows. For example, after identifying the AHJ,
    it might search for "Johnson City TN water utility" with context about
    the AHJ's location.
    
    Function Name Explanation:
    - "search_with_context": Distinguishes from basic web_search
    - "context": Indicates this tool uses additional information
    - Why separate function: Different use case than general search
    
    Args:
        query (str): The main search query (e.g., "water utility provider contact information")
        context (str): Additional context to inform the search 
            (e.g., "The AHJ is Johnson City, Tennessee, population 70,000")
        max_results (int): Maximum results (default: 3)
    
    Returns:
        Dict[str, Any]: Same structure as web_search()
            - Consistency: Agent can handle both tools the same way
    
    How Context Improves Search:
    - Without context: "water utility" → Generic results about water utilities
    - With context: "water utility" + "Johnson City TN" → Specific local results
    """
    
    # Build enhanced query by combining query and context
    # Why combine: Search engines work better with complete information
    # f-string: Allows embedding variables in strings
    enhanced_query = f"{context} {query}"
    # Example result: "Johnson City TN water utility provider contact information"
    # Why this format: Natural language that search engines understand
    
    # Perform the search using the enhanced query
    # We reuse web_search() instead of duplicating code
    # Why reuse: DRY principle (Don't Repeat Yourself)
    # - Easier to maintain
    # - Bugs only need to be fixed once
    # - Consistent behavior
    result = web_search(
        query=enhanced_query,  # Use enhanced query with context
        max_results=max_results  # Pass through max_results parameter
    )
    # result: Dictionary with search results (or error)
    
    # Add original query and context to result for traceability
    # Why add: Helps debugging and understanding agent's reasoning
    result["original_query"] = query
    result["context_used"] = context
    # These fields allow us to see what information the agent provided
    
    # Return the result
    return result
    # Return value: Dictionary with status, results, and metadata


# ==============================================================================
# Tool 3: Search Specific Domain (Bonus Tool)
# ==============================================================================
def search_specific_domain(
    query: str,
    domain: str,
    max_results: int = 3
) -> Dict[str, Any]:
    """
    Search within a specific website domain.
    
    This tool is useful when you know which website to search
    (e.g., a specific utility company's website).
    
    Function Name Explanation:
    - "search_specific_domain": Clearly indicates domain-limited search
    - "domain": Refers to website domain (e.g., duke-energy.com)
    
    Args:
        query (str): What to search for (e.g., "service application process")
        domain (str): Website domain to search within (e.g., "duke-energy.com")
        max_results (int): Maximum results
    
    Returns:
        Dict[str, Any]: Standard search result structure
    
    Use Case Example:
    - Agent knows the utility is Duke Energy
    - Needs to find their application process
    - Searches only duke-energy.com for authoritative info
    """
    
    # Build domain-specific query using site: operator
    # site:domain: Google search operator that limits results to one domain
    # Why use site: operator: Standard across all search engines
    domain_query = f"site:{domain} {query}"
    # Example: "site:duke-energy.com service application process"
    # This tells search engine to only return results from duke-energy.com
    
    # Perform the search with domain restriction
    result = web_search(query=domain_query, max_results=max_results)
    # Reuses web_search() with modified query
    # Why reuse: Same logic, just different query format
    
    # Add domain info to result
    result["domain_searched"] = domain
    result["original_query"] = query
    # Metadata helps track what was searched and where
    
    return result


# ==============================================================================
# Tool Registration Information
# ==============================================================================
# When the agent is initialized, these functions will be "bound" to the LLM.
# This means the LLM can choose to call them when needed.
#
# How Tool Binding Works:
# 1. Function signature analyzed: Name, parameters, types
# 2. Docstring converted to tool description
# 3. LLM receives tool information in its system prompt
# 4. LLM can output tool calls in a special format
# 5. LangGraph executes the tool and returns results
# 6. LLM sees results and continues reasoning
#
# Why Detailed Docstrings Matter:
# - LLM reads docstrings to understand what tool does
# - Clear descriptions → Better tool selection
# - Example parameters → Better parameter formatting
# - Return value docs → Better result interpretation

