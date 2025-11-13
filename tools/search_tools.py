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

# Google Search API for Search Grounding
# Why import requests: To make HTTP calls to Google Custom Search API
# Why import json: To parse JSON responses from Google API
import requests
import json

# concurrent.futures: For parallel execution of multiple search APIs
# ThreadPoolExecutor: Runs multiple functions simultaneously in separate threads
# Why needed: Call Tavily and Google searches at the same time for faster results
from concurrent.futures import ThreadPoolExecutor, as_completed

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
# Initialize Google Search Configuration
# ==============================================================================
# _google_search_available: Boolean flag to check if Google Search is configured
# Why check both: Need both API key AND search engine ID for Google Search to work
# Why store as boolean: Quick check without repeatedly checking settings
_google_search_available = bool(settings.google_search_api_key and settings.google_search_engine_id)
# bool(): Converts truthy/falsy values to True/False
# Why: If either is empty string, result is False

# Google Custom Search API endpoint
# Why this URL: Official Google Custom Search JSON API endpoint
# This is the base URL for all Google Custom Search requests
_GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"
# Why v1: Current stable version of the API
# Why customsearch: Google's programmable search service


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
            "source": "tavily",  # Identify source
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
            "source": "tavily",  # Identify source
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
            "source": "tavily",  # Identifies this as Tavily results
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
            "source": "tavily",  # Identify source even on error
            "error": f"Search failed: {str(e)}",  # Convert exception to string
            # f"...": f-string for string interpolation
            # str(e): Converts exception object to readable message
            "query": query,
            "results": []
        }
        # Why include error details: Helps debug issues in production


# ==============================================================================
# Tool 1b: Google Search with Grounding
# ==============================================================================
def google_search_grounding(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Perform a Google search with grounding capability.
    
    This function uses Google's Custom Search API to retrieve high-quality
    search results directly from Google. These results can be used for
    "grounding" - anchoring AI-generated responses in real search data.
    
    Function Name Explanation:
    - "google_search_grounding": Clearly indicates this uses Google Search
    - "grounding": Refers to the practice of anchoring AI responses in real data
    - Why separate from web_search: Different provider, different capabilities
    
    What is "Grounding"?
    - Grounding means connecting AI responses to verifiable sources
    - Instead of hallucinating, the AI references actual search results
    - Increases accuracy and credibility of responses
    - Users can verify information by checking sources
    
    Why Google Search:
    - Industry-leading search quality
    - Most comprehensive index of web content
    - Rich metadata (snippets, titles, URLs)
    - Trusted brand for information retrieval
    
    Args:
        query (str): The search query (e.g., "Johnson City TN gas utility provider")
        max_results (int): Maximum number of results to return (default: 5)
            - Google Custom Search allows up to 10 results per request
            - More results = more API cost
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - status: "success" or "error"
            - source: "google" (to identify the search provider)
            - results: List of search results (if success)
            - error: Error message (if error)
            - query: The original query (for traceability)
        
        Why include "source" field:
        - When combining multiple search providers, we need to know which is which
        - Allows comparison of results from different sources
        - Helps with attribution and citing sources
    
    Example Return Value:
        {
            "status": "success",
            "source": "google",
            "query": "Johnson City TN gas utility provider",
            "results": [
                {
                    "title": "Nicor Gas - Service Area",
                    "url": "https://nicorgas.com/service-area",
                    "snippet": "Nicor Gas serves Johnson City...",
                    "displayLink": "nicorgas.com"
                },
                ...
            ],
            "count": 5
        }
    """
    
    # Validate input: Ensure query is not empty
    # Why validate: Same as web_search - prevent wasted API calls
    if not query or not query.strip():
        # not query: Checks if query is None, empty string, or False
        # not query.strip(): Checks if query is only whitespace
        return {
            "status": "error",
            "source": "google",  # Still identify source even on error
            "error": "Search query cannot be empty",
            "query": query,
            "results": []
        }
    
    # Check if Google Search is configured
    # Why check: Need both API key and search engine ID
    if not _google_search_available:
        # _google_search_available: Boolean flag set at module initialization
        # False means either API key or search engine ID is missing
        return {
            "status": "error",
            "source": "google",
            "error": "Google Search API not configured. Please set GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID.",
            "query": query,
            "results": []
        }
        # Why descriptive error: Helps user know exactly what's missing
    
    # Perform the search
    try:
        # try block: Catches network errors, API errors, invalid responses
        # Why needed: External API calls can fail in many ways
        
        # Build request parameters
        # params: Dictionary of query parameters for the API request
        # These will be URL-encoded and appended to the request URL
        params = {
            # q: The search query
            # Why "q": Standard query parameter name (short for "query")
            "q": query,
            
            # key: Your Google API key for authentication
            # Why needed: Google requires authentication for all API calls
            "key": settings.google_search_api_key,
            
            # cx: Custom Search Engine ID
            # Why needed: Identifies which search engine configuration to use
            # cx stands for "Custom Search Engine ID"
            "cx": settings.google_search_engine_id,
            
            # num: Number of results to return
            # Why min(): Google allows max 10 results per request
            # If user requests more, we cap at 10
            "num": min(max_results, 10),
            # min(max_results, 10): Takes smaller of the two values
            # Example: min(5, 10) = 5, min(15, 10) = 10
        }
        
        # Make the API request
        # requests.get(): Sends HTTP GET request to the URL
        # Why GET: Read-only operation (retrieving data, not modifying)
        # _GOOGLE_SEARCH_URL: The base URL for Google Custom Search API
        # params=params: Appends query parameters to URL
        # timeout=10: Wait maximum 10 seconds for response
        response = requests.get(
            _GOOGLE_SEARCH_URL,
            params=params,
            timeout=10  # Why timeout: Prevents hanging if API is slow
        )
        # response: HTTP response object with status code, headers, body
        
        # Check if request was successful
        # raise_for_status(): Raises exception if status code indicates error
        # Why call this: Converts HTTP errors (404, 500, etc.) to Python exceptions
        # Status codes: 200-299 = success, 400-499 = client error, 500-599 = server error
        response.raise_for_status()
        
        # Parse JSON response
        # response.json(): Parses the response body as JSON
        # Why: Google API returns data in JSON format
        # Returns: Python dict with search results
        data = response.json()
        # data: Dictionary containing search results and metadata
        
        # Extract search results from response
        # data.get("items", []): Gets the "items" key from response
        # Why "items": Google API puts search results in an "items" array
        # Why default []: If no results found, "items" key might be missing
        items = data.get("items", [])
        # items: List of search result dictionaries
        
        # Process and structure the results
        # Why process: Extract only the fields we need, ignore extra metadata
        processed_results = []
        # processed_results: Empty list to store cleaned results
        
        # Iterate through each search result
        for item in items:
            # item: One search result (a dictionary)
            
            # Extract and enhance content from multiple sources
            # Why use multiple sources: the Google snippet is short (~160 chars), so we need more info
            
            # Get the basic snippet
            snippet = item.get("snippet", "")
            # snippet: Basic text summary (approximately 160 characters)
            
            # Get HTML snippet (may contain additional information)
            html_snippet = item.get("htmlSnippet", "")
            # htmlSnippet: HTML-formatted summary, may contain extra information
            
            # Extract metadata from pagemap if available
            # pagemap: Contains structured page data (like metatags, contactinfo, etc.)
            pagemap = item.get("pagemap", {})
            additional_info = []
            # additional_info: List of extra information extracted from pagemap
            
            # Try to extract contact information from pagemap
            # Why pagemap: Sometimes contains structured data like phone, address
            if "metatags" in pagemap and pagemap["metatags"]:
                metatags = pagemap["metatags"][0]  # First metatag set
                # metatags: The page's meta tags (may include description, keywords, etc.)
                
                # Extract description meta tag (often more detailed than snippet)
                if "og:description" in metatags:
                    additional_info.append(metatags["og:description"])
                    # og:description: Open Graph description, usually more detailed than snippet
                elif "description" in metatags:
                    additional_info.append(metatags["description"])
                    # description: Standard meta description
            
            # Try to get contact info from pagemap
            if "contactpoint" in pagemap:
                # contactpoint: Structured contact information
                for contact in pagemap["contactpoint"]:
                    if "telephone" in contact:
                        additional_info.append(f"Phone: {contact['telephone']}")
                    if "email" in contact:
                        additional_info.append(f"Email: {contact['email']}")
            
            # Combine all available content
            # Why combine: The more content, the better chance to find contact details
            content_parts = []
            # content_parts: Store all unique content fragments here
            
            # Add basic snippet first
            if snippet:
                content_parts.append(snippet)
            
            if html_snippet and html_snippet != snippet:
                # Remove HTML tags and entities from htmlSnippet
                import re
                clean_html = re.sub(r'<[^>]+>', '', html_snippet)
                # Remove HTML tags
                clean_html = re.sub(r'&[a-z]+;', ' ', clean_html)
                # Remove HTML entities (like &nbsp;)
                clean_html = clean_html.strip()
                
                # Only add if significantly different from snippet
                # Why check: Avoid duplicate content
                if clean_html and len(clean_html) > 50:
                    # Check if not substring of snippet and vice versa
                    if clean_html not in snippet and snippet not in clean_html:
                        content_parts.append(clean_html)
                    elif len(clean_html) > len(snippet):
                        # If clean_html contains snippet but has more info, replace
                        content_parts = [clean_html]
            
            # Add additional info from pagemap (usually unique structured data)
            if additional_info:
                content_parts.extend(additional_info)
            
            # Combine into single content string
            enhanced_content = " | ".join(filter(None, content_parts))
            # filter(None, ...): Filters out empty strings and None values
            # " | ".join(): Joins all unique pieces of content with a separator
            # Why " | ": Easy visual separation so the LLM can tell the source of info
            
            # Extract relevant fields
            processed_results.append({
                # "title": The title of the webpage
                "title": item.get("title", "N/A"),
                
                # "url": The full URL of the webpage
                "url": item.get("link", "N/A"),
                
                # "content": Enhanced content combining snippet, htmlSnippet, and pagemap data
                # Why enhanced: The Google snippet alone is too short (~160 chars)
                # This combines multiple sources for more complete information
                "content": enhanced_content if enhanced_content else "N/A",
                
                # "displayLink": The domain name (e.g., "example.com")
                "displayLink": item.get("displayLink", "N/A"),
                
                # Note: Google doesn't provide relevance scores in the response
                # Results are already ordered by relevance (best first)
            })
        # Return successful response
        return {
            "status": "success",  # Indicates successful search
            "source": "google",  # Identifies this as Google results
            "query": query,  # Echo back query for context
            "results": processed_results,  # List of search results
            "count": len(processed_results)  # How many results returned
            # Why include count: Agent can check if it got enough information
        }
    
    except requests.exceptions.Timeout:
        # Timeout: Request took longer than specified timeout
        # Why catch separately: Provides specific error message
        return {
            "status": "error",
            "source": "google",
            "error": "Search request timed out after 10 seconds",
            "query": query,
            "results": []
        }
    
    except requests.exceptions.RequestException as e:
        # RequestException: Base class for all requests library exceptions
        # Catches: Connection errors, DNS failures, SSL errors, etc.
        # as e: Stores the exception object in variable 'e'
        return {
            "status": "error",
            "source": "google",
            "error": f"Search request failed: {str(e)}",
            # f"...": f-string for string interpolation
            # str(e): Converts exception to readable message
            "query": query,
            "results": []
        }
    
    except json.JSONDecodeError as e:
        # JSONDecodeError: Response body is not valid JSON
        # Why catch: API might return HTML error page instead of JSON
        return {
            "status": "error",
            "source": "google",
            "error": f"Invalid JSON response from Google API: {str(e)}",
            "query": query,
            "results": []
        }
    
    except Exception as e:
        # Exception: Catches any other unexpected errors
        # Why needed: Catch-all for unknown error types
        return {
            "status": "error",
            "source": "google",
            "error": f"Unexpected error during Google search: {str(e)}",
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
    result = google_search_grounding(
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
    result = google_search_grounding(query=domain_query, max_results=max_results)
    # Reuses google_search_grounding() with modified query
    # Why reuse: Same logic, just different query format
    
    # Add domain info to result
    result["domain_searched"] = domain
    result["original_query"] = query
    # Metadata helps track what was searched and where
    
    return result


# ==============================================================================
# Tool 4: Combined Search (Tavily + Google Simultaneously)
# ==============================================================================
def combined_web_search(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Perform web search using BOTH Tavily and Google simultaneously.
    
    This function runs both search engines in parallel and combines their results,
    allowing you to see responses from both providers side-by-side. This is useful
    for comparing search quality, getting diverse perspectives, and maximizing
    information coverage.
    
    Function Name Explanation:
    - "combined_web_search": Clearly indicates this combines multiple sources
    - "combined": Means results from multiple search engines are merged
    - Why combine: Different search engines have different strengths
    
    Why Search Multiple Sources:
    1. Redundancy: If one API fails, you still have results from the other
    2. Comparison: See which search engine provides better results for your use case
    3. Coverage: Different engines may find different information
    4. Quality: Cross-reference results to verify accuracy
    
    How Parallel Execution Works:
    - ThreadPoolExecutor: Runs multiple functions simultaneously in separate threads
    - Both searches start at the same time (not sequential)
    - Total time ≈ slowest search (not sum of both searches)
    - Example: If Tavily takes 2s and Google takes 3s, total is ~3s (not 5s)
    
    Args:
        query (str): The search query (e.g., "Johnson City TN gas utility provider")
        max_results (int): Maximum number of results per source (default: 5)
            - Each source will return up to max_results
            - Total results could be up to max_results * 2
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - status: "success", "partial", or "error"
                - "success": Both searches succeeded
                - "partial": One search succeeded, one failed
                - "error": Both searches failed
            - query: The original query
            - tavily: Results from Tavily (dict with status, results, etc.)
            - google: Results from Google (dict with status, results, etc.)
            - combined_results: All results merged together (list)
            - summary: Human-readable summary of what happened
        
        Why this structure:
        - Separate fields for each source: Easy to compare side-by-side
        - combined_results: Convenient when you just want all results
        - summary: Quick understanding without parsing full response
    
    Example Return Value:
        {
            "status": "success",
            "query": "Johnson City TN gas utility provider",
            "tavily": {
                "status": "success",
                "source": "tavily",
                "results": [...],
                "count": 5
            },
            "google": {
                "status": "success",
                "source": "google",
                "results": [...],
                "count": 5
            },
            "combined_results": [...10 results total...],
            "summary": "Successfully retrieved 5 results from Tavily and 5 results from Google"
        }
    """
    
    # Validate input
    # Why validate: Prevent wasted API calls to both services
    if not query or not query.strip():
        # Empty query: Return error for both sources
        return {
            "status": "error",
            "query": query,
            "tavily": {
                "status": "error",
                "source": "tavily",
                "error": "Search query cannot be empty",
                "results": []
            },
            "google": {
                "status": "error",
                "source": "google",
                "error": "Search query cannot be empty",
                "results": []
            },
            "combined_results": [],
            "summary": "Error: Search query cannot be empty"
        }
    
    # Initialize result containers
    # Why initialize: Store results as they complete
    tavily_result = None
    google_result = None
    
    # Use ThreadPoolExecutor for parallel execution
    # with statement: Ensures executor is properly cleaned up after use
    # Why ThreadPoolExecutor: Allows running multiple functions simultaneously
    # max_workers=2: We're running 2 searches, so we need 2 worker threads
    with ThreadPoolExecutor(max_workers=2) as executor:
        # ThreadPoolExecutor: Creates a pool of 2 worker threads
        # max_workers=2: One thread for Tavily, one for Google
        # Why 2: We're only running 2 concurrent operations
        
        # Submit both search tasks
        # executor.submit(): Schedules a function to run in a thread
        # Returns: Future object that will contain the result later
        # Why submit: Non-blocking - doesn't wait for function to complete
        
        # Submit Tavily search
        # lambda: Anonymous function (function without a name)
        # Why lambda: Wraps the function call so we can pass it to submit()
        tavily_future = executor.submit(
            lambda: web_search(query, max_results)
            # web_search: The Tavily search function we defined earlier
            # query, max_results: Parameters passed to web_search
        )
        # tavily_future: Represents the Tavily search happening in background
        
        # Submit Google search
        google_future = executor.submit(
            lambda: google_search_grounding(query, max_results)
            # google_search_grounding: The Google search function we defined
        )
        # google_future: Represents the Google search happening in background
        
        # At this point, both searches are running simultaneously
        # Neither has completed yet - they're executing in parallel
        
        # Wait for both searches to complete
        # as_completed(): Returns futures as they complete (whoever finishes first)
        # [tavily_future, google_future]: The list of futures to wait for
        # Why as_completed: Process results as soon as they're available
        for future in as_completed([tavily_future, google_future]):
            # future: One of the completed futures (either Tavily or Google)
            # This loop will run twice - once for each future
            
            # Get the result from the completed future
            # future.result(): Blocks until the future completes, then returns result
            # Why safe here: Future has already completed (from as_completed)
            # result: The dictionary returned by web_search or google_search_grounding
            result = future.result()
            # result: Dict with status, results, source, etc.
            
            # Determine which search this result is from
            # result.get("source", ""): Gets the "source" field
            # Tavily results have source="tavily", Google results have source="google"
            if result.get("source") == "tavily" or (future == tavily_future):
                # This is the Tavily result
                # Why check both: Tavily results should have source="tavily"
                # But we also check future identity as backup
                tavily_result = result
                # Store Tavily result for later use
                
            elif result.get("source") == "google" or (future == google_future):
                # This is the Google result
                google_result = result
                # Store Google result for later use
        
        # At this point, both searches have completed
        # tavily_result and google_result both contain data
    
    # Determine overall status
    # Logic:
    # - If both succeeded: "success"
    # - If one succeeded: "partial"
    # - If both failed: "error"
    
    # Check if both searches succeeded
    # Why check: Need to know if we have complete information
    tavily_success = tavily_result and tavily_result.get("status") == "success"
    google_success = google_result and google_result.get("status") == "success"
    # tavily_success: Boolean - True if Tavily search succeeded
    # google_success: Boolean - True if Google search succeeded
    # and operator: Both conditions must be true
    # Why check tavily_result first: Avoid error if tavily_result is None
    
    # Determine overall status based on individual statuses
    if tavily_success and google_success:
        # Both searches succeeded - best case
        overall_status = "success"
        # Why "success": We have results from both sources
        
    elif tavily_success or google_success:
        # One search succeeded, one failed - partial success
        overall_status = "partial"
        # Why "partial": We have some results but not from both sources
        
    else:
        # Both searches failed - worst case
        overall_status = "error"
        # Why "error": No results available from either source
    
    # Combine results from both sources
    # Why combine: Sometimes you just want all results in one list
    combined_results = []
    # combined_results: Empty list to store all results
    
    # Add Tavily results to combined list
    if tavily_success:
        # If Tavily succeeded, add its results
        # tavily_result.get("results", []): Gets results list
        # Why get with default []: Safety - handles missing "results" key
        combined_results.extend(tavily_result.get("results", []))
        # .extend(): Adds all items from the list to combined_results
        # Why extend not append: append would add the list as a single item
        #   extend adds each result individually
    
    # Add Google results to combined list
    if google_success:
        # If Google succeeded, add its results
        combined_results.extend(google_result.get("results", []))
    
    # Create human-readable summary
    # Why summary: Quick understanding of what happened
    # Example: "Successfully retrieved 5 results from Tavily and 5 results from Google"
    if overall_status == "success":
        # Both succeeded
        tavily_count = tavily_result.get("count", 0)
        google_count = google_result.get("count", 0)
        summary = f"Successfully retrieved {tavily_count} results from Tavily and {google_count} results from Google"
        # f-string: Embeds variables in string
        
    elif overall_status == "partial":
        # One succeeded, one failed
        if tavily_success:
            # Tavily succeeded, Google failed
            count = tavily_result.get("count", 0)
            summary = f"Retrieved {count} results from Tavily only. Google search failed: {google_result.get('error', 'Unknown error')}"
        else:
            # Google succeeded, Tavily failed
            count = google_result.get("count", 0)
            summary = f"Retrieved {count} results from Google only. Tavily search failed: {tavily_result.get('error', 'Unknown error')}"
    
    else:
        # Both failed
        summary = f"Both searches failed. Tavily: {tavily_result.get('error', 'Unknown error')}. Google: {google_result.get('error', 'Unknown error')}"
    
    # Return combined response
    return {
        # Overall status: "success", "partial", or "error"
        "status": overall_status,
        
        # Original query for reference
        "query": query,
        
        # Complete Tavily result (includes status, results, error, etc.)
        "tavily": tavily_result,
        
        # Complete Google result
        "google": google_result,
        
        # All results from both sources in one list
        "combined_results": combined_results,
        # Why combined: Convenient when you don't care about the source
        
        # Human-readable summary
        "summary": summary,
        # Why summary: Quick understanding without parsing full response
        
        # Total number of results
        "total_count": len(combined_results)
        # len(): Returns number of items in list
        # Why include: Quick check of how much information we got
    }
    # This dictionary gives you:
    # 1. Complete information from each source (tavily, google fields)
    # 2. Combined view (combined_results field)
    # 3. Quick status check (status, summary fields)


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

