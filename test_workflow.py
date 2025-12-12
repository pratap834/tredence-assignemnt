import requests
import json

BASE_URL = "http://localhost:8000"

example_code = """
from typing import List, Dict, Any

def calculate_total(price: float, quantity: int, tax_rate: float, discount: float, shipping: float, handling_fee: float) -> float:
    # Basic validation
    if quantity < 0 or price < 0:
        raise ValueError("price and quantity must be non-negative")
    subtotal = float(price) * int(quantity)
    # compute tax explicitly
    tax = subtotal * float(tax_rate)
    total = subtotal + tax - float(discount) + float(shipping) + float(handling_fee)
    # don't allow negative totals
    if total < 0:
        total = 0.0
    # stable, two-decimal rounding for money
    return round(total, 2)


def process_order(order_id: str, customer_name: str, items: List[Dict[str, Any]], payment_method: str, delivery_address: str, notes: str) -> Dict[str, Any]:
    if not order_id:
        # explicit error instead of silent None
        raise ValueError("order_id is required")

    if not isinstance(items, list):
        raise TypeError("items must be a list")

    subtotal = 0.0
    for i, item in enumerate(items):
        # expect dicts like {'price': .., 'quantity': ..}
        try:
            price = float(item.get("price", 0))
            qty = int(item.get("quantity", 0))
        except Exception as e:
            raise ValueError(f"invalid item at index {i}: {e}")

        if price < 0 or qty < 0:
            raise ValueError(f"negative price/quantity at item index {i}")

        item_total = price * qty
        subtotal += item_total

    # if you want tax/discount/shipping as part of items or top-level, change here.
    total = round(subtotal, 2)

    # apply payment fee
    if (payment_method or "").lower() == 'credit':
        total = round(total * 1.02, 2)

    return {
        'order_id': order_id,
        'customer': customer_name,
        'subtotal': round(subtotal, 2),
        'total': total,
        'payment': payment_method
    }

"""

def test_workflow():
    print("Creating code review workflow...")
    create_response = requests.post(
        f"{BASE_URL}/graph/create",
        json={
            "workflow_type": "code_review",
            "config": {"max_iterations": 5}
        }
    )
    
    if create_response.status_code != 200:
        print(f"Error creating graph: {create_response.text}")
        return
    
    graph_data = create_response.json()
    graph_id = graph_data["graph_id"]
    print(f"Created graph: {graph_id}")
    
    print("\nRunning workflow...")
    run_response = requests.post(
        f"{BASE_URL}/graph/run",
        json={
            "graph_id": graph_id,
            "initial_state": {
                "code": example_code,
                "quality_threshold": 75,
                "max_iterations": 3
            }
        }
    )
    
    if run_response.status_code != 200:
        print(f"Error running graph: {run_response.text}")
        return
    
    result = run_response.json()
    run_id = result["run_id"]
    
    print(f"\nRun ID: {run_id}")
    print(f"Quality Score: {result['final_state'].get('quality_score', 'N/A')}")
    print(f"Functions Found: {result['final_state'].get('function_count', 0)}")
    print(f"Issues Detected: {result['final_state'].get('issue_count', 0)}")
    print(f"Suggestions: {result['final_state'].get('suggestion_count', 0)}")
    print(f"Iterations: {result['metadata'].get('iterations_used', 0)}")
    
    print("\nExecution Log:")
    for log_entry in result["execution_log"]:
        print(f"  - {log_entry['node']}: {log_entry['status']}")
    
    print("\nSuggestions:")
    for suggestion in result['final_state'].get('suggestions', []):
        print(f"  [{suggestion['priority']}] {suggestion['suggestion']}")
    
    print("\nFetching state...")
    state_response = requests.get(f"{BASE_URL}/graph/state/{run_id}")
    
    if state_response.status_code == 200:
        print("State retrieved successfully")
    else:
        print(f"Error fetching state: {state_response.text}")

if __name__ == "__main__":
    try:
        test_workflow()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server.")
        print("Make sure the server is running with: uvicorn app.main:app --reload")
