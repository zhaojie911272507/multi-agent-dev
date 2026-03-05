"""启动 MCP Agent 示例（需先启动 MCP 服务器）"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    subprocess.run(
        [sys.executable, str(ROOT / "mcp_src" / "example" / "agent_client.py")],
        cwd=ROOT,
    )


if __name__ == "__main__":
    main()
