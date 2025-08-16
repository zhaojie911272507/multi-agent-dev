import os

from langgraph.graph import MessagesState
from langchain.chat_models import init_chat_model
from sympy import print_glsl

from langgraph_src.AgenticRAG.create_a_retriever_tool import retriever_tool

response_model = init_chat_model("deepseek-chat",temperature=0)


def generate_query_or_respond(state: MessagesState):
    """Call the model to generate a response based on the current state. Given
    the question, it will decide to retrieve using the retriever tool, or simply respond to the user.
    """
    response = (
        response_model
        .bind_tools([retriever_tool]).invoke(state["messages"])
    )
    return {"messages": [response]}


# # Try it on a random input:
# # 尝试一下随机输入：
# input = {"messages": [{"role": "user", "content": "hello!"}]}
# generate_query_or_respond(input)["messages"][-1].pretty_print()


# Ask a question that requires semantic search:
# 提出一个需要语义搜索的问题：
input = {
    "messages": [
        {
            "role": "user",
            "content": "What does Lilian Weng say about types of reward hacking? Must be output in Chinese.",
        }
    ]
}
generate_query_or_respond(input)["messages"][-1].pretty_print()

# ================================== Ai Message ==================================
# Tool Calls:
#   retrieve_blog_posts (call_0_979f50d8-5fb3-4a5a-accc-f85d504a4cc3)
#  Call ID: call_0_979f50d8-5fb3-4a5a-accc-f85d504a4cc3
#   Args:
#     query: types of reward hacking


