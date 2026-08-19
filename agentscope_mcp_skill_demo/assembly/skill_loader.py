# -*- coding: utf-8 -*-
"""技能加载器：动态扫描 skills 目录。

AgentScope 的「技能（Skill）」是一组指令/脚本/资源，约定放在一个
目录下，核心是 ``SKILL.md`` 文件：frontmatter 里声明 ``name`` 和
``description``，正文是给智能体的完整操作说明。

技能 **不是** 可以直接调用的工具。智能体在系统提示词中会看到技能列表，
需要通过内置的 ``Skill`` 查看工具读取技能正文，再按说明执行。
"""

from pathlib import Path

from agentscope.skill import LocalSkillLoader, Skill

# 默认技能目录：本示例的 skills/ 目录（只扫描一层，不递归子目录）
_DEFAULT_SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"


def get_skills_dir() -> str:
    """返回技能根目录的绝对路径。"""
    return str(_DEFAULT_SKILLS_DIR)


def create_skill_loader(
    directory: str | None = None,
    scan_subdir: bool = True,
) -> LocalSkillLoader:
    """创建技能加载器，用于动态扫描目录下的 SKILL.md。

    两种用法（Toolkit 都支持）：

    1. 直接把目录字符串传给 ``Toolkit(skills_or_loaders=[directory])``，
       框架内部会自动创建 LocalSkillLoader；
    2. 自己创建 LocalSkillLoader 再传进去，可以额外拿到技能清单
       （如下面的 ``list_skills`` 演示）。

    Args:
        directory: 技能目录，默认使用本示例的 skills/
        scan_subdir: 是否递归扫描子目录（每个含 SKILL.md 的子目录都是一个技能）

    Returns:
        配置好的 LocalSkillLoader 实例
    """
    return LocalSkillLoader(
        directory=directory or get_skills_dir(),
        scan_subdir=scan_subdir,
    )


async def list_skills(directory: str | None = None) -> list[Skill]:
    """动态加载并列出当前可用的技能（供日志/调试展示）。"""
    loader = create_skill_loader(directory=directory)
    return await loader.list_skills()
