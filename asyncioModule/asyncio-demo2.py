import asyncio
import random
import time
from datetime import datetime


# 1. 异步任务执行器 - 模拟不同类型的异步任务
async def async_task(task_id: int, task_type: str):
    """执行不同类型的异步任务"""
    start_time = time.time()
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] 任务 {task_id} ({task_type}) 开始")

    try:
        # 根据任务类型执行不同的异步操作
        if task_type == "io":
            # 模拟IO密集型任务（如网络请求）
            await asyncio.sleep(random.uniform(0.5, 2.0))
        elif task_type == "cpu":
            # 模拟CPU密集型任务（在事件循环中运行计算）
            # 注意：真正的CPU密集型任务应该使用run_in_executor
            await asyncio.sleep(0.1)  # 模拟计算时间
            # 实际计算任务可以这样处理：
            # loop = asyncio.get_running_loop()
            # await loop.run_in_executor(None, cpu_intensive_function)
        elif task_type == "error":
            # 模拟可能失败的任务
            if random.random() < 0.3:
                raise ValueError(f"任务 {task_id} 随机失败")
            await asyncio.sleep(1.0)
        else:
            await asyncio.sleep(1.0)

        duration = time.time() - start_time
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] 任务 {task_id} 完成 ({duration:.2f}s)")
        return f"任务 {task_id} 结果"

    except Exception as e:
        duration = time.time() - start_time
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] 任务 {task_id} 失败: {str(e)} ({duration:.2f}s)")
        return None


# 2. 任务处理管道 - 使用信号量限制并发数
async def task_processing_pipeline(tasks: list, max_concurrency: int = 3):
    """使用信号量控制并发数的任务处理管道"""
    semaphore = asyncio.Semaphore(max_concurrency)
    results = []

    async def process_task(task):
        print(results,task)
        async with semaphore:  # 获取信号量，限制并发
            print("semaphore:",semaphore.__str__())
            return await async_task(*task)

    # 创建并等待所有任务完成
    tasks_to_run = [process_task(task) for task in tasks]
    print(f"taks_to_run的并发限制: {max_concurrency}, 任务总数: {len(tasks_to_run)}")
    results = await asyncio.gather(*tasks_to_run, return_exceptions=False)

    return results


# 3. 异步上下文管理器 - 资源管理
class AsyncResource:
    """模拟需要异步初始化和清理的资源"""

    def __init__(self, name):
        self.name = name

    async def __aenter__(self):
        print(f"初始化资源: {self.name}")
        await asyncio.sleep(0.5)  # 模拟初始化耗时
        return self

    async def __aexit__(self, exc_type, exc, tb):
        print(f"清理资源: {self.name}")
        await asyncio.sleep(0.3)  # 模拟清理耗时

    async def perform_operation(self):
        """使用资源的操作"""
        print(f"使用资源: {self.name}")
        await asyncio.sleep(1.0)
        return f"{self.name}操作结果"


# 4. 主异步函数
async def main():
    """主异步函数"""
    print("=" * 50)
    print("开始高级asyncio示例")
    print("=" * 50)

    # 创建任务列表 (任务ID, 任务类型)
    tasks = [
        (1, "io"),
        (2, "cpu"),
        (3, "io"),
        (4, "error"),
        (5, "io"),
        (6, "cpu"),
        (7, "error"),
        (8, "io"),
        (9, "cpu"),
        (10, "io")
    ]

    # 使用任务处理管道执行任务
    print("\n执行任务管道 (并发限制=3)")
    results = await task_processing_pipeline(tasks, max_concurrency=3)
    print(
        f"\n任务完成统计: 成功={len([r for r in results if r is not None])}, 失败={len([r for r in results if r is None])}")

    # 使用异步上下文管理器
    print("\n使用异步上下文管理器:")
    async with AsyncResource("数据库连接") as db_resource:
        result = await db_resource.perform_operation()
        print(f"资源操作结果: {result}")

    # 使用asyncio.wait处理不同完成时间的任务
    print("\n使用asyncio.wait处理任务:")
    task_coros = [async_task(i, "io") for i in range(11, 16)]
    tasks_set = {asyncio.create_task(coro) for coro in task_coros}

    # 等待任务完成，但最多等待2秒
    done, pending = await asyncio.wait(tasks_set, timeout=2.0)
    print(f"已完成任务: {len(done)}, 仍在进行: {len(pending)}")

    # 取消剩余任务
    for task in pending:
        task.cancel()

    # 等待取消的任务完成
    await asyncio.gather(*pending, return_exceptions=True)

    print("\n所有任务处理完成")


# 5. 运行主函数
if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    print(f"\n总执行时间: {time.time() - start_time:.2f}秒")
