"""
config_loader.py —— 配置加载器

职责：读取 yaml 配置文件（MCP 注册表 + 技能定义），并做占位符解析。
所有路径类占位符（${DEMO_DIR}）在这里统一替换，下游模块无需关心路径细节。
"""
from __future__ import annotations

import os
from pathlib import Path

import yaml

# 示例根目录：assembly/config_loader.py 的上一级目录
DEMO_DIR = Path(__file__).resolve().parent.parent


def _expand_placeholders(value):
    """
    递归解析配置中的占位符：
      ${DEMO_DIR} -> 示例根目录绝对路径
      ${VAR}      -> 其余环境变量（os.path.expandvars 负责）
    """
    if isinstance(value, str):
        value = value.replace("${DEMO_DIR}", str(DEMO_DIR))
        return os.path.expandvars(value)
    if isinstance(value, list):
        return [_expand_placeholders(v) for v in value]
    if isinstance(value, dict):
        return {k: _expand_placeholders(v) for k, v in value.items()}
    return value


def load_mcp_config(path: str | Path | None = None) -> dict:
    """
    加载 MCP 服务器注册表。

    Returns:
        形如 {"math": {"command": "python", "args": [...], "transport": "stdio"}, ...}
    """
    path = Path(path) if path else DEMO_DIR / "config" / "mcp_servers.yaml"
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    cfg = _expand_placeholders(raw)
    return cfg.get("servers", {})   # 取出 servers 节点；缺省为空 dict


def load_skill_defs(skills_dir: str | Path | None = None) -> list[dict]:
    """
    加载 config/skills/ 目录下的全部技能定义（一个 yaml 文件 = 一个技能）。

    Returns:
        每个元素是一个技能定义 dict，包含 name / description / triggers /
        mcp_servers / system_prompt 等字段。
    """
    skills_dir = Path(skills_dir) if skills_dir else DEMO_DIR / "config" / "skills"
    defs: list[dict] = []
    for yaml_file in sorted(skills_dir.glob("*.yaml")):
        with open(yaml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data:  # 跳过空文件
            defs.append(data)
    return defs
