# LlamaIndex 百炼 Qwen 示例

使用百炼平台 Qwen 模型（OpenAI 兼容 API）的 LlamaIndex 示例。

## 依赖

```bash
pip install llama-index llama-index-llms-openai-like
```

## 配置

在 `.env` 中设置 `DASHSCOPE_API_KEY`。

## 运行

```bash
# 从项目根目录
python llama_index_src/main.py

# 或通过统一入口
python example/run_llama_index_demo.py
```

## 模块说明

| 文件       | 说明                         |
|------------|------------------------------|
| `config.py` | LLM 配置与实例（百炼兼容端点） |
| `examples.py` | Completion / Chat / Streaming / RAG 示例 |
| `main.py`  | 入口                         |
