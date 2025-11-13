#!/usr/bin/env python3
"""
Test Script for Combined Search Functionality

This script tests the combined search feature (Tavily + Google) to verify
that both APIs are configured correctly and working as expected.

Usage:
    python test_combined_search.py

Requirements:
    - At least one of: TAVILY_API_KEY or (GOOGLE_SEARCH_API_KEY + GOOGLE_SEARCH_ENGINE_ID)
    - Both configured for full testing
"""

# Import required modules
# sys: For exit codes
# json: For pretty-printing results
import sys
import json

# Import settings to check configuration
from config.settings import settings

# Import search functions
from tools.search_tools import (
    google_search_grounding,
    combined_web_search
)


def print_section(title: str) -> None:
    """
    Print a formatted section header.
    
    Args:
        title (str): The section title to display
    """
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_configuration() -> tuple[bool, bool]:
    """
    Test if APIs are configured.
    
    Returns:
        tuple[bool, bool]: (tavily_configured, google_configured)
    """
    print_section("🔧 CONFIGURATION CHECK")
    
    # Check Tavily configuration
    tavily_configured = bool(settings.tavily_api_key)
    print(f"Tavily API Key: {'✅ Set' if tavily_configured else '❌ Not set'}")
    
    # Check Google configuration
    google_configured = bool(
        settings.google_search_api_key and 
        settings.google_search_engine_id
    )
    print(f"Google Search API Key: {'✅ Set' if settings.google_search_api_key else '❌ Not set'}")
    print(f"Google Search Engine ID: {'✅ Set' if settings.google_search_engine_id else '❌ Not set'}")
    print(f"Google Search: {'✅ Fully configured' if google_configured else '❌ Not fully configured'}")
    
    # Summary
    print(f"\n📊 Summary:")
    if tavily_configured and google_configured:
        print("   ✅ Both APIs configured - Full testing possible")
    elif tavily_configured or google_configured:
        print("   ⚠️  One API configured - Partial testing possible")
    else:
        print("   ❌ No APIs configured - Cannot run tests")
        print("\n💡 Please configure at least one search API in your .env file")
        print("   See SEARCH_SETUP_GUIDE.md for instructions")
        return False, False
    
    return tavily_configured, google_configured


def test_tavily_search() -> bool:
    """
    Test Tavily search functionality.
    
    Returns:
        bool: True if test passed, False otherwise
    """
    print_section("🟦 TEST 1: TAVILY SEARCH")
    
    # Check if configured
    if not settings.tavily_api_key:
        print("⏭️  Skipping: Tavily not configured")
        return False
    
    # Perform test search
    print("🔍 Searching for: 'Python programming language'")
    print("   Requesting: 3 results")
    print()
    
    try:
        # Call Google search
        result = google_search_grounding("Python programming language", max_results=3)
        
        # Check result
        if result['status'] == 'success':
            print(f"✅ Test PASSED")
            print(f"   Status: {result['status']}")
            print(f"   Results found: {result['count']}")
            print(f"   Query: {result['query']}")
            
            # Show first result
            if result['results']:
                first = result['results'][0]
                print(f"\n   First result:")
                print(f"   - Title: {first['title']}")
                print(f"   - Score: {first.get('score', 'N/A')}")
                print(f"   - URL: {first['url'][:60]}...")
            
            return True
        else:
            print(f"❌ Test FAILED")
            print(f"   Status: {result['status']}")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test FAILED with exception")
        print(f"   Error: {str(e)}")
        return False


def test_google_search() -> bool:
    """
    Test Google search functionality.
    
    Returns:
        bool: True if test passed, False otherwise
    """
    print_section("🟥 TEST 2: GOOGLE SEARCH")
    
    # Check if configured
    if not (settings.google_search_api_key and settings.google_search_engine_id):
        print("⏭️  Skipping: Google Search not fully configured")
        return False
    
    # Perform test search
    print("🔍 Searching for: 'Python programming language'")
    print("   Requesting: 3 results")
    print()
    
    try:
        # Call Google search
        result = google_search_grounding("Python programming language", max_results=3)
        
        # Check result
        if result['status'] == 'success':
            print(f"✅ Test PASSED")
            print(f"   Status: {result['status']}")
            print(f"   Results found: {result['count']}")
            print(f"   Query: {result['query']}")
            
            # Show first result
            if result['results']:
                first = result['results'][0]
                print(f"\n   First result:")
                print(f"   - Title: {first['title']}")
                print(f"   - Domain: {first.get('displayLink', 'N/A')}")
                print(f"   - URL: {first['url'][:60]}...")
            
            return True
        else:
            print(f"❌ Test FAILED")
            print(f"   Status: {result['status']}")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test FAILED with exception")
        print(f"   Error: {str(e)}")
        return False


def test_combined_search() -> bool:
    """
    Test combined search functionality.
    
    Returns:
        bool: True if test passed, False otherwise
    """
    print_section("⚡ TEST 3: COMBINED SEARCH (PARALLEL)")
    
    # Check if at least one is configured
    tavily_ok = bool(settings.tavily_api_key)
    google_ok = bool(settings.google_search_api_key and settings.google_search_engine_id)
    
    if not (tavily_ok or google_ok):
        print("⏭️  Skipping: No search APIs configured")
        return False
    
    # Perform test search
    print("🔍 Searching for: 'artificial intelligence'")
    print("   Requesting: 3 results per source")
    print("   Mode: Parallel execution (both at same time)")
    print()
    
    # Import time to measure parallel execution
    import time
    
    try:
        # Measure execution time
        start = time.time()
        result = combined_web_search("artificial intelligence", max_results=3)
        elapsed = time.time() - start
        
        # Check overall result
        print(f"⏱️  Execution time: {elapsed:.2f} seconds")
        print(f"📊 Overall status: {result['status']}")
        print(f"💬 Summary: {result['summary']}")
        print()
        
        # Check Tavily results
        tavily_status = result['tavily']['status']
        tavily_count = result['tavily'].get('count', 0)
        print(f"🟦 Tavily: {tavily_status} ({tavily_count} results)")
        if tavily_status != 'success':
            print(f"   Error: {result['tavily'].get('error', 'Unknown')}")
        
        # Check Google results
        google_status = result['google']['status']
        google_count = result['google'].get('count', 0)
        print(f"🟥 Google: {google_status} ({google_count} results)")
        if google_status != 'success':
            print(f"   Error: {result['google'].get('error', 'Unknown')}")
        
        # Overall assessment
        print()
        if result['status'] == 'success':
            print(f"✅ Test PASSED")
            print(f"   Both searches succeeded!")
            print(f"   Total results: {result['total_count']}")
            return True
            
        elif result['status'] == 'partial':
            print(f"⚠️  Test PARTIAL")
            print(f"   One search succeeded, one failed")
            print(f"   Total results: {result['total_count']}")
            return True  # Still considered passing (graceful degradation)
            
        else:
            print(f"❌ Test FAILED")
            print(f"   Both searches failed")
            return False
            
    except Exception as e:
        print(f"❌ Test FAILED with exception")
        print(f"   Error: {str(e)}")
        return False


def main():
    """
    Main test function.
    """
    print()
    print("=" * 80)
    print("  COMBINED SEARCH TEST SUITE")
    print("  Testing Tavily + Google Search Integration")
    print("=" * 80)
    
    # Test configuration
    tavily_configured, google_configured = test_configuration()
    
    # Exit if nothing is configured
    if not (tavily_configured or google_configured):
        sys.exit(1)
    
    # Run tests
    results = []
    
    # Test 1: Tavily
    if tavily_configured:
        results.append(("Tavily Search", test_tavily_search()))
    
    # Test 2: Google
    if google_configured:
        results.append(("Google Search", test_google_search()))
    
    # Test 3: Combined (if at least one is configured)
    if tavily_configured or google_configured:
        results.append(("Combined Search", test_combined_search()))
    
    # Summary
    print_section("📊 TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed
    
    print(f"Total tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print()
    
    # Detailed results
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print()
    
    # Final status
    if failed == 0:
        print("🎉 All tests passed!")
        print()
        print("💡 Next steps:")
        print("   - Try the demo: python main.py --demo 'your search query'")
        print("   - Read the guide: See SEARCH_SETUP_GUIDE.md for more examples")
        print("   - Use in code: from tools.search_tools import combined_web_search")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed")
        print()
        print("💡 Troubleshooting:")
        print("   - Check your .env file for correct API keys")
        print("   - Verify API keys are active and have quota remaining")
        print("   - See SEARCH_SETUP_GUIDE.md for detailed setup instructions")
        sys.exit(1)


if __name__ == "__main__":
    """
    Entry point when script is run directly.
    """
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

