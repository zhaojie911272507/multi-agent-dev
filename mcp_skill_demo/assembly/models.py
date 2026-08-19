"""
models.py —— 数据模型定义

Skill 是"技能"在内存中的载体：
- 前半段信息（name/triggers/mcp_servers/system_prompt）来自 yaml 配置文件
- tools 字段是运行时装配阶段注入的（把 MCP 发现的工具绑定到技能上）
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # 仅用于类型标注，避免运行时循环依赖
    from langchain_core.tools import BaseTool


@dataclass
class Skill:
    """一个技能 = 触发规则 + 依赖的 MCP 服务器 + 系统提示词 + 绑定好的工具集。"""

    name: str                                # 技能唯一标识
    description: str = ""                    # 技能描述（LLM 路由时作为依据）
    triggers: list[str] = field(default_factory=list)  # 触发关键词（大小写不敏感）
    mcp_servers: list[str] = field(default_factory=list)  # 依赖的 MCP 服务器名
    system_prompt: str = ""                  # 注入给该技能 Agent 的系统提示词
    # 运行时装配阶段注入：该技能实际可调用的工具（来自 MCP 动态发现）
    tools: list["BaseTool"] = field(default_factory=list)

    # ------------------------------------------------------------------
    # 关键词匹配：纯规则路由用
    # ------------------------------------------------------------------
    def matches(self, text: str) -> bool:
        """判断一段用户文本是否命中本技能的任意触发关键词。"""
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in self.triggers)

    def __repr__(self) -> str:  # 便于打印装配清单
        tool_names = [t.name for t in self.tools]
        return (
            f"Skill(name={self.name!r}, triggers={self.triggers}, "
            f"mcp_servers={self.mcp_servers}, tools={tool_names})"
        )
