# -*- coding: utf-8 -*-
"""动态组装核心组件包。

- ``config_loader``：读取 ``config/mcp_servers.yaml``，产出服务配置对象
- ``mcp_manager``：动态连接 MCP 服务、发现工具、包装成 Pi 的 AgentTool
- ``skill_loader``：动态扫描 ``skills/`` 目录、提供懒加载技能工具
- ``agent_builder``：构造 pi_ai Model + pi_agent_core Agent
"""
