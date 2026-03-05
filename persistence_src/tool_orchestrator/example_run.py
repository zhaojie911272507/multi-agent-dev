"""
示例：运行工具编排器（仅 MCP 工具，无 audit skill）。

运行前确保：
  1. 已配置 .env 中的 DEEPSEEK_API_KEY
  2. math_server 路径正确

运行（任选其一）：
  python -m persistence_src.tool_orchestrator.example_run
  python persistence_src/tool_orchestrator/example_run.py  # 需在项目根目录
"""
import asyncio
import os
import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中，支持直接运行脚本
_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("DEEPSEEK_API_KEY", os.getenv("DEEPSEEK_API_KEY", ""))


async def main():
    from persistence_src.tool_orchestrator import create_orchestrator

    # 仅启用 MCP math 工具（可按需添加 audit_skill、store）
    math_server_path = Path(__file__).resolve().parents[2] / "mcp_src" / "example" / "custom_mcp_servers" / "math_server.py"
    orchestrator = await create_orchestrator(
        mcp_servers={
            "math": {
                "command": "python",
                "args": [str(math_server_path)],
                "transport": "stdio",
            }
        },
        enable_audit_skill=False,
    )

    config = {
        "configurable": {"thread_id": "demo-1"},
        "recursion_limit": 15,  # 限制最大迭代，防止无限循环
    }
    print("Invoking orchestrator... (LLM 调用较慢，请耐心等待)")
    result = await orchestrator.ainvoke(
        {"messages": [{"role": "user", "content": "计算 (3 + 5) * 12 等于多少？"}]},
        config,
    )
    last_msg = result["messages"][-1]
    print("Response:", getattr(last_msg, "content", last_msg))


if __name__ == "__main__":
    asyncio.run(main())
