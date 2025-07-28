from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List, Optional
import operator

# ================== Step 1: 定义状态 ==================
class State(TypedDict):
    messages: Annotated[List, operator.add] # 消息历史
    user_input: str                         # 用户输入
    problem_type: Optional[str]             # 问题类型（技术/非技术）
    assistant_response: Optional[str]       # 最终回复

# ================== Step 2: 定义节点函数 ==================
def classify_problem(state: State) -> State:
    """判断用户输入是否是技术问题"""
    user_input = state["user_input"].lower()
    if any(keyword in user_input for keyword in ["bug", "error", "code", "technical"]):
        return {"problem_type": "technical"}
    else:
        return {"problem_type": "general"}

def handle_technical_issue(state: State) -> State:
    """处理技术问题"""
    response = "This seems like a technical issue. Let me help you debug it:\n\n"
    response += "1. Can you provide the error message you're seeing?\n"
    response += "2. What steps led to this issue?\n"
    return {"assistant_response": response}

def handle_general_issue(state: State) -> State:
    """处理非技术问题"""
    response = "Thank you for reaching out. How can I assist you today?\n"
    response += "We're happy to help with any questions or feedback you have."
    return {"assistant_response": response}

# ================== Step 3: 定义条件分支 ==================
def route_problem(state: State) -> str:
    if state["problem_type"] == "technical":
        return "technical"
    else:
        return "general"

# ================== Step 4: 构建图流程 ==================
workflow = StateGraph(State)

# 添加节点
workflow.add_node("classify_problem", classify_problem)
workflow.add_node("handle_technical_issue", handle_technical_issue)
workflow.add_node("handle_general_issue", handle_general_issue)

# 添加入口点
workflow.set_entry_point("classify_problem")

# 添加条件边
workflow.add_conditional_edges(
    "classify_problem",
    route_problem,
    {
        "technical": "handle_technical_issue",
        "general": "handle_general_issue"
    }
)

# 添加结束边
workflow.add_edge("handle_technical_issue", END)
workflow.add_edge("handle_general_issue", END)

# ================== Step 5: 编译和运行 ==================
app = workflow.compile()

# 示例输入
user_input = "I'm getting an error when I try to log in."

# 构造初始状态
initial_state = {
    "messages": [HumanMessage(content=user_input)],
    "user_input": user_input
}

# 运行流程
result = app.invoke(initial_state, config={})

# 输出结果
print("Assistant Response:")
print(result["assistant_response"])

