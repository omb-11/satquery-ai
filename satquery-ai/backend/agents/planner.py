from typing import List, Dict, Any
from .state import AgentState

class TaskPlanner:
    def plan(self, state: AgentState) -> List[Dict[str, Any]]:
        plan = []
        for tool in state.selected_tools:
            plan.append({
                'tool': tool,
                'parameters': {
                    'input_paths': state.input_paths,
                    'query': state.query
                }
            })
        return plan
