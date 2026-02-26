"""
FastAPI plugin for financial audit — async, Prometheus, webhook.
"""
import os
from contextlib import asynccontextmanager
from decimal import Decimal
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Prometheus (optional)
try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Histogram,
        generate_latest,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from .models import AuditConclusion
from .orchestrator import run_audit

# Metrics
if PROMETHEUS_AVAILABLE:
    AUDIT_TOTAL = Counter(
        "financial_audit_total",
        "Total audit requests",
        ["conclusion"],
    )
    AUDIT_DURATION = Histogram(
        "financial_audit_duration_seconds",
        "Audit processing duration",
    )
    AI_RECALL_RATE = Counter(
        "financial_audit_ai_recall_total",
        "AI-triggered human review count",
    )


class AuditRequest(BaseModel):
    invoice_data: dict[str, Any] | list[dict[str, Any]]
    contract_data: dict[str, Any] | str | None = None
    payment_data: dict[str, Any] | str | None = None
    amount_threshold: str | None = Field(
        default="100000", description="Decimal string"
    )


class WebhookNotifier:
    """Sends risk alerts to WeChat / DingTalk."""

    def __init__(
        self,
        webhook_url: str | None = None,
        enabled: bool | None = None,
    ) -> None:
        self.webhook_url = webhook_url or os.getenv("AUDIT_WEBHOOK_URL", "")
        self.enabled = enabled if enabled is not None else bool(self.webhook_url)

    async def notify_risk(
        self, audit_id: str, conclusion: str, message: str
    ) -> None:
        if not self.enabled or not self.webhook_url:
            return
        import httpx

        payload = {
            "msgtype": "text",
            "text": {
                "content": f"[财务审计告警] audit_id={audit_id} conclusion={conclusion} msg={message}"
            },
        }
        async with httpx.AsyncClient() as client:
            await client.post(self.webhook_url, json=payload)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Cleanup: no persistent intermediates


def create_app(llm_invoke_fn: Any | None = None) -> FastAPI:
    app = FastAPI(
        title="Financial Audit API",
        description="Three-way reconciliation (invoice, statement, contract)",
        version="1.0.0",
        lifespan=lifespan,
    )
    notifier = WebhookNotifier()

    @app.post("/api/v1/audit")
    async def audit_endpoint(req: AuditRequest) -> JSONResponse:
        """Async audit — processes PDFs/bulk in background."""
        import time

        start = time.perf_counter()
        threshold = (
            Decimal(req.amount_threshold or "100000") if req.amount_threshold else None
        )

        try:
            conclusion, trail = await run_audit(
                invoice_data=req.invoice_data,
                contract_data=req.contract_data,
                payment_data=req.payment_data,
                llm_invoke_fn=llm_invoke_fn,
                amount_threshold=threshold,
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        elapsed = time.perf_counter() - start
        if PROMETHEUS_AVAILABLE:
            AUDIT_TOTAL.labels(conclusion=conclusion.value).inc()
            AUDIT_DURATION.observe(elapsed)
            if conclusion == AuditConclusion.PENDING_HUMAN_REVIEW:
                AI_RECALL_RATE.inc()

        # Webhook on risk
        if conclusion in (
            AuditConclusion.CRITICAL_MISMATCH,
            AuditConclusion.PENDING_HUMAN_REVIEW,
        ):
            await notifier.notify_risk(
                trail.audit_id,
                conclusion.value,
                trail.reasoning_path[-1] if trail.reasoning_path else "",
            )

        return JSONResponse(
            content={
                "conclusion": conclusion.value,
                "audit_id": trail.audit_id,
                "audit_trail": trail.model_dump(mode="json"),
                "duration_seconds": round(elapsed, 4),
            }
        )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "financial-audit"}

    if PROMETHEUS_AVAILABLE:

        @app.get("/metrics")
        async def metrics():
            from fastapi.responses import Response

            return Response(
                content=generate_latest(),
                media_type=CONTENT_TYPE_LATEST,
            )

    return app


# Standalone run
if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8001)
