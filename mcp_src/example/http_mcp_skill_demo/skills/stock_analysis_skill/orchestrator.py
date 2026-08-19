"""股票估值分析 Skill 的实现（确定性规则，不依赖 LLM 发挥）

与 skills_src/audit_skill 同一设计原则：
- 数值计算全部走确定性规则（Decimal 精确计算），绝不让模型估算数字
- skill 内部可以包装内部 API / 数据库 / 模型，此处用内置表模拟行情
"""

from decimal import Decimal

# 模拟的财务数据：每股收益 EPS（元/股）；生产环境替换为真实行情接口
_EPS_TABLE = {
    "AAPL": Decimal("6.50"),
    "MSFT": Decimal("11.20"),
    "TSLA": Decimal("3.10"),
    "600519": Decimal("55.30"),  # 贵州茅台（示例代码）
}

# 估值判断规则：PE 区间 → 结论
_RULES = [
    (Decimal("0"), Decimal("15"), "低估：PE 低于行业均值，可关注"),
    (Decimal("15"), Decimal("30"), "合理：PE 处于正常区间"),
    (Decimal("30"), Decimal("50"), "偏高：PE 高于行业均值，注意回调风险"),
    (Decimal("50"), None, "高估：PE 显著偏高，谨慎介入"),
]


def run_analysis(symbol: str, price: float) -> str:
    """股票估值分析入口（skill.yaml 的 entry 指向本函数）。

    Args:
        symbol: 股票代码，如 AAPL / 600519。
        price: 当前股价（元或美元）。

    Returns:
        一段结构化的估值分析结论。
    """
    symbol = symbol.upper()
    eps = _EPS_TABLE.get(symbol)
    if eps is None:
        return f"未收录股票 {symbol} 的财务数据，无法分析"

    # 用 Decimal 精确计算市盈率 = 股价 / 每股收益
    pe = Decimal(str(price)) / eps

    # 按规则表给出估值结论
    verdict = "未知"
    for low, high, label in _RULES:
        if low <= pe < high if high is not None else low <= pe:
            verdict = label
            break

    return (
        f"【{symbol} 估值分析】\n"
        f"- 每股收益 EPS: {eps} 元/股\n"
        f"- 当前股价: {price}\n"
        f"- 市盈率 PE: {pe.quantize(Decimal('0.01'))}\n"
        f"- 结论: {verdict}"
    )
