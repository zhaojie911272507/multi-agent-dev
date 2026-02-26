# Financial Audit Skill — 财务数据自动审计

生产级三单合一校验（发票、对账单、合同），强调**不可篡改性**、**规则合规性**、**异常溯源**。

## 目录结构

```
audit_skill/
├── skill.yaml          # 意图定义：何时调用
├── validators.py       # 硬规则：税率、黑名单
├── ai_analyzer.py      # 软逻辑：合同条款语义对齐
├── desensitizer.py     # 数据脱敏（AI 逻辑前必须执行）
├── circuit_breaker.py  # 断路器：金额 > 10万 → 人工审核
├── orchestrator.py     # 编排流程
├── api_plugin.py       # FastAPI 插件（Async + Prometheus + Webhook）
├── models.py           # 数据模型
└── tests/              # 边界测试
```

## 核心原则

| 原则 | 实现 |
|------|------|
| **逻辑隔离** | `desensitizer` 在 AI 前脱敏 |
| **计算精确** | 全程 `decimal.Decimal`，禁止 AI 估算数值 |
| **可追溯** | `AuditTrail` 带 Line ID、Source File |
| **断路器** | 单笔 > $100,000 → `PENDING_HUMAN_REVIEW` |

## 运行

```bash
# 测试
cd skills_src && python -m pytest audit_skill/tests -v

# API 服务
cd skills_src/audit_skill && python api_plugin.py
# 或: uvicorn skills_src.audit_skill.api_plugin:create_app --factory --host 0.0.0.0 --port 8001
```

## 环境变量

- `AUDIT_WEBHOOK_URL`：企业微信/钉钉 Webhook，风险时推送告警

## 审计足迹

- `AuditTrail.json`：每次审计输出，含 `audit_id`、`reasoning_path`、`conclusion`
- `security_audit.log`：运行时由调用方按需写入（本模块不持久化中间变量）
