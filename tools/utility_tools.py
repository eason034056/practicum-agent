"""
Utility Provider Identification Tools

This module provides tools for identifying utility service providers
(gas, electric, water, sewer, stormwater) for specific locations.

Why These Tools Are Critical:
- Utility identification is the core purpose of this agent
- Each utility type requires different providers
- Contact information and connection requirements vary by provider
- Accurate information prevents project delays and cost overruns

Utility Types Covered:
1. Gas Provider: Natural gas service (e.g., Nicor Gas, Dominion Energy)
2. Electric Provider: Electrical service (e.g., ComEd, Duke Energy)
3. Water Provider: Potable water service (municipal or private)
4. Sewer Provider: Wastewater service (municipal or private)
5. Stormwater Authority: Stormwater management and drainage

Key Insight: Most locations have ONE provider per utility type
- Why: Utilities are natural monopolies (infrastructure intensive)
- Exception: Some areas have choice for electric/gas (deregulation)
- Implication: Agent should find THE provider, not multiple options
"""

# Type hints for better code quality
from typing import Dict, List, Any, Optional

# Import search functionality
from tools.search_tools import search_with_context, google_search_grounding


# ==============================================================================
# PATTERN: Utility Provider Search Functions
# ==============================================================================
# The following functions follow a consistent pattern:
# 1. search_[utility_type]_provider(location) -> Provider info
# 2. Similar structure, different search queries
# 3. Why pattern: Consistency helps LLM understand and choose tools
#
# Each function:
# - Takes location as input
# - Constructs specific search query
# - Returns structured provider information
# - Includes error handling
#
# This pattern makes the code:
# - Predictable: Easy to understand and maintain
# - Testable: Same test structure for all
# - Extensible: Easy to add new utility types


# ==============================================================================
# Tool 1: Search Gas Provider
# ==============================================================================
def search_gas_provider(location: str) -> Dict[str, Any]:
    """
    Identify the natural gas utility provider for a specific location.
    
    Gas utilities are typically regional monopolies. One provider serves
    each geographic area. This function identifies which company provides
    natural gas service to the specified location.
    
    Function Name Explanation:
    - "search_gas_provider": Clear action (search) + specific target (gas provider)
    - Why "search": Implies active information retrieval
    - Why "gas_provider": Specific and unambiguous (not "gas company" or "gas utility")
    - Why singular "provider": Usually one provider per area
    
    Args:
        location (str): Geographic location (e.g., "Johnson City, TN", 
            "123 Main Street, Raleigh, NC", or "Durham County, North Carolina").
            Any readable location description.
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - status: "success" or "error"
            - location: Echo of input location
            - provider_type: "gas" (for consistency)
            - information: Text about the gas provider
            - sources: URLs where information was found
        
        Information typically includes:
        - Provider name (e.g., "Dominion Energy")
        - Service area
        - Contact information
        - Website
        - Service availability
    
    Example Return Value:
        {
            "status": "success",
            "location": "Johnson City, TN",
            "provider_type": "gas",
            "information": "Dominion Energy provides natural gas service...",
            "sources": [{"title": "...", "url": "..."}]
        }
    
    Common Gas Providers in US:
    - Nicor Gas (Illinois)
    - Dominion Energy (Multiple states)
    - National Grid (Northeast)
    - Southern California Gas
    - Con Edison (New York)
    """
    
    # Input validation
    # Why validate: Prevents errors and provides clear feedback
    if not location or not location.strip():
        # Check for empty or whitespace-only input
        return {
            "status": "error",
            "error": "Location cannot be empty",
            "location": location,
            "provider_type": "gas"
        }
        # Early return pattern (guard clause)
    
    # Construct search query for gas provider
    # Query design principles:
    # 1. Include utility type: "natural gas"
    # 2. Include what we want: "provider", "utility", "company"
    # 3. Include location: {location}
    # 4. Optional: "service area" helps find coverage maps
    query = f"natural gas utility provider company serving {location}"
    # Query components:
    # - "natural gas": Specifies the utility type
    # - "utility provider company": Multiple synonyms increase recall
    # - "serving": Indicates we want the active service provider
    # - "{location}": The specific area we're interested in
    
    # Alternative query patterns (for future enhancement):
    # - f"who provides natural gas service in {location}"
    # - f"{location} gas utility company"
    # - f"natural gas service area {location}"
    
    # Perform web search
    # max_results=8: Get multiple sources for validation
    # Why 8: Google snippets are short (~160 chars), need more sources to find contact details
    # Balance between thoroughness and API cost/time
    search_result = google_search_grounding(query=query, max_results=8)
    # search_result: Dict with status, query, results, or error
    
    # Check if search was successful
    if search_result["status"] != "success":
        # Search failed - return error with details
        return {
            "status": "error",
            "error": f"Failed to search for gas provider: {search_result.get('error', 'Unknown error')}",
            # Include original error message for debugging
            "location": location,
            "provider_type": "gas"
        }
    
    # Extract results from search
    results = search_result.get("results", [])
    # .get("results", []): Safe access with empty list default
    
    # Check if we got results
    if not results:
        # No results found
        return {
            "status": "error",
            "error": f"No gas provider information found for {location}",
            "location": location,
            "provider_type": "gas"
        }
    
    # Compile information from all results
    # Why compile: Multiple sources provide more complete picture
    all_content = []  # List to store content from each result
    sources = []      # List to track sources
    
    # Process each search result
    for result in results:
        # result: One search result dict with title, url, content, score
        
        content = result.get("content", "")
        # Get the content (text snippet) from this result
        
        if content:  # Only include non-empty content
            all_content.append(content)
            # Add to our compilation
            
            sources.append({
                "title": result.get("title", ""),
                "url": result.get("url", "")
            })
            # Track source for citation and verification
    
    # Return structured response
    return {
        "status": "success",
        "location": location,
        "provider_type": "gas",
        "information": "\n\n".join(all_content),
        # Join all content with blank lines between for readability
        # The LLM will parse this to extract provider name and details
        "sources": sources,
        # List of source dicts for grounding/verification
        "result_count": len(sources)
        # How many sources we found (metadata)
    }
    # The agent will read "information" field and extract:
    # - Provider name
    # - Contact information
    # - Service details


# ==============================================================================
# Tool 2: Search Electric Provider
# ==============================================================================
def search_electric_provider(location: str) -> Dict[str, Any]:
    """
    Identify the electric utility provider for a specific location.
    
    Electric utilities are typically regional monopolies, though some states
    have deregulated markets with multiple suppliers. This function identifies
    the distribution utility (infrastructure owner) for the location.
    
    Function Name Explanation:
    - "search_electric_provider": Parallel structure to gas provider
    - "electric": Clearly distinguishes from other utilities
    - Why not "electricity": "electric" is more commonly used in utility context
    
    Args:
        location (str): Geographic location
    
    Returns:
        Dict[str, Any]: Same structure as gas provider
            - Consistency: Agent can handle all utility types similarly
    
    Common Electric Providers in US:
    - Duke Energy (Southeast)
    - ComEd (Illinois)
    - PG&E (California)
    - Con Edison (New York)
    - Florida Power & Light
    
    Note on Deregulated Markets:
    - Some states allow choice of electricity supplier
    - But distribution utility (poles/wires) is still monopoly
    - This function finds the distribution utility
    """
    
    # Input validation (same pattern as gas)
    if not location or not location.strip():
        return {
            "status": "error",
            "error": "Location cannot be empty",
            "location": location,
            "provider_type": "electric"
        }
    
    # Construct search query for electric provider
    query = f"electric utility provider company serving {location}"
    # Similar pattern to gas query but with "electric"
    # Why consistent pattern: Helps with code maintainability
    
    # Perform search
    # max_results=8: Google snippets are short, need more sources for contact details
    search_result = google_search_grounding(query=query, max_results=8)
    
    # Error handling
    if search_result["status"] != "success":
        return {
            "status": "error",
            "error": f"Failed to search for electric provider: {search_result.get('error', 'Unknown error')}",
            "location": location,
            "provider_type": "electric"
        }
    
    # Extract and process results
    results = search_result.get("results", [])
    
    if not results:
        return {
            "status": "error",
            "error": f"No electric provider information found for {location}",
            "location": location,
            "provider_type": "electric"
        }
    
    # Compile information
    all_content = []
    sources = []
    
    for result in results:
        content = result.get("content", "")
        if content:
            all_content.append(content)
            sources.append({
                "title": result.get("title", ""),
                "url": result.get("url", "")
            })
    
    # Return structured response
    return {
        "status": "success",
        "location": location,
        "provider_type": "electric",
        "information": "\n\n".join(all_content),
        "sources": sources,
        "result_count": len(sources)
    }


# ==============================================================================
# Tool 3: Search Water Provider
# ==============================================================================
def search_water_provider(location: str) -> Dict[str, Any]:
    """
    Identify the water utility provider for a specific location.
    
    Water utilities can be:
    - Municipal (city-operated)
    - County-operated
    - Private utility company
    - Water district
    
    This function identifies which entity provides potable water service.
    
    Function Name Explanation:
    - "search_water_provider": Consistent with other utilities
    - "water": Distinguishes from wastewater/sewer
    
    Args:
        location (str): Geographic location
    
    Returns:
        Dict[str, Any]: Standard utility provider response structure
    
    Water vs. Sewer:
    - Often same provider, but not always
    - Water = incoming clean water
    - Sewer = outgoing wastewater
    - Must search for each separately
    """
    
    # Input validation
    if not location or not location.strip():
        return {
            "status": "error",
            "error": "Location cannot be empty",
            "location": location,
            "provider_type": "water"
        }
    
    # Construct search query
    # Note: Include "drinking water" and "potable" as alternatives
    query = f"water utility provider serving {location} drinking water"
    # "drinking water": Clarifies we want potable water (not wastewater)
    # Why important: Disambiguates from sewer/wastewater searches
    
    # Perform search
    # max_results=8: Google snippets are short, need more sources for contact details
    search_result = google_search_grounding(query=query, max_results=8)
    
    # Error handling
    if search_result["status"] != "success":
        return {
            "status": "error",
            "error": f"Failed to search for water provider: {search_result.get('error', 'Unknown error')}",
            "location": location,
            "provider_type": "water"
        }
    
    # Extract and process results
    results = search_result.get("results", [])
    
    if not results:
        return {
            "status": "error",
            "error": f"No water provider information found for {location}",
            "location": location,
            "provider_type": "water"
        }
    
    # Compile information
    all_content = []
    sources = []
    
    for result in results:
        content = result.get("content", "")
        if content:
            all_content.append(content)
            sources.append({
                "title": result.get("title", ""),
                "url": result.get("url", "")
            })
    
    # Return structured response
    return {
        "status": "success",
        "location": location,
        "provider_type": "water",
        "information": "\n\n".join(all_content),
        "sources": sources,
        "result_count": len(sources)
    }


# ==============================================================================
# Tool 4: Search Sewer Provider
# ==============================================================================
def search_sewer_provider(location: str) -> Dict[str, Any]:
    """
    Identify the sewer/wastewater utility provider for a specific location.
    
    Sewer service handles wastewater treatment and disposal. Providers include:
    - Municipal sewer systems
    - County sewer districts
    - Regional wastewater authorities
    - Private systems (septic) in rural areas
    
    Function Name Explanation:
    - "search_sewer_provider": "sewer" is more common term than "wastewater"
    - Parallel structure with other utilities
    
    Args:
        location (str): Geographic location
    
    Returns:
        Dict[str, Any]: Standard utility provider response structure
    
    Special Considerations:
    - Rural areas may not have sewer (septic systems instead)
    - Some areas use regional wastewater authorities
    - Connection requirements vary significantly
    """
    
    # Input validation
    if not location or not location.strip():
        return {
            "status": "error",
            "error": "Location cannot be empty",
            "location": location,
            "provider_type": "sewer"
        }
    
    # Construct search query
    query = f"sewer wastewater utility provider serving {location}"
    # Include both "sewer" and "wastewater" to maximize recall
    # Why both terms: Different authorities use different terminology
    
    # Perform search
    # max_results=8: Google snippets are short, need more sources for contact details
    search_result = google_search_grounding(query=query, max_results=8)
    
    # Error handling
    if search_result["status"] != "success":
        return {
            "status": "error",
            "error": f"Failed to search for sewer provider: {search_result.get('error', 'Unknown error')}",
            "location": location,
            "provider_type": "sewer"
        }
    
    # Extract and process results
    results = search_result.get("results", [])
    
    if not results:
        return {
            "status": "error",
            "error": f"No sewer provider information found for {location}",
            "location": location,
            "provider_type": "sewer"
        }
    
    # Compile information
    all_content = []
    sources = []
    
    for result in results:
        content = result.get("content", "")
        if content:
            all_content.append(content)
            sources.append({
                "title": result.get("title", ""),
                "url": result.get("url", "")
            })
    
    # Return structured response
    return {
        "status": "success",
        "location": location,
        "provider_type": "sewer",
        "information": "\n\n".join(all_content),
        "sources": sources,
        "result_count": len(sources)
    }


# ==============================================================================
# Tool 5: Search Stormwater Authority
# ==============================================================================
def search_stormwater_authority(location: str) -> Dict[str, Any]:
    """
    Identify the stormwater management authority for a specific location.
    
    Stormwater authorities regulate:
    - Stormwater runoff from developed sites
    - Detention/retention requirements
    - Drainage permits
    - Water quality protection
    
    Unlike other utilities, stormwater is often managed by:
    - Municipal engineering/public works departments
    - Regional water management districts
    - County drainage departments
    - State environmental agencies
    
    Function Name Explanation:
    - "search_stormwater_authority": "authority" instead of "provider"
    - Why "authority": Stormwater is regulatory, not a service like gas/water
    - Why "stormwater": Standard term in civil engineering and land development
    
    Args:
        location (str): Geographic location
    
    Returns:
        Dict[str, Any]: Similar structure but with "authority" language
            - provider_type: "stormwater" for consistency
            - but referred to as "authority" in content
    
    Special Considerations:
    - Stormwater regulations vary widely by jurisdiction
    - Some areas require onsite detention, others allow offsite
    - Fees and requirements depend on development size/type
    """
    
    # Input validation
    if not location or not location.strip():
        return {
            "status": "error",
            "error": "Location cannot be empty",
            "location": location,
            "provider_type": "stormwater"
        }
    
    # Construct search query
    query = f"stormwater management authority regulations {location}"
    # "management authority": More appropriate than "provider" for stormwater
    # "regulations": Indicates we want regulatory information
    # Why different pattern: Stormwater is regulatory, not service-oriented
    
    # Perform search
    # max_results=8: Google snippets are short, need more sources for contact details
    search_result = google_search_grounding(query=query, max_results=8)
    
    # Error handling
    if search_result["status"] != "success":
        return {
            "status": "error",
            "error": f"Failed to search for stormwater authority: {search_result.get('error', 'Unknown error')}",
            "location": location,
            "provider_type": "stormwater"
        }
    
    # Extract and process results
    results = search_result.get("results", [])
    
    if not results:
        return {
            "status": "error",
            "error": f"No stormwater authority information found for {location}",
            "location": location,
            "provider_type": "stormwater"
        }
    
    # Compile information
    all_content = []
    sources = []
    
    for result in results:
        content = result.get("content", "")
        if content:
            all_content.append(content)
            sources.append({
                "title": result.get("title", ""),
                "url": result.get("url", "")
            })
    
    # Return structured response
    return {
        "status": "success",
        "location": location,
        "provider_type": "stormwater",
        "authority_type": "stormwater_management",  # Additional field
        "information": "\n\n".join(all_content),
        "sources": sources,
        "result_count": len(sources)
    }


# ==============================================================================
# Tool 6: Get Utility Contact Information
# ==============================================================================
def get_utility_contact_info(
    provider_name: str,
    utility_type: str
) -> Dict[str, Any]:
    """
    Retrieve detailed contact information for a specific utility provider.
    
    After identifying a provider, this tool gets specific contact details:
    - Main phone number
    - Customer service phone
    - New service connection department
    - Email addresses
    - Physical address
    - Website
    - Office hours
    
    Function Name Explanation:
    - "get_utility_contact_info": "get" implies retrieval of specific data
    - "utility_contact_info": Specific enough to be clear
    - Why not "get_contact": Need to specify it's utility contact info
    
    Args:
        provider_name (str): Name of the utility provider 
            (e.g., "Duke Energy", "City of Raleigh Water Utility")
        utility_type (str): Type of utility 
            ("gas", "electric", "water", "sewer", or "stormwater")
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - status: "success" or "error"
            - provider_name: Echo of input
            - utility_type: Echo of input
            - contact_information: Structured contact details
            - sources: Where information was found
    
    Use Case:
        Agent: [search_gas_provider("Johnson City") returns "Dominion Energy"]
        Agent: [Call get_utility_contact_info("Dominion Energy", "gas")]
        Result: Phone numbers, address, website for gas department
    """
    
    # Input validation
    if not provider_name or not provider_name.strip():
        return {
            "status": "error",
            "error": "Provider name cannot be empty",
            "provider_name": provider_name,
            "utility_type": utility_type
        }
    
    if not utility_type or not utility_type.strip():
        return {
            "status": "error",
            "error": "Utility type cannot be empty",
            "provider_name": provider_name,
            "utility_type": utility_type
        }
    
    # Construct search query for contact information
    # Include multiple relevant terms to get comprehensive results
    query = f"{provider_name} {utility_type} customer service contact phone number address"
    # Query components:
    # - provider_name: The specific company/organization
    # - utility_type: The specific utility (helps with multi-utility companies)
    # - "customer service": Common department name
    # - "contact phone number address": Specific information we want
    
    # Perform search
    # max_results=8: Google snippets are short, need more sources for contact details
    search_result = google_search_grounding(query=query, max_results=8)
    
    # Error handling
    if search_result["status"] != "success":
        return {
            "status": "error",
            "error": f"Failed to search for contact info: {search_result.get('error', 'Unknown error')}",
            "provider_name": provider_name,
            "utility_type": utility_type
        }
    
    # Extract results
    results = search_result.get("results", [])
    
    if not results:
        return {
            "status": "error",
            "error": f"No contact information found for {provider_name}",
            "provider_name": provider_name,
            "utility_type": utility_type
        }
    
    # Compile contact information
    all_content = []
    sources = []
    
    for result in results:
        content = result.get("content", "")
        if content:
            all_content.append(content)
            sources.append({
                "title": result.get("title", ""),
                "url": result.get("url", "")
            })
    
    # Return structured response
    return {
        "status": "success",
        "provider_name": provider_name,
        "utility_type": utility_type,
        "contact_information": "\n\n".join(all_content),
        "sources": sources,
        "guidance": "Look for: phone numbers, addresses, email, website, department names, office hours"
        # Guidance helps LLM extract relevant details
    }


# ==============================================================================
# Tool 7: Get Connection Requirements
# ==============================================================================
def get_connection_requirements(provider_name: str) -> Dict[str, Any]:
    """
    Retrieve utility connection requirements and process for a provider.
    
    This tool finds information about:
    - New service application process
    - Required forms and documents
    - Fees (connection fees, tap fees, impact fees)
    - Timeline for connection
    - Technical requirements (pipe sizes, equipment specs)
    - Engineering approval process
    
    Function Name Explanation:
    - "get_connection_requirements": Specific to new connections
    - "connection": Standard term in utility industry
    - "requirements": Implies process, fees, and specifications
    - Why not "get_setup": "connection" is more precise industry term
    
    Args:
        provider_name (str): Name of the utility provider (e.g., "Raleigh Water Utility")
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - status: "success" or "error"
            - provider_name: Echo of input
            - requirements: Information about connection process
            - sources: Where information was found
    
    Typical Requirements Found:
    - Application forms
    - Engineering review fees
    - Connection/tap fees
    - Required documentation (surveys, plans, permits)
    - Timeline estimates
    - Contact person for new connections
    
    Use Case:
        Developer: "What's required to connect to water in Raleigh?"
        Agent: [Call get_connection_requirements("Raleigh Water Utility")]
        Result: Application process, $15,000 tap fee, engineering review steps
    """
    
    # Input validation
    if not provider_name or not provider_name.strip():
        return {
            "status": "error",
            "error": "Provider name cannot be empty",
            "provider_name": provider_name
        }
    
    # Construct search query for connection requirements
    query = f"{provider_name} new service connection application requirements fees process"
    # Query components:
    # - provider_name: The specific utility
    # - "new service connection": Standard term for new utility hookup
    # - "application": Looking for forms and procedures
    # - "requirements": Looking for what's needed
    # - "fees": Important cost information
    # - "process": Looking for step-by-step procedures
    
    # Perform search
    # max_results=8: Google snippets are short, need more sources for contact details
    search_result = google_search_grounding(query=query, max_results=8)
    
    # Error handling
    if search_result["status"] != "success":
        return {
            "status": "error",
            "error": f"Failed to search for requirements: {search_result.get('error', 'Unknown error')}",
            "provider_name": provider_name
        }
    
    # Extract results
    results = search_result.get("results", [])
    
    if not results:
        return {
            "status": "error",
            "error": f"No connection requirements found for {provider_name}",
            "provider_name": provider_name
        }
    
    # Compile requirements information
    all_content = []
    sources = []
    
    for result in results:
        content = result.get("content", "")
        if content:
            all_content.append(content)
            sources.append({
                "title": result.get("title", ""),
                "url": result.get("url", "")
            })
    
    # Return structured response
    return {
        "status": "success",
        "provider_name": provider_name,
        "requirements": "\n\n".join(all_content),
        "sources": sources,
        "guidance": "Look for: application forms, fees, required documents, timeline, technical specs, approval process"
    }


# ==============================================================================
# Design Patterns and Principles Used
# ==============================================================================
#
# 1. Consistent Function Signatures
#    - All provider search functions take (location: str)
#    - All return Dict[str, Any]
#    - Why: Predictable interface for LLM and developers
#
# 2. Structured Return Values
#    - Always include "status" field
#    - Always include original input parameters
#    - Always include "sources" for grounding
#    - Why: Enables reliable parsing and error handling
#
# 3. Descriptive Function Names
#    - Action verb + specific target
#    - Example: search_gas_provider (not get_gas or find_utility)
#    - Why: LLM can match function to intent
#
# 4. Comprehensive Docstrings
#    - What the function does
#    - Why it's named that way
#    - Parameter explanations
#    - Return value structure
#    - Example use cases
#    - Why: LLM uses these to decide when to call function
#
# 5. Defensive Programming
#    - Input validation
#    - Error handling (try/except in google_search_grounding)
#    - Graceful failures with clear error messages
#    - Why: Production reliability
#
# 6. DRY Principle (Don't Repeat Yourself)
#    - Common logic in google_search_grounding()
#    - Similar pattern across all provider functions
#    - Why: Easier maintenance, consistent behavior
#
# 7. Single Responsibility
#    - Each function does ONE thing
#    - search_gas_provider ONLY searches for gas provider
#    - get_connection_requirements ONLY gets requirements
#    - Why: Modularity, testability, clarity

