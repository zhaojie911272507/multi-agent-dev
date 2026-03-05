"""启动监督者模式多智能体"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    subprocess.run(
        [sys.executable, str(ROOT / "langgraph_src" / "agent_supervisor" / "create_worker_agent" / "agent_supervisor_d.py")],
        cwd=ROOT,
    )


if __name__ == "__main__":
    main()
