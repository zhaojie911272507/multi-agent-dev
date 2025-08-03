from init_chat_model import llm


# 2. Create a StateGraph
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)


# 3. Add a node
# We can now incorporate the chat model into a simple node:
# 我们现在可以将聊天模型合并到一个简单的节点中：
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)

graph_builder.add_node("chatbot2", chatbot)
# 4. Add an entry point
# Add an entry point to tell the graph where to start its work each time it is run:
# 添加一个 entry 点来告诉图表每次运行时从哪里开始工作
graph_builder.add_edge(START, "chatbot")


# 5. Add an exit point¶
# 5. 添加 exit 点
# Add an exit point to indicate where the graph should finish execution. This is helpful for more complex flows, but even in a simple graph like this, adding an end node improves clarity.
# 添加 exit 点，指示图表应在何处结束执行 。这对于更复杂的流程很有帮助，但即使在像这样的简单图表中，添加结束节点也可以提高清晰度。
graph_builder.add_edge("chatbot", END)


# 6. Compile the graph
# 编译图表
# Before running the graph, we'll need to compile it. We can do so by calling compile() on the graph builder. This creates a CompiledStateGraph we can invoke on our state.
# 在运行图表之前，我们需要编译它。我们可以通过调用 compile() 来实现。 在图形构建器上。这将创建一个 CompiledStateGraph ，我们可以在状态上调用它。
graph = graph_builder.compile()

print(graph)

# 7.You can visualize the graph using the get_graph method and one of the "draw" methods, like draw_ascii or draw_png. The draw methods each require additional dependencies.
# 您可以使用 get_graph 方法和其中一种“draw”方法（例如 draw_ascii 或 draw_png 来可视化图形。每种 draw 方法都需要额外的依赖项。
from IPython.display import Image, display

try:
    # display(Image(graph.get_graph().draw_mermaid_png()))
    # 获取 PNG 数据
    png_data = graph.get_graph().draw_mermaid_png()

    # 保存到本地
    with open("graph.png", "wb") as f:
        f.write(png_data)

    # 显示图像（确保路径正确）
    display(Image(filename="graph.png"))

except Exception:
    # This requires some extra dependencies and is optional
    pass


# 8. Run the chatbot
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break
