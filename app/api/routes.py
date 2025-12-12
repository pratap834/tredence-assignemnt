from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.api.models import GraphCreate, GraphRun, GraphResponse, RunResponse, StateResponse, AsyncRunResponse
from app.workflows.code_review import create_code_review_graph
from app.storage import storage
from typing import Dict
import uuid

router = APIRouter(prefix="/graph", tags=["graph"])

@router.post("/create", response_model=GraphResponse)
async def create_graph(request: GraphCreate):
    graph_id = str(uuid.uuid4())
    
    if request.workflow_type == "code_review":
        graph = create_code_review_graph(graph_id, request.config)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown workflow type: {request.workflow_type}")
    
    storage.add_graph(graph_id, graph)
    
    return GraphResponse(
        graph_id=graph_id,
        message=f"Graph created successfully with type: {request.workflow_type}"
    )

@router.post("/run", response_model=RunResponse)
async def run_graph(request: GraphRun):
    graph = storage.get_graph(request.graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")
    
    run_id = str(uuid.uuid4())
    
    final_state, execution_log = await graph.run(request.initial_state, run_id)
    
    storage.add_run(run_id, {
        "state": final_state.data,
        "metadata": final_state.metadata,
        "log": execution_log
    })
    
    return RunResponse(
        run_id=run_id,
        final_state=final_state.data,
        execution_log=execution_log,
        metadata=final_state.metadata
    )

@router.get("/state/{run_id}", response_model=StateResponse)
async def get_state(run_id: str):
    run_data = storage.get_run(run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return StateResponse(
        run_id=run_id,
        state=run_data["state"],
        metadata=run_data["metadata"]
    )

@router.get("/list")
async def list_graphs():
    graph_list = storage.list_graphs()
    return {
        "graphs": graph_list,
        "total": len(graph_list)
    }

@router.get("/runs")
async def list_runs():
    run_list = storage.list_runs()
    return {
        "runs": run_list,
        "total": len(run_list)
    }

async def execute_graph_background(graph_id: str, initial_state: Dict, run_id: str):
    try:
        graph = storage.get_graph(graph_id)
        if not graph:
            storage.add_run(run_id, {
                "status": "failed",
                "error": "Graph not found",
                "state": {},
                "metadata": {},
                "log": []
            })
            return
        
        final_state, execution_log = await graph.run(initial_state, run_id)
        
        storage.add_run(run_id, {
            "status": "completed",
            "state": final_state.data,
            "metadata": final_state.metadata,
            "log": execution_log
        })
    except Exception as e:
        storage.add_run(run_id, {
            "status": "failed",
            "error": str(e),
            "state": {},
            "metadata": {},
            "log": []
        })

@router.post("/run-async", response_model=AsyncRunResponse)
async def run_graph_async(request: GraphRun, background_tasks: BackgroundTasks):
    graph = storage.get_graph(request.graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")
    
    run_id = str(uuid.uuid4())
    
    storage.add_run(run_id, {
        "status": "running",
        "state": {},
        "metadata": {},
        "log": []
    })
    
    background_tasks.add_task(
        execute_graph_background,
        request.graph_id,
        request.initial_state,
        run_id
    )
    
    return AsyncRunResponse(
        run_id=run_id,
        status="running",
        message="Graph execution started in background"
    )
