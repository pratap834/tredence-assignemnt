from typing import Dict, Any

class InMemoryStorage:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.graphs = {}
            cls._instance.runs = {}
        return cls._instance
    
    def add_graph(self, graph_id: str, graph: Any):
        self.graphs[graph_id] = graph
    
    def get_graph(self, graph_id: str):
        return self.graphs.get(graph_id)
    
    def list_graphs(self):
        return list(self.graphs.keys())
    
    def add_run(self, run_id: str, run_data: Dict):
        self.runs[run_id] = run_data
    
    def get_run(self, run_id: str):
        return self.runs.get(run_id)
    
    def list_runs(self):
        return list(self.runs.keys())

storage = InMemoryStorage()
