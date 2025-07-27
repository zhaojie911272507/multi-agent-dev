import asyncio
import time
import threading
import random
from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Any


class TaskState(Enum):
    PENDING = "等待中"
    PROCESSING = "处理中"
    COMPLETED = "已完成"
    FAILED = "失败"


@dataclass
class AIProgress:
    current_step: int
    total_steps: int
    status_message: str


class AsyncObserver:
    """观察者模式基础类"""

    def __init__(self):
        self._callbacks = []

    def subscribe(self, callback: Callable):
        """订阅状态更新"""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unsubscribe(self, callback: Callable):
        """取消订阅"""
        self._callbacks.remove(callback)

    def notify(self, *args, **kwargs):
        """通知所有订阅者"""
        for callback in self._callbacks:
            callback(*args, **kwargs)


class AIAsyncPromise(AsyncObserver):
    """AI任务Promise对象，结合Observer模式"""

    def __init__(self, task_id: str):
        super().__init__()
        self.task_id = task_id
        self.state = TaskState.PENDING
        self.result = None
        self.error = None
        self.progress = AIProgress(0, 1, "初始化任务")
        self.lock = threading.Lock()

    def update_state(self, new_state: TaskState, message: str = None):
        """更新任务状态并通知订阅者"""
        with self.lock:
            self.state = new_state
            if message:
                self.progress.status_message = message
            self.notify(self)

    def update_progress(self, current: int, total: int, message: str = None):
        """更新进度并通知订阅者"""
        with self.lock:
            self.progress.current_step = current
            self.progress.total_steps = total
            if message:
                self.progress.status_message = message
            self.notify(self)

    def set_result(self, result: Any):
        """设置任务结果并标记为完成"""
        with self.lock:
            self.result = result
            self.update_state(TaskState.COMPLETED, "任务执行成功")

    def set_error(self, error: Exception):
        """设置错误并标记为失败"""
        with self.lock:
            self.error = error
            self.update_state(TaskState.FAILED, f"任务失败: {str(error)}")

    def __repr__(self):
        return (f"<AIAsyncPromise task_id={self.task_id} state={self.state.name} "
                f"progress={self.progress.current_step}/{self.progress.total_steps}>")


class AIAsyncOrchestrator:
    """AI任务异步编排器"""

    def __init__(self):
        self.tasks = {}

    def create_task(self, task_name: str) -> AIAsyncPromise:
        """创建新异步任务"""
        task_id = f"task-{int(time.time() * 1000)}"
        promise = AIAsyncPromise(task_id)
        self.tasks[task_id] = promise
        return promise

    async def execute_ai_task(self, promise: AIAsyncPromise, workflow: List[Callable]):
        """执行AI工作流（模拟长时间任务）"""
        try:
            promise.update_state(TaskState.PROCESSING, "启动工作流")
            await asyncio.sleep(0.1)  # 模拟延迟

            # 顺序执行工作流中的每个步骤
            for step_idx, step_fn in enumerate(workflow, 1):
                promise.update_progress(step_idx, len(workflow),
                                        f"执行步骤 {step_idx}/{len(workflow)}")
                result = await step_fn()
                await asyncio.sleep(0.1)  # 模拟处理时间

            promise.set_result("AI任务完成")
        except Exception as e:
            promise.set_error(e)
        finally:
            return promise


class AIWorkflows:
    """预定义的AI工作流集合"""

    @staticmethod
    async def image_processing():
        """模拟图像处理流程"""
        steps = len(AIWorkflows.IMG_STEPS)
        for i, step in enumerate(AIWorkflows.IMG_STEPS):
            await asyncio.sleep(random.uniform(0.1, 0.3))
            print(f"图像处理步骤: {step}")
        return f"图像处理完成 {steps} 步"

    @staticmethod
    async def nlp_analysis():
        """模拟NLP处理流程"""
        steps = len(AIWorkflows.NLP_STEPS)
        for i, step in enumerate(AIWorkflows.NLP_STEPS):
            await asyncio.sleep(random.uniform(0.05, 0.2))
            print(f"NLP分析步骤: {step}")
        return f"NLP分析完成 {steps} 步"

    # 预定义工作流步骤
    IMG_STEPS = [
        "图像解码", "噪声消除", "特征提取", "目标检测", "结果可视化"
    ]

    NLP_STEPS = [
        "文本清洗", "分词处理", "命名实体识别",
        "情感分析", "语义理解", "结果生成"
    ]


def progress_callback(promise: AIAsyncPromise):
    """进度回调函数"""
    progress = promise.progress
    print(f"[回调] 任务 {promise.task_id[:8]} - {progress.status_message} "
          f"({progress.current_step}/{progress.total_steps})")


def result_callback(promise: AIAsyncPromise):
    """结果回调函数"""
    if promise.state == TaskState.COMPLETED:
        print(f"\n✅ 任务完成: {promise.task_id[:8]} - 结果: {promise.result}")
    elif promise.state == TaskState.FAILED:
        print(f"\n❌ 任务失败: {promise.task_id[:8]} - 错误: {promise.error}")


def simulate_long_running_tasks():
    """模拟多个长时间运行的AI任务"""
    orchestrator = AIAsyncOrchestrator()

    # 创建三个不同类型的任务
    image_task = orchestrator.create_task("图像处理")
    nlp_task = orchestrator.create_task("NLP分析")
    batch_task = orchestrator.create_task("批量数据处理")

    # 注册回调函数
    image_task.subscribe(progress_callback)
    image_task.subscribe(result_callback)

    nlp_task.subscribe(progress_callback)
    nlp_task.subscribe(result_callback)

    batch_task.subscribe(progress_callback)
    batch_task.subscribe(result_callback)

    # 定义工作流
    image_workflow = [
        lambda: AIWorkflows.image_processing(),
        lambda: AIWorkflows.nlp_analysis()
    ]

    nlp_workflow = [
        lambda: AIWorkflows.nlp_analysis(),
        lambda: AIWorkflows.image_processing(),
        lambda: AIWorkflows.nlp_analysis()
    ]

    batch_workflow = [
        lambda: asyncio.sleep(0.5),
        lambda: AIWorkflows.image_processing(),
        lambda: asyncio.sleep(0.3),
        lambda: AIWorkflows.nlp_analysis(),
        lambda: asyncio.sleep(0.4)
    ]

    # 使用线程池异步执行任务
    def run_task(loop, promise, workflow):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            orchestrator.execute_ai_task(promise, workflow)
        )

    # 创建并启动任务线程
    loops = [asyncio.new_event_loop() for _ in range(3)]
    threads = [
        threading.Thread(
            target=run_task,
            args=(loops[0], image_task, image_workflow)
        ),
        threading.Thread(
            target=run_task,
            args=(loops[1], nlp_task, nlp_workflow)
        ),
        threading.Thread(
            target=run_task,
            args=(loops[2], batch_task, batch_workflow)
        )
    ]

    print("开始执行所有AI任务...")
    for t in threads:
        t.start()

    # 等待所有任务完成
    for t in threads:
        t.join()

    print("\n所有任务执行完毕！")


if __name__ == "__main__":
    simulate_long_running_tasks()
