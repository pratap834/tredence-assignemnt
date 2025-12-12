from typing import Callable, Dict, Any

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
    
    def register(self, name: str, func: Callable):
        self._tools[name] = func
    
    def get(self, name: str) -> Callable:
        return self._tools.get(name)
    
    def call(self, name: str, *args, **kwargs) -> Any:
        tool = self.get(name)
        if not tool:
            raise ValueError(f"Tool {name} not found")
        return tool(*args, **kwargs)
    
    def list_tools(self) -> list:
        return list(self._tools.keys())

registry = ToolRegistry()
