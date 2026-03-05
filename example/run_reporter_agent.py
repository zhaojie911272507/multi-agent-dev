"""启动 Reporter Agent"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    subprocess.run(
        [sys.executable, str(ROOT / "langgraph_src" / "reporter_agent" / "main.py")],
        cwd=ROOT,
    )


if __name__ == "__main__":
    main()
