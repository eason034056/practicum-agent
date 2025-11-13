"""
Authority Having Jurisdiction (AHJ) Identification Tools

This module provides tools for identifying and gathering information about
the Authority Having Jurisdiction for a specific location.

What is AHJ:
- AHJ: The local government (city or county) that regulates land development
- Responsibilities: Zoning, permits, site plans, development regulations
- Why important: Different AHJs have different rules, fees, and processes

Why These Tools Are Critical:
- First step: Must identify AHJ before finding utility providers
- Regulations: Different AHJs have different development requirements
- Contacts: Need AHJ contact info for permit applications
"""

# Type hints for better code documentation
from typing import Dict, List, Any, Optional

# Import web search functionality from our search tools
from tools.search_tools import web_search, search_with_context


# ==============================================================================
# Tool 1: Identify Authority Having Jurisdiction (AHJ)
# ==============================================================================
def identify_ahj(location: str) -> Dict[str, Any]:
    """
    Identify the Authority Having Jurisdiction (AHJ) for a given location.
    
    The AHJ is typically a city or county government that has regulatory
    authority over land development, building permits, and utility connections.
    
    Function Name Explanation:
    - "identify_ahj": Action verb "identify" + target "ahj"
    - Why "identify" not "find": Implies determination/analysis, not just search
    - Why lowercase with underscore: Python naming convention for functions
    
    Args:
        location (str): Location description (e.g., "123 Main St, Johnson City, TN", 
            "Johnson City, Tennessee", or "Washington County, TN"). Can be an address,
            city name, county name, or general area description.
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - status: "success" or "error"
            - ahj_name: Name of the AHJ (e.g., "City of Johnson City")
            - ahj_type: Type of jurisdiction ("city" or "county")
            - location: The location that was searched
            - details: Additional information about the AHJ
            - sources: URLs where information was found
        
        Why this structure:
        - ahj_name: Core piece of information needed
        - ahj_type: Helps agent understand jurisdiction level
        - sources: Enables verification and grounding
    
    Process Flow:
    1. Construct search query for AHJ identification
    2. Perform web search
    3. Parse results to extract AHJ information
    4. Return structured response
    
    Example Usage by Agent:
        User: "Find utilities for Johnson City, TN"
        Agent: [Calls identify_ahj("Johnson City, TN")]
        Result: {"ahj_name": "City of Johnson City", "ahj_type": "city", ...}
        Agent: [Now knows to search for Johnson City utility providers]
    """
    
    # Input validation: Check if location is provided
    # Why validate: Prevents wasted API calls and provides clear errors
    if not location or not location.strip():
        # not location: Checks for None or empty string
        # not location.strip(): Checks for whitespace-only strings
        #   - strip() removes leading/trailing whitespace
        #   - If result is empty, location was only whitespace
        return {
            "status": "error",
            "error": "Location cannot be empty",
            "location": location,
            "ahj_name": None,
            "ahj_type": None
        }
        # Return early on error (guard clause pattern)
        # Why early return: Prevents nested if statements
    
    # Construct search query for AHJ identification
    # Why specific query: Better search results than generic "location government"
    # Format: "what city or county is responsible for land development in [location]"
    query = f"what city or county is responsible for land development permits and zoning in {location}"
    # Query components:
    # - "city or county": Narrows to government type we need
    # - "land development permits": Specific domain we care about
    # - "zoning": Another keyword that indicates AHJ
    # - "in {location}": Provides the geographic context
    
    # Alternative queries we could add (for future enhancement):
    # - "building department {location}"
    # - "planning department {location}"
    # - "AHJ authority having jurisdiction {location}"
    
    # Perform web search for AHJ information
    # web_search: Our search tool from search_tools.py
    # max_results=5: Get multiple sources for cross-validation
    search_result = web_search(
        query=query,
        max_results=5  # More results = better chance of accurate info
    )
    # search_result: Dictionary with status and results
    
    # Check if search was successful
    # Why check: Search might fail due to network issues, API limits, etc.
    if search_result["status"] != "success":
        # If search failed, return error response
        return {
            "status": "error",
            "error": f"Failed to search for AHJ: {search_result.get('error', 'Unknown error')}",
            # f-string: Embeds the actual error message
            # .get('error', 'Unknown error'): Safe access with default
            "location": location,
            "ahj_name": None,
            "ahj_type": None
        }
    
    # Extract search results
    # results: List of dictionaries, each containing title, url, content, score
    results = search_result.get("results", [])
    # .get("results", []): Safe access, defaults to empty list if missing
    
    # Check if we got any results
    # Why check: No results means we can't identify AHJ
    if not results:
        return {
            "status": "error",
            "error": "No information found for the specified location",
            "location": location,
            "ahj_name": None,
            "ahj_type": None
        }
    
    # Parse results to identify AHJ
    # In a production system, we might use NLP or a specialized extraction model
    # For now, we return structured data for the LLM to interpret
    # Why let LLM interpret: LLMs are good at extracting entities from text
    
    # Collect all content for LLM analysis
    # Why collect all: LLM can synthesize information from multiple sources
    all_content = []
    sources = []  # Track source URLs
    
    # Iterate through search results
    for result in results:
        # result: One search result dictionary
        
        # Extract content from this result
        content = result.get("content", "")
        # Why get content: This is the text snippet from the webpage
        
        # Only include non-empty content
        if content:
            all_content.append(content)
            # Add to our content collection
            
            sources.append({
                "title": result.get("title", ""),
                "url": result.get("url", "")
            })
            # Track source for citation purposes
    
    # Attempt to extract AHJ name from the search results
    # Why extract: So state can track AHJ identification status
    # Method: Simple keyword matching for common patterns
    
    combined_content = " ".join(all_content).lower()
    # combined_content: All search results combined into one lowercase string
    # Why lowercase: Makes pattern matching case-insensitive
    
    ahj_name = None  # Will store the extracted AHJ name
    ahj_type = None  # Will store "city" or "county"
    
    # Try to extract AHJ name using common patterns
    # Pattern 1: "City of [Name]"
    if "city of" in combined_content:
        # Found "city of" pattern
        import re
        # re: Regular expression module for pattern matching
        
        # Look for "City of [Name]" pattern
        # Why regex: Can extract the actual city name
        match = re.search(r'city of ([a-z\s]+)', combined_content)
        # r'city of ([a-z\s]+)': Pattern that captures city name
        # (): Capture group - extracts the city name
        # [a-z\s]+: One or more letters or spaces
        
        if match:
            # Found a match!
            city_name = match.group(1).strip().title()
            # match.group(1): The captured city name
            # .strip(): Remove extra whitespace
            # .title(): Capitalize Each Word
            
            ahj_name = f"City of {city_name}"
            # Format as "City of [Name]"
            ahj_type = "city"
            # Type is city
    
    # Pattern 2: "[Name] County" (if city not found)
    if not ahj_name and "county" in combined_content:
        # Didn't find city pattern, try county
        import re
        
        # Look for "[Name] County" pattern
        match = re.search(r'([a-z\s]+)\s+county', combined_content)
        # r'([a-z\s]+)\s+county': Pattern that captures county name
        # ([a-z\s]+): Capture the county name (before "county")
        # \s+county: Whitespace + "county"
        
        if match:
            county_name = match.group(1).strip().title()
            # Extract and format county name
            
            ahj_name = f"{county_name} County"
            # Format as "[Name] County"
            ahj_type = "county"
            # Type is county
    
    # Return structured response with all gathered information
    # The agent's LLM will analyze this to extract the actual AHJ name
    return {
        "status": "success",
        "location": location,
        "ahj_name": ahj_name,
        # ahj_name: Extracted AHJ name (e.g., "City of Johnson City")
        # Why include: So nodes.py can update state["identified_ahj"]
        # Can be None if extraction failed
        
        "ahj_type": ahj_type,
        # ahj_type: "city" or "county" (or None if not found)
        # Why include: Helps agent understand jurisdiction level
        
        # Note: In a more sophisticated implementation, we would parse
        # the content to extract the exact AHJ name and type.
        # For now, we return the raw information for the LLM to interpret.
        "information": "\n\n".join(all_content),
        # "\n\n".join(): Combines all content with blank lines between
        # Why join: Creates a single readable text block
        
        "sources": sources,
        # sources: List of dicts with title and URL
        
        "guidance": "The above information should help identify the AHJ. "
                   "Look for mentions of 'City of...', 'County of...', "
                   "'[City Name] Planning Department', or similar."
        # guidance: Instructions for the LLM on how to interpret the data
        # Why include: Helps LLM focus on relevant information
    }
    # In the next reasoning step, the agent will:
    # 1. Read the "information" field
    # 2. Extract the AHJ name (e.g., "City of Johnson City")
    # 3. Use that name in subsequent tool calls


# ==============================================================================
# Tool 2: Get Development Regulations
# ==============================================================================
def get_development_regulations(ahj_name: str) -> Dict[str, Any]:
    """
    Retrieve development regulations and requirements for a specific AHJ.
    
    This tool searches for information about zoning, permits, site plan review,
    and fees associated with land development in the AHJ's jurisdiction.
    
    Function Name Explanation:
    - "get_development_regulations": "get" implies retrieval, "development_regulations" is specific
    - Why not "get_regulations": Too generic; could mean any type of regulations
    - Why "development": Aligns with user's domain (land development)
    
    Args:
        ahj_name (str): Name of the AHJ (e.g., "City of Johnson City", "Washington County", "Raleigh").
            Can include "City of" or "County of" prefix.
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - status: "success" or "error"
            - ahj_name: The AHJ that was searched
            - regulations: Information about regulations
            - sources: Where information was found
            - topics_covered: List of regulation topics found
    
    Information Typically Found:
    - Zoning requirements
    - Permit application processes
    - Site plan review requirements
    - Development fees and schedules
    - Design standards
    - Utility connection requirements
    
    Why This Tool Is Important:
    - Due Diligence: Developers need to know regulations before starting
    - Cost Estimation: Fees vary significantly by AHJ
    - Timeline: Different AHJs have different approval processes
    - Compliance: Must follow local regulations
    """
    
    # Input validation
    if not ahj_name or not ahj_name.strip():
        return {
            "status": "error",
            "error": "AHJ name cannot be empty",
            "ahj_name": ahj_name
        }
    
    # Construct search queries for different types of regulations
    # Why multiple queries: Different information might be on different pages
    queries = [
        # Query 1: Site plan review (common requirement)
        f"{ahj_name} site plan review requirements checklist",
        # "site plan review": Standard land development process
        # "checklist": Often provides comprehensive lists of requirements
        
        # Query 2: Development fees
        f"{ahj_name} land development fees schedule",
        # "fees schedule": Often a published document with all fees
        
        # Query 3: Zoning regulations
        f"{ahj_name} zoning ordinance land development code",
        # "ordinance": Legal document with regulations
        # "land development code": Comprehensive regulation document
    ]
    # Why these specific queries:
    # - Based on common documents AHJs publish
    # - Target the specific information developers need
    # - Use terminology that appears in official documents
    
    # Store results from all queries
    all_information = []  # List to hold content from all searches
    all_sources = []      # List to hold all source URLs
    
    # Execute each search query
    # Why loop: We want to search multiple topics
    for query in queries:
        # query: One of our search queries
        
        # Perform the search
        # max_results=3: Fewer results per query since we have multiple queries
        # Total results: 3 queries × 3 results = 9 pieces of information
        search_result = web_search(query=query, max_results=3)
        
        # Check if search succeeded
        if search_result["status"] == "success":
            # Extract results from this search
            results = search_result.get("results", [])
            
            # Process each result
            for result in results:
                content = result.get("content", "")
                
                if content:  # Only include non-empty content
                    # Add content with a header showing which query it came from
                    # Why header: Helps LLM understand context of each piece
                    all_information.append(f"[From query: {query}]\n{content}")
                    
                    # Track the source
                    all_sources.append({
                        "query": query,  # Which query found this
                        "title": result.get("title", ""),
                        "url": result.get("url", "")
                    })
    
    # Check if we found any information
    if not all_information:
        return {
            "status": "error",
            "error": f"No regulation information found for {ahj_name}",
            "ahj_name": ahj_name,
            "searched_queries": queries  # Show what we tried
        }
    
    # Identify topics covered
    # This helps the agent understand what information is available
    topics_covered = []
    # List of topics we successfully found information about
    
    # Check for keywords to identify topics
    # Why keywords: Quick way to categorize information
    combined_content = " ".join(all_information).lower()
    # combined_content: All content as one lowercase string
    # Why lowercase: Makes keyword matching case-insensitive
    
    # Check for different topic keywords
    if "site plan" in combined_content:
        topics_covered.append("Site Plan Review")
    if "fee" in combined_content or "cost" in combined_content:
        topics_covered.append("Fees and Costs")
    if "zoning" in combined_content:
        topics_covered.append("Zoning Regulations")
    if "permit" in combined_content:
        topics_covered.append("Permits")
    if "utility" in combined_content or "water" in combined_content:
        topics_covered.append("Utility Requirements")
    # Why check for keywords: Helps agent know what information is available
    # Could add more keywords based on common topics
    
    # Return structured response
    return {
        "status": "success",
        "ahj_name": ahj_name,
        "information": "\n\n---\n\n".join(all_information),
        # Separates different pieces with "---" for readability
        "sources": all_sources,
        "topics_covered": topics_covered,
        "total_sources": len(all_sources)
        # Metadata about the response
    }
    # The agent will use this information to:
    # 1. Understand AHJ requirements
    # 2. Answer questions about regulations
    # 3. Provide accurate fee estimates
    # 4. Identify required permits


# ==============================================================================
# Why Two Separate Tools Instead of One Combined Tool?
# ==============================================================================
# Design Decision Explanation:
#
# Option 1: Combined tool "get_ahj_information(location)"
#   - Pro: One call does everything
#   - Con: Always retrieves all information (slow, expensive)
#   - Con: Less flexible for agent's reasoning
#
# Option 2: Separate tools (current design)
#   - Pro: Agent can choose what it needs
#   - Pro: Faster when only AHJ name is needed
#   - Pro: Follows single responsibility principle
#   - Pro: Easier to test and maintain
#
# Real-world scenario:
# - User: "Find gas provider for Johnson City, TN"
# - With combined: Agent must get AHJ + all regulations (unnecessary)
# - With separate: Agent only calls identify_ahj(), skips regulations
#
# Conclusion: Separate tools provide better modularity and efficiency

