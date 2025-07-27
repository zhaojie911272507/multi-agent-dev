# 为模型添加监控和验证
import time


def log_execution(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"Executed {func.__name__} in {end-start:.4f}s")
        return result
    return wrapper

def validate_input(func):
    def wrapper(*args, **kwargs):
        data = kwargs.get('data', "")
        if len(data) < 3:
            raise ValueError("Input too short")
        if len(data) > 100:
            raise ValueError("Input too long")
        return func(*args, **kwargs)
    return wrapper

class AIService:
    @log_execution
    @validate_input
    def predict(self, data=""):
        # 模拟模型处理
        time.sleep(0.5)
        return f"Processed: {data[::-1]}"

# 使用装饰后的服务
service = AIService()
print(service.predict(data="hello"))  # 正常执行
try:
    service.predict(data="a")  # 触发验证
except ValueError as e:
    print("Validation Error:", e)
