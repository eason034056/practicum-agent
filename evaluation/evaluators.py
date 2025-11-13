"""
Agent Evaluators

This module implements evaluation functions for assessing agent performance.

AgentOps Methodology:
- Trajectory Evaluation: Did the agent reason correctly?
- Outcome Evaluation: Is the final answer accurate?
- Efficiency: How many steps did it take?
- Grounding: Are answers based on sources?

Why Evaluate:
- Quality: Ensure high-quality outputs
- Trust: Build confidence in agent
- Improvement: Identify areas for enhancement
- Compliance: Meet accuracy requirements
"""

# Type hints
from typing import Dict, Any, List
# For type annotations

# For trajectory analysis
from agent.state import AgentState
# AgentState: State schema


# ==============================================================================
# Trajectory Evaluator
# ==============================================================================
def evaluate_trajectory(state: AgentState) -> Dict[str, Any]:
    """
    Evaluate the agent's reasoning trajectory.
    
    Trajectory evaluation assesses:
    - Tool selection: Did agent choose appropriate tools?
    - Tool order: Were tools called in logical sequence?
    - Error handling: Did agent recover from errors?
    - Redundancy: Did agent repeat unnecessary steps?
    
    Function Name: "evaluate_trajectory"
    - "evaluate": Action of assessment
    - "trajectory": The path the agent took
    - Why: Distinguishes from outcome evaluation
    
    Args:
        state (AgentState): Final state after execution
            - Contains: messages, iterations, intermediate_steps
    
    Returns:
        Dict[str, Any]: Evaluation results
            - score: 0.0 to 1.0 (1.0 = perfect)
            - issues: List of problems found
            - strengths: List of good decisions
            - recommendations: How to improve
    
    Evaluation Criteria:
    1. Appropriate tool selection
    2. Logical sequencing
    3. No unnecessary repetition
    4. Efficient path to answer
    """
    
    # Initialize evaluation result
    evaluation = {
        "type": "trajectory",
        # Type of evaluation performed
        
        "score": 1.0,
        # Start with perfect score, deduct for issues
        # Why start at 1.0: Assume good until proven otherwise
        
        "issues": [],
        # List of problems found
        
        "strengths": [],
        # List of good decisions
        
        "recommendations": []
        # How to improve
    }
    
    # Extract messages for analysis
    # state["messages"]: List of all messages (Human, AI, Tool)
    messages = state.get("messages", [])
    # messages: Conversation history
    
    # Analyze iterations
    # state["iterations"]: Number of reasoning steps
    iterations = state.get("iterations", 0)
    # iterations: Count of how many times agent reasoned
    
    # Check 1: Did agent complete successfully?
    # state["output"]: Final answer (empty if failed)
    if not state.get("output"):
        # No output means agent didn't finish successfully
        evaluation["score"] -= 0.5
        # Deduct significant points for failure
        
        evaluation["issues"].append(
            "Agent did not produce final output"
        )
        # Record the issue
    else:
        # Agent completed successfully
        evaluation["strengths"].append(
            "Agent completed task successfully"
        )
    
    # Check 2: Efficiency (iterations)
    # Why check: Too many iterations indicates inefficiency
    if iterations > 15:
        # More than 15 iterations is inefficient
        # Why 15: Based on typical task complexity
        evaluation["score"] -= 0.1
        # Small deduction for inefficiency
        
        evaluation["issues"].append(
            f"High iteration count: {iterations} (expected < 15)"
        )
        
        evaluation["recommendations"].append(
            "Review tool selection logic for efficiency"
        )
    elif iterations < 5:
        # Very few iterations might mean incomplete search
        # Why check: Comprehensive search usually takes 5+ steps
        evaluation["recommendations"].append(
            "Verify all required information was gathered"
        )
    else:
        # Appropriate number of iterations
        evaluation["strengths"].append(
            f"Efficient execution: {iterations} iterations"
        )
    
    # Check 3: Error handling
    # state["error"]: Error message if something failed
    if state.get("error"):
        # Error occurred during execution
        evaluation["score"] -= 0.3
        # Deduct for errors
        
        evaluation["issues"].append(
            f"Error occurred: {state['error']}"
        )
    
    # Check 4: Tool usage analysis
    # Count how many times tools were called
    tool_call_count = 0
    # Counter for tool calls
    
    for message in messages:
        # message: One message from history
        
        # Check if this is an AI message with tool calls
        # hasattr: Check if object has attribute
        if hasattr(message, "tool_calls") and message.tool_calls:
            # This message contains tool calls
            tool_call_count += len(message.tool_calls)
            # Add number of tool calls in this message
    
    # Analyze tool call count
    if tool_call_count == 0:
        # No tools were called
        # Why issue: Agent should use tools for information gathering
        evaluation["score"] -= 0.4
        evaluation["issues"].append(
            "No tools were called (agent didn't gather information)"
        )
    elif tool_call_count > 20:
        # Too many tool calls
        # Why issue: Might indicate redundant searches
        evaluation["score"] -= 0.1
        evaluation["issues"].append(
            f"High tool call count: {tool_call_count} (possible redundancy)"
        )
    else:
        # Appropriate tool usage
        evaluation["strengths"].append(
            f"Appropriate tool usage: {tool_call_count} tool calls"
        )
    
    # Ensure score stays in valid range [0, 1]
    # max(0, ...): Ensure score doesn't go below 0
    # min(1, ...): Ensure score doesn't go above 1
    evaluation["score"] = max(0.0, min(1.0, evaluation["score"]))
    # Clamp score to [0, 1]
    
    return evaluation
    # Return evaluation results


# ==============================================================================
# Outcome Evaluator
# ==============================================================================
def evaluate_outcome(state: AgentState) -> Dict[str, Any]:
    """
    Evaluate the quality of the final answer.
    
    Outcome evaluation assesses:
    - Completeness: Did agent find all required information?
    - Accuracy: Is information grounded in sources?
    - Clarity: Is answer well-structured?
    - Usefulness: Does it answer the user's need?
    
    Function Name: "evaluate_outcome"
    - "outcome": The final result/answer
    - Why: Distinguishes from trajectory evaluation
    
    Args:
        state (AgentState): Final state after execution
    
    Returns:
        Dict[str, Any]: Evaluation results
            - score: 0.0 to 1.0
            - completeness: What information was found
            - missing: What information is missing
            - quality_notes: Assessment of answer quality
    
    Note: This is a simplified evaluator.
    Production version would use:
    - LLM-as-judge for semantic evaluation
    - Ground truth comparisons for known locations
    - User feedback collection
    """
    
    # Initialize evaluation
    evaluation = {
        "type": "outcome",
        "score": 0.0,
        # Start at 0, add points for what was found
        # Why start at 0: Build up score based on completeness
        
        "completeness": {},
        # What was found
        
        "missing": [],
        # What's missing
        
        "quality_notes": []
        # Notes about quality
    }
    
    # Check what information was gathered
    # Each utility found = +0.16 points (total 0.8 for all 5)
    # AHJ found = +0.2 points
    # Total = 1.0 if everything found
    
    # Check 1: AHJ identified
    if state.get("identified_ahj"):
        # AHJ was found
        evaluation["score"] += 0.2
        # 20% of score for AHJ
        
        evaluation["completeness"]["ahj"] = True
        # Mark as complete
    else:
        # AHJ not found
        evaluation["missing"].append("Authority Having Jurisdiction (AHJ)")
        evaluation["completeness"]["ahj"] = False
    
    # Check 2: Gas provider
    if state.get("gas_provider"):
        evaluation["score"] += 0.16
        evaluation["completeness"]["gas"] = True
    else:
        evaluation["missing"].append("Gas Provider")
        evaluation["completeness"]["gas"] = False
    
    # Check 3: Electric provider
    if state.get("electric_provider"):
        evaluation["score"] += 0.16
        evaluation["completeness"]["electric"] = True
    else:
        evaluation["missing"].append("Electric Provider")
        evaluation["completeness"]["electric"] = False
    
    # Check 4: Water provider
    if state.get("water_provider"):
        evaluation["score"] += 0.16
        evaluation["completeness"]["water"] = True
    else:
        evaluation["missing"].append("Water Provider")
        evaluation["completeness"]["water"] = False
    
    # Check 5: Sewer provider
    if state.get("sewer_provider"):
        evaluation["score"] += 0.16
        evaluation["completeness"]["sewer"] = True
    else:
        evaluation["missing"].append("Sewer Provider")
        evaluation["completeness"]["sewer"] = False
    
    # Check 6: Stormwater authority
    if state.get("stormwater_authority"):
        evaluation["score"] += 0.16
        evaluation["completeness"]["stormwater"] = True
    else:
        evaluation["missing"].append("Stormwater Authority")
        evaluation["completeness"]["stormwater"] = False
    
    # Quality assessment
    output = state.get("output", "")
    # output: Final answer text
    
    if len(output) > 100:
        # Substantial answer
        # Why 100: Reasonable minimum for informative answer
        evaluation["quality_notes"].append(
            "Answer is substantial (>100 characters)"
        )
    else:
        # Short answer might be incomplete
        evaluation["quality_notes"].append(
            "Answer is short - may be incomplete"
        )
    
    # Check if answer mentions sources
    if "http" in output or "www." in output:
        # Answer includes URLs
        # Why check: Shows answer is grounded
        evaluation["quality_notes"].append(
            "Answer includes source URLs (good grounding)"
        )
    
    return evaluation


# ==============================================================================
# Efficiency Evaluator
# ==============================================================================
def evaluate_efficiency(state: AgentState) -> Dict[str, Any]:
    """
    Evaluate agent efficiency metrics.
    
    Metrics evaluated:
    - Iterations: How many reasoning steps
    - Message count: Total messages exchanged
    - Tool calls: How many tools were invoked
    - Tokens (if available): API usage
    
    Function Name: "evaluate_efficiency"
    - "efficiency": Resource usage and performance
    - Why: Understand cost and speed
    
    Args:
        state (AgentState): Final state
    
    Returns:
        Dict[str, Any]: Efficiency metrics
            - iterations: Number of reasoning loops
            - messages: Total message count
            - tool_calls: Total tool invocations
            - efficiency_score: 0.0 to 1.0 (higher = more efficient)
    """
    
    # Extract metrics
    iterations = state.get("iterations", 0)
    messages = state.get("messages", [])
    
    # Count tool calls
    tool_call_count = 0
    for message in messages:
        if hasattr(message, "tool_calls") and message.tool_calls:
            tool_call_count += len(message.tool_calls)
    
    # Calculate efficiency score
    # Lower iterations and tool calls = higher efficiency
    # Perfect score: 1-5 iterations, 1-10 tool calls
    # Score decreases with more iterations/calls
    
    efficiency_score = 1.0
    
    # Penalize high iterations
    if iterations > 15:
        efficiency_score -= (iterations - 15) * 0.05
    
    # Penalize excessive tool calls
    if tool_call_count > 20:
        efficiency_score -= (tool_call_count - 20) * 0.02
    
    # Clamp to [0, 1]
    efficiency_score = max(0.0, min(1.0, efficiency_score))
    
    return {
        "type": "efficiency",
        "iterations": iterations,
        "message_count": len(messages),
        "tool_call_count": tool_call_count,
        "efficiency_score": efficiency_score,
        "notes": [
            f"Completed in {iterations} iterations",
            f"Made {tool_call_count} tool calls",
            f"Exchanged {len(messages)} messages"
        ]
    }


# ==============================================================================
# Grounding Evaluator
# ==============================================================================
def evaluate_grounding(state: AgentState) -> Dict[str, Any]:
    """
    Evaluate whether answers are grounded in sources.
    
    Grounding check:
    - Are sources cited in final answer?
    - Are tool results included in answer?
    - Can claims be traced to sources?
    
    Function Name: "evaluate_grounding"
    - "grounding": Factual basis for claims
    - Why: Ensure accuracy and verifiability
    
    Args:
        state (AgentState): Final state
    
    Returns:
        Dict[str, Any]: Grounding assessment
            - has_sources: Boolean
            - source_count: Number of sources mentioned
            - grounding_score: 0.0 to 1.0
    """
    
    output = state.get("output", "")
    messages = state.get("messages", [])
    
    # Count sources in output
    # Look for URLs as evidence of source citation
    source_indicators = ["http", "www.", ".com", ".org", ".gov"]
    source_count = sum(1 for indicator in source_indicators if indicator in output)
    
    # Check if tool results are reflected
    # Count tool messages
    tool_message_count = sum(1 for msg in messages 
                            if hasattr(msg, "type") and msg.type == "tool")
    
    # Calculate grounding score
    grounding_score = 0.0
    
    # Add points for sources
    if source_count > 0:
        grounding_score += 0.5
    
    # Add points if tool results were used
    if tool_message_count > 0 and len(output) > 0:
        grounding_score += 0.5
    
    return {
        "type": "grounding",
        "has_sources": source_count > 0,
        "source_count": source_count,
        "tool_results_used": tool_message_count,
        "grounding_score": grounding_score,
        "notes": [
            f"Found {source_count} source indicators in answer",
            f"Agent used {tool_message_count} tool results"
        ]
    }


# ==============================================================================
# Comprehensive Evaluation
# ==============================================================================
def evaluate_agent_run(state: AgentState) -> Dict[str, Any]:
    """
    Run all evaluations and return comprehensive results.
    
    Function Name: "evaluate_agent_run"
    - "evaluate_agent_run": Complete evaluation of one execution
    - Why: Convenience function for full assessment
    
    Args:
        state (AgentState): Final state
    
    Returns:
        Dict[str, Any]: All evaluation results
            - trajectory: Trajectory evaluation
            - outcome: Outcome evaluation
            - efficiency: Efficiency metrics
            - grounding: Grounding assessment
            - overall_score: Weighted average
    """
    
    # Run all evaluators
    trajectory_eval = evaluate_trajectory(state)
    outcome_eval = evaluate_outcome(state)
    efficiency_eval = evaluate_efficiency(state)
    grounding_eval = evaluate_grounding(state)
    
    # Calculate overall score (weighted average)
    # Weights: Outcome (40%), Trajectory (30%), Grounding (20%), Efficiency (10%)
    overall_score = (
        outcome_eval["score"] * 0.4 +
        trajectory_eval["score"] * 0.3 +
        grounding_eval["grounding_score"] * 0.2 +
        efficiency_eval["efficiency_score"] * 0.1
    )
    
    return {
        "trajectory": trajectory_eval,
        "outcome": outcome_eval,
        "efficiency": efficiency_eval,
        "grounding": grounding_eval,
        "overall_score": overall_score,
        "summary": {
            "score": overall_score,
            "completed": bool(state.get("output")),
            "iterations": state.get("iterations", 0),
            "completeness_percentage": outcome_eval["score"] * 100
        }
    }


# ==============================================================================
# Usage Example
# ==============================================================================
#
# from agent.graph import run_agent
# from evaluation import evaluate_agent_run
#
# # Run agent
# result = run_agent("Find utilities for Johnson City, TN")
#
# # Evaluate
# evaluation = evaluate_agent_run(result)
#
# # Print results
# print(f"Overall Score: {evaluation['overall_score']:.2f}")
# print(f"Trajectory: {evaluation['trajectory']['score']:.2f}")
# print(f"Outcome: {evaluation['outcome']['score']:.2f}")
# print(f"Efficiency: {evaluation['efficiency']['efficiency_score']:.2f}")
# print(f"Grounding: {evaluation['grounding']['grounding_score']:.2f}")

