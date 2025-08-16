import random
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

class MyNode:
    def __init__(self, name: str):
        self.name = name
    def __call__(self, state: State):
        return {"messages": [("assistant", f"Called node {self.name}")]}

def route(state) -> Literal["entry_node", "__end__"]:
    if len(state["messages"]) > 10:
        return "__end__"
    return "entry_node"

def add_fractal_nodes(builder, current_node, level, max_level):
    if level > max_level:
        return
    # Number of nodes to create at this level
    num_nodes = random.randint(1, 3)  # Adjust randomness as needed
    for i in range(num_nodes):
        nm = ["A", "B", "C"][i]
        node_name = f"node_{current_node}_{nm}"
        builder.add_node(node_name, MyNode(node_name))
        builder.add_edge(current_node, node_name)
        # Recursively add more nodes
        r = random.random()
        if r > 0.2 and level + 1 < max_level:
            add_fractal_nodes(builder, node_name, level + 1, max_level)
        elif r > 0.05:
            builder.add_conditional_edges(node_name, route, node_name)
        else:
            # End
            builder.add_edge(node_name, "__end__")

def build_fractal_graph(max_level: int):
    builder = StateGraph(State)
    entry_point = "entry_node"
    builder.add_node(entry_point, MyNode(entry_point))
    builder.add_edge(START, entry_point)
    add_fractal_nodes(builder, entry_point, 1, max_level)
    # Optional: set a finish point if required
    builder.add_edge(entry_point, END)  # or any specific node
    return builder.compile()

app = build_fractal_graph(3)

print(app.get_graph().draw_mermaid())

from IPython.display import Image, display
# from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles

display(Image(app.get_graph().draw_mermaid_png()))
from IPython.display import Image, display

try:
    # display(Image(graph.get_graph().draw_mermaid_png()))
    # 获取 PNG 数据
    png_data = app.get_graph().draw_mermaid_png()
    filename = "test-visualize-graph-3-3.png"
    # 保存到本地
    with open(filename, "wb") as f:
        f.write(png_data)

    # 显示图像（确保路径正确）
    display(Image(filename=filename))

except Exception:
    # This requires some extra dependencies and is optional
    pass