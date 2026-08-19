"""LangGraph 调用「外部 HTTP 类 MCP」+「Skill」的完整示例

本示例演示两件事：
1. 如何让 LangGraph Agent 调用一个**外部、运行在 HTTP 上的 MCP Server**
   （Agent 进程与 MCP Server 进程互相独立，仅通过网络协议通信）；
2. 如何把项目里的 **Skill**（skill.yaml 声明 + Python 实现，同 skills_src/audit_skill 模式）
   包装成工具交给 Agent 自主调用。

核心概念：
- MCP 工具：通过 langchain-mcp-adapters 连接远端 MCP Server，拉取其暴露的工具；
- Skill 工具：读取本地 skill.yaml，动态加载实现入口，包装成 LangChain @tool；
- 在 LangGraph 里两者最终都是「工具」，LLM 根据工具 description 自主选择调用哪个。

运行方式（需要先启动 MCP Server，见 README.md）：
    python langgraph_agent.py
"""

import asyncio
import importlib.util
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import BaseTool, StructuredTool
from langchain_mcp_adapters.client import MultiServerMCPClient

# 本项目示例目录结构：
#   http_mcp_skill_demo/
#   ├── mcp_server.py                  <- 外部 HTTP MCP 服务端（独立进程）
#   ├── skills/stock_analysis_skill/
#   │   ├── skill.yaml                 <- skill 声明（名称/描述/触发词/入口）
#   │   └── orchestrator.py            <- skill 实现
#   └── langgraph_agent.py             <- 本文件：LangGraph 客户端
BASE_DIR = Path(__file__).parent
SKILLS_DIR = BASE_DIR / "skills"

# 外部 HTTP MCP 端点：即 mcp_server.py 启动后的地址（Streamable HTTP 端点固定为 /mcp）
MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp")

# 给 Agent 的系统提示词（可选），说明它手里有哪些工具
SYSTEM_PROMPT = """你是一个全能助手，可以使用两类工具：
1. MCP 工具（来自外部 HTTP MCP Server）：天气、汇率查询；
2. Skill 工具（本地技能）：股票估值分析。
请根据用户问题选择合适的工具，若工具结果不足以回答，如实说明。"""


# ---------------------------------------------------------------------------
# 1. Skill 加载：把 skills/ 目录下每个 skill.yaml 包装成一个 LangChain 工具
# ---------------------------------------------------------------------------
def _import_module_from_path(module_path: Path):
    """从任意文件路径动态加载 Python 模块（不依赖 sys.path 和 cwd）。"""
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_skills_as_tools(skills_dir: Path = SKILLS_DIR) -> list[BaseTool]:
    """扫描 skills 目录，把每个 skill 包装为 LangChain Tool。

    约定（与 audit_skill 一致）：
    - 每个子目录 = 一个 skill，内含 skill.yaml 与实现模块；
    - skill.yaml 的 `entry` 字段指明实现入口（"模块.函数"）；
    - `description` 写入工具的 description，`triggers` 附在描述里提示 LLM 何时调用。
    """
    skill_tools: list[BaseTool] = []

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        yaml_path = skill_dir / "skill.yaml"
        if not yaml_path.exists():
            continue

        # 读取 skill 声明
        with open(yaml_path, encoding="utf-8") as f:
            skill_meta = yaml.safe_load(f)

        skill_name = skill_meta["name"]
        # 工具名需符合 OpenAI 工具命名规范（字母数字下划线），skill 名可能带连字符
        tool_name = skill_name.replace("-", "_")

        # 动态加载实现入口，例如 entry="orchestrator.run_analysis"
        module_name, func_name = skill_meta["entry"].split(".")
        module = _import_module_from_path(skill_dir / f"{module_name}.py")
        entry_fn = getattr(module, func_name)

        # 把触发词拼进 description，强化 LLM 选择该 skill 的意图
        keywords = "、".join(skill_meta.get("triggers", {}).get("keywords", []))
        description = (
            f"{skill_meta['description']}。"
            f"当用户输入涉及以下关键词时优先使用：{keywords}"
        )

        # StructuredTool.from_function 直接包装现有函数：
        # 保留原函数签名（参数 schema 由签名类型注解自动推断），仅覆盖 name / description
        skill_tools.append(
            StructuredTool.from_function(
                func=entry_fn,
                name=tool_name,
                description=description,
            )
        )
        print(f"[skill] 已加载: {skill_name} -> {tool_name} (entry={skill_meta['entry']})")

    return skill_tools


# ---------------------------------------------------------------------------
# 2. 连接外部 HTTP MCP 并拉取工具
# ---------------------------------------------------------------------------
async def load_http_mcp_tools() -> list[BaseTool]:
    """通过 MultiServerMCPClient 连接外部 HTTP MCP Server，拉取其工具列表。

    langchain-mcp-adapters 0.2.x 的配置是 TypedDict，支持多种 transport：
    - stdio: 本地子进程（见 mcp_src/example/agent_client.py 的 math 示例）
    - http / streamable_http: **外部 HTTP（本示例）**，走 Streamable HTTP 协议
    - sse / websocket: 其他远程传输
    """
    client = MultiServerMCPClient(
        {
            # server 名可任意起，仅用于区分多个连接
            "weather": {
                "url": MCP_URL,          # 外部 HTTP MCP 端点
                "transport": "http",     # mcp>=1.10 新命名；等价写法 "streamable_http"
                # 远端需要鉴权时还可传 headers / auth，例如:
                # "headers": {"Authorization": "Bearer xxx"},
            },
        }
    )
    # get_tools() 会与远端完成 MCP 握手（initialize），并拉取 tools/prompts/resources
    try:
        tools = await client.get_tools()
    except Exception as e:
        # 常见原因：mcp_server.py 未启动 / 端口被占用 / URL 写错
        print(
            f"[mcp] 连接外部 MCP Server 失败 ({type(e).__name__}: {e})\n"
            f"      请先确认 mcp_server.py 已在另一终端启动，监听 {MCP_URL}"
        )
        raise
    for t in tools:
        print(f"[mcp] 已加载外部工具: {t.name} <- {MCP_URL}")
    return tools


# ---------------------------------------------------------------------------
# 3. 组装 LangGraph Agent 并执行
# ---------------------------------------------------------------------------
async def main():
    # 加载环境变量（.env 中的 DEEPSEEK_API_KEY 等）
    load_dotenv()
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("警告: 未找到 DEEPSEEK_API_KEY，请检查项目根目录的 .env 文件")
        return

    # 步骤 1: 从外部 HTTP MCP Server 拉取工具（远程进程，网络调用）
    mcp_tools = await load_http_mcp_tools()

    # 步骤 2: 加载本地 skill，包装成工具
    skill_tools = load_skills_as_tools()

    # 步骤 3: 创建 LLM 并组装 Agent（create_agent 即原 create_react_agent，
    # LangGraph V1.0 起迁移到 langchain.agents，参数 prompt 更名为 system_prompt）。
    # 在 Agent 视角下，MCP 工具与 Skill 工具没有区别，都是 tools，
    # 由 LLM 依据各自的 description 自主决定调用顺序与次数。
    llm = init_chat_model(os.getenv("LLM_MODEL", "deepseek-chat"))
    agent = create_agent(
        llm,
        tools=[*mcp_tools, *skill_tools],
        system_prompt=SYSTEM_PROMPT,
        name="http_mcp_skill_agent",
    )

    # 步骤 4: 测试调用。
    # 问题 1 走「外部 HTTP MCP」链路；问题 2 走「skill」链路。
    test_questions = [
        "今天上海和北京的天气怎么样？",            # -> get_weather（HTTP MCP）
        "帮我分析一下 AAPL 的估值，当前股价 210",  # -> stock_analysis（skill）
    ]
    for question in test_questions:
        print(f"\n{'='*60}\n用户问题: {question}\n{'='*60}")
        result = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})
        # 打印 agent 的最终回答
        print("\n最终回答:")
        print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
