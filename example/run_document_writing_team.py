"""启动分层 Agent 团队 - 文档写作（大纲 → 写作 → 图表）"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    subprocess.run(
        [sys.executable, str(ROOT / "langgraph_src" / "hierarchical_agent_teams" / "document_writing_team.py")],
        cwd=ROOT,
    )


if __name__ == "__main__":
    main()
