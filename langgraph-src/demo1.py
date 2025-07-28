import operator
import os
from typing import Annotated, Any, Dict, List, Optional, TypedDict

from dotenv import load_dotenv
from langchain_core.agents import AgentFinish, AgentAction
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


# 定义状态
class AgentState(TypedDict):
    input: str
    history: Annotated[List[Dict[str, Any]], operator.add]
    agent_outcome: Optional[Dict[str, Any]] = None
    intermediate_steps: Annotated[List[AgentAction], operator.add]
    counter: int = 0


load_dotenv()
print(os.getenv("DEEPSEEK_API_KEY"))
# exit(0)
# 创建大模型实例
model = ChatOpenAI(model="deepseek-chat",
                   openai_api_key= os.getenv("DEEPSEEK_API_KEY"),
                   temperature=0)


# 定义工具函数
def search_tool(query: str) -> str:
    """模拟搜索工具"""
    return f"查询结果: {query} (来源: 模拟数据)"


def calculate_tool(expression: str) -> str:
    """模拟计算工具"""
    try:
        result = eval(expression)
        return f"计算结果: {expression} = {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


# 可用工具列表
TOOLS = [
    {
        "name": "search",
        "description": "用于查询信息",
        "func": search_tool
    },
    {
        "name": "calculate",
        "description": "用于数学计算",
        "func": calculate_tool
    }
]

# 构建提示模板
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "你是专业的AI助手，当前计数: {counter}"),
    ("user", "{input}")
])


# 定义节点函数
def agent_node(state: AgentState) -> Dict:
    """代理节点: 决定下一步操作"""
    messages = prompt_template.format_messages(
        counter=state["counter"],
        input=state["input"]
    )

    response = model.invoke(messages).content

    # 尝试解析工具调用
    if "[" in response and "]" in response:
        tool_name = response.split("[")[1].split("]")[0]
        tool_input = response.split("(")[1].split(")")[0] if "(" in response else ""

        # 检查工具是否可用
        for tool in TOOLS:
            if tool["name"] == tool_name:
                return {
                    "agent_outcome": AgentAction(
                        tool=tool_name,
                        tool_input=tool_input,
                        log=response
                    )
                }

    # 没有工具调用则直接返回结果
    return {
        "agent_outcome": AgentFinish(
            return_values={"output": response},
            log=response
        )
    }


def tool_node(state: AgentState) -> Dict:
    """工具节点: 执行工具调用"""
    action = state["agent_outcome"]
    for tool in TOOLS:
        if tool["name"] == action.tool:
            tool_result = tool["func"](action.tool_input)
            return {
                "intermediate_steps": [action],
                "history": [{
                    "step": "工具调用",
                    "tool": action.tool,
                    "input": action.tool_input,
                    "output": tool_result,
                    "counter": state["counter"]
                }],
                "counter": state["counter"] + 1
            }
    return {"output": f"找不到工具: {action.tool}"}


def should_continue(state: AgentState) -> str:
    """条件判断: 决定后续流程"""
    if isinstance(state["agent_outcome"], AgentFinish):
        return "end"
    return "continue"


# 构建流程图
workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)
workflow.add_node("tool", tool_node)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tool",
        "end": END
    }
)

workflow.add_edge("tool", "agent")

app = workflow.compile()

# 测试运行
if __name__ == "__main__":
    # 初始化状态
    initial_state = AgentState(
        input="请查询什么是LangGraph，然后计算2的10次方",
        history=[],
        intermediate_steps=[],
        counter=0
    )

    # 执行流程
    for step in app.stream(initial_state):
        node, state = next(iter(step.items()))

        if node == "agent":
            action = state["agent_outcome"]
            if isinstance(action, AgentAction):
                print(f"Agent 决定调用工具: {action.tool}({action.tool_input})")
            else:
                print(f"Agent 最终回答: {action.return_values['output']}")
        elif node == "tool" and "output" in state:
            print(f"工具执行结果: {state['output']}")
        elif node == "__end__":
            print("流程结束")
