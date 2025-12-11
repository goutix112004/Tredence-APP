from typing import Dict, Callable
from .engine import State


def extract_functions(state: State) -> State:
    # Very naive: treat each "def" as a function
    lines = state.code.splitlines()
    funcs = [line.strip() for line in lines if line.strip().startswith("def ")]
    state.functions = funcs
    return state


def check_complexity(state: State) -> State:
    # Silly heuristic: more lines => higher complexity
    num_lines = len(state.code.splitlines())
    state.complexity_score = min(1.0, num_lines / 100.0)
    return state


def detect_issues(state: State) -> State:
    # Count "TODO" and "print(" as "issues"
    text = state.code
    state.issues = text.count("TODO") + text.count("print(")
    return state


def suggest_improvements(state: State) -> State:
    suggestions = []
    if state.complexity_score > 0.5:
        suggestions.append("Refactor large functions into smaller ones.")
    if state.issues > 0:
        suggestions.append("Remove debug prints and resolve TODO comments.")
    if not suggestions:
        suggestions.append("Code looks clean. Consider adding more tests.")
    state.suggestions = suggestions
    return state


def compute_quality(state: State) -> State:
    # Simple rule-based quality score
    base = 1.0 - state.complexity_score
    penalty = min(0.5, state.issues * 0.05)
    state.quality_score = max(0.0, base - penalty)
    return state


def get_tool_registry() -> Dict[str, Callable[[State], State]]:
    return {
        "extract_functions": extract_functions,
        "check_complexity": check_complexity,
        "detect_issues": detect_issues,
        "suggest_improvements": suggest_improvements,
        "compute_quality": compute_quality,
    }
