from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph
from typing_extensions import TypedDict
from sqlalchemy.sql.annotation import Annotated

# list = [1, 2, 3, 4, 5]
# print(list.extend([3, 4, 5, 6, 7]))
# print(list)


from operator import add
class A(TypedDict):
    a : str
    b : Annotated[list[str], add]



t = A(a="a", b=[1, 2, 3, 4, 5])
# a = A(b=2)

print(t)





from typing import Annotated
from typing_extensions import TypedDict
from operator import add

class State(TypedDict):
    foo: str
    bar: Annotated[list[str], add]

def node_a(state: State)-> State:

    return {"foo": "a", "bar": ["a"]}

def node_b(state: State) -> State:
    return {"foo": "b", "bar": ["b"]}

workflow = StateGraph(State)
workflow.add_node(node_a)
workflow.add_node(node_b)
workflow.add_edge(START, "node_a")
workflow.add_edge("node_a", "node_b")
workflow.add_edge("node_b", END)

print(workflow.complile("node_a"))
