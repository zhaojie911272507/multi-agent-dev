# 单例模式用于确保一个类只有一个实例，并提供全局访问点
# 单例模式代码示例
# 单例模式用于确保一个类只有一个实例，并提供全局访问点。以下是Python实现：

# 单例模式Python实现
#
# 关键技术点说明
# 线程安全双重检查锁
# 使用类变量_instance存储单例实例
# 线程锁确保多线程环境下安全初始化
# 减少锁竞争提高性能

# 延迟初始化
# 仅在首次访问时实例化
# 避免不必要的资源开销

# 单例特征
# __new__方法控制实例创建
# 返回已存在实例而非创建新对象
# 多线程/多次访问返回相同实例

import threading
class ModelConfigManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ModelConfigManager, cls).__new__(cls)
                    # 初始化操作
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """初始化配置数据"""
        print("Initializing model configuration manager...")
        self.config = {
            "max_batch_size": 32,
            "precision": "fp16",
            "cache_size": "10GB"
        }

    def get_config(self, key):
        return self.config.get(key, None)

    def update_config(self, key, value):
        with self._lock:
            self.config[key] = value
            print(f"Updated config: {key} = {value}")


# 测试单例模式
if __name__ == "__main__":

    def access_config(thread_id):
        manager = ModelConfigManager()
        print(f"Thread {thread_id} config:", manager.config)
        if thread_id == 1:
            manager.update_config("max_batch_size", 64)


    # 多线程测试
    threads = []
    for i in range(1, 4):
        t = threading.Thread(target=access_config, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # 单线程验证
    manager1 = ModelConfigManager()
    manager2 = ModelConfigManager()
    print("Same instance?" if manager1 is manager2 else "Different instances")
    print("Final config:", manager1.config)
