"""
Quick Test - Gemini Grounding Output

A simple script to quickly see what Gemini returns vs what the agent outputs.
Run this to debug response quality issues.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.search_tools import google_search_grounding
from tools.utility_tools import search_gas_provider


def quick_test():
    """
    Quick test to see both outputs side by side
    """
    print("=" * 80)
    print("  🔬 QUICK GROUNDING TEST")
    print("=" * 80)
    
    # Test query
    location = "Evanston IL"
    query = f"natural gas provider {location} contact information connection requirements"
    
    print(f"\n📍 Testing Location: {location}")
    print(f"🔍 Query: {query}\n")
    
    # ========================================================================
    # STEP 1: Direct Gemini Grounding
    # ========================================================================
    print("\n" + "─" * 80)
    print("STEP 1: What Gemini Returns (Raw)")
    print("─" * 80)
    
    direct_result = google_search_grounding(query=query, max_results=8)
    
    print(f"Status: {direct_result.get('status')}")
    print(f"Has Grounding: {direct_result.get('has_grounding')}")
    
    gemini_answer = direct_result.get('answer', '')
    
    if gemini_answer:
        print(f"\n🤖 GEMINI'S ANSWER ({len(gemini_answer)} characters):")
        print("┌" + "─" * 78 + "┐")
        # Print with box
        for line in gemini_answer.split('\n'):
            if line:
                print(f"│ {line[:76]:<76} │")
        print("└" + "─" * 78 + "┘")
    else:
        print("\n❌ NO ANSWER FROM GEMINI!")
        print("Possible reasons:")
        print("  - API key not set")
        print("  - Grounding not enabled")
        print("  - Network error")
    
    # Show sources
    sources_count = len(direct_result.get('results', []))
    print(f"\n📚 Sources Used: {sources_count}")
    
    # ========================================================================
    # STEP 2: Utility Tool Output
    # ========================================================================
    print("\n" + "─" * 80)
    print("STEP 2: What Utility Tool Returns (Processed)")
    print("─" * 80)
    
    tool_result = search_gas_provider(location=location)
    
    print(f"Status: {tool_result.get('status')}")
    
    # Get information field (the actual field name used by utility tools)
    provider_info = tool_result.get('information', '')
    
    if provider_info:
        print(f"\n📋 UTILITY TOOL OUTPUT ({len(provider_info)} characters):")
        print("┌" + "─" * 78 + "┐")
        for line in provider_info.split('\n'):
            if line:
                print(f"│ {line[:76]:<76} │")
        print("└" + "─" * 78 + "┘")
    else:
        print("\n❌ NO OUTPUT FROM UTILITY TOOL!")
        print(f"   Available fields: {list(tool_result.keys())}")
    
    # ========================================================================
    # STEP 3: Comparison
    # ========================================================================
    print("\n" + "─" * 80)
    print("STEP 3: Comparison")
    print("─" * 80)
    
    print(f"\nGemini Answer Length:    {len(gemini_answer):>6} chars")
    print(f"Tool Output Length:      {len(provider_info):>6} chars")
    print(f"Difference:              {len(gemini_answer) - len(provider_info):>6} chars")
    
    if gemini_answer and provider_info:
        # Check if Gemini answer is in tool output
        if gemini_answer in provider_info:
            print("\n✅ GOOD: Gemini's answer is included in tool output")
        elif gemini_answer[:200] in provider_info:
            print("\n⚠️  WARNING: Only part of Gemini's answer is in tool output")
        else:
            print("\n❌ PROBLEM: Gemini's answer is NOT in tool output!")
            print("\n🔍 Debugging:")
            print(f"  Gemini answer starts with: {gemini_answer[:100]}...")
            print(f"  Tool output starts with: {provider_info[:100]}...")
    
    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "=" * 80)
    print("  📊 SUMMARY")
    print("=" * 80)
    
    issues_found = []
    
    if not gemini_answer:
        issues_found.append("❌ Gemini not returning answers")
    
    if not provider_info:
        issues_found.append("❌ Utility tool not returning info")
    
    if gemini_answer and provider_info:
        if len(gemini_answer) > len(provider_info) * 1.5:
            issues_found.append("⚠️  Significant information loss in processing")
        
        if gemini_answer not in provider_info:
            issues_found.append("❌ Gemini answer not being used by tool")
    
    if issues_found:
        print("\n🔴 Issues Found:")
        for issue in issues_found:
            print(f"  {issue}")
        
        print("\n💡 Recommendations:")
        if not gemini_answer:
            print("  1. Check GEMINI_API_KEY in .env file")
            print("  2. Verify google-genai package is installed")
            print("  3. Check network connectivity")
        
        if gemini_answer and not provider_info:
            print("  1. Check utility_tools.py processing logic")
            print("  2. Verify search_result['answer'] is being extracted")
        
        if gemini_answer not in provider_info and gemini_answer and provider_info:
            print("  1. Check if utility tool is using 'answer' field")
            print("  2. Verify the if gemini_answer: logic in utility_tools.py")
            print("  3. Add debug prints to see which branch is executed")
    else:
        print("\n✅ No major issues detected!")
        print("   Gemini grounding is working correctly.")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        quick_test()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 Common Issues:")
        print("  - GEMINI_API_KEY not set in .env")
        print("  - google-genai package not installed")
        print("  - Network connectivity issues")

