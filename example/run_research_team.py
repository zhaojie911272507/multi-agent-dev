"""启动分层 Agent 团队 - 研究团队"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    subprocess.run(
        [sys.executable, str(ROOT / "langgraph_src" / "hierarchical_agent_teams" / "research_team.py")],
        cwd=ROOT,
    )


if __name__ == "__main__":
    main()
