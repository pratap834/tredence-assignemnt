from typing import Dict, List, Callable, Any, Optional
from app.engine.node import Node
from app.engine.state import WorkflowState
import uuid
from datetime import datetime

class WorkflowGraph:
    def __init__(self, graph_id: str = None):
        self.graph_id = graph_id or str(uuid.uuid4())
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, str] = {}
        self.conditional_edges: Dict[str, Callable] = {}
        self.start_node: Optional[str] = None
        self.max_iterations = 50
    
    def add_node(self, name: str, func: Callable, condition: Callable = None):
        self.nodes[name] = Node(name, func, condition)
        if not self.start_node:
            self.start_node = name
    
    def add_edge(self, from_node: str, to_node: str):
        self.edges[from_node] = to_node
    
    def add_conditional_edge(self, from_node: str, condition_func: Callable):
        self.conditional_edges[from_node] = condition_func
    
    def set_start(self, node_name: str):
        self.start_node = node_name
    
    async def run(self, initial_state: Dict[str, Any], run_id: str = None) -> tuple[WorkflowState, List[Dict]]:
        if not run_id:
            run_id = str(uuid.uuid4())
            
        state = WorkflowState(data=initial_state, metadata={"run_id": run_id})
        execution_log = []
        
        current_node_name = self.start_node
        iterations = 0
        
        while current_node_name and iterations < self.max_iterations:
            if current_node_name not in self.nodes:
                break
                
            node = self.nodes[current_node_name]
            
            if not node.should_execute(state):
                execution_log.append({
                    "node": current_node_name,
                    "status": "skipped",
                    "iteration": state.iteration,
                    "timestamp": datetime.utcnow().isoformat()
                })
                current_node_name = self.edges.get(current_node_name)
                continue
            
            try:
                state = await node.execute(state)
                execution_log.append({
                    "node": current_node_name,
                    "status": "success",
                    "iteration": state.iteration,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                execution_log.append({
                    "node": current_node_name,
                    "status": "error",
                    "error": str(e),
                    "iteration": state.iteration,
                    "timestamp": datetime.utcnow().isoformat()
                })
                break
            
            if current_node_name in self.conditional_edges:
                next_node = self.conditional_edges[current_node_name](state)
                current_node_name = next_node
            elif current_node_name in self.edges:
                current_node_name = self.edges[current_node_name]
            else:
                current_node_name = None
            
            iterations += 1
        
        state.metadata["iterations_used"] = iterations
        state.metadata["completed"] = current_node_name is None
        
        return state, execution_log
