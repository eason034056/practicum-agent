"""
Evaluation Package

This package provides tools for evaluating agent performance,
implementing AgentOps best practices.

Evaluation Types:
1. Trajectory Evaluation - Analyze reasoning path
2. Outcome Evaluation - Verify final answer
3. Efficiency Metrics - Iterations, time, cost
4. Grounding Check - Verify source citations

Why Evaluation Matters:
- Quality Assurance: Ensure agent provides accurate information
- Debugging: Identify where agent makes mistakes
- Optimization: Find opportunities for improvement
- Compliance: Verify adherence to requirements
"""

from evaluation.evaluators import (
    evaluate_trajectory,
    evaluate_outcome,
    evaluate_efficiency,
    evaluate_grounding
)

__all__ = [
    "evaluate_trajectory",
    "evaluate_outcome",
    "evaluate_efficiency",
    "evaluate_grounding"
]

