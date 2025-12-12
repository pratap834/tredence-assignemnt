from app.engine.graph import WorkflowGraph
from app.engine.state import WorkflowState
from app.tools.code_tools import (
    extract_functions,
    check_complexity,
    detect_issues,
    suggest_improvements,
    calculate_quality_score
)
from typing import Dict, Any

def extract_node(state: WorkflowState) -> Dict[str, Any]:
    code = state.get("code", "")
    result = extract_functions(code)
    
    return {
        "functions": result["functions"],
        "function_count": result["count"]
    }

def analyze_node(state: WorkflowState) -> Dict[str, Any]:
    functions = state.get("functions", [])
    complexity = check_complexity(functions)
    
    return {
        "complexity_scores": complexity["scores"],
        "average_complexity": complexity["average"],
        "high_complexity_funcs": complexity["high_complexity"]
    }

def detect_node(state: WorkflowState) -> Dict[str, Any]:
    code = state.get("code", "")
    functions = state.get("functions", [])
    issues = detect_issues(code, functions)
    
    return {
        "issues": issues["issues"],
        "issue_count": issues["count"]
    }

def suggest_node(state: WorkflowState) -> Dict[str, Any]:
    complexity_data = {
        "average": state.get("average_complexity", 0),
        "high_complexity": state.get("high_complexity_funcs", [])
    }
    issues_data = {
        "issues": state.get("issues", [])
    }
    
    suggestions = suggest_improvements(complexity_data, issues_data)
    quality_score = calculate_quality_score(complexity_data, issues_data)
    
    state.iteration += 1
    
    return {
        "suggestions": suggestions["suggestions"],
        "suggestion_count": suggestions["count"],
        "quality_score": quality_score
    }

def should_continue(state: WorkflowState) -> str:
    threshold = state.get("quality_threshold", 70)
    score = state.get("quality_score", 0)
    max_iterations = state.get("max_iterations", 3)
    
    if score >= threshold:
        return None
    
    if state.iteration >= max_iterations:
        return None
    
    return "extract"

def create_code_review_graph(graph_id: str, config: Dict[str, Any]) -> WorkflowGraph:
    graph = WorkflowGraph(graph_id)
    
    graph.add_node("extract", extract_node)
    graph.add_node("analyze", analyze_node)
    graph.add_node("detect", detect_node)
    graph.add_node("suggest", suggest_node)
    
    graph.add_edge("extract", "analyze")
    graph.add_edge("analyze", "detect")
    graph.add_edge("detect", "suggest")
    graph.add_conditional_edge("suggest", should_continue)
    
    graph.set_start("extract")
    
    if "max_iterations" in config:
        graph.max_iterations = config["max_iterations"]
    
    return graph
