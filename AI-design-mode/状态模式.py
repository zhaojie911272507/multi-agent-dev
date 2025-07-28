# -*- coding: utf-8 -*-
"""
状态模式实现：AI推理状态管理器
演示AI系统在不同状态下的行为变化：
1. 空闲状态(IdleState) → 初始状态
2. 准备状态(PreparingState) → 加载模型/数据
3. 运行状态(RunningState) → 执行推理
4. 维护状态(MaintenanceState) → 系统更新
"""

import time
from abc import ABC, abstractmethod


class InferenceState(ABC):
    """抽象状态接口"""

    @abstractmethod
    def handle_request(self, context):
        """处理请求方法"""
        pass

    @abstractmethod
    def switch_state(self, context, new_state):
        """切换状态方法"""
        pass


class IdleState(InferenceState):
    """空闲状态：系统待命"""

    def handle_request(self, context):
        print("🟢 系统处于空闲状态，等待指令...")
        print("输入 'start' 开始处理，'maintenance' 进入维护模式")

    def switch_state(self, context, new_state):
        context.state = new_state


class PreparingState(InferenceState):
    """准备状态：加载资源"""

    def handle_request(self, context):
        print("🟡 进入准备状态，加载模型和数据...")
        time.sleep(1.5)  # 模拟加载过程
        print("✅ 模型加载完成，资源准备就绪")
        self.switch_state(context, RunningState())

    def switch_state(self, context, new_state):
        context.state = new_state


class RunningState(InferenceState):
    """运行状态：执行推理任务"""

    def handle_request(self, context):
        print("🚀 进入运行状态，开始AI推理...")
        try:
            # 模拟实际推理过程
            for i in range(1, 4):
                print(f"▶️ 正在处理第 {i} 批数据...")
                time.sleep(0.8)

            # 生成模拟结果
            print(f"📊 推理结果: {{'score': 0.92}}")

            # 自动转回空闲状态
            self.switch_state(context, IdleState())

        except Exception as e:
            print(f"❌ 推理过程中发生错误: {e}")
            self.switch_state(context, MaintenanceState())

    def switch_state(self, context, new_state):
        context.state = new_state


class MaintenanceState(InferenceState):
    """维护状态：系统更新/修复"""

    def handle_request(self, context):
        print("🛠️ 进入维护状态，开始系统更新...")

        # 模拟更新过程
        steps = [
            "验证依赖库...",
            "下载模型更新...",
            "应用安全补丁...",
            "清理缓存..."
        ]

        for step in steps:
            print(f"⏳ {step}")
            time.sleep(1.2)

        print("✅ 系统维护完成")

        # 自动转回空闲状态
        self.switch_state(context, IdleState())

    def switch_state(self, context, new_state):
        context.state = new_state


class AIInferenceSystem:
    """AI推理系统（上下文类）"""

    def __init__(self):
        # 初始状态为空闲
        self.state = IdleState()

    def request(self, user_input=None):
        """处理用户请求"""
        if user_input == "start" and isinstance(self.state, IdleState):
            self.state.switch_state(self, PreparingState())
        elif user_input == "maintenance":
            self.state.switch_state(self, MaintenanceState())

        # 执行当前状态的处理
        self.state.handle_request(self)


# 客户端代码：模拟用户与AI系统交互
if __name__ == "__main__":
    # 创建AI推理系统
    ai_system = AIInferenceSystem()

    print("\n==== AI推理系统启动 ====")

    # 初始状态处理
    ai_system.request()

    # 开始处理请求
    print("\n用户输入: 'start'")
    ai_system.request("start")

    # 等待3秒后直接进入维护模式
    time.sleep(3)
    print("\n用户输入: 'maintenance'")
    ai_system.request("maintenance")

    # 返回空闲状态
    print("\n系统当前状态:")
    ai_system.request()
