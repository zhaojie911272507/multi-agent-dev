from operator import add
from typing import Annotated

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict


class State(TypedDict):
    foo: str
    bar: Annotated[list[str], add]


def node_a(state: State) -> State:
    return {"foo": "a", "bar": ["a"]}


def node_b(state: State) -> State:
    return {"foo": "b", "bar": ["b"]}


workflow = StateGraph(State)
workflow.add_node(node_a)
workflow.add_node(node_b)
workflow.add_edge(START, "node_a")
workflow.add_edge("node_a", "node_b")
workflow.add_edge("node_b", END)

graph = workflow.compile()
print(graph.invoke({"foo": "", "bar": []}))
