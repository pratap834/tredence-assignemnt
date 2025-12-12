import asyncio
from app.workflows.code_review import create_code_review_graph

async def demo_async():
    print("=== Workflow Engine Demo ===\n")
    
    graph = create_code_review_graph("demo", {})
    
    sample_code = """
def calculate_average(numbers, weights, mode, precision):
    if not numbers:
        return 0
    if mode == "weighted":
        total = sum(n * w for n, w in zip(numbers, weights))
        return round(total / len(numbers), precision)
    else:
        return round(sum(numbers) / len(numbers), precision)
"""
    
    print("Analyzing code...")
    print(sample_code)
    
    initial_state = {
        "code": sample_code,
        "quality_threshold": 75,
        "max_iterations": 2
    }
    
    final_state, log = await graph.run(initial_state)
    
    print("\n=== Results ===")
    print(f"Functions found: {final_state.data.get('function_count', 0)}")
    print(f"Quality score: {final_state.data.get('quality_score', 0):.1f}")
    print(f"Issues detected: {final_state.data.get('issue_count', 0)}")
    print(f"Iterations: {final_state.metadata.get('iterations_used', 0)}")
    
    print("\n=== Execution Log ===")
    for entry in log:
        print(f"  {entry['node']}: {entry['status']}")
    
    print("\n=== Suggestions ===")
    for suggestion in final_state.data.get('suggestions', []):
        print(f"  [{suggestion['priority']}] {suggestion['suggestion']}")

if __name__ == "__main__":
    asyncio.run(demo_async())
