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

# Google Search API for Search Grounding (Legacy)
# Why import requests: To make HTTP calls to Google Custom Search API
# Why import json: To parse JSON responses from Google API
import requests
import json

# Google Generative AI (Gemini) for Grounding with Google Search
# Why import genai: New official SDK for Gemini with native Google Search grounding
# Why import types: Type definitions for Gemini API requests/responses
from google import genai
from google.genai import types

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
# Initialize Google Search Configuration (Legacy)
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
# Initialize Gemini Client for Grounding with Google Search
# ==============================================================================
# _gemini_client: Client for Gemini API with native Google Search grounding
# Why initialize here: Reuse same client across all function calls
# Why conditional: Only create if API key is available
_gemini_client = None
if settings.gemini_api_key:
    # genai.Client(): Creates a Gemini API client
    # api_key: Authentication for Gemini API
    _gemini_client = genai.Client(api_key=settings.gemini_api_key)
    # If API key is not set, _gemini_client stays None
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
# Tool 1b: Grounding with Google Search (Gemini)
# ==============================================================================
def google_search_grounding(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Perform search using Gemini's Grounding with Google Search capability.
    
    This function uses Google's Gemini API with native Google Search grounding.
    Unlike traditional search APIs, Gemini:
    1. Analyzes the query and determines if search is needed
    2. Automatically generates and executes search queries
    3. Processes and synthesizes search results
    4. Returns a grounded response with automatic citations
    
    Function Name Explanation:
    - "google_search_grounding": Clearly indicates this uses Google Search
    - "grounding": Refers to Gemini's native feature that anchors responses in real-time web data
    - Why this name: Matches Gemini's official "Grounding with Google Search" feature
    
    What is "Grounding with Google Search"?
    - Native Gemini feature that connects the model to real-time web content
    - Model automatically decides when to search and what queries to use
    - Responses are synthesized from search results with automatic citations
    - Reduces hallucinations by basing responses on verifiable sources
    - Works with all available languages and Gemini models
    
    Why Gemini Grounding vs Traditional Search:
    - Automatic: Model decides when search is needed
    - Intelligent: Generates optimal search queries automatically
    - Synthesized: Returns coherent answers, not just raw results
    - Citations: Provides structured citation data with inline references
    - Real-time: Accesses current web content beyond training cutoff
    
    Args:
        query (str): The search query/question (e.g., "Who won euro 2024?")
            - Can be a natural language question
            - Model will determine if search is needed and generate appropriate queries
        max_results (int): Maximum number of results to process (default: 5)
            - Controls how many search results Gemini processes
            - More results = more comprehensive but slower
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - status: "success" or "error"
            - source: "gemini_grounding" (to identify this as Gemini grounding)
            - query: The original query (for traceability)
            - answer: Synthesized answer from Gemini (if success)
            - results: List of web sources used (if success)
            - citations: Citation mapping for inline references (if success)
            - web_search_queries: List of search queries used by Gemini (if available)
            - error: Error message (if error)
        
        Why this structure:
        - answer: The main AI-synthesized response
        - results: Source URLs and titles for verification
        - citations: Maps text segments to their sources
        - web_search_queries: Shows what the model searched for (debugging)
    
    Example Return Value:
        {
            "status": "success",
            "source": "gemini_grounding",
            "query": "Who won euro 2024?",
            "answer": "Spain won Euro 2024, defeating England 2-1 in the final.[1], [2]",
            "results": [
                {
                    "title": "UEFA Euro 2024 Final",
                    "url": "https://example.com/euro2024",
                    "index": 0
                }
            ],
            "citations": [
                {
                    "text": "Spain won Euro 2024, defeating England 2-1 in the final.",
                    "sources": [0, 1]
                }
            ],
            "web_search_queries": ["UEFA Euro 2024 winner"],
            "count": 2
        }
    """
    
    # Validate input: Ensure query is not empty
    # Why validate: Prevent wasted API calls
    if not query or not query.strip():
        # not query: Checks if query is None, empty string, or False
        # not query.strip(): Checks if query is only whitespace
        return {
            "status": "error",
            "source": "gemini_grounding",  # Identify source even on error
            "error": "Search query cannot be empty",
            "query": query,
            "results": []
        }
    
    # Check if Gemini client is configured
    # Why check: Need Gemini API key to use this feature
    if not _gemini_client:
        # _gemini_client: Global client initialized at module load
        # None means GEMINI_API_KEY was not set
        return {
            "status": "error",
            "source": "gemini_grounding",
            "error": "Gemini API not configured. Please set GEMINI_API_KEY in your .env file.",
            "query": query,
            "results": []
        }
        # Why descriptive error: Helps user know exactly what's missing
    
    # Perform grounded search with Gemini
    try:
        # try block: Catches API errors, network issues, invalid responses
        # Why needed: External API calls can fail in many ways
        
        # Create the Google Search grounding tool
        # types.Tool: Defines a tool that Gemini can use
        # google_search: Native Google Search integration
        # types.GoogleSearch(): Configuration for search grounding
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        # Why this structure: Official Gemini API format for grounding
        # The model will automatically use this tool when it determines search is needed
        
        # Configure the generation with the grounding tool
        # types.GenerateContentConfig: Configuration for content generation
        # tools=[grounding_tool]: List of tools available to the model
        config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )
        # Why pass as config: Tools need to be registered before generation
        
        # Build a detailed prompt to get comprehensive answers
        # Why detailed prompt: Ensures Gemini provides thorough, actionable information
        # Instead of just passing the query, we give clear instructions for what we need
        detailed_prompt = f"""Search the web and provide comprehensive, detailed information about: {query}

Please include:
- Complete contact information (phone numbers, email addresses, websites)
- Specific addresses and service areas
- Step-by-step connection/application requirements
- Required documents and fees
- Technical specifications if applicable
- Any important policies or regulations
- Links to relevant forms or applications

Provide a thorough, well-structured answer with all details that would be useful for someone taking action."""
        
        # Generate content with grounding
        # _gemini_client.models.generate_content(): Main generation method
        # model: Which Gemini model to use
        # contents: The user's query/prompt with detailed instructions
        # config: Configuration including tools
        response = _gemini_client.models.generate_content(
            model="gemini-2.0-flash-exp",  # Fast model with grounding support
            # Why gemini-2.0-flash-exp: Fast, supports grounding, good quality
            # Alternative: gemini-2.5-flash, gemini-1.5-pro
            contents=detailed_prompt,  # Detailed prompt for comprehensive answer
            config=config,  # Configuration with grounding tool
        )
        # response: Contains generated text and grounding metadata
        
        # Extract the main text answer
        # response.text: The AI-generated answer
        # Why .text: Convenience property that extracts text from response
        answer_text = response.text
        # answer_text: Main synthesized answer from Gemini
        
        # Extract grounding metadata if available
        # grounding_metadata: Contains search queries, sources, and citations
        # Why check: Response might not have grounding metadata if search wasn't used
        grounding_metadata = None
        if response.candidates and len(response.candidates) > 0:
            # response.candidates: List of generated responses (usually just one)
            # Why check: Ensure at least one candidate exists
            candidate = response.candidates[0]
            # candidate: The first (and usually only) response candidate
            
            # Get grounding metadata from the candidate
            # grounding_metadata: Contains web search queries, sources, citations
            grounding_metadata = candidate.grounding_metadata
            # Why important: Contains all the citation and source information
        
        # Process grounding metadata to extract results and citations
        # Why process: Convert Gemini's structure to our standard format
        processed_results = []
        web_search_queries = []
        citations = []
        
        if grounding_metadata:
            # grounding_metadata exists: Model used search grounding
            
            # Extract web search queries used by the model
            # web_search_queries: List of queries Gemini generated and executed
            # Why useful: Debugging, understanding model reasoning
            if hasattr(grounding_metadata, 'web_search_queries'):
                web_search_queries = grounding_metadata.web_search_queries or []
                # hasattr: Check if attribute exists
                # or []: Default to empty list if None
            
            # Extract grounding chunks (source URLs)
            # grounding_chunks: List of web sources used
            # Each chunk contains: uri (URL), title
            if hasattr(grounding_metadata, 'grounding_chunks'):
                chunks = grounding_metadata.grounding_chunks or []
                # chunks: List of source web pages
                
                for i, chunk in enumerate(chunks):
                    # i: Index of the chunk (used for citation references)
                    # chunk: One source web page
                    
                    if hasattr(chunk, 'web'):
                        # chunk.web: Contains web-specific information
                        web_info = chunk.web
                        # web_info: Object with uri and title
                        
                        title = getattr(web_info, 'title', 'N/A')
                        url = getattr(web_info, 'uri', 'N/A')
                        
                        # Extract domain from URL for displayLink compatibility
                        # Why: Old code expects displayLink field
                        displayLink = 'N/A'
                        if url and url != 'N/A':
                            try:
                                from urllib.parse import urlparse
                                parsed = urlparse(url)
                                displayLink = parsed.netloc
                                # netloc: Domain name (e.g., "example.com")
                            except:
                                displayLink = 'N/A'
                        
                        processed_results.append({
                            "title": title,
                            # getattr: Safe way to get attribute with default
                            # title: The webpage title
                            
                            "url": url,
                            # uri: The webpage URL
                            
                            "displayLink": displayLink,
                            # displayLink: Domain name for compatibility with old code
                            
                            "index": i,
                            # index: Position in chunks list (used for citations)
                            
                            "content": answer_text if i == 0 else f"Source: {title}",
                            # content: For backward compatibility, include synthesized answer
                            # Why: Old code expects content field with actual information
                            # First result gets the full answer, others get title
                            # This ensures tools that iterate results still get useful info
                        })
            
            # Extract grounding supports (citations)
            # grounding_supports: Maps text segments to their sources
            # Each support contains: segment (text), grounding_chunk_indices (source references)
            if hasattr(grounding_metadata, 'grounding_supports'):
                supports = grounding_metadata.grounding_supports or []
                # supports: List of citation mappings
                
                for support in supports:
                    # support: One citation mapping
                    
                    if hasattr(support, 'segment'):
                        # segment: The text segment being cited
                        segment = support.segment
                        # segment: Object with text, start_index, end_index
                        
                        # Extract citation information
                        citation_info = {
                            "text": getattr(segment, 'text', ''),
                            # text: The actual text being cited
                            
                            "start_index": getattr(segment, 'start_index', 0),
                            # start_index: Character position where citation starts
                            
                            "end_index": getattr(segment, 'end_index', 0),
                            # end_index: Character position where citation ends
                            
                            "sources": []
                            # sources: List of source indices that support this text
                        }
                        
                        # Extract source references
                        if hasattr(support, 'grounding_chunk_indices'):
                            citation_info["sources"] = support.grounding_chunk_indices or []
                            # grounding_chunk_indices: List of indices into grounding_chunks
                            # Example: [0, 1] means this text is supported by sources 0 and 1
                        
                        citations.append(citation_info)
                        # Add this citation to our list
        
        # Handle case where no grounding was used (answered from model knowledge)
        # Why: Sometimes Gemini answers from its own knowledge without searching
        # In this case, we still need to provide a results list for backward compatibility
        if not processed_results and answer_text:
            # No web sources but we have an answer
            # Create a synthetic result entry for backward compatibility
            processed_results.append({
                "title": "Gemini Knowledge Base",
                "url": "https://gemini.google.com",
                "displayLink": "gemini.google.com",
                "content": answer_text,
                "index": 0
            })
            # Why: Tools that iterate results expect at least one result
            # This ensures they get the answer even if no web search was performed
        
        # Return successful response
        return {
            "status": "success",  # Indicates successful grounding
            "source": "gemini_grounding",  # Identifies this as Gemini grounding
            "query": query,  # Echo back original query
            "answer": answer_text,  # The synthesized AI answer
            "results": processed_results,  # List of source web pages
            "citations": citations,  # Citation mapping for inline references
            "web_search_queries": web_search_queries,  # Queries used by model
            "count": len(processed_results),  # Number of sources
            "has_grounding": grounding_metadata is not None
            # has_grounding: Boolean indicating if search was actually used
            # Why useful: Sometimes model answers from knowledge without searching
        }
    
    except AttributeError as e:
        # AttributeError: Accessing attribute that doesn't exist
        # Why catch: API response structure might change
        return {
            "status": "error",
            "source": "gemini_grounding",
            "error": f"Error parsing Gemini response structure: {str(e)}",
            "query": query,
            "results": []
        }
    
    except Exception as e:
        # Exception: Catches any other unexpected errors
        # Why needed: Catch-all for unknown error types
        return {
            "status": "error",
            "source": "gemini_grounding",
            "error": f"Gemini grounding failed: {str(e)}",
            # str(e): Converts exception to readable message
            "query": query,
            "results": []
        }
        # Why include error details: Helps debug issues in production


# ==============================================================================
# Helper Function: Add Citations to Text
# ==============================================================================
def add_citations_to_text(answer: str, citations: List[Dict], sources: List[Dict]) -> str:
    """
    Add inline citations to text based on grounding metadata.
    
    This helper function takes the answer text, citation information, and source list
    to create a text with inline citations like [1](url), [2](url).
    
    Function Name Explanation:
    - "add_citations_to_text": Clearly describes the function's purpose
    - "citations": Refers to the citation metadata from Gemini
    - "text": The output is formatted text with inline citations
    
    How Citations Work:
    - Gemini provides citation data that maps text segments to sources
    - Each text segment has start/end indices and source references
    - We insert citation links at the end of each segment
    - Citations are formatted as clickable markdown links: [1](url)
    
    Args:
        answer (str): The AI-generated answer text
        citations (List[Dict]): List of citation objects with:
            - text: The cited text segment
            - start_index: Start position in answer
            - end_index: End position in answer
            - sources: List of source indices
        sources (List[Dict]): List of source objects with:
            - url: Source URL
            - title: Source title
            - index: Source index
    
    Returns:
        str: Text with inline citations added
        
        Example:
        Input: "Spain won Euro 2024."
        Output: "Spain won Euro 2024.[1](https://...)"
    
    How it Works:
    1. Sort citations by end_index (descending) to avoid index shifting
    2. For each citation, create citation links for its sources
    3. Insert citation links at the end_index position
    4. Result: Text with inline citations
    """
    
    # If no citations, return original text
    # Why check: Some responses might not have citations
    if not citations:
        return answer
    
    # Create a working copy of the text
    # Why copy: We'll be modifying it by inserting citations
    text = answer
    
    # Sort citations by end_index in descending order
    # Why descending: Prevents index shifting when inserting
    # Example: If we insert at position 100 first, position 50 stays unchanged
    # But if we insert at 50 first, position 100 shifts to 110
    sorted_citations = sorted(
        citations,
        key=lambda c: c.get("end_index", 0),
        reverse=True  # Descending order
    )
    # lambda c: Function that extracts end_index from citation dict
    # key=: Tells sorted() what to sort by
    
    # Process each citation
    for citation in sorted_citations:
        # citation: One citation mapping
        
        end_index = citation.get("end_index", 0)
        # end_index: Where to insert the citation
        
        source_indices = citation.get("sources", [])
        # source_indices: List of source indices for this citation
        # Example: [0, 1] means cite sources 0 and 1
        
        if not source_indices:
            # No sources for this citation, skip it
            continue
        
        # Create citation links
        # Format: [1](url), [2](url)
        citation_links = []
        for idx in source_indices:
            # idx: Index into sources list
            
            if idx < len(sources):
                # Make sure index is valid
                # Why check: Prevent index out of range errors
                
                source = sources[idx]
                # source: The source dictionary
                
                url = source.get("url", "")
                # url: The source URL
                
                if url and url != "N/A":
                    # Only add if URL is valid
                    # Why check: Some sources might not have URLs
                    
                    # Create markdown link: [index](url)
                    # +1: Convert from 0-indexed to 1-indexed for display
                    # Example: [1](https://example.com)
                    citation_links.append(f"[{idx + 1}]({url})")
        
        if citation_links:
            # We have at least one citation link
            
            # Join multiple citations with comma separator
            # Example: "[1](url1), [2](url2)"
            citation_string = ", ".join(citation_links)
            # join(): Combines list items into single string
            
            # Insert citation at end_index
            # text[:end_index]: Everything before the insertion point
            # citation_string: The citations to insert
            # text[end_index:]: Everything after the insertion point
            text = text[:end_index] + citation_string + text[end_index:]
            # Why this works: String slicing and concatenation
    
    # Return text with citations added
    return text
    # text: Original answer with inline citation links


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

