"""启动 LangGraph 基础示例"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    subprocess.run(
        [sys.executable, str(ROOT / "langgraph_src" / "demo1.py")],
        cwd=ROOT,
    )


if __name__ == "__main__":
    main()
