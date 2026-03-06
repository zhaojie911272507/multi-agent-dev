"""启动 Reporter Agent"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    subprocess.run(
        [sys.executable, "-m", "langgraph_src.reporter_agent.main"],
        cwd=ROOT,
    )


if __name__ == "__main__":
    main()
