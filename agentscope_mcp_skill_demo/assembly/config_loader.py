# -*- coding: utf-8 -*-
"""配置加载器：YAML 配置 → AgentScope MCP 配置对象。

动态组装的第一步是从配置文件中读取“要连接哪些 MCP 服务”，
而不是在代码里写死。这样以后加一个服务，只需要在
``config/mcp_servers.yaml`` 里追加一条记录。
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from agentscope.mcp import StdioMCPConfig  # 本示例只用 stdio 传输

# {DEMO_ROOT} 占位符：在 YAML 中表示示例根目录的绝对路径
_DEMO_ROOT = Path(__file__).resolve().parent.parent
_PLACEHOLDER = "{DEMO_ROOT}"


@dataclass
class MCPServerEntry:
    """一条 MCP 服务配置（对应 YAML 中的一个条目）。"""

    name: str                      # 客户端名称，工具名前缀 mcp__{name}__
    mcp_config: StdioMCPConfig     # AgentScope 的 MCP 配置对象（stdio）
    enable_tools: list[str] | None = None   # 只启用这些工具；None = 全部
    disable_tools: list[str] | None = None  # 禁用这些工具
    env: dict[str, str] = field(default_factory=dict)  # 传给服务子进程的环境变量


def load_mcp_servers(yaml_path: str | Path) -> list[MCPServerEntry]:
    """读取 MCP 服务配置文件，返回配置条目列表。

    Args:
        yaml_path: ``config/mcp_servers.yaml`` 的路径

    Returns:
        每个服务一条 :class:`MCPServerEntry`

    Raises:
        FileNotFoundError: 配置文件不存在
        ValueError: YAML 内容缺少必填字段
    """
    yaml_path = Path(yaml_path)
    if not yaml_path.exists():
        raise FileNotFoundError(f"MCP 配置文件不存在: {yaml_path}")

    # 读取 YAML（PyYAML 返回 dict / list）
    with open(yaml_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    entries: list[MCPServerEntry] = []
    for item in raw.get("mcp_servers", []):
        # 校验必填字段，缺了直接报错，避免把错误配置带进运行时
        name = item.get("name")
        command = item.get("command")
        args = item.get("args") or []
        if not name or not command:
            raise ValueError(f"MCP 配置条目缺少 name 或 command: {item}")

        # 把 args 里的 {DEMO_ROOT} 占位符替换成绝对路径，
        # 保证无论从哪个目录运行 run_demo.py 都能找到服务脚本
        resolved_args = [
            str(_DEMO_ROOT) + str(arg)[len(_PLACEHOLDER):]
            if isinstance(arg, str) and arg.startswith(_PLACEHOLDER)
            else arg
            for arg in args
        ]

        # 构造 AgentScope 的 stdio 配置对象
        mcp_config = StdioMCPConfig(
            command=command,
            args=resolved_args,
            env=item.get("env"),
        )

        entries.append(
            MCPServerEntry(
                name=name,
                mcp_config=mcp_config,
                enable_tools=item.get("enable_tools"),
                disable_tools=item.get("disable_tools"),
                env=item.get("env") or {},
            ),
        )

    return entries


def ensure_env_loaded() -> None:
    """加载示例根目录下的 .env 文件（若存在），把变量写入环境变量。

    与 langgraph 项目共享同一个 ``.env``（含 DEEPSEEK_API_KEY）。
    若已存在同名环境变量则跳过，避免覆盖外部传入的配置。
    """
    env_path = _DEMO_ROOT.parent / ".env"  # 仓库根目录的 .env
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
