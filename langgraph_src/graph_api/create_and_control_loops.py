

import operator
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    # The operator.add reducer fn makes this append-only
    aggregate: Annotated[list, operator.add]

def a(state: State):
    print(f'Node A sees {state["aggregate"]}')
    return {"aggregate": ["A"]}

def b(state: State):
    print(f'Node B sees {state["aggregate"]}')
    return {"aggregate": ["B"]}

# Define nodes
builder = StateGraph(State)
builder.add_node(a)
builder.add_node(b)

# Define edges
def route(state: State) -> Literal["b", END]:
    if len(state["aggregate"]) < 7:
        return "b"
    else:
        return END

builder.add_edge(START, "a")
builder.add_conditional_edges("a", route)
builder.add_edge("b", "a")
graph = builder.compile()


if __name__ == "__main__":
    from IPython.display import Image, display

    try:
        # display(Image(graph.get_graph().draw_mermaid_png()))
        # 获取 PNG 数据
        png_data = graph.get_graph().draw_mermaid_png()
        filename = "CreateAndControlLoops.png"
        # 保存到本地
        with open(filename, "wb") as f:
            f.write(png_data)

        # 显示图像（确保路径正确）
        display(Image(filename=filename))

    except Exception:
        # This requires some extra dependencies and is optional
        pass