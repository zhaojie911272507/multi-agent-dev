# Harness 实践模块

这里放本仓库的最小可运行评测 Harness 示例。

## 运行

需要先配置 `DEEPSEEK_API_KEY`，默认会使用 `deepseek-chat`。

```bash
python example/run_harness_demo.py
```

可选输出到 JSON：

```bash
python -m harness_src.weather_harness.runner --output /tmp/weather_harness.json
```

## 当前示例

- 默认评测天气 Agent
- 使用规则评分，不依赖外部评测平台
- 结果包含每个 case 的分数、是否调用工具、最终回答和汇总信息
