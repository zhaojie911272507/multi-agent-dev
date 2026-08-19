# -*- coding: utf-8 -*-
"""模型与 Agent 组装。

把前面动态准备好的三样东西拼成一个可对话的 Pi 智能体：

    - ``pi_ai.Model``：描述用哪个模型（DeepSeek，OpenAI-compatible API）
    - 系统提示词：角色说明 + 技能摘要（format_skills_for_prompt 的产物）
    - 工具列表：MCP 工具（MCPManager 发现） + read_skill（技能懒加载）
      + 可选的运行时动态注册的普通函数工具

另提供 ``make_function_tool``：把任意 Python 函数包装成 Pi 的
AgentTool —— 运行时动态挂载/卸载工具都靠它（见 run_demo 的场景三）。
"""

from __future__ import annotations

import inspect
import os

from pi_ai import AssistantMessage, Model, TextContent, ToolCall
from pi_agent_core import Agent, AgentOptions, AgentToolResult

# 模型参数集中在这里，方便换成其它 OpenAI-compatible 厂商
_DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"


def build_model() -> Model:
    """构造 DeepSeek 模型描述（pi_ai 的 Model 是 Pydantic 模型）。

    注意：
        - ``api="openai-completions"`` 是 pi_ai 内置的 OpenAI 兼容 provider，
          所以任意 OpenAI-compatible 端点（DeepSeek/月之暗面/本地 vLLM 等）
          都可以用同样的配置方式接入，只改 base_url 和模型 id。
        - API Key 不写在这里，通过 Agent 的 get_api_key 钩子从环境变量取。
    """
    return Model(
        id="deepseek-chat",
        name="DeepSeek Chat",
        api="openai-completions",          # 协议 = OpenAI Chat Completions
        provider="deepseek",               # 只是标识，可随意命名
        base_url=_DEEPSEEK_BASE_URL,
        reasoning=False,
        input=["text"],
        context_window=64000,
        max_tokens=4096,
    )


def make_function_tool(
    func,
    name: str,
    description: str,
) -> type:  # 返回符合 AgentTool 协议的工具类（鸭子类型，无公共基类）
    """把普通 Python 函数动态包装成 Pi 的 AgentTool。

    用于演示"运行时动态挂载能力"：对话过程中把一段新逻辑变成工具
    立即交给模型使用（Agent 的 state.tools 是普通 list，随时可改，
    下一次 prompt 时 Pi 循环就会把最新的工具列表发给模型）。

    Args:
        func: 同步或异步函数
        name: 工具名（对模型可见）
        description: 工具描述（对模型可见）

    Returns:
        一个符合 AgentTool 协议的工具对象
    """
    is_async = inspect.iscoroutinefunction(func)

    # 注意：Python 的"类体"作用域不闭包外层函数的局部变量（name/description 拿不到），
    # 所以字段都放 __init__ 里；而"方法体"可以闭包 func/is_async，故 execute 没问题。
    class FunctionTool:
        execution_mode: None = None

        def __init__(self):
            self.name = name
            self.description = description
            self.label = f"function:{name}"

        # 从函数签名生成参数 JSON Schema：
        # 按注解推断类型（int/float → number），无注解时退回 string
        @property
        def parameters(self) -> dict:
            hints = {k: v for k, v in inspect.signature(func).parameters.items()}
            properties: dict[str, dict] = {}
            for pname, param in hints.items():
                ann = param.annotation
                if ann in (int, float):
                    ptype = "number"
                elif ann is bool:
                    ptype = "boolean"
                else:  # str / 无注解 / 其它
                    ptype = "string"
                properties[pname] = {"type": ptype, "description": f"参数 {pname}"}
            return {
                "type": "object",
                "properties": properties,
                "required": list(hints),
            }

        async def execute(self, tool_call_id, params, cancel_event=None, on_update=None):
            args = list(params.values()) if params else []
            value = func(*args) if not is_async else await func(*args)
            return AgentToolResult(content=[TextContent(text=str(value))])

    return FunctionTool()


def _clean_messages_for_openai(messages, cancel_event=None):
    """每次 LLM 请求前的消息清洗钩子（transform_context）。

    规避 pi_ai 0.84.1 的一个序列化 bug + DeepSeek 的严格校验：

    **bug**：pi_ai 的 OpenAI provider 把 assistant 消息转成请求体时
    （``pi_ai/providers/openai_provider.py``），循环遍历 content 块
    只处理 ``ToolCall``，``text_parts`` 从未被填充 —— 文本块被完全
    丢弃。因此**不带 tool_call 的纯文本 assistant 消息**（模型的最终
    答复等）序列化后变成只有 ``role`` 的空消息。

    **校验**：DeepSeek 等 OpenAI 兼容端点要求历史里的每条 assistant
    消息 **content 或 tool_calls 至少一个非空**，空消息返回 400
    ``Invalid assistant message``，且错误消息会留在历史里导致雪崩。

    **修复**：把"无 tool_call 的 assistant 消息"从历史中剔除
    （工具调用链 toolCall → toolResult 完整保留，模型仍能理解之前的
    推理过程）；错误消息（无内容）也被同一条规则删除。

    Args:
        messages: Pi 循环准备发送的消息列表
        cancel_event: Pi 传入的取消信号（本钩子不使用）

    Returns:
        清洗后的消息列表
    """
    kept = []
    for msg in messages:
        if isinstance(msg, AssistantMessage):
            blocks = list(getattr(msg, "content", None) or [])
            has_tool = any(isinstance(b, ToolCall) for b in blocks)
            if not has_tool:
                # 纯文本 / 空 / 错误消息：pi_ai 序列化后为空 → 删除
                continue
        kept.append(msg)
    return kept


def build_agent(system_prompt: str, tools: list) -> Agent:
    """组装 Pi 智能体。

    Args:
        system_prompt: 系统提示词（含技能摘要块）
        tools: 启动时注册的工具列表（MCP 工具 + read_skill + ...）

    Returns:
        Agent: 可直接 prompt() 对话的有状态智能体
    """
    agent = Agent(
        AgentOptions(
            initial_state={
                "system_prompt": system_prompt,
                "model": build_model(),
                "tools": tools,
            },
            # Pi 循环调用 LLM 时先调这个钩子拿 API Key：
            # 返回 None 则回退到 AgentLoopConfig.api_key，再没有就报错
            get_api_key=lambda provider: os.environ.get("DEEPSEEK_API_KEY"),
            # 每次请求前清洗历史消息，兼容 OpenAI 严格校验（见上）
            transform_context=_clean_messages_for_openai,
        )
    )
    return agent
