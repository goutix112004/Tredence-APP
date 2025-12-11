from typing import Callable, Dict, Any, List, Optional
from pydantic import BaseModel
import uuid


class State(BaseModel):
    code: str
    functions: List[str] = []
    complexity_score: float = 0.0
    issues: int = 0
    suggestions: List[str] = []
    quality_score: float = 0.0
    threshold: float = 0.8
    loop_count: int = 0
    max_loops: int = 5


class Node(BaseModel):
    name: str
    tool_name: str
    next_node: Optional[str] = None
    branch_on: Optional[str] = None  # state field name
    branch_map: Optional[Dict[str, str]] = None  # value -> next_node
    loop_until: Optional[str] = None  # state field name to check
    loop_condition: Optional[str] = None  # "ge" / "le" etc.


class Graph(BaseModel):
    id: str
    nodes: Dict[str, Node]
    start_node: str


class RunLogEntry(BaseModel):
    node: str
    state_snapshot: Dict[str, Any]


class Run(BaseModel):
    id: str
    graph_id: str
    logs: List[RunLogEntry] = []
    final_state: Optional[State] = None
    finished: bool = False


class GraphEngine:
    def __init__(self, tools: Dict[str, Callable[[State], State]]):
        self.tools = tools
        self.graphs: Dict[str, Graph] = {}
        self.runs: Dict[str, Run] = {}

    def create_graph(self, nodes_spec: List[Dict[str, Any]], start_node: str) -> str:
        graph_id = str(uuid.uuid4())
        nodes: Dict[str, Node] = {}
        for spec in nodes_spec:
            node = Node(**spec)
            nodes[node.name] = node
        graph = Graph(id=graph_id, nodes=nodes, start_node=start_node)
        self.graphs[graph_id] = graph
        return graph_id

    def _eval_loop_condition(self, state: State, field: str, cond: str, target: float) -> bool:
        value = getattr(state, field)
        if cond == "ge":
            return value >= target
        if cond == "le":
            return value <= target
        return False

    def run_graph(self, graph_id: str, initial_state: Dict[str, Any]) -> Run:
        graph = self.graphs[graph_id]
        state = State(**initial_state)
        run_id = str(uuid.uuid4())
        run = Run(id=run_id, graph_id=graph_id, logs=[])
        self.runs[run_id] = run

        current_name = graph.start_node
        while current_name is not None:
            node = graph.nodes[current_name]
            tool = self.tools[node.tool_name]
            state = tool(state)

            run.logs.append(
                RunLogEntry(node=current_name, state_snapshot=state.dict())
            )

            # Loop handling
            if node.loop_until and node.loop_condition:
                # For this assignment, compare against state.threshold
                target = state.threshold
                if self._eval_loop_condition(state, node.loop_until, node.loop_condition, target):
                    # loop done
                    current_name = node.next_node
                else:
                    # loop again on same node sequence; simple guard
                    state.loop_count += 1
                    if state.loop_count >= state.max_loops:
                        current_name = node.next_node
                continue

            # Branching
            if node.branch_on and node.branch_map:
                key = str(getattr(state, node.branch_on))
                current_name = node.branch_map.get(key, node.next_node)
            else:
                current_name = node.next_node

        run.final_state = state
        run.finished = True
        self.runs[run_id] = run
        return run

    def get_run_state(self, run_id: str) -> Run:
        return self.runs[run_id]
