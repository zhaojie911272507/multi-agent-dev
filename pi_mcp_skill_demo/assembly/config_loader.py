# -*- coding: utf-8 -*-
"""配置加载：``config/mcp_servers.yaml`` → 服务配置对象。

这是"动态组装"的数据源：所有要连接的 MCP 服务都声明在 YAML 里，
代码运行时才逐条读取，因此新增 / 停用 / 裁剪服务不需要改任何 Python 代码。

职责：
    1. 从仓库根目录的 ``.env`` 加载环境变量（DEEPSEEK_API_KEY 等）
    2. 解析 YAML，把 ``{DEMO_ROOT}`` 占位符替换为示例目录绝对路径
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

try:  # 有 python-dotenv 就用它加载 .env，没有则跳过（不影响核心功能）
    from dotenv import load_dotenv

    _HAVE_DOTENV = True
except ImportError:  # pragma: no cover
    _HAVE_DOTENV = False


@dataclass
class MCPServerEntry:
    """一条 MCP 服务配置（对应 YAML 里的一个列表元素）。"""

    name: str
    command: str
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    enable_tools: list[str] | None = None  # None = 启用该服务全部工具
    disable_tools: list[str] = field(default_factory=list)


def ensure_env_loaded() -> None:
    """加载仓库根目录的 ``.env``（DEEPSEEK_API_KEY 等），幂等。

    ``pi_ai`` 的 OpenAI-compatible provider 需要 API Key 才能调用模型，
    我们通过 ``Agent`` 的 ``get_api_key`` 钩子读取环境变量（见 agent_builder）。
    """
    if _HAVE_DOTENV:
        # 仓库根目录（本文件的上三级）存放 .env
        load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")


def load_mcp_servers(config_path: str | Path, demo_root: Path) -> list[MCPServerEntry]:
    """读取 YAML 配置，返回服务配置对象列表。

    Args:
        config_path: mcp_servers.yaml 的路径
        demo_root: 示例目录绝对路径，用于替换 args 里的 {DEMO_ROOT} 占位符

    Returns:
        按配置声明顺序排列的服务配置列表
    """
    raw = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    entries: list[MCPServerEntry] = []
    for item in raw.get("mcp_servers", []):
        entry = MCPServerEntry(
            name=item["name"],
            command=item["command"],
            args=[a.replace("{DEMO_ROOT}", str(demo_root)) for a in item.get("args", [])],
            env=dict(item.get("env") or {}),
            enable_tools=item.get("enable_tools"),
            disable_tools=list(item.get("disable_tools") or []),
        )
        entries.append(entry)
    return entries
