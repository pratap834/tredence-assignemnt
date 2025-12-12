# Workflow Engine

A simple but powerful workflow engine for building multi-step agent workflows with state management, conditional routing, and looping.

## Features

- **Node-based workflow execution** - Define steps as Python functions
- **State management** - Shared state flows through the workflow
- **Conditional edges** - Dynamic routing based on state conditions
- **Loop support** - Run workflows until conditions are met
- **FastAPI endpoints** - RESTful API for creating and running workflows
- **Code review workflow** - Example implementation with quality analysis

## Project Structure

```
app/
├── main.py              # FastAPI application entry point
├── engine/              # Core workflow engine
│   ├── graph.py         # Graph execution logic
│   ├── node.py          # Node definitions
│   └── state.py         # State management
├── api/                 # API layer
│   ├── routes.py        # HTTP endpoints
│   └── models.py        # Request/response models
├── tools/               # Tool registry
│   ├── registry.py      # Tool management
│   └── code_tools.py    # Code analysis tools
└── workflows/           # Workflow implementations
    └── code_review.py   # Code review agent
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Usage

### Create a workflow

```bash
curl -X POST "http://localhost:8000/graph/create" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "code_review",
    "config": {"max_iterations": 3}
  }'
```

Response:
```json
{
  "graph_id": "abc-123-def",
  "message": "Graph created successfully with type: code_review"
}
```

### Run a workflow

```bash
curl -X POST "http://localhost:8000/graph/run" \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "abc-123-def",
    "initial_state": {
      "code": "def calculate(a, b, c, d, e, f):\n    result = a + b + c + d + e + f\n    return result",
      "quality_threshold": 75,
      "max_iterations": 3
    }
  }'
```

Response includes:
- `run_id` - Unique identifier for this execution
- `final_state` - Complete state after workflow completion
- `execution_log` - Step-by-step execution details
- `metadata` - Run statistics (iterations, completion status)

### Get workflow state

```bash
curl -X GET "http://localhost:8000/graph/state/{run_id}"
```

## Code Review Workflow

The included code review workflow demonstrates all engine capabilities:

1. **Extract** - Parse functions from code
2. **Analyze** - Calculate complexity metrics
3. **Detect** - Find code issues
4. **Suggest** - Generate improvement recommendations
5. **Loop** - Repeat until quality threshold is met

The workflow automatically loops back if:
- Quality score is below threshold
- Max iterations not reached

## Engine Capabilities

### Nodes
Nodes are Python functions that receive and modify state:

```python
def my_node(state: WorkflowState) -> Dict[str, Any]:
    return {"new_key": "value"}
```

### Edges
Connect nodes in sequence:

```python
graph.add_edge("node_a", "node_b")
```

### Conditional Edges
Dynamic routing based on state:

```python
def router(state: WorkflowState) -> str:
    if state.get("score") > 80:
        return "success_node"
    return "retry_node"

graph.add_conditional_edge("check_node", router)
```

### Looping
Return a node name to loop back, or `None` to end:

```python
def should_continue(state: WorkflowState) -> str:
    if state.iteration < 5:
        return "start_node"
    return None
```

## API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## What Could Be Improved

With more time, I would add:

- **Persistence** - SQLite/Postgres for graph and run storage
- **WebSocket streaming** - Real-time execution updates
- **Async node execution** - Background tasks for long-running nodes
- **Better error handling** - Retry logic and error recovery
- **Monitoring** - Execution metrics and performance tracking
- **More workflows** - Text summarization, data quality pipelines
- **Graph visualization** - Visual workflow builder
- **Node composition** - Reusable sub-workflows
- **Authentication** - API key management
- **Rate limiting** - Request throttling

## Example Request

Here's a complete example of running the code review workflow:

```python
import requests

# Create workflow
create_response = requests.post(
    "http://localhost:8000/graph/create",
    json={"workflow_type": "code_review", "config": {}}
)
graph_id = create_response.json()["graph_id"]

# Run workflow
run_response = requests.post(
    "http://localhost:8000/graph/run",
    json={
        "graph_id": graph_id,
        "initial_state": {
            "code": """
def process_data(x, y, z, a, b, c, d, e):
    total = x + y + z + a + b + c + d + e
    average = total / 8
    if average > 100:
        return average * 2
    else:
        return average
            """,
            "quality_threshold": 70,
            "max_iterations": 2
        }
    }
)

result = run_response.json()
print(f"Quality Score: {result['final_state']['quality_score']}")
print(f"Suggestions: {len(result['final_state']['suggestions'])}")
```

## License

MIT
