# -*- coding: utf-8 -*-
"""动态组装模块。

本包把「MCP 服务 / Skill / Agent」的组装过程拆成四个可复用组件：

- config_loader : 读取 YAML 配置，把配置描述翻译成 AgentScope 的 MCP 配置对象
- mcp_manager   : 动态连接 MCP 服务，管理客户端的生命周期（连接/关闭）
- skill_loader  : 动态扫描 skills 目录，加载 SKILL.md 技能
- agent_builder : 把工具、技能、模型组装成最终的 Agent

每个组件都保持“只依赖输入参数、不硬编码具体服务”的设计，
因此新增一个 MCP 服务或技能时只需要改配置/加目录，不用改代码。
"""
