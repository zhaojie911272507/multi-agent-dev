# 门面模式 (Facade)
# 统一网关：提供/ai-api/v1/predict整合多个内部复杂子系统
# 简化：客户端只需关心输入/输出，忽略多模型协调细节


# 简化复杂AI系统的统一接口
class Preprocessor:
    def run(self, data):
        return f"Processed: {data.strip()}"


class ModelService:
    def predict(self, data):
        return f"AI Result: {hash(data) % 100}"


class Postprocessor:
    def format(self, result):
        return {"prediction": result}


class AIFacade:
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.model = ModelService()
        self.postprocessor = Postprocessor()

    def execute(self, raw_data):
        clean_data = self.preprocessor.run(raw_data)
        raw_result = self.model.predict(clean_data)
        return self.postprocessor.format(raw_result)


# 客户端简单调用
facade = AIFacade()
print(facade.execute(" who is  the  best  AI  model "))
# 输出: {'prediction': 'AI Result: 42'}