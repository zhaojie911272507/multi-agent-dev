# 代理模式 (Proxy)
# 关键用途：
# 远程代理：封装gRPC/REST调用远端GPU服务器
# 缓存代理：对频繁请求的模型结果缓存（如对话历史缓存）
# 防护代理：请求限流与模型访问权限控制
# AI特化：动态切换模型版本（v1→v2）无需客户端修改


# 带缓存的模型代理
from functools import lru_cache
import time


class RealModel:
    def predict(self, input_data):
        """模拟耗时计算"""
        time.sleep(2)
        return sum(input_data) / len(input_data)


class ModelProxy:
    def __init__(self):
        self._model = RealModel()
        self.cache_enabled = True

    @lru_cache(maxsize=100)
    def _cached_predict(self, input_tuple):
        return self._model.predict(input_tuple)

    def predict(self, input_data):
        input_tuple = tuple(input_data)
        if self.cache_enabled:
            return self._cached_predict(input_tuple)
        return self._model.predict(input_data)


# 使用代理
proxy = ModelProxy()

# 首次请求 (耗时)
start = time.time()
print("Result:", proxy.predict([1, 2, 3, 4]), "Time:", time.time() - start)

# 相同请求 (缓存)
start = time.time()
print("Result:", proxy.predict([1, 2, 3, 4]), "Time:", time.time() - start)

# 关闭缓存
proxy.cache_enabled = False
start = time.time()
print("Result:", proxy.predict([1, 2, 3, 4]), "Time:", time.time() - start)