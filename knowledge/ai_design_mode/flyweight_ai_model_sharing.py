# 享元模式AI模型共享 - 原文件: 享元模式AI模型共享.py
# 享元模式：共享相同配置的AI模型实例，减少内存占用

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
import threading


@dataclass(frozen=True)
class ModelKey:
    """不可变键类，标识模型"""
    model_name: str
    model_version: str
    quantized: bool


class AIModel(ABC):
    """抽象模型接口"""

    @abstractmethod
    def predict(self, input_data):
        pass


class ModelFlyweight(AIModel):
    """具体享元对象 - 包含模型实现和状态"""

    def __init__(self, model_key):
        self.model_key = model_key
        # 模拟加载大型模型权重
        self.weights = f"weights_{model_key.model_name}_{model_key.model_version}"
        print(f"🔄 加载模型: {model_key.model_name}-{model_key.model_version} "
              f"(量化={model_key.quantized}) - 权重大小: {len(self.weights)} MB")

    def predict(self, input_data):
        """模型预测方法"""
        # 模拟计算耗时
        time.sleep(0.5)

        # 模拟使用模型权重进行预测
        result = f"{self.weights.split('_')[1]}预测: 输入'{input_data}' → "
        if "图像" in input_data:
            return result + f"检测到{len(input_data)}个物体"
        elif "文本" in input_data:
            return result + f"情感分析:{'积极' if len(input_data) > 5 else '消极'}"
        else:
            return result + "未知类型"


class ModelFactory:
    """享元工厂 - 管理模型实例"""
    _models = {}
    _lock = threading.Lock()

    @classmethod
    def get_model(cls, model_key):
        """获取模型实例 - 如果存在则共享，否则创建"""
        if model_key not in cls._models:
            with cls._lock:
                # 双重检查锁定（线程安全）
                if model_key not in cls._models:
                    cls._models[model_key] = ModelFlyweight(model_key)
        return cls._models[model_key]


class Client:
    """客户端类 - 使用模型服务"""

    def __init__(self, name):
        self.name = name

    def make_request(self, model_key, input_data):
        """发起预测请求"""
        model = ModelFactory.get_model(model_key)

        print(f"👤 客户端[{self.name}]请求: {model_key.model_name}-{model_key.model_version}")
        start_time = time.time()
        result = model.predict(input_data)
        latency = time.time() - start_time

        print(f"✅ 返回结果: {result} | 延迟: {latency:.2f}s")
        return result


def main():
    """主函数 - 模拟多个客户端请求"""
    print("🌟 享元模式演示: AI模型资源共享系统")

    # 定义模型键
    resnet_model = ModelKey("ResNet50", "v2.1", False)
    bert_model = ModelKey("BERT", "base", False)
    bert_quant = ModelKey("BERT", "base", True)

    # 创建客户端
    clients = [
        Client("图像处理系统"),
        Client("NLP服务1"),
        Client("边缘设备"),
        Client("NLP服务2")
    ]

    # 模拟请求序列
    requests = [
        (resnet_model, "分析图像: 猫狗沙滩"),
        (bert_model, "处理文本: 今天天气真好"),
        (bert_quant, "分析文本: 产品质量改进建议"),
        (bert_model, "处理文本: 用户反馈报告"),
        (bert_quant, "处理文本: 设备日志分析"),
        (resnet_model, "分析图像: 医疗X光片")
    ]

    # 多线程处理请求
    threads = []
    results = {}

    def process_request(i, client, model_key, input_data):
        thread_id = threading.get_ident()
        results[i] = client.make_request(model_key, input_data)
        print(f"线程 {thread_id} 请求完成")

    print("\n=== 开始处理请求 ===")
    start_total = time.time()

    # 启动线程处理请求
    for i, (client, (model_key, input_data)) in enumerate(zip(clients * 2, requests)):
        t = threading.Thread(
            target=process_request,
            args=(i, client, model_key, input_data)
        )
        threads.append(t)
        t.start()

    # 等待所有线程完成
    for t in threads:
        t.join()

    total_time = time.time() - start_total
    print(f"\n=== 所有请求处理完成 | 总时间: {total_time:.2f}s ===")

    # 统计模型加载次数
    print("\n📊 资源使用统计:")
    print(f"创建的模型实例: {len(ModelFactory._models)}")
    print(f"资源复用情况: BERT模型加载了{1 if bert_model in ModelFactory._models else 0}次，但服务了4个请求")


if __name__ == "__main__":
    main()
