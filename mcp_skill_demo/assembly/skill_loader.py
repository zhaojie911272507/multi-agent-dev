"""
skill_loader.py —— 技能装配器（动态装配的第 2 步）

职责：
    1. 读取 config/skills/*.yaml 的技能定义
    2. 与 MCP 动态发现的工具做"按名装配"：
       技能声明依赖哪个服务器，就把该服务器的工具绑定给谁
    3. 返回可直接用于构图的一组 Skill 对象

核心点：
    - 技能与 MCP 服务器通过"名称"解耦，新增组合零代码
    - 若某技能依赖的服务器未在注册表中（比如被注释掉了），
      会给出提示并继续装配其他技能 —— 装配过程是容错的
"""
from __future__ import annotations

from langchain_core.tools import BaseTool

from .config_loader import load_skill_defs
from .models import Skill


def assemble_skills(
    skill_defs: list[dict],
    tools_by_server: dict[str, list[BaseTool]],
) -> list[Skill]:
    """
    把技能定义与 MCP 发现的工具组装成可运行的 Skill 列表。

    Args:
        skill_defs: config_loader.load_skill_defs() 的返回值
        tools_by_server: mcp_manager.connect() 的返回值 {服务器名: [工具]}

    Returns:
        装配完成的 Skill 列表（tools 字段已填充）
    """
    skills: list[Skill] = []
    for definition in skill_defs:
        # 1. 用定义中的字段构造 Skill 对象（此时 tools 还是空的）
        skill = Skill(
            name=definition.get("name", ""),
            description=definition.get("description", ""),
            triggers=definition.get("triggers", []),
            mcp_servers=definition.get("mcp_servers", []),
            system_prompt=definition.get("system_prompt", ""),
        )

        # 2. 按技能声明的服务器名，把动态发现的工具绑定进来
        for server_name in skill.mcp_servers:
            server_tools = tools_by_server.get(server_name, [])
            skill.tools.extend(server_tools)
            if not server_tools:
                print(
                    f"[SkillLoader] 警告：技能 {skill.name!r} 依赖服务器 "
                    f"{server_name!r}，但该服务器未连接（检查 mcp_servers.yaml）"
                )

        if skill.name:
            skills.append(skill)
        else:
            print("[SkillLoader] 警告：跳过了一个缺少 name 字段的技能定义")

    return skills


def find_skill_by_name(skills: list[Skill], name: str) -> Skill | None:
    """按名字查找技能；找不到返回 None。"""
    for skill in skills:
        if skill.name == name:
            return skill
    return None
