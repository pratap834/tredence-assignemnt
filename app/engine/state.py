from typing import Any, Dict
from pydantic import BaseModel
from datetime import datetime

class WorkflowState(BaseModel):
    data: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    iteration: int = 0
    
    class Config:
        arbitrary_types_allowed = True

    def get(self, key: str, default=None):
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        self.data[key] = value
    
    def update(self, updates: Dict[str, Any]):
        self.data.update(updates)
