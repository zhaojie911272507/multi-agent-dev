
import operator
import time
from typing import Annotated, Literal, Sequence
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    aggregate: Annotated[list, operator.add]
    # Add a key to the state. We will set this key to determine
    # how we branch.
    which: str

def a(state: State):
    print(f'Adding "A" to {state["aggregate"]}',state["which"])
    return {"aggregate": ["A"], "which": "c"}

def b(state: State):
    print("enter b")
    time.sleep(1)
    for i in range(10):
        time.sleep(1)
        print(f'"B" to {i}')
    print(f'Adding "B" to {state["aggregate"]}')
    return {"aggregate": ["B"]}

def c(state: State):
    print("enter c")
    time.sleep(3)
    for i in range(10):
        time.sleep(1)
        print(f'"C" to {i}')
    print(f'Adding "C" to {state["aggregate"]}')
    return {"aggregate": ["C"]}

def d(state: State):
    print("enter d")
    time.sleep(2)
    for i in range(10):
        time.sleep(1)
        print(f'"D" to {i}')
    print(f'Adding "D" to {state["aggregate"]}')
    return {"aggregate": ["D"]}

builder = StateGraph(State)
builder.add_node(a)
builder.add_node(b)
builder.add_node(c)
builder.add_node(d)
builder.add_edge(START, "a")
builder.add_edge("b", END)
builder.add_edge("c", END)
builder.add_edge("d", END)

# def conditional_edge(state: State) -> Literal["b", "c"]:
#     # Fill in arbitrary logic here that uses the state
#     # to determine the next node
#     return state["which"]

def route_bc_or_cd(state: State) -> Sequence[str]:
    # if state["which"] == "cd":
    #     return ["c", "d"]
    return ["b", "c"]

builder.add_conditional_edges("a", route_bc_or_cd,["b", "c", "d"])
graph = builder.compile()


if __name__ == "__main__":

    result = graph.invoke({"aggregate": [],"which": "cd"})
    print(result)

    from IPython.display import Image, display

    try:
        # display(Image(graph.get_graph().draw_mermaid_png()))
        # 获取 PNG 数据
        png_data = graph.get_graph().draw_mermaid_png()
        filename = "ConditionalBranchingRouteToMultipleNode_validate_path_map.png"
        # 保存到本地
        with open(filename, "wb") as f:
            f.write(png_data)

        # 显示图像（确保路径正确）
        display(Image(filename=filename))

    except Exception:
        # This requires some extra dependencies and is optional
        pass