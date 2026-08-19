# -*- coding: utf-8 -*-
"""技能（Skill）动态加载。

采用 Pi 上游（@earendil-works/pi-agent-core）的设计哲学——**元数据优先、
按需懒加载**：

    1. 启动时只把每个技能的名字 + 描述（``format_skills_for_prompt``）
       注入系统提示词，模型据此判断"哪个技能可能相关"；
    2. 模型一旦觉得某个任务匹配某技能，就调用内置的 ``read_skill``
       工具，把对应 SKILL.md 的**完整内容**读入上下文后按流程执行。

好处：不相关技能的全文字永远不会进上下文，节省 token、降低噪音；
技能本身只是 ``skills/`` 目录下的一个 ``SKILL.md`` 文件，增删技能
不改任何代码（遵循 agentskills.io 标准）。
"""

from __future__ import annotations

from pathlib import Path

from pi_ai import TextContent
from pi_agent_core import (
    AgentToolResult,
    Skill,
    format_skill_invocation,
    format_skills_for_prompt,
    load_skills_from_dir,
)


class ReadSkillTool:
    """内置"读技能"工具：按名读取 SKILL.md 全文（懒加载的入口）。

    同样按 Pi 的 AgentTool 协议实现（鸭子类型），注册进 agent 的工具
    列表后，模型即可自行决定何时读取哪个技能。
    """

    name = "read_skill"
    description = (
        "读取指定技能的完整说明（SKILL.md 全文）。"
        "系统提示词里列出的 <available_skills> 只是技能摘要，"
        "当用户请求与某个技能匹配时，必须先调用本工具读取全文，"
        "再严格按照技能说明执行。"
    )
    parameters = {
        "type": "object",
        "properties": {
            "skill_name": {
                "type": "string",
                "description": "技能名（available_skills 中的 <name> 字段）",
            }
        },
        "required": ["skill_name"],
    }
    label = "read skill file"
    execution_mode: None = None

    def __init__(self, skills: list[Skill]):
        # name -> Skill 的索引，启动时由 load_skill_components 填好
        self._by_name: dict[str, Skill] = {s.name: s for s in skills}

    async def execute(self, tool_call_id, params, cancel_event=None, on_update=None):
        skill = self._by_name.get(params.get("skill_name", ""))
        if skill is None:
            # 失败语义：抛异常 = 工具调用失败，由 Pi 循环编码为错误结果
            raise ValueError(f"未找到技能 '{params.get('skill_name')}'，"
                             f"可用技能: {', '.join(sorted(self._by_name))}")
        # format_skill_invocation 会附带技能文件路径与"相对路径基准"说明
        content = format_skill_invocation(skill)
        return AgentToolResult(content=[TextContent(text=content)])


def load_skill_components(skills_dir: str | Path):
    """动态扫描技能目录，返回 (技能列表, 注入 system prompt 的摘要块, read_skill 工具)。

    Args:
        skills_dir: 示例的 skills/ 目录

    Returns:
        三元组：
          - skills: 加载到的 Skill 列表（Pi 提供的 dataclass）
          - prompt_block: 技能摘要 XML（拼进 system prompt）
          - read_skill: ReadSkillTool 实例（注册进 agent 工具列表）
    """
    result = load_skills_from_dir(str(skills_dir))
    for diag in result.diagnostics:
        print(f"  [技能警告] {diag.path}: {diag.message}")
    skills = result.skills
    print(f"  [技能加载] {len(skills)} 个技能: "
          f"{', '.join(f'{s.name}({s.description[:20]}...)' for s in skills)}")
    return skills, format_skills_for_prompt(skills), ReadSkillTool(skills)
