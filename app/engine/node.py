from typing import Callable, Any
from app.engine.state import WorkflowState

class Node:
    def __init__(self, name: str, func: Callable, condition: Callable = None):
        self.name = name
        self.func = func
        self.condition = condition
    
    async def execute(self, state: WorkflowState) -> WorkflowState:
        result = self.func(state)
        if result and isinstance(result, dict):
            state.update(result)
        return state
    
    def should_execute(self, state: WorkflowState) -> bool:
        if self.condition:
            return self.condition(state)
        return True
