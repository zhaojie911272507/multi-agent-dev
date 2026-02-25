# app/main.py（API层+意图识别层）
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI(title="MCP用户意图识别服务")

# 加载意图识别模型（使用HuggingFace的微调模型）
classifier = pipeline(
    "text-classification",
    model="mrm8488/bert-tiny-finetuned-intent-recognition",  # 示例模型
    return_all_scores=True
)

# 支持的意图映射
INTENT_MAPPING = {
    "deploy_container": "部署容器",
    "get_resource_status": "查看资源状态",
    "scale_resource": "扩缩容资源",
    "delete_resource": "删除资源"
}


class UserInput(BaseModel):
    text: str  # 用户输入文本，如"帮我启动3个Nginx容器"


class IntentResult(BaseModel):
    intent: str  # 识别的意图（中文）
    confidence: float  # 置信度
    mcp_command: str  # 生成的MCP指令


@app.post("/recognize", response_model=IntentResult)
async def recognize_intent(input: UserInput):
    # 1. 意图识别
    results = classifier(input.text)[0]
    top_intent = max(results, key=lambda x: x["score"])
    intent_label = top_intent["label"]
    confidence = top_intent["score"]

    # 2. 生成MCP指令（简化逻辑，实际需解析参数）
    mcp_command = ""
    if intent_label == "deploy_container":
        mcp_command = "kubectl create deployment nginx --image=nginx:latest --replicas=1"
    elif intent_label == "get_resource_status":
        mcp_command = "kubectl get pods"
    # 其他意图指令生成逻辑...

    return {
        "intent": INTENT_MAPPING.get(intent_label, "未知意图"),
        "confidence": round(confidence, 3),
        "mcp_command": mcp_command
    }

# 启动命令：uvicorn app.main:app --host 0.0.0.0 --port 8000