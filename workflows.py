from typing import List, Dict, Any


def code_review_workflow_spec() -> Dict[str, Any]:
    """
    Code Review Mini-Agent:
    1) extract functions
    2) check complexity
    3) detect issues
    4) suggest improvements
    5) compute quality and loop until quality_score >= threshold
    """
    nodes: List[Dict[str, Any]] = [
        {
            "name": "extract",
            "tool_name": "extract_functions",
            "next_node": "complexity",
        },
        {
            "name": "complexity",
            "tool_name": "check_complexity",
            "next_node": "issues",
        },
        {
            "name": "issues",
            "tool_name": "detect_issues",
            "next_node": "suggest",
        },
        {
            "name": "suggest",
            "tool_name": "suggest_improvements",
            "next_node": "quality",
        },
        {
            "name": "quality",
            "tool_name": "compute_quality",
            "next_node": None,          # stop when condition met
            "loop_until": "quality_score",
            "loop_condition": "ge",     # quality_score >= threshold
        },
    ]
    return {
        "start_node": "extract",
        "nodes": nodes,
    }
