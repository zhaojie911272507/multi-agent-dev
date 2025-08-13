import asyncio
import json
import time
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

# --- 配置日志记录 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ai_backend.log')
    ]
)
logger = logging.getLogger("ai-backend")

# --- 全局配置 ---
CONFIG = {
    "max_concurrent": 100,  # 最大并发请求数
    "max_batch_size": 32,  # 批处理最大大小
    "max_batch_time": 0.1,  # 批处理最大等待时间(秒)
    "model_cache_size": 2,  # 模型缓存数量
}


# --- 核心数据结构 ---
@dataclass
class AIRequest:
    request_id: str
    data: Any
    created_at: float = time.time()
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class AIResponse:
    request_id: str
    result: Any
    latency: float
    processed_at: float = time.time()


# --- 模型服务抽象层 ---
class AIModelAdapter:
    """统一模型接口适配器"""

    def __init__(self, model_name: str):
        self.model_name = model_name
        logger.info(f"Initialized model adapter for: {model_name}")

    async def warmup(self):
        """预热模型(加载权重等)"""
        logger.info(f"Warming up model: {self.model_name}")
        await asyncio.sleep(0.1)  # 模拟加载时间

    async def predict(self, inputs: List[Any]) -> List[Any]:
        """批量推理接口"""
        # 实际项目中替换为真实模型调用
        await asyncio.sleep(0.05)  # 模拟推理延迟

        # 模拟推理结果
        return [f"{self.model_name}: Result for {input} at {time.time()}"
                for input in inputs]

    async def health_check(self) -> bool:
        """模型健康检查"""
        return True


# --- 模型工厂(享元模式) ---
class ModelFactory:
    """模型工厂，提供模型实例的共享和复用"""

    _models = {}

    @classmethod
    async def get_model(cls, model_name: str) -> AIModelAdapter:
        """获取模型实例(共享)"""
        if model_name not in cls._models:
            model = AIModelAdapter(model_name)
            await model.warmup()
            cls._models[model_name] = model
            logger.info(f"Created new model instance: {model_name}")
        else:
            logger.info(f"Reusing cached model: {model_name}")
        return cls._models[model_name]


# --- 批处理系统 ---
class BatchProcessor:
    """智能批处理系统，提高吞吐量"""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.batch: List[AIRequest] = []
        self.batch_event = asyncio.Event()
        self.is_processing = False
        self.model = None
        logger.info(f"Initialized batch processor for: {model_name}")

    async def start_processing(self):
        """启动批处理任务循环"""
        asyncio.create_task(self._process_batches())

    async def add_request(self, request: AIRequest):
        """添加请求到批处理队列"""
        self.batch.append(request)

        # 触发批处理条件
        if len(self.batch) >= CONFIG["max_batch_size"]:
            self.batch_event.set()
            self.batch_event.clear()

    async def _process_batches(self):
        """批处理核心逻辑"""
        while True:
            # 等待触发条件：达到最大批处理大小或超时
            await asyncio.wait_for(
                self.batch_event.wait(),
                timeout=CONFIG["max_batch_time"]
            )

            if not self.batch:
                continue

            # 获取当前批处理
            current_batch = self.batch.copy()
            self.batch = []

            # 确保模型加载
            if not self.model:
                self.model = await ModelFactory.get_model(self.model_name)

            # 健康检查
            if not await self.model.health_check():
                logger.error(f"Model {self.model_name} health check failed!")
                for req in current_batch:
                    req.error = "Model unavailable"
                continue

            try:
                # 准备输入数据
                inputs = [req.data for req in current_batch]

                # 执行批量推理
                start_time = time.time()
                results = await self.model.predict(inputs)
                latency = time.time() - start_time

                # 分配结果
                for req, result in zip(current_batch, results):
                    req.result = AIResponse(
                        request_id=req.request_id,
                        result=result,
                        latency=latency
                    )
                logger.info(f"Processed batch of {len(current_batch)} requests in {latency:.4f}s")

            except Exception as e:
                logger.exception("Batch processing failed")
                for req in current_batch:
                    req.error = f"Processing error: {str(e)}"


# --- 缓存服务(策略模式) ---
class PredictionCache:
    """带TTL的预测缓存服务"""

    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存结果"""
        if key in self.cache:
            result, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return result
            # 缓存过期
            del self.cache[key]
        return None

    async def set(self, key: str, value: Any):
        """设置缓存"""
        self.cache[key] = (value, time.time())


# --- 限流系统(责任链模式) ---
class RateLimiter:
    """令牌桶限流算法实现"""

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity  # 令牌桶容量
        self.tokens = capacity  # 当前令牌数量
        self.refill_rate = refill_rate  # 每秒补充速率(令牌/秒)
        self.last_refill = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """获取一个令牌，成功返回True"""
        async with self.lock:
            # 补充令牌
            current_time = time.time()
            time_elapsed = current_time - self.last_refill
            tokens_to_add = time_elapsed * self.refill_rate

            if tokens_to_add > 0:
                self.tokens = min(self.capacity, self.tokens + tokens_to_add)
                self.last_refill = current_time

            # 检查令牌
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False


# --- API服务核心 ---
class AIService:
    """AI后端服务核心"""

    def __init__(self):
        # 初始化各个组件
        self.rate_limiter = RateLimiter(
            capacity=CONFIG["max_concurrent"],
            refill_rate=CONFIG["max_concurrent"] / 10  # 每秒补充10%容量
        )
        self.cache = PredictionCache(ttl=300)
        self.processors = {}
        logger.info("AI Service initialized")

    def get_processor(self, model_name: str) -> BatchProcessor:
        """获取模型处理器(工厂方法)"""
        if model_name not in self.processors:
            processor = BatchProcessor(model_name)
            asyncio.create_task(processor.start_processing())
            self.processors[model_name] = processor
        return self.processors[model_name]

    async def process_request(self, request: AIRequest, model_name: str = "default") -> AIResponse:
        """处理单个AI请求(核心方法)"""
        start_time = time.time()

        # 1. 限流检查
        if not await self.rate_limiter.acquire():
            request.error = "Rate limit exceeded"
            return AIResponse(
                request_id=request.request_id,
                result=None,
                latency=time.time() - start_time,
                error="Rate limit exceeded"
            )

        # 2. 缓存检查
        cache_key = f"{model_name}:{request.data}"
        if cached_result := await self.cache.get(cache_key):
            logger.info(f"Cache hit for request {request.request_id}")
            return AIResponse(
                request_id=request.request_id,
                result=cached_result,
                latency=0.001,
                processed_at=time.time()
            )

        # 3. 添加到批处理队列
        processor = self.get_processor(model_name)
        await processor.add_request(request)

        # 4. 等待结果(带超时)
        try:
            await asyncio.wait_for(
                asyncio.shield(request.result),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            request.error = "Processing timeout"

        # 5. 缓存结果
        if request.result and not request.error:
            await self.cache.set(cache_key, request.result)

        return request.result or AIResponse(
            request_id=request.request_id,
            result=None,
            latency=time.time() - start_time,
            error=request.error or "Unknown error"
        )

    @asynccontextmanager
    async def lifespan(self):
        """应用生命周期管理"""
        logger.info("Starting AI service...")
        yield
        logger.info("Shutting down AI service...")


# --- API端点(使用FastAPI风格) ---
ai_service = AIService()


@lru_cache(maxsize=CONFIG["model_cache_size"])
async def get_cached_model(model_name: str):
    """带缓存的模型获取(减少模型加载开销)"""
    return await ModelFactory.get_model(model_name)


async def ai_inference_endpoint(request_id: str, input_data: Any, model_name: str = "default"):
    """API端点处理函数"""
    # 创建请求对象
    request = AIRequest(request_id=request_id, data=input_data)

    # 处理请求
    response = await ai_service.process_request(request, model_name)

    # 监控日志
    logger.info(f"Processed request {request_id} in {response.latency:.4f}s")

    return {
        "request_id": response.request_id,
        "result": response.result,
        "latency": response.latency,
        "error": response.error
    }


# --- 测试模拟 ---
async def simulate_clients(num_clients: int):
    """模拟多个并发客户端请求"""
    tasks = []
    for i in range(num_clients):
        request_id = f"req_{i}"
        input_data = f"input_{i % 10}"  # 10种不同输入模式
        tasks.append(ai_inference_endpoint(request_id, input_data))
    return await asyncio.gather(*tasks)


async def main():
    """主测试函数"""
    # 启动服务生命周期
    async with ai_service.lifespan():
        # 模拟客户端请求
        start_time = time.time()
        results = await simulate_clients(15) # 原100
        elapsed = time.time() - start_time

        # 分析结果
        success = sum(1 for res in results if not res.get('error'))
        cache_hits = sum(1 for res in results if res.get('latency', 0) < 0.01)
        avg_latency = sum(res.get('latency', 0) for res in results) / len(results)

        print(f"\n=== 性能报告 ===")
        print(f"总请求数: {len(results)}")
        print(f"成功请求: {success} ({success / len(results) * 100:.1f}%)")
        print(f"缓存命中: {cache_hits}")
        print(f"平均延迟: {avg_latency:.4f}s")
        print(f"总处理时间: {elapsed:.4f}s")
        print(f"吞吐量: {len(results) / elapsed:.2f} req/s")


# 运行测试
if __name__ == "__main__":
    asyncio.run(main())