"""
Tool Registry: 统一注册 Skills 与 MCP 工具，供 LangGraph ToolNode 调用。

- Skills: 如 financial-audit，封装为 LangChain @tool
- MCP: 通过 MultiServerMCPClient 获取远程工具定义
"""

from typing import Any

# ---------------------------------------------------------------------------
# Skill 工具封装（可选依赖，运行时按需加载）
# ---------------------------------------------------------------------------


def _build_audit_tool(llm_invoke_fn: Any | None = None):
    """
    将 financial-audit Skill 封装为 LangChain 工具。
    当用户提及 三单合一、财务审计、发票校验 等时，由 LLM 触发该工具。
    """
    try:
        from langchain_core.tools import tool
        from skills_src.audit_skill import run_audit
        from decimal import Decimal
        import json
    except ImportError as e:
        raise ImportError(
            "financial-audit skill 未安装或路径不正确，请检查 skills_src.audit_skill"
        ) from e

    @tool
    async def financial_audit(
        invoice_data_json: str,
        contract_data_json: str | None = None,
        payment_data_json: str | None = None,
        amount_threshold: str = "100000",
    ) -> str:
        """
        执行三单合一财务审计：发票、对账单、合同比对。
        适用于：三单合一、财务审计、发票校验、payment verification。
        输入为 JSON 字符串，输出审计结论与 AuditTrail。
        """
        invoice_data = json.loads(invoice_data_json)
        contract_data = json.loads(contract_data_json) if contract_data_json else None
        payment_data = json.loads(payment_data_json) if payment_data_json else None
        threshold = Decimal(amount_threshold)

        conclusion, trail = await run_audit(
            invoice_data=invoice_data,
            contract_data=contract_data,
            payment_data=payment_data,
            llm_invoke_fn=llm_invoke_fn,
            amount_threshold=threshold,
        )
        return json.dumps(
            {"conclusion": conclusion.value, "audit_trail": trail.model_dump(mode="json")},
            ensure_ascii=False,
        )

    return financial_audit


async def build_tools(
    mcp_servers: dict[str, Any] | None = None,
    enable_audit_skill: bool = False,
    audit_llm_invoke_fn: Any | None = None,
) -> list:
    """
    构建工具列表：MCP 工具 + 可选 Skills。

    Args:
        mcp_servers: MCP 服务器配置，例如 {"math": {...}}
        enable_audit_skill: 是否启用 financial-audit
        audit_llm_invoke_fn: 审计 Skill 使用的 LLM 调用函数（可选）

    Returns:
        供 ToolNode 使用的 tools 列表
    """
    tools: list = []

    # 1. MCP 工具
    if mcp_servers:
        from langchain_mcp_adapters.client import MultiServerMCPClient

        client = MultiServerMCPClient(mcp_servers)
        mcp_tools = await client.get_tools()
        tools.extend(mcp_tools)

    # 2. Skills
    if enable_audit_skill:
        audit_tool = _build_audit_tool(llm_invoke_fn=audit_llm_invoke_fn)
        tools.append(audit_tool)

    return tools
