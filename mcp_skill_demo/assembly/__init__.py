"""
assembly —— 「动态组装 MCP 与 Skill」示例的核心包

组装流水线（三步，全部由运行时配置驱动，不写死任何工具）：

    1. MCPManager      : 读取 config/mcp_servers.yaml，动态连接 MCP 服务器，
                         自动发现每个服务器暴露的工具
    2. SkillLoader     : 读取 config/skills/*.yaml，加载技能定义，
                         按技能声明的依赖把工具绑定到技能上
    3. GraphBuilder    : 把"路由节点 + 每个技能一个 Agent 节点"动态组装成
                         一个 LangGraph 图，编译后即可运行

通过该包导出的便捷函数：
    run_demo.main()    —— 一键运行交互式示例
"""
from . import config_loader, graph_builder, main, mcp_manager, models, router, skill_loader

__all__ = [
    "config_loader",
    "graph_builder",
    "main",
    "mcp_manager",
    "models",
    "router",
    "skill_loader",
]
