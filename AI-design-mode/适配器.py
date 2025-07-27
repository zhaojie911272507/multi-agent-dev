# 适配器模式 (Adapter)
# 场景：统一不同AI框架接口（TensorFlow/PyTorch/ONNX Runtime）
# 实现：创建InferenceAdapter接口，为每个框架实现transform_request()方法
# 示例：将Hugging Face模型API封装成统一预测接口



from abc import ABC, abstractmethod


class AIModelInterface(ABC):
    """AI模型统一接口规范"""

    @abstractmethod
    def predict(self, input_data):
        """模型预测方法"""
        pass


class TensorFlowModel:
    """TensorFlow模型实现"""

    def predict_tf(self, input_data):
        """TensorFlow特定预测方法"""
        if not input_data:
            raise ValueError("输入数据不能为空")
        return {"framework": "TensorFlow", "result": sum(input_data)}


class PyTorchModel:
    """PyTorch模型实现"""

    def infer_pt(self, input_data):
        """PyTorch特定推理方法"""
        if not input_data:
            raise ValueError("输入数据不能为空")
        return {"framework": "PyTorch", "result": max(input_data)}


class BaseAdapter(AIModelInterface):
    """适配器基类"""

    def __init__(self, model):
        if not hasattr(model, self._required_method()):
            raise TypeError(f"模型必须实现 {self._required_method()} 方法")
        self.model = model

    @abstractmethod
    def _required_method(self):
        """子类需指定的模型方法名"""
        pass

    @abstractmethod
    def _transform_input(self, input_data):
        """输入数据转换方法"""
        pass


class TensorFlowAdapter(BaseAdapter):
    """TensorFlow适配器"""

    def _required_method(self):
        return "predict_tf"

    def _transform_input(self, input_data):
        """转换输入为TensorFlow所需格式"""
        if not isinstance(input_data, list):
            return [float(input_data)]
        return input_data

    def predict(self, input_data):
        data = self._transform_input(input_data)
        return self.model.predict_tf(data)


class PyTorchAdapter(BaseAdapter):
    """PyTorch适配器"""

    def _required_method(self):
        return "infer_pt"

    def _transform_input(self, input_data):
        """转换输入为PyTorch所需格式"""
        if isinstance(input_data, list):
            return input_data
        return [input_data]

    def predict(self, input_data):
        data = self._transform_input(input_data)
        return self.model.infer_pt(data)


def unified_inference(adapter, input_data):
    """
    统一调用不同框架的模型

    Args:
        adapter: 适配器实例 (TensorFlowAdapter/PyTorchAdapter)
        input_data: 输入数据

    Returns:
        标准化的预测结果字典
    """
    if not isinstance(adapter, AIModelInterface):
        raise TypeError("必须提供有效的适配器实例")
    return adapter.predict(input_data)


# 测试用例
if __name__ == "__main__":
    # 创建模型实例
    tf_model = TensorFlowModel()
    pt_model = PyTorchModel()

    # 创建适配器实例
    tf_adapter = TensorFlowAdapter(tf_model)
    pt_adapter = PyTorchAdapter(pt_model)

    # 统一调用测试
    print("TensorFlow 测试:")
    print("数值列表:", unified_inference(tf_adapter, [1, 2, 3]))
    print("单数值:", unified_inference(tf_adapter, 5))

    print("\nPyTorch 测试:")
    print("数值列表:", unified_inference(pt_adapter, [1, 2, 3]))
    print("单数值:", unified_inference(pt_adapter, 5))

    # 错误处理测试
    try:
        print("\n无效输入测试:", unified_inference(tf_adapter, None))
    except Exception as e:
        print(f"错误捕获: {str(e)}")
