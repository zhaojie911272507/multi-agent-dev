import time
from pprint import pprint

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from typing_extensions import TypedDict, Annotated
import operator

class OverallState(TypedDict):
    topic: str
    subjects: list[str]
    # subjects: Annotated[list[str], operator.add]
    jokes: Annotated[list[str], operator.add]
    best_selected_joke: str

def generate_topics(state: OverallState):
    print("进入generate-topics:",state)
    return {"subjects": ["lions", "elephants", "penguins"]}

def generate_joke(state: OverallState):
    joke_map = {
        "lions": "Why don't lions like fast food? Because they can't catch it!",
        "elephants": "Why don't elephants use computers? They're afraid of the mouse!",
        "penguins": "Why don't penguins like talking to strangers at parties? Because they find it hard to break the ice."
    }
    print("进入generate-joke:",[joke_map[state["subject"]]])
    for i in range(10):
        time.sleep(1.0)
        print("joke1 :",i)
    return {"jokes": [joke_map[state["subject"]]]}

# def continue_to_jokes(state: OverallState):
#     print("进入continue-to-jokes:",state)
#     return [Send("generate_joke", {"subject": s}) for s in state["subjects"]]
def generate_joke2(state: OverallState):
    print("进入generate-joke2:")
    for i in range(10):
        time.sleep(1.6)
        print("joke2 :",i)
    return {"jokes":["haha, haha, haha"],
            # "subjects":["haha-joke2"]
            }

def generate_joke3(state: OverallState):
    print("进入generate-joke3:")
    for i in range(10):
        time.sleep(1.1)
        print("joke3 :",i)
    return {"jokes":["This is just a joke3!"]}

def continue_to_jokes(state: OverallState):
    print("进入continue-to-jokes:",state)
    return [Send("generate_joke", {"subject": "lions"}),
            Send("generate_joke", {"subject": "elephants"}),
            Send("generate_joke", {"subject": "penguins"}),
            Send("generate_joke2", {"subject": "haha"}),
            Send("generate_joke3", {"subject": "tets"})
            ]

def best_joke(state: OverallState):
    print("进入best-joke:",state)
    return {"best_selected_joke": "penguins"}

builder = StateGraph(OverallState)
builder.add_node("generate_topics", generate_topics)
builder.add_node("generate_joke", generate_joke)
builder.add_node("generate_joke2", generate_joke2)
builder.add_node("generate_joke3", generate_joke3)
builder.add_node("best_joke", best_joke)
builder.add_edge(START, "generate_topics")
builder.add_conditional_edges("generate_topics", continue_to_jokes, ["generate_joke","generate_joke2","generate_joke3"])
builder.add_edge("generate_joke", "best_joke")
builder.add_edge("generate_joke2", "best_joke")
builder.add_edge("generate_joke3", "best_joke")
builder.add_edge("best_joke", END)
builder.add_edge("generate_topics", END)
graph = builder.compile()


if __name__ == "__main__":
    # from IPython.display import Image, display
    #
    # try:
    #     # display(Image(graph.get_graph().draw_mermaid_png()))
    #     # 获取 PNG 数据
    #     png_data = graph.get_graph().draw_mermaid_png()
    #     filename = "Send3.png"
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


    # Call the graph: here we call it to generate a list of jokes
    for step in graph.stream({"topic": "animals"}):
        print(step)

    # for step in graph.stream({"topic": "animals"}):
    #     print(step)



    # import asyncio

    # 假设graph是已经构建并编译好的LangGraph图，且支持异步流式调用

    # async def main():
    #     # 输入数据
    #     inputs = {"topic": "animals"}
    #
    #     # 异步流式调用图，获取异步迭代器
    #     async for chunk in graph.astream(inputs, stream_mode="updates"):
    #         # 实时处理每个流式输出块
    #         print("Received chunk:", chunk)
    #
    #
    # # 运行异步主函数
    # asyncio.run(main())