# 观察链/责任链模式 (Chain of Responsibility)
# 场景：多阶段AI处理流水线（如：数据清洗 → 特征提取 → 模型推理 → 结果后处理）
# 优势：解耦处理步骤，灵活增删阶段（例如动态插入数据校验模块）
# AI实例：图像处理流程中，动态组合超分辨率预处理与目标检测模型链


# AI处理流水线：文本清洗 → 特征提取 → 模型推理 → 结果格式化
from abc import ABC, abstractmethod


class Handler(ABC):
    def __init__(self, successor=None):
        self._successor = successor

    @abstractmethod
    def handle(self, request):
        pass


class TextCleaner(Handler):
    def handle(self, request):
        if "text" not in request:
            raise ValueError("Missing text input")

        # 模拟文本清洗
        request['clean_text'] = request['text'].lower().strip()
        print(f"Cleaned text: {request['clean_text']}")

        if self._successor:
            return self._successor.handle(request)


class FeatureExtractor(Handler):
    def handle(self, request):
        # 模拟特征提取
        request['features'] = [ord(c) for c in request['clean_text'][:5]]
        print(f"Extracted features: {request['features']}")

        if self._successor:
            return self._successor.handle(request)


class ModelInference(Handler):
    def handle(self, request):
        # 模拟模型推理 (平均ASCII值作为预测结果)
        request['prediction'] = sum(request['features']) / len(request['features'])
        print(f"Model prediction: {request['prediction']:.2f}")

        if self._successor:
            return self._successor.handle(request)


class ResultFormatter(Handler):
    def handle(self, request):
        # 格式化输出
        return {
            "input": request['text'],
            "result": f"AI Score: {request['prediction']:.2f}"
        }


# 构建责任链
pipeline = TextCleaner(
    FeatureExtractor(
        ModelInference(
            ResultFormatter()
        )
    )
)

# 执行处理流程
input_data = {"text": "  AI Design Patterns  "}
result = pipeline.handle(input_data)
print("Final Result:", result)