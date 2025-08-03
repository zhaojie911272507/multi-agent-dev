import asyncio
import time


# 1. 定义协程函数 - 使用 async def 声明
async def say_after(delay, message):
    # 使用 await 挂起当前协程，等待指定时间
    await asyncio.sleep(delay)
    print(f"[{time.strftime('%X')}] {message}")


# 2. 创建事件循环并运行协程
async def main():
    print(f"[{time.strftime('%X')}] 开始执行")

    # 3. 并行执行多个协程 - 同时等待多个任务完成
    await asyncio.gather(
        say_after(1, "任务1完成"),
        say_after(7, "任务2完成"),
        say_after(3, "任务3完成")
    )

    print(f"[{time.strftime('%X')}] 所有任务并行完成")
    print("-" * 40)

    # 4. 任务对象创建和管理
    print(f"[{time.strftime('%X')}] 创建独立任务")
    task1 = asyncio.create_task(say_after(2, "独立任务1完成"))
    task2 = asyncio.create_task(say_after(6, "独立任务2完成"))

    # 5. 等待特定任务完成
    await task1
    print(f"[{time.strftime('%X')}] 任务1已等待完成")

    # 6. 取消任务
    if not task2.done():
        print(f"[{time.strftime('%X')}] 取消任务2")
        task2.cancel()

        try:
            await task2
        except asyncio.CancelledError:
            print(f"[{time.strftime('%X')}] 任务2已被取消")

    print(f"[{time.strftime('%X')}] 主协程结束")


# 7. 使用 asyncio.run() 启动事件循环
if __name__ == "__main__":
    print("=== asyncio 核心功能演示 ===")
    # 启动主协程并管理事件循环
    asyncio.run(main())
    print("=== 程序结束 ===")
