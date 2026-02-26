"""
Example: Wire LLM into ContractConsistencySkill.
Replace with your actual LangChain/OpenAI call.

Run from project root: python skills_src/audit_skill/examples/llm_integration.py
"""
import sys
from pathlib import Path

# Ensure project root in path
_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))

from skills_src.audit_skill import run_audit


async def _llm_invoke(prompt: str) -> str:
    """Example: LangChain LLM call. Replace with your implementation."""
    try:
        from langchain_core.messages import HumanMessage
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content if hasattr(response, "content") else str(response)
    except ImportError:
        # Fallback: return low-confidence stub
        return "CONFIDENCE: 0\nREASONING: LLM not configured"


async def main() -> None:
    invoice_data = [
        {
            "line_id": "L001",
            "amount": "50000",
            "tax_rate": "0.13",
            "tax_amount": "6500",
            "source_file": "inv_001.pdf",
        }
    ]
    contract_text = "合同约定按项目进度支付，每完成一个里程碑支付20%。"
    payment_text = "本次申请对应第三里程碑，已提交项目报告。"

    conclusion, trail = await run_audit(
        invoice_data=invoice_data,
        contract_data=contract_text,
        payment_data=payment_text,
        llm_invoke_fn=_llm_invoke,
    )
    print(f"Conclusion: {conclusion}")
    print(f"AuditTrail: {trail.model_dump(mode='json')}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
