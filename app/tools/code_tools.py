import re
import ast
from typing import Dict, List, Any

def extract_functions(code: str) -> Dict[str, Any]:
    functions = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "lineno": node.lineno,
                    "args": len(node.args.args),
                    "lines": node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 1
                })
    except:
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                match = re.search(r'def\s+(\w+)\s*\(', line)
                if match:
                    functions.append({
                        "name": match.group(1),
                        "lineno": i + 1,
                        "args": line.count(',') + 1 if '(' in line else 0,
                        "lines": 1
                    })
    
    return {"functions": functions, "count": len(functions)}

def check_complexity(functions: List[Dict]) -> Dict[str, Any]:
    complexity_scores = []
    for func in functions:
        score = 1
        if func["lines"] > 50:
            score += 3
        elif func["lines"] > 20:
            score += 2
        elif func["lines"] > 10:
            score += 1
        
        if func["args"] > 5:
            score += 2
        elif func["args"] > 3:
            score += 1
        
        complexity_scores.append({
            "name": func["name"],
            "complexity": score,
            "reason": f"lines={func['lines']}, args={func['args']}"
        })
    
    avg_complexity = sum(s["complexity"] for s in complexity_scores) / len(complexity_scores) if complexity_scores else 0
    
    return {
        "scores": complexity_scores,
        "average": avg_complexity,
        "high_complexity": [s for s in complexity_scores if s["complexity"] > 3]
    }

def detect_issues(code: str, functions: List[Dict]) -> Dict[str, Any]:
    issues = []
    
    if len(code) > 5000:
        issues.append({"type": "file_too_large", "severity": "warning", "message": "File is too large"})
    
    for func in functions:
        if len(func["name"]) < 3:
            issues.append({
                "type": "naming",
                "severity": "info",
                "function": func["name"],
                "message": f"Function name '{func['name']}' is too short"
            })
        
        if func["lines"] > 100:
            issues.append({
                "type": "complexity",
                "severity": "warning",
                "function": func["name"],
                "message": f"Function has {func['lines']} lines, consider breaking it down"
            })
    
    lines = code.split('\n')
    for i, line in enumerate(lines):
        if len(line) > 120:
            issues.append({
                "type": "line_length",
                "severity": "info",
                "line": i + 1,
                "message": "Line exceeds 120 characters"
            })
    
    return {"issues": issues, "count": len(issues)}

def suggest_improvements(complexity_data: Dict, issues_data: Dict) -> Dict[str, Any]:
    suggestions = []
    
    if complexity_data["average"] > 3:
        suggestions.append({
            "category": "complexity",
            "suggestion": "Consider refactoring functions with high complexity",
            "priority": "high"
        })
    
    for item in complexity_data["high_complexity"]:
        suggestions.append({
            "category": "refactor",
            "suggestion": f"Refactor {item['name']} - {item['reason']}",
            "priority": "medium"
        })
    
    warning_count = sum(1 for i in issues_data["issues"] if i["severity"] == "warning")
    if warning_count > 5:
        suggestions.append({
            "category": "quality",
            "suggestion": f"Address {warning_count} warnings to improve code quality",
            "priority": "high"
        })
    
    return {"suggestions": suggestions, "count": len(suggestions)}

def calculate_quality_score(complexity_data: Dict, issues_data: Dict) -> float:
    base_score = 100
    
    base_score -= complexity_data["average"] * 5
    base_score -= len(complexity_data["high_complexity"]) * 8
    
    for issue in issues_data["issues"]:
        if issue["severity"] == "warning":
            base_score -= 3
        elif issue["severity"] == "info":
            base_score -= 1
    
    return max(0, min(100, base_score))
