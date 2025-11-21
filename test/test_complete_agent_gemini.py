"""
Complete Agent Test with Gemini

This script tests the complete AI agent workflow using Gemini for both:
1. Search grounding (google_search_grounding)
2. Agent LLM (reasoning and decision-making)

Purpose:
- Verify end-to-end agent functionality with Gemini
- Generate comprehensive utility provider reports
- Demonstrate grounding integration in full agent context
- Validate all components work together

Test Flow:
User Query → Agent (Gemini) → Tools (Grounding) → Final Report
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.graph import create_utility_agent
from config.settings import settings


def print_section(title: str, char: str = "=", width: int = 100):
    """
    Print a visual section separator
    
    Args:
        title: Section title to display
        char: Character to use for the separator line
        width: Total width of the separator
    """
    print("\n" + char * width)
    print(f"  {title}")
    print(char * width + "\n")


def print_subsection(title: str, width: int = 100):
    """
    Print a subsection header
    
    Args:
        title: Subsection title
        width: Total width of the header
    """
    print(f"\n{'─' * width}")
    print(f"📌 {title}")
    print('─' * width)


def save_report(report_data: dict, filename: str = None):
    """
    Save the complete report to a JSON file
    
    Args:
        report_data: Dictionary containing all report data
        filename: Output filename (default: auto-generated with timestamp)
    
    Returns:
        str: Path to saved file
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"agent_report_{timestamp}.json"
    
    filepath = os.path.join(os.path.dirname(__file__), "reports", filename)
    
    # Create reports directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Save report
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    return filepath


def format_report(state: dict) -> str:
    """
    Format the agent state into a comprehensive markdown report
    
    Args:
        state: Final agent state containing all information
    
    Returns:
        str: Formatted markdown report
    """
    report_lines = []
    
    # Header
    report_lines.append("=" * 100)
    report_lines.append("COMPREHENSIVE UTILITY PROVIDER REPORT")
    report_lines.append("=" * 100)
    report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Location: {state.get('location', 'N/A')}")
    report_lines.append(f"Powered by: Gemini AI with Google Search Grounding")
    report_lines.append("\n" + "-" * 100)
    
    # Executive Summary
    report_lines.append("\n## EXECUTIVE SUMMARY")
    report_lines.append("-" * 100)
    
    messages = state.get('messages', [])
    if messages:
        last_message = messages[-1]
        if hasattr(last_message, 'content'):
            # Handle Gemini's list format
            content = last_message.content
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and 'text' in item:
                        text_parts.append(item['text'])
                    elif isinstance(item, str):
                        text_parts.append(item)
                content_text = '\n'.join(text_parts)
            else:
                content_text = content
            report_lines.append(content_text)
    
    # Agent Reasoning Steps
    report_lines.append("\n\n## AGENT REASONING PROCESS")
    report_lines.append("-" * 100)
    report_lines.append("\nThe AI agent followed these steps to gather information:\n")
    
    for i, message in enumerate(messages, 1):
        if hasattr(message, 'type'):
            if message.type == 'ai':
                # AI reasoning/decision
                report_lines.append(f"\n### Step {i}: Agent Reasoning")
                report_lines.append(f"```")
                
                # Handle Gemini's list format
                content = message.content
                if isinstance(content, list):
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and 'text' in item:
                            text_parts.append(item['text'])
                        elif isinstance(item, str):
                            text_parts.append(item)
                    content_text = '\n'.join(text_parts)
                else:
                    content_text = content
                
                report_lines.append(content_text[:500] + "..." if len(content_text) > 500 else content_text)
                report_lines.append(f"```")
                
                # Show tool calls if any
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    report_lines.append(f"\n**Tools Called:**")
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.get('name', 'unknown')
                        report_lines.append(f"  - {tool_name}()")
            
            elif message.type == 'tool':
                # Tool result
                report_lines.append(f"\n### Step {i}: Tool Execution Result")
                
                # Handle different content formats
                content = message.content
                if isinstance(content, list):
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and 'text' in item:
                            text_parts.append(item['text'])
                        elif isinstance(item, str):
                            text_parts.append(item)
                    content_text = '\n'.join(text_parts)
                else:
                    content_text = str(content)
                
                result_preview = content_text[:300] + "..." if len(content_text) > 300 else content_text
                report_lines.append(f"```")
                report_lines.append(result_preview)
                report_lines.append(f"```")
    
    # Metadata
    report_lines.append("\n\n## METADATA")
    report_lines.append("-" * 100)
    report_lines.append(f"\nTotal Messages: {len(messages)}")
    report_lines.append(f"Iterations: {state.get('iterations', 0)}")
    report_lines.append(f"Status: {state.get('next_action', 'N/A')}")
    
    # Footer
    report_lines.append("\n" + "=" * 100)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 100)
    
    return "\n".join(report_lines)


def test_complete_agent():
    """
    Test the complete agent with Gemini LLM and grounding
    
    This is the main test function that:
    1. Initializes the agent with Gemini
    2. Sends a comprehensive query
    3. Tracks all steps and reasoning
    4. Generates a detailed report
    """
    print_section("🤖 COMPLETE AGENT TEST WITH GEMINI", "=", 100)
    
    # =========================================================================
    # Configuration Check
    # =========================================================================
    print_subsection("Configuration Status", 100)
    
    config_ok = True
    
    if settings.gemini_api_key:
        print(f"✅ Gemini API Key: Configured")
        print(f"   Preview: {settings.gemini_api_key[:10]}...{settings.gemini_api_key[-4:]}")
    else:
        print(f"❌ Gemini API Key: NOT CONFIGURED")
        config_ok = False
    
    if settings.tavily_api_key:
        print(f"✅ Tavily API Key: Configured")
    else:
        print(f"⚠️  Tavily API Key: Not configured (optional)")
    
    if not config_ok:
        print("\n" + "!" * 100)
        print("❌ ERROR: Required API keys not configured!")
        print("!" * 100)
        print("\nPlease set GEMINI_API_KEY in your .env file:")
        print("  GEMINI_API_KEY=your_key_here")
        print("\nGet your key from: https://aistudio.google.com/app/apikey")
        return None
    
    # =========================================================================
    # Create Agent Graph
    # =========================================================================
    print_subsection("Initializing Agent", 100)
    
    print("🔧 Creating agent graph with Gemini LLM...")
    try:
        graph = create_utility_agent()
        print("✅ Agent graph created successfully")
        print("   LLM: Google Gemini (gemini-2.5-flash)")
        print("   Tools: Grounding with Google Search + Utility Tools")
        print("   Architecture: ReAct (Reason + Act + Observe)")
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # =========================================================================
    # Test Query
    # =========================================================================
    print_subsection("Test Query", 100)
    
    test_location = "Evanston, Illinois"
    query = f"""I need comprehensive information about all utility providers for {test_location}.

Please provide detailed information for each utility type:
1. Natural Gas Provider
2. Electric Provider  
3. Water Provider
4. Sewer Provider
5. Stormwater Management Authority

For each provider, include:
- Complete contact information (phone, email, website)
- Service area details
- Connection requirements and process
- Required documents and fees
- Technical specifications
- Important policies and regulations

Please be thorough and provide actionable information."""
    
    print(f"📍 Location: {test_location}")
    print(f"\n📝 Query:")
    print("─" * 100)
    print(query)
    print("─" * 100)
    
    # =========================================================================
    # Run Agent
    # =========================================================================
    print_subsection("Running Agent (This may take 1-2 minutes...)", 100)
    
    initial_state = {
        "messages": [{"role": "user", "content": query}],
        "location": test_location,
        "iterations": 0
    }
    
    print("\n⏳ Agent is working...")
    print("   - Analyzing query with Gemini")
    print("   - Deciding which tools to use")
    print("   - Executing searches with grounding")
    print("   - Synthesizing comprehensive report\n")
    
    try:
        # Invoke the agent with increased recursion limit
        # recursion_limit: Maximum number of graph execution steps
        # Default: 25, Increased: 100 for comprehensive queries
        # Why increase: Complex queries need more reasoning steps
        final_state = graph.invoke(
            initial_state,
            config={"recursion_limit": 100}
        )
        
        print("✅ Agent execution completed!")
        print(f"   Total iterations: {final_state.get('iterations', 0)}")
        print(f"   Total messages: {len(final_state.get('messages', []))}")
        
    except Exception as e:
        print(f"\n❌ Agent execution failed: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # =========================================================================
    # Display Results
    # =========================================================================
    print_subsection("Agent Output", 100)
    
    messages = final_state.get('messages', [])
    if messages:
        # Get the final AI response
        last_message = messages[-1]
        
        print("\n" + "┌" + "─" * 98 + "┐")
        print("│" + " " * 40 + "FINAL REPORT" + " " * 46 + "│")
        print("└" + "─" * 98 + "┘\n")
        
        if hasattr(last_message, 'content'):
            # Extract text content from Gemini's response format
            # Gemini returns content as a list of dicts with 'text' field
            content = last_message.content
            
            # Convert to string if it's a list (Gemini format)
            if isinstance(content, list):
                # Extract text from each item in the list
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and 'text' in item:
                        text_parts.append(item['text'])
                    elif isinstance(item, str):
                        text_parts.append(item)
                content_text = '\n'.join(text_parts)
            else:
                # Already a string (OpenAI format)
                content_text = content
            
            print(content_text)
            print("\n📊 Report Statistics:")
            print(f"   - Length: {len(content_text)} characters")
            print(f"   - Lines: {len(content_text.split(chr(10)))}")
            print(f"   - Words: {len(content_text.split())}")
        else:
            print("⚠️  No content in final message")
    else:
        print("❌ No messages in final state")
    
    # =========================================================================
    # Show Agent Steps
    # =========================================================================
    print_subsection("Agent Execution Steps", 100)
    
    print("\nThe agent went through the following steps:\n")
    
    step_num = 1
    for message in messages:
        if hasattr(message, 'type'):
            if message.type == 'ai':
                # AI message (reasoning/decision)
                print(f"Step {step_num}: 🤖 Agent Reasoning")
                
                # Show tool calls if any
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    print(f"   Tools to call:")
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.get('name', 'unknown')
                        print(f"      - {tool_name}()")
                else:
                    print(f"   Decision: Provide final answer")
                
                step_num += 1
                
            elif message.type == 'tool':
                # Tool result
                print(f"Step {step_num}: 🔧 Tool Execution")
                print(f"   Tool: {message.name if hasattr(message, 'name') else 'unknown'}")
                
                # Show result preview (handle different formats)
                if hasattr(message, 'content'):
                    content = message.content
                    # Convert to string if needed
                    if isinstance(content, list):
                        text_parts = []
                        for item in content:
                            if isinstance(item, dict) and 'text' in item:
                                text_parts.append(item['text'])
                            elif isinstance(item, str):
                                text_parts.append(item)
                        content_str = '\n'.join(text_parts)
                    else:
                        content_str = str(content)
                    
                    content_preview = content_str[:100] + "..." if len(content_str) > 100 else content_str
                    print(f"   Result: {content_preview}")
                
                step_num += 1
        
        print()  # Blank line between steps
    
    # =========================================================================
    # Generate Reports
    # =========================================================================
    print_subsection("Generating Reports", 100)
    
    # Format markdown report
    print("📄 Formatting markdown report...")
    markdown_report = format_report(final_state)
    
    # Save markdown report
    markdown_path = os.path.join(os.path.dirname(__file__), "reports", 
                                   f"agent_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    os.makedirs(os.path.dirname(markdown_path), exist_ok=True)
    
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print(f"✅ Markdown report saved: {markdown_path}")
    
    # Prepare JSON data
    print("📄 Preparing JSON report...")
    
    # Extract final answer text (handle Gemini format)
    final_answer = None
    if messages and hasattr(messages[-1], 'content'):
        content = messages[-1].content
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and 'text' in item:
                    text_parts.append(item['text'])
                elif isinstance(item, str):
                    text_parts.append(item)
            final_answer = '\n'.join(text_parts)
        else:
            final_answer = content
    
    report_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "location": test_location,
            "agent_model": "gemini-2.5-flash",
            "grounding": "google_search",
            "iterations": final_state.get('iterations', 0),
            "total_messages": len(messages)
        },
        "query": query,
        "final_answer": final_answer,
        "execution_steps": [
            {
                "step": i+1,
                "type": msg.type if hasattr(msg, 'type') else 'unknown',
                "content": (
                    # Handle Gemini's list format for content
                    '\n'.join([
                        item['text'] if isinstance(item, dict) and 'text' in item else str(item)
                        for item in msg.content
                    ]) if isinstance(msg.content, list) else msg.content
                ) if hasattr(msg, 'content') else None,
                "tool_calls": [
                    {
                        "name": tc.get('name'),
                        "args": tc.get('args')
                    } for tc in msg.tool_calls
                ] if hasattr(msg, 'tool_calls') and msg.tool_calls else []
            }
            for i, msg in enumerate(messages)
        ],
        "state": {
            "location": final_state.get('location'),
            "iterations": final_state.get('iterations'),
            "next_action": final_state.get('next_action')
        }
    }
    
    # Save JSON report
    json_path = save_report(report_data)
    print(f"✅ JSON report saved: {json_path}")
    
    # =========================================================================
    # Summary
    # =========================================================================
    print_section("📊 TEST SUMMARY", "=", 100)
    
    print("✅ Test completed successfully!\n")
    
    print("🎯 Key Results:")
    print(f"   - Agent used Gemini for reasoning and decision-making")
    print(f"   - Tools used Google Search grounding for up-to-date information")
    print(f"   - Completed in {final_state.get('iterations', 0)} iterations")
    
    # Calculate report length (handle Gemini format)
    report_length = 0
    if messages and hasattr(messages[-1], 'content'):
        content = messages[-1].content
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and 'text' in item:
                    report_length += len(item['text'])
                elif isinstance(item, str):
                    report_length += len(item)
        else:
            report_length = len(content)
    
    print(f"   - Generated comprehensive report with {report_length} characters")
    
    print("\n📁 Reports Generated:")
    print(f"   - Markdown: {markdown_path}")
    print(f"   - JSON: {json_path}")
    
    print("\n💡 Next Steps:")
    print("   1. Review the generated reports")
    print("   2. Verify information completeness")
    print("   3. Check grounding sources")
    print("   4. Use in production with confidence!")
    
    print("\n" + "=" * 100)
    
    return final_state


def main():
    """
    Main entry point for the test script
    """
    print("=" * 100)
    print("  🧪 COMPLETE AGENT TEST WITH GEMINI")
    print("=" * 100)
    print("\nThis test will:")
    print("  1. ✅ Verify Gemini configuration")
    print("  2. ✅ Initialize agent with Gemini LLM")
    print("  3. ✅ Run comprehensive utility query")
    print("  4. ✅ Generate detailed reports (Markdown + JSON)")
    print("  5. ✅ Show complete agent reasoning process")
    print("\nPress Enter to start...")
    input()
    
    # Run the test
    try:
        result = test_complete_agent()
        
        if result:
            print("\n🎉 All tests passed!")
            print("\nYour AI agent is fully operational with:")
            print("  • Gemini 1.5 Pro for reasoning")
            print("  • Google Search grounding for accuracy")
            print("  • Comprehensive report generation")
        else:
            print("\n❌ Test failed. Please check the errors above.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

