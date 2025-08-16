
# 延迟节点执行
import operator
from typing import Annotated, Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    # The operator.add reducer fn makes this append-only
    aggregate: Annotated[list, operator.add]

def a(state: State):
    print(f'Adding "A" to {state["aggregate"]}')
    return {"aggregate": ["A"]}

def b(state: State):
    print(f'Adding "B" to {state["aggregate"]}')
    return {"aggregate": ["B"]}

def b_2(state: State):
    print(f'Adding "B_2" to {state["aggregate"]}')
    return {"aggregate": ["B_2"]}

def c(state: State):
    print(f'Adding "C" to {state["aggregate"]}')
    return {"aggregate": ["C"]}

def d(state: State):
    print(f'Adding "D" to {state["aggregate"]}')
    return {"aggregate": ["D"]}

builder = StateGraph(State)
builder.add_node(a)
builder.add_node(b)
builder.add_node(b_2)
builder.add_node(c)
builder.add_node(d, defer=True)
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "b_2")
builder.add_edge("b_2", "d")
builder.add_edge("c", "d")
builder.add_edge("d", END)
graph = builder.compile()


if __name__ == "__main__":
    graph.invoke({"aggregate": []})

    from IPython.display import Image, display

    try:
        # display(Image(graph.get_graph().draw_mermaid_png()))
        # 获取 PNG 数据
        png_data = graph.get_graph().draw_mermaid_png()
        filename = "DeferNodeExecution.png"
        # 保存到本地
        with open(filename, "wb") as f:
            f.write(png_data)

        # 显示图像（确保路径正确）
        display(Image(filename=filename))

    except Exception:
        # This requires some extra dependencies and is optional
        pass

