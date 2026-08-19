"""
router.py —— 意图路由（二选一，均可独立工作）

路由决定"用户这句话交给哪个技能处理"，提供两种实现：

    1. KeywordRouter  —— 纯规则，零依赖零成本，开箱即用
    2. LLMRouter      —— 让 LLM 在技能清单中做意图识别（更准确、更灵活），
                        需要配置 DEEPSEEK_API_KEY

设计取舍：
    - 不配置 API Key 时自动回退到 KeywordRouter，示例仍然可完整运行
    - LLM 路由把"技能清单"直接格式化为工具 schema 传给模型，
      模型输出 tool_call 即所选技能 —— 无需解析自由文本
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from langchain_core.messages import HumanMessage, SystemMessage

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel

    from .models import Skill


# ----------------------------------------------------------------------------
# 实现一：关键词路由（纯规则）
# ----------------------------------------------------------------------------
class KeywordRouter:
    """按技能 triggers 关键词做包含匹配，按技能声明顺序返回第一个命中。"""

    def route(self, skills: list["Skill"], text: str) -> "Skill | None":
        for skill in skills:
            if skill.matches(text):
                return skill
        return None  # 无命中 -> 由调用方决定兜底


# ----------------------------------------------------------------------------
# 实现二：LLM 路由（意图识别）
# ----------------------------------------------------------------------------
class LLMRouter:
    """把技能清单格式化为工具 schema，让 LLM 一次性完成意图识别。"""

    def __init__(self, llm: "BaseChatModel"):
        self._llm = llm

    @staticmethod
    def _skills_to_tool_schema(skills: list["Skill"]) -> list[dict]:
        """
        把技能列表转换为 OpenAI 风格的工具 schema。
        每个技能对应一个"工具"：description 是判断依据，工具名即技能名。
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": skill.name,          # 工具名 = 技能名
                    "description": skill.description,  # 模型据此判断
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            }
            for skill in skills
        ]

    async def route(self, skills: list["Skill"], text: str) -> "Skill | None":
        """
        让 LLM 在给定技能清单中选择最合适的一个。

        Returns:
            选中的 Skill；模型未调用工具（不认账）时返回 None。
        """
        tools_schema = self._skills_to_tool_schema(skills)
        model = self._llm.bind_tools(tools_schema, tool_choice="auto")

        response = await model.ainvoke(
            [
                SystemMessage(
                    "你是技能调度器。根据用户问题，从可用技能中选择最合适的一个。"
                ),
                HumanMessage(text),
            ]
        )

        # 模型输出 tool_call 即它的选择；取第一个即可
        if response.tool_calls:
            chosen_name = response.tool_calls[0]["name"]
            for skill in skills:
                if skill.name == chosen_name:
                    return skill
        return None  # 模型拒绝选择 -> 兜底


# ----------------------------------------------------------------------------
# 工厂函数：根据是否配置了 LLM 自动选择路由实现
# ----------------------------------------------------------------------------
def create_router(llm: "BaseChatModel | None") -> KeywordRouter | LLMRouter:
    """有 LLM 用 LLM 路由，否则用关键词路由。"""
    return LLMRouter(llm) if llm is not None else KeywordRouter()
