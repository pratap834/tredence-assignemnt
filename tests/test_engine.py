import pytest
from app.engine.node import Node
from app.engine.state import WorkflowState
from app.engine.graph import WorkflowGraph

def test_node_execution():
    def add_value(state):
        return {"count": state.get("count", 0) + 1}
    
    node = Node(name="increment", func=add_value)
    state = WorkflowState(data={"count": 0})
    result = node.execute(state)
    
    assert result.data["count"] == 1

def test_node_with_condition():
    def process(state):
        return {"value": 10}
    
    def check_condition(state):
        return state.get("value", 0) > 5
    
    node = Node(name="check", func=process, condition=check_condition)
    
    state_high = WorkflowState(data={"value": 8})
    assert node.should_execute(state_high) == True
    
    state_low = WorkflowState(data={"value": 3})
    assert node.should_execute(state_low) == False

def test_state_operations():
    state = WorkflowState(data={"key1": "value1"})
    
    assert state.get("key1") == "value1"
    assert state.get("missing", "default") == "default"
    
    state.set("key2", "value2")
    assert state.get("key2") == "value2"
    
    state.update({"key3": "value3", "key4": "value4"})
    assert state.get("key3") == "value3"
    assert state.get("key4") == "value4"

@pytest.mark.asyncio
async def test_graph_linear_execution():
    def step1(state):
        return {"step": 1}
    
    def step2(state):
        return {"step": 2}
    
    def step3(state):
        return {"step": 3}
    
    graph = WorkflowGraph()
    graph.add_node("step1", step1)
    graph.add_node("step2", step2)
    graph.add_node("step3", step3)
    graph.add_edge("step1", "step2")
    graph.add_edge("step2", "step3")
    
    state, log = await graph.run({"start": True})
    
    assert state.data["step"] == 3
    assert len(log) == 3
    assert all(entry["status"] == "success" for entry in log)

@pytest.mark.asyncio
async def test_graph_conditional_branching():
    def check(state):
        return {"value": 10}
    
    def path_a(state):
        return {"path": "A"}
    
    def path_b(state):
        return {"path": "B"}
    
    def router(state):
        if state.get("value", 0) > 5:
            return "path_a"
        return "path_b"
    
    graph = WorkflowGraph()
    graph.add_node("check", check)
    graph.add_node("path_a", path_a)
    graph.add_node("path_b", path_b)
    graph.add_edge("check", "path_a")
    graph.add_conditional_edge("check", router)
    
    state, log = await graph.run({"start": True})
    
    assert state.data["path"] == "A"
    assert state.data["value"] == 10

@pytest.mark.asyncio
async def test_graph_loop_termination():
    def increment(state):
        state.iteration += 1
        return {"counter": state.get("counter", 0) + 1}
    
    def should_loop(state):
        if state.get("counter", 0) < 5:
            return "increment"
        return None
    
    graph = WorkflowGraph()
    graph.add_node("increment", increment)
    graph.add_conditional_edge("increment", should_loop)
    
    state, log = await graph.run({"counter": 0})
    
    assert state.data["counter"] == 5
    assert len(log) == 5

@pytest.mark.asyncio
async def test_graph_max_iterations_safety():
    def infinite_loop(state):
        return {"count": state.get("count", 0) + 1}
    
    def always_loop(state):
        return "infinite_loop"
    
    graph = WorkflowGraph()
    graph.max_iterations = 10
    graph.add_node("infinite_loop", infinite_loop)
    graph.add_conditional_edge("infinite_loop", always_loop)
    
    state, log = await graph.run({"count": 0})
    
    assert len(log) == 10
    assert state.metadata["iterations_used"] == 10

@pytest.mark.asyncio
async def test_graph_error_handling():
    def failing_node(state):
        raise ValueError("Intentional error")
    
    def success_node(state):
        return {"success": True}
    
    graph = WorkflowGraph()
    graph.add_node("fail", failing_node)
    graph.add_node("success", success_node)
    graph.add_edge("fail", "success")
    
    state, log = await graph.run({})
    
    assert log[0]["status"] == "error"
    assert "Intentional error" in log[0]["error"]
    assert len(log) == 1
