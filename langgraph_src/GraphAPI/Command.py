import random
from operator import add
from typing import Sequence

from sqlalchemy.sql.annotation import Annotated
from sympy import print_glsl
from typing_extensions import TypedDict, Literal
from langgraph.graph import StateGraph, START
from langgraph.types import Command

# Define graph state
class State(TypedDict):
    foo: str

# Define the nodes

def node_a(state: State) -> Command[Literal["node_b", "node_c"]]:
    print("Called A")
    value = random.choice(["b", "c"])
    # this is a replacement for a conditional edge function
    if value == "b":
        goto = "node_b"
    else:
        goto = "node_c"

    # note how Command allows you to BOTH update the graph state AND route to the next node
    return Command(
        # this is the state update
        # update={"foo": value},
        update={"foo": goto},
        # this is a replacement for an edge
        goto=goto,
    )

def node_b(state: State):
    print("Called B")
    print(state)

    return {"foo": state["foo"] + "b"}

def node_c(state: State):
    print("Called C")
    print(state)
    return {"foo": state["foo"] + "c"}


builder = StateGraph(State)
builder.add_edge(START, "node_a")
builder.add_node(node_a)
builder.add_node(node_b)
builder.add_node(node_c)
# NOTE: there are no edges between nodes A, B and C!

graph = builder.compile()

if __name__ == "__main__":
    # from IPython.display import Image, display
    #
    # try:
    #     # display(Image(graph.get_graph().draw_mermaid_png()))
    #     # 获取 PNG 数据
    #     png_data = graph.get_graph().draw_mermaid_png()
    #     filename = "Command2.png"
    #     # 保存到本地
    #     with open(filename, "wb") as f:
    #         f.write(png_data)
    #
    #     # 显示图像（确保路径正确）
    #     display(Image(filename=filename))
    #
    # except Exception:
    #     # This requires some extra dependencies and is optional
    #     pass
    graph.invoke({"foo": "sdfsfsf"})