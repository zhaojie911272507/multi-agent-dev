from abc import ABC, abstractmethod
from typing import List

# 统一不同AI框架的推理接口
class TensorFlowModel:
    def predict_tf(self, input_data: List[int]) -> str:
        return f"TF: {sum(input_data)}"  # 模拟TF预测


class PyTorchModel:
    def infer_pt(self, data: List[int]) -> str:
        return f"PT: {max(data)}"  # 模拟PyTorch预测


class AIAdapter(ABC):
    @abstractmethod
    def predict(self, data: List[int]) -> str:
        pass


class TFAdapter(AIAdapter):
    def __init__(self, tf_model: TensorFlowModel):
        self.model = tf_model

    def predict(self, data: List[int]) -> str:
        # 转换TF输入格式
        return self.model.predict_tf(data)


class PTAdapter(AIAdapter):
    def __init__(self, pt_model: PyTorchModel):
        self.model = pt_model

    def predict(self, data: List[int]) -> str:
        # 转换PyTorch输入格式
        return self.model.infer_pt(data)


# 客户端统一调用
def client_code(adapter: AIAdapter, data: List[int]) -> str:
    return adapter.predict(data)


# 使用示例
tf_adapter = TFAdapter(TensorFlowModel())
pt_adapter = PTAdapter(PyTorchModel())

print(client_code(tf_adapter, [1, 2, 3]))  # TF: 6
print(client_code(pt_adapter, [1, 2, 3]))  # PT: 3