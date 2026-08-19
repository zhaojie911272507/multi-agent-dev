#!/usr/bin/env python3
"""
run_demo.py —— 一键运行入口

用法（在 mcp_skill_demo 目录下执行）：
    python run_demo.py

如需 LLM 路由与智能回复，先准备 .env 文件：
    DEEPSEEK_API_KEY=sk-xxxx
"""
import asyncio
import sys
from pathlib import Path

# 把示例根目录加入 sys.path，保证 `python run_demo.py` 能导入 assembly 包
sys.path.insert(0, str(Path(__file__).resolve().parent))

from assembly.main import main  # noqa: E402

if __name__ == "__main__":
    asyncio.run(main())
