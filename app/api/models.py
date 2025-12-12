from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class GraphCreate(BaseModel):
    workflow_type: str
    config: Optional[Dict[str, Any]] = {}

class GraphRun(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]

class GraphResponse(BaseModel):
    graph_id: str
    message: str

class RunResponse(BaseModel):
    run_id: str
    final_state: Dict[str, Any]
    execution_log: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class StateResponse(BaseModel):
    run_id: str
    state: Dict[str, Any]
    metadata: Dict[str, Any]

class AsyncRunResponse(BaseModel):
    run_id: str
    status: str
    message: str
