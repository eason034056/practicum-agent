"""
Unit Tests for AI Agent

This module contains tests for the utility identification agent.

Why Test:
- Reliability: Ensure agent works correctly
- Regression Prevention: Catch bugs early
- Documentation: Tests show how to use code
- Confidence: Deploy with confidence

Test Categories:
1. Tool Tests: Verify each tool works
2. State Tests: Verify state management
3. Node Tests: Verify graph nodes
4. Integration Tests: Verify full agent
"""

# pytest: Testing framework
import pytest
# pytest: Modern testing framework for Python
# Why pytest: Better than unittest (cleaner syntax, fixtures, parametrize)

# Import components to test
from agent.state import AgentState, create_initial_state
# State-related functions

from agent.nodes import agent_node, tool_executor_node, should_continue
# Node functions

from agent.graph import create_utility_agent, run_agent
# Graph construction

from tools.search_tools import web_search
# Example tool to test

# Mock for testing without API calls
from unittest.mock import Mock, patch, MagicMock
# Mock: Create mock objects
# patch: Replace real objects with mocks during test
# Why mock: Test without calling real APIs (faster, no API keys needed)


# ==============================================================================
# Test Fixtures
# ==============================================================================
# Fixtures: Reusable test setup code
# Why fixtures: DRY principle for test setup

@pytest.fixture
def sample_state():
    """
    Create a sample state for testing.
    
    Fixture Name: "sample_state"
    - Why fixture: Reusable state for multiple tests
    - @pytest.fixture: Decorator that marks this as a fixture
    
    Returns:
        AgentState: A test state
    
    Usage in tests:
        def test_something(sample_state):
            # sample_state is automatically passed by pytest
            assert sample_state["input"] == "test location"
    """
    # Create initial state with test input
    return create_initial_state("test location")
    # Returns a complete AgentState dict


@pytest.fixture
def mock_llm_response():
    """
    Create a mock LLM response for testing.
    
    Why: Tests shouldn't call real LLM (slow, costs money)
    """
    # Create mock message
    mock_message = Mock()
    # Mock: Fake object that can have attributes set
    
    # Set attributes for agent response without tool calls
    mock_message.tool_calls = []
    # Empty list = agent is done
    
    mock_message.content = "This is a test response"
    # The final answer content
    
    return mock_message


# ==============================================================================
# State Tests
# ==============================================================================
# Test state creation and management

def test_create_initial_state():
    """
    Test that initial state is created correctly.
    
    Test Name: "test_create_initial_state"
    - Prefix "test_": pytest discovers tests by this prefix
    - Descriptive: Clear what's being tested
    
    What we're testing:
    - create_initial_state() returns correct structure
    - All required fields are present
    - Initial values are correct
    """
    # Arrange: Set up test inputs
    # Why "Arrange-Act-Assert" pattern: Clear test structure
    user_input = "Find utilities in Raleigh, NC"
    
    # Act: Perform the action being tested
    state = create_initial_state(user_input)
    
    # Assert: Verify expectations
    # Why multiple asserts: Each checks different aspect
    
    # Check that state has the input
    assert state["input"] == user_input
    # assert: Python keyword that raises error if condition is False
    # If this fails: Test fails with helpful message
    
    # Check initial values
    assert state["iterations"] == 0
    # Should start at 0 iterations
    
    assert state["next_action"] == "continue"
    # Should be ready to continue
    
    assert state["output"] == ""
    # No output yet
    
    assert len(state["messages"]) == 1
    # Should have one initial message
    
    # Check provider fields are empty
    assert state["gas_provider"] == {}
    assert state["electric_provider"] == {}
    assert state["water_provider"] == {}
    assert state["sewer_provider"] == {}
    assert state["stormwater_authority"] == {}
    # All should be empty dicts initially


def test_state_fields_exist(sample_state):
    """
    Test that all required state fields exist.
    
    sample_state: Fixture parameter (pytest injects it)
    - pytest sees this parameter name
    - Looks for fixture with same name
    - Calls fixture function and passes result
    """
    # List of required fields
    required_fields = [
        "input",
        "output",
        "messages",
        "intermediate_steps",
        "identified_ahj",
        "gas_provider",
        "electric_provider",
        "water_provider",
        "sewer_provider",
        "stormwater_authority",
        "next_action",
        "iterations",
        "error"
    ]
    
    # Check each field exists
    for field in required_fields:
        assert field in sample_state, f"Missing required field: {field}"
        # f"...": Includes field name in error message if assertion fails
        # Why helpful: Know exactly which field is missing


# ==============================================================================
# Router Tests
# ==============================================================================
# Test conditional routing logic

def test_should_continue_when_continue(sample_state):
    """
    Test router when agent wants to continue.
    
    What we're testing:
    - should_continue() returns "continue" when next_action is "continue"
    """
    # Arrange
    sample_state["next_action"] = "continue"
    
    # Act
    result = should_continue(sample_state)
    
    # Assert
    assert result == "continue"
    # Router should return "continue"


def test_should_continue_when_end(sample_state):
    """
    Test router when agent is done.
    """
    # Arrange
    sample_state["next_action"] = "end"
    
    # Act
    result = should_continue(sample_state)
    
    # Assert
    assert result == "end"


# ==============================================================================
# Tool Tests
# ==============================================================================
# Test individual tools

@patch('tools.search_tools._tavily_client')
# @patch: Replace _tavily_client with a mock during this test
# Why: Don't make real API calls in tests
# Argument is the full path to what we're mocking
def test_web_search_success(mock_tavily):
    """
    Test web_search with successful API response.
    
    mock_tavily: The mock object for _tavily_client
    - pytest-mock or unittest.mock provides this
    - We can control what it returns
    """
    # Arrange: Set up mock response
    mock_tavily.results.return_value = {
        "results": [
            {
                "title": "Test Result",
                "url": "https://example.com",
                "content": "Test content",
                "score": 0.95
            }
        ]
    }
    # mock_tavily.results.return_value: What the mocked function returns
    # When web_search calls _tavily_client.results(), it gets this
    
    # Act: Call the function
    result = web_search("test query")
    
    # Assert: Verify result structure
    assert result["status"] == "success"
    # Should indicate success
    
    assert result["query"] == "test query"
    # Should echo the query
    
    assert len(result["results"]) == 1
    # Should have one result
    
    assert result["results"][0]["title"] == "Test Result"
    # Should have the mocked data


def test_web_search_empty_query():
    """
    Test web_search with empty query.
    
    What we're testing:
    - web_search handles empty input gracefully
    - Returns error status with helpful message
    """
    # Act
    result = web_search("")
    # Call with empty string
    
    # Assert
    assert result["status"] == "error"
    # Should return error
    
    assert "empty" in result["error"].lower()
    # Error message should mention "empty"
    # .lower(): Case-insensitive check


# ==============================================================================
# Integration Tests
# ==============================================================================
# Test full agent execution (mocked)

@patch('agent.nodes.llm_with_tools')
# Mock the LLM so we don't make real API calls
def test_agent_completes_successfully(mock_llm):
    """
    Integration test: Full agent execution (mocked).
    
    mock_llm: Mocked LLM instance
    - We control what responses it gives
    - Test logic without spending money on API calls
    """
    # Arrange: Set up mock LLM to return done message
    mock_response = Mock()
    mock_response.tool_calls = []  # No more tools needed
    mock_response.content = "Test final answer"
    mock_llm.invoke.return_value = mock_response
    # When LLM is called, it returns this mock response
    
    # Create agent
    from agent.state import create_initial_state
    initial_state = create_initial_state("test query")
    
    # Act: Run agent node
    result = agent_node(initial_state)
    
    # Assert: Check that agent decided to end
    assert result["next_action"] == "end"
    # Agent should be done
    
    assert "output" in result
    # Should have output field
    
    assert result["iterations"] == 1
    # Should have incremented iterations


@patch('agent.nodes.llm_with_tools')
def test_agent_max_iterations(mock_llm):
    """
    Test that agent stops at max iterations.
    
    What we're testing:
    - Agent respects MAX_ITERATIONS setting
    - Prevents infinite loops
    """
    # Arrange: Set up state at max iterations
    state = create_initial_state("test")
    state["iterations"] = 100  # Way over limit
    
    # Act
    result = agent_node(state)
    
    # Assert
    assert result["next_action"] == "end"
    # Should force end
    
    assert "error" in result
    # Should have error message
    
    assert "maximum iterations" in result["error"].lower()
    # Error should mention max iterations


# ==============================================================================
# Running Tests
# ==============================================================================
#
# Run all tests:
#   pytest tests/test_agent.py
#
# Run with verbose output:
#   pytest tests/test_agent.py -v
#
# Run specific test:
#   pytest tests/test_agent.py::test_create_initial_state
#
# Run with coverage:
#   pytest tests/test_agent.py --cov=agent --cov=tools
#
# Run and see print statements:
#   pytest tests/test_agent.py -s


# ==============================================================================
# Test Best Practices Used
# ==============================================================================
#
# 1. Descriptive Test Names
#    - test_create_initial_state (clear what's tested)
#    - Not: test_state() (too vague)
#
# 2. Arrange-Act-Assert Pattern
#    - Arrange: Set up inputs
#    - Act: Perform action
#    - Assert: Verify results
#
# 3. One Concept Per Test
#    - Each test checks one thing
#    - Not: test_everything()
#
# 4. Fixtures for Reusable Setup
#    - @pytest.fixture for common setup
#    - Reduces duplication
#
# 5. Mocking External Dependencies
#    - @patch for API calls
#    - Tests are fast and don't require API keys
#
# 6. Helpful Error Messages
#    - assert with custom messages
#    - Know exactly what failed
#
# 7. Test Both Success and Failure
#    - test_web_search_success
#    - test_web_search_empty_query


# ==============================================================================
# Additional Tests to Add
# ==============================================================================
#
# 1. Tool Tests
#    - Test each tool individually
#    - Test error cases
#    - Test edge cases (special characters, long inputs)
#
# 2. State Management Tests
#    - Test message appending (operator.add)
#    - Test state updates
#    - Test state validation
#
# 3. Graph Tests
#    - Test graph construction
#    - Test edge routing
#    - Test conditional edges
#
# 4. Integration Tests
#    - End-to-end with real APIs (separate, not run by default)
#    - Test full workflows
#    - Test error recovery
#
# 5. Performance Tests
#    - Test execution time
#    - Test memory usage
#    - Test with large inputs

