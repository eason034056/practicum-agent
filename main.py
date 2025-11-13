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
            
            # Run agent
            result = agent.invoke(initial_state)
            # agent.invoke(): Execute graph with initial state
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
    
    # Parse arguments
    # parse_args(): Parses sys.argv (command-line arguments)
    args = parser.parse_args()
    # args: Namespace object with parsed arguments
    # Access: args.location, args.verbose, args.interactive
    
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
    
    # Validate configuration
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
        # User didn't provide --interactive or --location
        
        # Print error message
        print("❌ Error: Must provide --location or --interactive")
        print("\nUsage:")
        print("  Single query:   python main.py --location 'Johnson City, TN'")
        print("  Interactive:    python main.py --interactive")
        print("\nFor more help:  python main.py --help")
        # Provide usage examples
        
        sys.exit(1)
        # Exit with error code


# ==============================================================================
# Script Entry Point
# ==============================================================================

if __name__ == "__main__":
    """
    Entry point when script is run directly.
    
    if __name__ == "__main__":
    - Python idiom for script entry point
    - Why: Separates "run as script" from "import as module"
    
    How it works:
    - When run as script: __name__ == "__main__" (True)
    - When imported: __name__ == "main" (False)
    
    Why important:
    - Code in this block only runs when script executed directly
    - Doesn't run when imported by other modules
    - Allows module to be both library and executable
    
    Example:
    - python main.py → Runs this block
    - from main import run_agent → Doesn't run this block
    """
    
    # Call main function
    main()
    # main(): Entry point function defined above
    # All execution logic is in main() and its called functions
    
    # Why separate main() function:
    # - Testing: Can test main() without running immediately
    # - Organization: Clear entry point
    # - Flexibility: Could call main() from other contexts


# ==============================================================================
# Usage Examples
# ==============================================================================
#
# 1. Single Query:
#    python main.py --location "Johnson City, TN"
#    Output: Complete utility information for Johnson City
#
# 2. Single Query with Verbose:
#    python main.py --location "Raleigh, NC" --verbose
#    Output: Detailed information including iterations, steps, etc.
#
# 3. Interactive Mode:
#    python main.py --interactive
#    Prompts for location repeatedly until quit
#
# 4. Help:
#    python main.py --help
#    Shows all available options
#
# 5. As Module:
#    from main import run_agent
#    result = run_agent("Find utilities in Durham")
#    print(result["output"])


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

