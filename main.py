"""
Main Entry Point for Utility Identification AI Agent

This is the main script to run the agent.

Usage:
    python main.py --location "Johnson City, TN"
    python main.py --location "Raleigh, NC" --verbose
    python main.py --interactive

Why This File:
- Single entry point for the application
- Command-line interface for users
- Handles argument parsing
- Provides different modes (single query, interactive, API)
"""

# Standard library imports
import argparse
# argparse: Parse command-line arguments
# Why: User-friendly CLI interface

import sys
# sys: System-specific parameters and functions
# Why: Access to stdin, stdout, exit codes

import json
# json: JSON encoding/decoding
# Why: Pretty-print results

from typing import Optional
# Optional: Type hint for optional parameters

# Import our agent
from agent import create_utility_agent
# create_utility_agent: Function that builds the agent graph

from agent.state import create_initial_state
# create_initial_state: Factory for initial state

from agent.graph import run_agent
# run_agent: Convenience function to run agent

# Import settings
from config.settings import settings

# Import search tools for demo
from tools.search_tools import combined_web_search, google_search_grounding
# settings: Configuration access


# ==============================================================================
# Main Execution Functions
# ==============================================================================

def run_single_query(location: str, verbose: bool = False) -> None:
    """
    Run a single query and print the result.
    
    Function Name: "run_single_query"
    - "run": Indicates execution
    - "single_query": One-time execution (vs. interactive)
    - Why: Handles command-line single query mode
    
    Args:
        location (str): Location to search
            - Example: "Johnson City, TN"
            - What user wants to search for
            
        verbose (bool): Whether to print detailed information
            - Default: False (only show final answer)
            - True: Show all steps, tool calls, etc.
    
    Returns:
        None (prints to console)
    
    Process:
    1. Print what we're doing
    2. Run the agent
    3. Print results (brief or detailed)
    """
    
    # Print header
    # Why: User feedback that processing started
    print("\n" + "=" * 80)
    # "=" * 80: Creates a line of 80 equal signs
    # Why 80: Standard terminal width
    
    print(f"🚀 UTILITY IDENTIFICATION AGENT - STARTING")
    # f-string: String with embedded variables
    print("=" * 80)
    print(f"📍 Location Query: {location}")
    # Show user what location we're searching
    print(f"🤖 Agent Mode: ReAct (Reason + Act + Observe)")
    print(f"🔄 Max Iterations: {settings.max_iterations}")
    print("=" * 80)
    print()  # Blank line
    
    # Run the agent
    # run_agent: Function from agent.graph
    # Returns: Final state dict
    print("🔍 Starting agent execution...")
    print("   The agent will now begin its reasoning process.")
    print("   You will see detailed logs of each step below.")
    print("   (This may take 30-60 seconds depending on complexity)")
    # Why message: Sets expectations (web searches take time)
    print()
    
    try:
        # try block: Catch any errors during execution
        # Why: Provide user-friendly error messages
        
        print("="*80)
        print("🎬 INITIALIZING AGENT GRAPH")
        print("="*80)
        print("Function: run_agent()")
        print("Purpose: Create initial state and invoke agent graph")
        print("-"*80 + "\n")
        
        result = run_agent(f"Find all utility providers for {location}")
        # run_agent: Convenience function that handles state creation
        # f-string: Constructs query
        # result: Final state after agent execution
        
        print("="*80)
        print("🎉 AGENT EXECUTION COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"Total Reasoning Iterations: {result.get('iterations', 0)}")
        print(f"Total Messages Exchanged: {len(result.get('messages', []))}")
        print("="*80 + "\n")
        
    except Exception as e:
        # Exception occurred during agent execution
        # e: Exception object with details
        
        # Print error message
        print("❌ Error occurred:")
        print(f"  {str(e)}")
        # str(e): Convert exception to string
        
        # Exit with error code
        sys.exit(1)
        # sys.exit(1): Exit program with code 1 (indicates error)
        # Why 1: Unix convention (0 = success, non-zero = error)
        return  # Won't reach here, but good practice
    
    # Print results
    print("\n" + "=" * 80)
    # \n: Newline before separator
    print("RESULTS")
    print("=" * 80 + "\n")
    
    # Print final answer
    # result["output"]: Final answer from agent
    print(result.get("output", "No output generated"))
    # .get("output", "..."): Safe access with default
    # Why safe access: Handles case where output key missing
    
    # Print additional details if verbose
    if verbose:
        # verbose: User requested detailed information
        # Show all the behind-the-scenes data
        
        print("\n" + "-" * 80)
        print("DETAILED INFORMATION")
        print("-" * 80)
        
        # Show identified AHJ
        print(f"\nAHJ: {result.get('identified_ahj', 'Not identified')}")
        # Why show: Helps user verify correctness
        
        # Show number of iterations
        print(f"Reasoning iterations: {result.get('iterations', 0)}")
        # Why show: Indicates agent efficiency
        
        # Show gathered providers
        print("\nGathered Information:")
        
        # Gas provider
        if result.get("gas_provider"):
            print(f"  ✓ Gas Provider")
            # ✓: Checkmark indicates found
        
        # Electric provider
        if result.get("electric_provider"):
            print(f"  ✓ Electric Provider")
        
        # Water provider
        if result.get("water_provider"):
            print(f"  ✓ Water Provider")
        
        # Sewer provider
        if result.get("sewer_provider"):
            print(f"  ✓ Sewer Provider")
        
        # Stormwater authority
        if result.get("stormwater_authority"):
            print(f"  ✓ Stormwater Authority")
        
        # Show message count
        print(f"\nTotal messages: {len(result.get('messages', []))}")
        # len(result.get('messages', [])): Count of messages
        # Why show: Indicates conversation length
    
    print("\n" + "=" * 80)


def demo_combined_search(query: str) -> None:
    """
    Demonstrate the combined search functionality (Tavily + Google).
    
    This function showcases how to use the combined_web_search function
    which queries both Tavily and Google simultaneously and displays
    their results side-by-side for comparison.
    
    Function Name Explanation:
    - "demo_combined_search": Clearly indicates this is a demonstration
    - "combined_search": Refers to using multiple search engines together
    - Why demo: Educational function to show how the feature works
    
    What This Demo Does:
    1. Calls combined_web_search with a query
    2. Displays results from both search engines
    3. Shows the comparison and summary
    4. Helps users understand the benefits of multi-source search
    
    Args:
        query (str): The search query to test
            Example: "Johnson City TN gas utility provider"
    
    Returns:
        None (prints results to console)
    
    How to Use This Function:
        python main.py --demo "your search query"
    
    Example Output:
        Shows:
        - Summary of both searches
        - Tavily results (with scores)
        - Google results (with snippets)
        - Comparison of result counts
        - Total execution time
    """
    
    # Print header
    # Why: Visual separation and clear indication of what's happening
    print("\n" + "=" * 80)
    # "=" * 80: Creates a line of 80 equal signs
    print("🔍 COMBINED SEARCH DEMO - TAVILY + GOOGLE")
    # 🔍: Magnifying glass emoji for search
    print("=" * 80)
    print(f"📝 Query: {query}")
    # 📝: Notepad emoji to indicate input
    print("=" * 80 + "\n")
    
    # Import time module to measure execution time
    # Why: Show users how parallel execution is faster
    import time
    # time: Module for time-related functions
    
    # Record start time
    # time.time(): Returns current time in seconds since epoch (Jan 1, 1970)
    # Why measure: Demonstrates speed advantage of parallel execution
    start_time = time.time()
    # start_time: Timestamp when search started (float number)
    
    # Perform the combined search
    # combined_web_search: Function that searches both Tavily and Google
    # query: The search query to execute
    # max_results=5: Get 5 results from each source (10 total)
    print("🚀 Starting parallel search (Tavily + Google)...")
    print("   Both searches are running simultaneously...")
    print()
    # Why message: User feedback that process started
    
    try:
        # try block: Catch any errors during search
        # Why needed: API calls can fail for various reasons
        
        result = combined_web_search(query, max_results=5)
        # result: Dictionary containing results from both sources
        # Structure: {status, query, tavily, google, combined_results, summary}
        
    except Exception as e:
        # Exception occurred during search
        # e: Exception object with error details
        print(f"❌ Error during search: {str(e)}")
        # str(e): Converts exception to readable string
        return
        # Exit function early on error
    
    # Record end time
    # time.time(): Current timestamp
    end_time = time.time()
    # end_time: Timestamp when search completed
    
    # Calculate elapsed time
    # Why subtract: Difference gives time taken in seconds
    elapsed_time = end_time - start_time
    # elapsed_time: How long the search took (in seconds)
    
    # Print results
    print("=" * 80)
    print("✅ SEARCH COMPLETED")
    # ✅: Green checkmark emoji for success
    print("=" * 80)
    print(f"⏱️  Execution Time: {elapsed_time:.2f} seconds")
    # ⏱️: Stopwatch emoji for time
    # {elapsed_time:.2f}: Format to 2 decimal places (e.g., 2.35 seconds)
    # Why show time: Demonstrates efficiency of parallel execution
    print(f"📊 Overall Status: {result['status'].upper()}")
    # 📊: Chart emoji for status
    # .upper(): Converts to uppercase (SUCCESS, PARTIAL, ERROR)
    print(f"💬 Summary: {result['summary']}")
    # 💬: Speech bubble emoji for summary
    print("=" * 80 + "\n")
    
    # Display Tavily Results
    # Why separate section: Clear distinction between sources
    print("-" * 80)
    print("🟦 TAVILY RESULTS")
    # 🟦: Blue square to represent Tavily
    print("-" * 80)
    
    # Get Tavily results from the response
    # result["tavily"]: Dictionary with Tavily search results
    tavily_data = result.get("tavily", {})
    # .get("tavily", {}): Safe access with empty dict as default
    # tavily_data: Dictionary with status, results, count, etc.
    
    # Check if Tavily search succeeded
    if tavily_data.get("status") == "success":
        # Tavily search was successful
        # Why check: Only display results if search succeeded
        
        # Get the list of results
        tavily_results = tavily_data.get("results", [])
        # tavily_results: List of search result dictionaries
        
        print(f"✓ Found {len(tavily_results)} results\n")
        # len(tavily_results): Count of results
        # ✓: Checkmark indicates success
        
        # Display each result
        # enumerate(): Returns index and item from list
        # enumerate(list, start=1): Start counting from 1 instead of 0
        for idx, item in enumerate(tavily_results, start=1):
            # idx: Result number (1, 2, 3, ...)
            # item: One search result dictionary
            
            print(f"{idx}. {item.get('title', 'N/A')}")
            # f"{idx}. ": Numbered list (1. , 2. , 3. ...)
            # item.get('title', 'N/A'): Get title, default to "N/A"
            
            print(f"   URL: {item.get('url', 'N/A')}")
            # "   ": Indentation for better readability
            
            print(f"   Score: {item.get('score', 0.0):.2f}")
            # item.get('score', 0.0): Relevance score (0.0 to 1.0)
            # {score:.2f}: Format to 2 decimal places
            # Why show score: Tavily provides relevance scores
            
            # Get content snippet
            content = item.get('content', 'N/A')
            # content: Text snippet from the page
            
            # Truncate content if too long
            # Why truncate: Keep console output readable
            if len(content) > 200:
                # Content is longer than 200 characters
                # Why 200: Good balance between info and readability
                content = content[:200] + "..."
                # [:200]: Take first 200 characters
                # + "...": Add ellipsis to indicate truncation
            
            print(f"   Content: {content}")
            # Display the content snippet
            print()
            # Blank line between results for readability
    
    else:
        # Tavily search failed
        # Why handle: Provide clear error message to user
        print(f"✗ Tavily search failed: {tavily_data.get('error', 'Unknown error')}")
        # ✗: X mark indicates failure
        # tavily_data.get('error', 'Unknown error'): Get error message
        print()
    
    # Display Google Results
    # Similar structure to Tavily section above
    print("-" * 80)
    print("🟥 GOOGLE RESULTS")
    # 🟥: Red square to represent Google
    print("-" * 80)
    
    # Get Google results from the response
    google_data = result.get("google", {})
    # google_data: Dictionary with Google search results
    
    # Check if Google search succeeded
    if google_data.get("status") == "success":
        # Google search was successful
        
        google_results = google_data.get("results", [])
        # google_results: List of search result dictionaries
        
        print(f"✓ Found {len(google_results)} results\n")
        
        # Display each result
        for idx, item in enumerate(google_results, start=1):
            # idx: Result number
            # item: One search result dictionary
            
            print(f"{idx}. {item.get('title', 'N/A')}")
            print(f"   URL: {item.get('url', 'N/A')}")
            print(f"   Domain: {item.get('displayLink', 'N/A')}")
            # displayLink: Domain name (e.g., "example.com")
            # Why show: Quick way to identify source
            
            # Get content/snippet
            # content: Text snippet from search result
            # Note: Now both Google and Tavily use "content" for consistency
            content = item.get('content', item.get('snippet', 'N/A'))
            # content: 搜索結果的文本片段
            # 字面意思：先嘗試獲取 'content' 字段，如果沒有則嘗試 'snippet'（向後兼容）
            # 為什麼這樣做：google_search_grounding() 現在返回 'content'，但為了兼容性也檢查 'snippet'
            
            # Truncate content if too long
            if len(content) > 200:
                content = content[:200] + "..."
            
            print(f"   Content: {content}")
            print()
    
    else:
        # Google search failed
        print(f"✗ Google search failed: {google_data.get('error', 'Unknown error')}")
        print()
    
    # Display comparison summary
    # Why: Helps user understand the value of multi-source search
    print("=" * 80)
    print("📈 COMPARISON SUMMARY")
    # 📈: Chart emoji for comparison
    print("=" * 80)
    
    # Count results from each source
    tavily_count = len(tavily_data.get("results", []))
    google_count = len(google_data.get("results", []))
    total_count = result.get("total_count", 0)
    # Get counts for comparison
    
    print(f"Tavily Results: {tavily_count}")
    print(f"Google Results: {google_count}")
    print(f"Total Unique Results: {total_count}")
    # Why show all three: Clear breakdown of information gathered
    
    print(f"\nExecution Time: {elapsed_time:.2f} seconds")
    # Remind user of execution time
    
    # Explain time savings
    # Why explain: Educational - shows benefit of parallel execution
    print("\n💡 Note: If these searches ran sequentially (one after another),")
    print("   the total time would be approximately the sum of both searches.")
    print("   Parallel execution saves time by running them simultaneously!")
    # Educational message about parallel execution benefits
    
    print("=" * 80 + "\n")
    # Final separator


def run_interactive_mode() -> None:
    """
    Run the agent in interactive mode (REPL).
    
    REPL: Read-Eval-Print Loop
    - Read: Get user input
    - Eval: Process with agent
    - Print: Show results
    - Loop: Repeat
    
    Function Name: "run_interactive_mode"
    - "interactive_mode": Continuous interaction with user
    - Why: Allows multiple queries without restarting
    
    Returns:
        None (runs until user exits)
    
    Process:
    1. Create agent once (reuse for all queries)
    2. Loop: Prompt → Run → Display → Repeat
    3. Exit on 'quit' or 'exit'
    """
    
    # Print welcome message
    print("=" * 80)
    print("Utility Identification Agent - Interactive Mode")
    print("=" * 80)
    print("\nEnter a location to search, or 'quit' to exit.")
    print("Example: Johnson City, TN")
    print()
    
    # Create agent once (reuse for multiple queries)
    # Why create once: More efficient than recreating each time
    agent = create_utility_agent()
    # agent: Compiled graph ready to invoke
    
    # Main loop
    # while True: Infinite loop (until break)
    while True:
        # Prompt for input
        # input(): Read from stdin
        # .strip(): Remove leading/trailing whitespace
        try:
            user_input = input("Enter location (or 'quit'): ").strip()
            # input(): Blocks until user presses Enter
            # .strip(): Clean up input
            
        except KeyboardInterrupt:
            # User pressed Ctrl+C
            # KeyboardInterrupt: Exception raised by Ctrl+C
            print("\n\nExiting...")
            break
            # break: Exit while loop
        
        except EOFError:
            # End of file (e.g., stdin closed)
            # EOFError: Raised when input() hits EOF
            print("\n\nExiting...")
            break
        
        # Check for exit commands
        # Why check: Provide way to exit
        if user_input.lower() in ["quit", "exit", "q"]:
            # .lower(): Case-insensitive comparison
            # ["quit", "exit", "q"]: Multiple exit options
            print("Goodbye!")
            break
        
        # Validate input
        if not user_input:
            # Empty input
            print("Please enter a location.")
            continue
            # continue: Skip to next iteration
        
        # Run agent
        print(f"\nSearching for utilities in {user_input}...")
        
        try:
            # Create initial state
            initial_state = create_initial_state(
                f"Find all utility providers for {user_input}"
            )
            # initial_state: Dict with user query
            
            # Run agent with increased recursion limit
            # recursion_limit: Maximum graph execution steps (default: 25, increased: 100)
            # Why increase: Complex utility queries need more reasoning steps
            result = agent.invoke(
                initial_state,
                config={"recursion_limit": 100}
            )
            # agent.invoke(): Execute graph with initial state
            # config: Configuration with recursion_limit
            # result: Final state
            
            # Display result
            print("\n" + "-" * 80)
            print(result.get("output", "No output generated"))
            print("-" * 80 + "\n")
            
        except Exception as e:
            # Error during execution
            print(f"\n❌ Error: {str(e)}\n")
            # Continue loop (don't exit on error)
            continue
    
    # Exited loop
    print("\nThank you for using the Utility Identification Agent!")


# ==============================================================================
# Command-Line Interface
# ==============================================================================

def parse_arguments():
    """
    Parse command-line arguments.
    
    Function Name: "parse_arguments"
    - Standard name for argument parsing function
    - Why: Encapsulates argparse logic
    
    Returns:
        argparse.Namespace: Parsed arguments
            - Access like: args.location, args.verbose
    
    Arguments Defined:
    - --location: Location to search
    - --verbose: Show detailed information
    - --interactive: Run in interactive mode
    """
    
    # Create argument parser
    # ArgumentParser: Class for CLI argument parsing
    parser = argparse.ArgumentParser(
        # prog: Program name (shown in help)
        prog="utility-agent",
        
        # description: What the program does
        description="AI Agent for identifying utility providers and regulatory information",
        
        # epilog: Text shown at end of help
        epilog="Example: python main.py --location 'Johnson City, TN'"
    )
    # parser: Configured argument parser
    
    # Add location argument
    # add_argument: Define a command-line argument
    parser.add_argument(
        # Argument name
        "--location",
        "-l",
        # --location: Long form
        # -l: Short form (user can use either)
        
        # Type
        type=str,
        # Argument value will be string
        
        # Required
        required=False,
        # Not required (because interactive mode doesn't need it)
        
        # Help text
        help="Location to search for utilities (e.g., 'Johnson City, TN')"
        # Shown in --help output
    )
    
    # Add verbose flag
    parser.add_argument(
        "--verbose",
        "-v",
        # Flag: No value needed (presence = True)
        
        action="store_true",
        # action="store_true": Argument is a boolean flag
        # If --verbose present: args.verbose = True
        # If --verbose absent: args.verbose = False
        
        help="Print detailed information"
    )
    
    # Add interactive mode flag
    parser.add_argument(
        "--interactive",
        "-i",
        
        action="store_true",
        
        help="Run in interactive mode (REPL)"
    )
    
    # Add demo mode argument
    # Why add: Allow users to test the combined search feature
    parser.add_argument(
        "--demo",
        "-d",
        # --demo: Long form
        # -d: Short form (quick to type)
        
        type=str,
        # Type: String (the search query)
        
        required=False,
        # Not required: This is an optional feature
        
        help="Run combined search demo with the provided query (e.g., 'OpenAI GPT-4')"
        # Help text: Explains what this flag does and gives example
    )
    # parser.add_argument: Registers a new command-line argument
    # After parsing, accessible as args.demo
    
    # Parse arguments
    # parse_args(): Parses sys.argv (command-line arguments)
    args = parser.parse_args()
    # args: Namespace object with parsed arguments
    # Access: args.location, args.verbose, args.interactive, args.demo
    
    return args
    # Return parsed arguments


def main() -> None:
    """
    Main entry point.
    
    Function Name: "main"
    - Standard name for entry point
    - Why: Convention from C/Java/etc.
    
    Returns:
        None
    
    Process:
    1. Parse arguments
    2. Validate configuration
    3. Route to appropriate mode
    """
    
    # Parse command-line arguments
    args = parse_arguments()
    # args: Parsed arguments
    
    # Route to demo mode first (doesn't need API validation)
    # Why check first: Demo mode has different requirements
    if args.demo:
        # Demo mode requested
        # args.demo: String containing the search query
        # Why demo first: Allows testing without full agent setup
        
        # Demo mode only requires search API keys, not OpenAI
        # Why different: Demo just tests search APIs, doesn't run the agent
        
        # Check if at least one search API is configured
        # Why check: Need at least one search provider for demo
        if not settings.tavily_api_key and not settings.google_search_api_key:
            # Neither Tavily nor Google is configured
            # Why check both: Demo can work with just one API
            print("❌ Error: No search API configured")
            print("Please set at least one of:")
            print("  - TAVILY_API_KEY")
            print("  - GOOGLE_SEARCH_API_KEY")
            print("  - GOOGLE_SEARCH_ENGINE_ID (also needed for Google)")
            print("\nAdd these to your .env file")
            # Provide clear instructions on what's needed
            sys.exit(1)
            # Exit with error code
        
        # Run the demo
        # demo_combined_search: Function that tests both search APIs
        # args.demo: The search query provided by user
        demo_combined_search(args.demo)
        # Call demo function with query
        return
        # Exit main function after demo completes
        # Why return: Don't continue to other modes
    
    # Validate configuration for agent modes
    # Why validate: Agent modes need OpenAI and Tavily
    # Check if required API keys are set
    # Why validate: Provide clear error message early
    if not settings.openai_api_key:
        print("❌ Error: OPENAI_API_KEY not set")
        print("Please set OPENAI_API_KEY in .env file")
        sys.exit(1)
        # Exit with error code
    
    if not settings.tavily_api_key:
        print("❌ Error: TAVILY_API_KEY not set")
        print("Please set TAVILY_API_KEY in .env file")
        sys.exit(1)
    
    # Route to appropriate mode
    # Check which mode user requested
    
    if args.interactive:
        # Interactive mode requested
        # args.interactive: True if --interactive flag present
        run_interactive_mode()
        # Call interactive mode function
        
    elif args.location:
        # Single query mode with location
        # args.location: String if --location provided
        run_single_query(args.location, verbose=args.verbose)
        # Call single query function
        # Pass verbose flag
        
    else:
        # No mode specified
        # User didn't provide --interactive, --location, or --demo
        
        # Print error message
        print("❌ Error: Must provide --location, --interactive, or --demo")
        print("\nUsage:")
        print("  Single query:   python main.py --location 'Johnson City, TN'")
        print("  Interactive:    python main.py --interactive")
        print("  Demo search:    python main.py --demo 'your search query'")
        print("\nFor more help:  python main.py --help")
        # Provide usage examples including new demo mode
        
        sys.exit(1)
        # Exit with error code


# ==============================================================================
# Script Entry Point
# ==============================================================================

if __name__ == "__main__":
    
    # Call main function
    main()
    # main(): Entry point function defined above
    # All execution logic is in main() and its called functions
    


# ==============================================================================
# Usage Examples
# ==============================================================================
#
# 1. Single Query:
#    python main.py --location "Johnson City, TN"
#    Output: Complete utility information for Johnson City
#    Why use: Quick one-time query for a specific location
#
# 2. Single Query with Verbose:
#    python main.py --location "Raleigh, NC" --verbose
#    Output: Detailed information including iterations, steps, etc.
#    Why use: Debug agent reasoning or see detailed process
#
# 3. Interactive Mode:
#    python main.py --interactive
#    Prompts for location repeatedly until quit
#    Why use: Multiple queries without restarting the program
#
# 4. Demo Combined Search:
#    python main.py --demo "OpenAI GPT-4"
#    Output: Side-by-side results from Tavily and Google search
#    Why use: Test search APIs, compare search quality, see parallel execution
#    Note: Works with just Tavily or just Google (doesn't need both)
#
# 5. Demo with Utility Query:
#    python main.py --demo "Johnson City TN gas utility provider"
#    Output: Search results from both providers for utility information
#    Why use: See how different search engines find utility information
#
# 6. Help:
#    python main.py --help
#    Shows all available options
#    Why use: Learn about all command-line arguments
#
# 7. As Module:
#    from main import run_agent
#    result = run_agent("Find utilities in Durham")
#    print(result["output"])
#    Why use: Integrate agent into your own Python code
#
# 8. As Module - Combined Search:
#    from tools.search_tools import combined_web_search
#    result = combined_web_search("python tutorials", max_results=3)
#    print(result["summary"])
#    print(f"Tavily: {len(result['tavily']['results'])} results")
#    print(f"Google: {len(result['google']['results'])} results")
#    Why use: Use combined search in your own projects


# ==============================================================================
# Future Enhancements
# ==============================================================================
#
# 1. API Mode:
#    - Add Flask/FastAPI server mode
#    - RESTful endpoints for utility search
#    - JSON responses
#
# 2. Batch Mode:
#    - Process multiple locations from CSV file
#    - Export results to CSV/JSON
#    - Progress tracking
#
# 3. Caching:
#    - Cache search results
#    - Reduce API calls for repeated queries
#    - Redis or file-based cache
#
# 4. Configuration File:
#    - YAML/JSON config file
#    - Override settings without changing .env
#    - Different configurations for different environments
#
# 5. Logging:
#    - Structured logging
#    - Log to file
#    - Different log levels
#
# 6. Progress Indicators:
#    - Show progress bar during execution
#    - Real-time status updates
#    - Estimate time remaining
#
# 7. Output Formats:
#    - JSON output option
#    - HTML report generation
#    - PDF export
#
# 8. Error Recovery:
#    - Retry failed searches
#    - Fallback strategies
#    - Partial results on error

