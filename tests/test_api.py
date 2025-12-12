import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import storage

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_storage():
    storage.graphs.clear()
    storage.runs.clear()
    yield
    storage.graphs.clear()
    storage.runs.clear()

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"

def test_create_code_review_graph():
    response = client.post("/graph/create", json={
        "workflow_type": "code_review",
        "config": {"max_iterations": 5}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "graph_id" in data
    assert "message" in data
    assert "code_review" in data["message"]

def test_create_unknown_workflow():
    response = client.post("/graph/create", json={
        "workflow_type": "unknown_type",
        "config": {}
    })
    
    assert response.status_code == 400
    assert "Unknown workflow type" in response.json()["detail"]

def test_run_graph_success():
    create_resp = client.post("/graph/create", json={
        "workflow_type": "code_review",
        "config": {}
    })
    graph_id = create_resp.json()["graph_id"]
    
    run_resp = client.post("/graph/run", json={
        "graph_id": graph_id,
        "initial_state": {
            "code": "def simple_function():\n    return 42",
            "quality_threshold": 50,
            "max_iterations": 2
        }
    })
    
    assert run_resp.status_code == 200
    data = run_resp.json()
    
    assert "run_id" in data
    assert "final_state" in data
    assert "execution_log" in data
    assert "metadata" in data
    assert "function_count" in data["final_state"]
    assert "quality_score" in data["final_state"]

def test_run_graph_not_found():
    response = client.post("/graph/run", json={
        "graph_id": "non-existent-id",
        "initial_state": {"code": "def test(): pass"}
    })
    
    assert response.status_code == 404
    assert "Graph not found" in response.json()["detail"]

def test_get_state_success():
    create_resp = client.post("/graph/create", json={
        "workflow_type": "code_review",
        "config": {}
    })
    graph_id = create_resp.json()["graph_id"]
    
    run_resp = client.post("/graph/run", json={
        "graph_id": graph_id,
        "initial_state": {
            "code": "def test(): pass",
            "quality_threshold": 60
        }
    })
    run_id = run_resp.json()["run_id"]
    
    state_resp = client.get(f"/graph/state/{run_id}")
    
    assert state_resp.status_code == 200
    data = state_resp.json()
    assert data["run_id"] == run_id
    assert "state" in data
    assert "metadata" in data

def test_get_state_not_found():
    response = client.get("/graph/state/invalid-run-id")
    
    assert response.status_code == 404
    assert "Run not found" in response.json()["detail"]

def test_list_graphs():
    client.post("/graph/create", json={
        "workflow_type": "code_review",
        "config": {}
    })
    client.post("/graph/create", json={
        "workflow_type": "code_review",
        "config": {}
    })
    
    response = client.get("/graph/list")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["graphs"]) == 2

def test_list_runs():
    create_resp = client.post("/graph/create", json={
        "workflow_type": "code_review",
        "config": {}
    })
    graph_id = create_resp.json()["graph_id"]
    
    client.post("/graph/run", json={
        "graph_id": graph_id,
        "initial_state": {"code": "def a(): pass"}
    })
    client.post("/graph/run", json={
        "graph_id": graph_id,
        "initial_state": {"code": "def b(): pass"}
    })
    
    response = client.get("/graph/runs")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["runs"]) == 2

def test_code_review_workflow_loop():
    create_resp = client.post("/graph/create", json={
        "workflow_type": "code_review",
        "config": {"max_iterations": 10}
    })
    graph_id = create_resp.json()["graph_id"]
    
    complex_code = """
def complex_function(a, b, c, d, e, f, g):
    if a > 10:
        result = a + b + c
    else:
        result = d + e + f + g
    for i in range(100):
        result += i
    return result
"""
    
    run_resp = client.post("/graph/run", json={
        "graph_id": graph_id,
        "initial_state": {
            "code": complex_code,
            "quality_threshold": 80,
            "max_iterations": 5
        }
    })
    
    assert run_resp.status_code == 200
    data = run_resp.json()
    
    assert data["metadata"]["iterations_used"] > 0
    assert "suggestions" in data["final_state"]
